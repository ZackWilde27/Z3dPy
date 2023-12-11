# -zw
'''
Z3dPy v0.4.1
*Nightly build, wiki/examples are based on the release build

LEGEND:
- Parameters marked with * are optional

- Most parameters have a starting letter denoting type.
Capitals mean normalized.

- Functions are CapitalizedCamelCase, variables are regularCamelCase.


Change Notes:


DEFINING OBJECTS

- The parameters when defining objects now have the same name as the associated property, and there's a lot more of them.

Instead of putting in parameters in-line, you can now select which properties you want to be adjusted, in whatever order.

For example:
    myThing = z3dpy.Thing([myMesh], position=[1.0, 2.0, 3.0], rotation=[0.0, 90.0, 0.0], scale=[0.5, 0.5, 0.5])

    myMesh = z3dpy.Mesh([thatTri], frame=0, colour=(255, 0, 255), position=[4.0, 5.0, 6.0])

    This also extends to hitboxes and physics for things, so they can be given one when creating.
    myThing = z3dpy.Thing([myMesh], hitbox=z3dpy.Hitbox(z3dpy.HITBOX_BOX, 0, 1.0, 1.0), physics=z3dpy.PhysicsBody(mass=5.0, friction=0.5))

LoadMesh() now has the same parameters as defining a mesh, so properties can be set on creation.

    z3dpy.LoadMesh("filename.dae", rotation=[90.0, 10.0, 0.0], colour=(255, 0, 0), material=z3dpy.MATERIAL_UNLIT)

    z3dpy.LoadAniMesh("filename.aobj", scale=[0.5, 0.5, 0.5], visible=False)


FOV & ASPECT RATIO

- Split FindHowVars() into SetFOV() and SetAspectRatio(). SetHowVars() is now SetCameraConstants()
The old functions are still there for backwards compatibility


MATRIXES

- MatrixMakeProjection() has been renamed to ProjectionMatrix()

- LookAtMatrix() has been renamed to ViewMatrix()

- Combined MatrixMakeRot_() into RotationMatrix( axis, degrees )
    Select an axis with a vector ([0, 1, 0] to select y for instance)

    myMatrix = z3dpy.RotationMatrix([0, 0, 1], 90)

    for tri in z3dpy.Render():
        z3dpy.TriMatrixMul(tri, myMatrix)

MESHES

- LoadMesh() now supports STL files, and PLY files, both ASCII and binary.

- LoadMesh()'s fail-safe only applied to OBJ files, that has been fixed.

- Mesh() will now automatically SetColour() on creation if given one.

- Local shaders no longer overwrite the original triangle's colour.


TRIS

- Tris have been simplified, as they don't need to carry as much information all the way to the draw stage anymore.
They no longer store normals, or world position. TriGetWPos(), TriSetWPos(), and TriSetNormal() has been removed, TriGetNormal() now calculates the normal.

Use TriAverage() to get the center point, instead of TriGetWPos()

Use TriGetNormal() to get the normal, instead of GetNormal()


MISC

- WhatIs() will now print the class name of an object if it's not a list.

- PgDrawTri__ and TkDrawTri__ have been removed, use the material system to draw certain meshes differently.

- RotTo() has been renamed to VectorRotate(), and it's parameters have been flipped to match the new name. VectorRotate( vector, rotation )

- RemoveThing() no longer needs a layer argument, it's also stored.

- Fast()'s error message is less vague now.

'''

# Time for delta-time calculations
from time import perf_counter as time

# Rand for finding projection constants
from random import random as rand

# Unpack for loading binary mesh files
from struct import unpack

# Math for, well...
from math import sqrt, floor, ceil, sin, cos, tan

# z3dpyfast is imported at the bottom of the script to replace functions.

print("Z3dPy v0.4.1")

#==========================================================================
#  
# Variables
#
#==========================================================================

# Delta calculations
timer = time()

delta = 0.016666



def GetDelta():
    global delta
    global timer
    now = time()
    delta = now - timer
    timer = now
    return delta

gravity = (0, 9.8, 0)

screenSize = (1280, 720)

worldColour = (0.0, 0.0, 0.0)

airDrag = 0.02

# Internal list of lights
lights = []

# Internal list of emitters
emitters = []

# Internal list of rays
rays = []

# Internal things list in layers
#
# Layers are sorted separately, to make sure that
# certain things are drawn over others.
#
# If you need more layers, create a new tuple like so
# z3dpy.layers = ([], [], [], [], [], ...)
layers = ([], [], [], [])




#==========================================================================
#
# Objects
#
#==========================================================================

# Vector:
# Standard 3D vector
# [0] - [2] are the x y and z
def Vector(x, y, z):
    return [x, y, z]

# Vector2:
# [0] is u, [1] is v

def Vector2(u, v):
    return [u, v]

# Vector4:
# [0] - [2] are the x, y, and z
# [3] is W

def Vector4(x, y, z, w):
    return [x, y, z, w]

# VectorUV:
# Complicated Vectors for rendering.
# [0] - [2] are the x y and z
# [3] is normal
# [4] is UV

def VectorUV(x, y, z, VNormal=[0, 0, 0], UV=[0, 0]):
    return [x, y, z, VNormal, UV]

# Triangles / Tris:
# [0] - [2] are the 3 points
# [3] is the baked shade
# [4] is colour
# [5] is id
# [6] is the user variable

def Tri(vector1, vector2, vector3):
    if len(vector1) != 5:
        vector1 = vector1 + [[0, 0, 0], [0, 0]]
    if len(vector2) != 5:
        vector2 = vector2 + [[0, 0, 0], [0, 0]]
    if len(vector3) != 5:
        vector3 = vector3 + [[0, 0, 0], [0, 0]]
    return [vector1, vector2, vector3, (0.0, 0.0, 0.0), (255, 255, 255), 0, 0]

# Meshes:
#
# Colour is copied to triangles, used when drawing.
#
# Id is copied to triangles, as a way to check
# where a tri came from.
#

def SHADER_UNLIT(tri): return tri[4]

def SHADER_SIMPLE(tri): return VectorMulF(tri[4], max(-TriGetNormal(tri)[2], 0))

def SHADER_DYNAMIC(tri): return VectorMul(tri[4], CheapLighting(tri))

def SHADER_STATIC(tri): return VectorMul(tri[4], tri[3])

class Material():
    def Local(tri):
        return
    
    def World(tri):
        return

    def View(tri):
        return

    def __init__(self, local=SHADER_UNLIT, world=SHADER_UNLIT, view=SHADER_UNLIT):
        self.Local = local
        self.World = world
        self.View = view


MATERIAL_UNLIT = Material(view = SHADER_UNLIT)
MATERIAL_SIMPLE = Material(view = SHADER_SIMPLE)
MATERIAL_DYNAMIC = Material(world = SHADER_DYNAMIC)
MATERIAL_STATIC = Material(view = SHADER_STATIC)

class Mesh():
    def __init__(self, tris, position=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0], scale=[1.0, 1.0, 1.0], colour=(255, 255, 255), id=0, cull=True, material=MATERIAL_UNLIT, visible=True, frame=-1):
        self.tris = tris
        self.position = position
        self.rotation = rotation
        self.colour = colour
        self.scale = scale
        self.id = id
        self.cull = cull
        self.material = material
        self.frame = frame
        self.visible = visible
        self.user = 0
        if colour[0] == colour[1] == colour[2] == 255:
            self.SetColour(colour)

    def SetColour(self, vColour):
        self.colour = vColour
        if self.frame == -1:
            for tri in self.tris:
                TriSetColour(tri, vColour)
        else:
            for frame in self.tris:
                for tri in frame:
                    TriSetColour(tri, vColour)
    
    def AddPos(self, vector):
        self.position[0] += vector[0]
        self.position[1] += vector[1]
        self.position[2] += vector[2]
    
    def AddRot(self, vector):
        self.rotation[0] += vector[0]
        self.rotation[1] += vector[1]
        self.rotation[2] += vector[2]
    
    def GetClass(self):
        return "Mesh"
    
    def __repr__(self):
        if self.frame == -1:
            return "Z3dPy Mesh:\n\tTris: " + str(len(self.tris)) + "\n\tPosition: " + str(self.position) + "\n\tRotation: " + str(self.rotation) + "\n\tScale: " + str(self.scale) + "\n\tColour: " + str(self.colour) + "\n\tMaterial: " + str(self.material) + "\n\tId: " + str(self.id)

        else:
            return "Z3dPy AniMesh:\n\tTris: " + str(len(self.tris)) + "\n\tPosition: " + str(self.position) + "\n\tRotation: " + str(self.rotation) + "\n\tScale: " + str(self.scale) + "\n\tColour: " + str(self.colour) + "\n\tMaterial: " + str(self.material) + "\n\tId: " + str(self.id) + "\n\tFrame: " + str(self.frame)

trainMesh = Mesh((), [0, 0, 0])


# Hitbox Object:
#
# Stores all the needed info regarding collisions, the type
# of hitbox, it's scale, and collision id.
#
# Only hitboxes with the same id will collide.
#
# Enable collisions with z3dpy.ThingSetupHitbox(myThing)

# Type: 0 = Sphere, 2 = Cube
# Radius: radius of the sphere, or length/width of
# the cube
# Height: height of the cube.
# Id: Objects with the same ID will check for collisions.
# Everything is 0 by default, so if unsure, use that.


HITBOX_SPHERE = 0
#HITBOX_CYLINDER = 1
HITBOX_BOX = 2

hitboxTypes = ["Sphere", "Cylinder", "Box"]

class Hitbox():
    def __init__(self, type=2, id=0, radius=1, height=1):
        self.type = type
        self.id = id
        self.radius = radius
        self.height = height
        self.mesh = None
        self.user = 0
        self.UpdateVis()
    
    def UpdateVis(self):
        match self.type:
            case 2:
                self.mesh = LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [self.radius, self.height, self.radius])
            case _:
                self.mesh = LoadMesh("z3dpy/mesh/sphere.obj", [0, 0, 0], [self.radius, self.height, self.radius])
        self.mesh.SetColour([255, 0, 0])
        self.mesh.id = -1
    
    def GetClass(self):
        return "Hitbox"
    
    def __repr__(self):
        return "Z3dPy Hitbox:\n\tType: " + hitboxTypes[self.type] + "\n\tId: " + str(self.id) + "\n\tRadius: " + str(self.radius) + "\n\tHeight: " + str(self.height) + "\n\t"


# OldPhysics Body:
#
# Enable physics with z3dpy.ThingSetupPhysics(myThing)
#
# Mass determines the magnitude of force an object exterts when colliding, scaled by velocity.
#
# Friction controls how quickly the velocity falls off when hitting the ground. Also, when other
# things collide, their new velocity scales by the friction.
#
# Bounciness is usually 0-1, 1 means it'll bounce with no loss of speed, 0 means it won't bounce.
# this applies when hitting the ground, or hitting things that don't have physics.
#
# Drag is now a global variable, representing air resistance.

class PhysicsBody():
    def __init__(self, mass=0.5, friction=15, bounciness=0.5):
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.mass = mass
        self.friction = friction
        self.bounciness = bounciness
        self.rotVelocity = [0, 0, 0]
        self.rotAcceleration = [0, 0, 0]
        self.user = 0

    def __repr__(self):
        return "Z3dPy PhysicsBody:\n\tVelocity: " + str(self.velocity) + "\n\tAcceleration: " + str(self.acceleration) + "\n\tMass: " + str(self.mass) + "\n\tFriction: " + str(self.friction) + "\n\tBounciness: " + str(self.bounciness) + "\n\tRotational Velocity: " + str(self.rotVelocity) + "\n\tRotational Acceleration: " + str(self.rotAcceleration) + "\n\t"


# Things:
#
# The Thing is what you would typically refer to as an 
# object, it has a collection of meshes, and collision data.
#
# Hitbox and Physics body are None till you assign them.
#
# Internal id is usually the index for RemoveThing().
# -1 means it's a Dupe.
# -2 means the rotation value is the PointAt target

class Thing():
    def __init__(self, meshList, position=[0, 0, 0], rotation=[0, 0, 0], scale=[1.0, 1.0, 1.0], hitbox=None, physics=None, movable=True, visible=True):
        self.meshes = meshList
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.hitbox = hitbox
        self.physics = physics
        self.movable = movable
        self.internalid = 0
        self.visible = visible
        self.user = 0
    
    def __repr__(self):
        return "Z3dPy Thing:\n\tPosition: " + str(self.position) + "\n\tRotation: " + str(self.rotation) + "\n\tScale: " + str(self.scale) + "\n\tHitbox: " + str(bool(self.hitbox)) + "\n\tPhysicsBody: " + str(bool(self.physics)) + "\n\tMovable?: " + str(self.movable) + "\n\tUser Variable: " + str(self.user) + "\n\t"

    def AddPos(self, vector):
        self.position[0] += vector[0]
        self.position[1] += vector[1]
        self.position[2] += vector[2]
    
    def AddRot(self, vector):
        self.rotation[0] += vector[0]
        self.rotation[1] += vector[1]
        self.rotation[2] += vector[2]
    
    def SetShader(self, shader):
        for mesh in self.meshes:
            mesh.shader = shader
    
    def SetId(self, id):
        for mesh in self.meshes:
            mesh.id = id
    
    def IncrementFrames(self):
        for mesh in self.meshes:
            if mesh.frame != -1:
                mesh.frame += 1
    
    def DecrementFrames(self):
        for mesh in self.meshes:
            if mesh.frame != -1:
                mesh.frame -= 1
    


# Dupes:
#
# A Dupe is a duplicate of a thing, reusing it's properties
# with a unique position and rotation
#
# [0] is the index of the thing to copy from
# [1] is position
# [2] is rotation
# [3] is -1 to indicate it's a dupe
# [4] is the user variable
#

def Dupe(iIndex, vPos, vRot):
    return [iIndex, vPos, vRot, -1, 0]

# Cameras:
#
# Cameras hold info about where the screen is located in the world, and where it's pointing.
# Rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the +Z direction.
#
# For a third person camera, set yourCam.target
# For a first person camera, call yourCam.SetTargetDir() or yourCam.SetTargetFP()
#
# To change the FOV, use FindHowVars()
#
    
class Cam():
    def __init__(self, position=[0, 0, 0], screenWidth=0, screenHeight=0):
        if screenWidth and screenHeight:
            global screenSize
            screenSize = (screenWidth, screenHeight)
        self.position = position
        self.rotation = [0, 0, 0]
        self.nearClip = 0.1
        self.farClip = 1500
        self.target = [0, 0, 1]
        self.up = [0, 1, 0]
        self.user = 0
    
    def __repr__(self):
        return "Z3dPy Camera:\n\tPosition: " + str(self.position) + "\n\tRotation: " + str(self.rotation) + "\n\tNear Clip: " + str(self.nearClip) + "\n\tFar Clip: " + str(self.farClip) + "\n\tTarget Location: " + str(self.target) + "\n\tUp Direction: " + str(self.up) + "\n\tUser Variable: " + str(self.user) + "\n\t"


    def GetTargetDir(self):
        return VectorNormalize(VectorSub(self.target, self.position))

    def SetTargetDir(self, vector):
        self.target = VectorAdd(self.position, VectorNormalize(vector))

    def SetTargetFP(self):
        dir = RotTo(self.rotation, [0, 0, 1])
        self.target = VectorAdd(self.position, dir)
    
    def GetRightVector(self):
        return CrossProduct(self.GetTargetDir(), self.up)
    
    def ScreenXYToWorld(self, x, y):
        up = VectorRotate([0, -1, 0], self.rotation)
        right = CrossProduct(self.GetTargetDir(), up)
        offset = VectorAdd(VectorMulF(right, x - (screenSize[0] * 0.5)), VectorMulF(up, y - (screenSize[1] * 0.5)))
        return VectorAdd(self.position, offset)
    
    def Chase(self, location, speed):
        dspeed = speed * delta
        line = VectorMulF((self.position[0] - location[0], self.position[1] - location[1], self.position[2] - location[2]), dspeed)
        if VectorGetLength(line) < 0.001:
            self.position = location
            return True
        self.position = VectorSub(self.position, line)
        return False

# Internal Camera
#
# the internal camera is used to store constants for various functions
# including the clipping planes, directions, and more.
# also, half screen height and half screen width are pre-calculated here as well.
#
# [0] is location
# [1] is rotation
# [2] is screen height / 2
# [3] is screen width / 2
# [4] is near clip
# [5] is far clip
# [6] is target direction
# [7] is up direction
#

iC = [[0, 0, 0], [0, 0, 0], 360, 640, 0.1, 1500, [0, 0, 1], [0, 1, 0]]

intMatV = ()

def SetInternalCam(camera):
    global intMatV
    global iC
    iC = [camera.position, camera.rotation, screenSize[1] * 0.5, screenSize[0] * 0.5, camera.nearClip, camera.farClip, camera.GetTargetDir(), camera.up]
    intMatV = ViewMatrix(camera.position, camera.target, camera.up)

# Lights:
#
# Point lights use a combination of comparing directions and distance to light triangles.
#
# Sun lights use a simple static direction to light triangles.
#

LIGHT_POINT = 0
LIGHT_SUN = 1
LIGHT_SPOT = 2

class Light():
    def __init__(self, type=0, position=[0, 0, 0], direction=[0, 0, 1], strength=1.0, radius=5.0, colour=(255, 255, 255)):
        self.type = type
        match type:
            case 0:
                self.position = position
            case 1:
                self.direction = RotTo(direction, [0, 0, 1])
            case 2:
                self.position = position
                self.direction = RotTo(direction)

        self.strength = strength
        self.radius = radius
        self.colour = VectorDivF(colour, 255)
        self.user = 0
    
    def __repr__(self):
        return "Z3dPy Light:\n\tType: " + ["LIGHT_POINT", "LIGHT_SUN"][self.type] + "\n\t" + ("Direction" if self.type else "Location") + ": " + str(self.position) + "\n\tStrength: " + str(self.strength) + "\n\tRadius: " + str(self.radius) + "\n\tColour: " + str(self.colour) + "\n\tUser: " + str(self.user) + "\n\t"


# Rays:
#
# Used for debug drawing rays in world space, or ray
# collisions.
#
# [0] is wether or not it's drawn as an arrow
# [1] is ray start location
# [2] is ray end location

def Ray(vRaySt, vRayNd, isArrow=False):
    return [isArrow, vRaySt, vRayNd, 0]

# Usage:
'''

myRay = z3dpy.Ray(myCam.position, thatTree.position)

# Add the ray to the global list to get drawn with DebugRender()
z3dpy.rays.append(myRay)

# and/or you could do a collision check
hit = zp.RayIntersectThingComplex(myRay, myCharacter)

if hit[0]:
    location = hit[1]
    distance = hit[2]
    normal = hit[3]
    triThatWasHit = hit[4]
    print(location, distance, normal, zp.TriGetWPos(triThatWasHit))
else:
    print("Nope")
'''



# Dots:
#
# Dots is a list of vectors that will be drawn as points
# with DebugRender().
#

dots = []

# Usage:
'''

# Start with a vector.
myVector = [0, 0, 0]

# Append it to the global list
z3dpy.dots.append(myVector)

# or take a vector from something

z3dpy.dots.append(myCharacter.position)

# This may or may not update depending on wether it's a 
# reference,
# so I'd recommend setting the list before drawing.

z3dpy.dots = [myVector, myCharacter.position]

# Now when debug rendering, it'll be drawn as a small trigon, with an id of -1.

for tri in z3dpy.DebugRender():
    pygame.draw.lines(surface, z3dpy.TriGetColour(tri), ((tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])))
            
'''


# Terrains / Trains:
#
# Z3dPy's terrain system to easily replace the flat floor
# of HandlePhysics(). Needs to be baked beforehand.
#
# [x][y] is the height at that particular location.
#
# Baking will create the mesh for the terrain, which is automatically drawn with
# Render()

def Train(x, y):
    # It has to be an even width and height to be drawn correctly.
    if x & 1: x += 1
    if y & 1: y += 1
    return [[0.0 for h in range(0, y)] for g in range(0, x)]

# Usage:
'''
# Creating a flat 10x10 plane
myTerrain = z3dpy.Train(10, 10)

# Changing height at certain points
myTerrain[2][8] = 3.2
myTerrain[7][3] = -5.1

# BakeTrain uses blurring to smooth the terrain
BakeTrain(myTerrain)

# Optional arguments to customize the blur:
# BakeTrain(train, *iPasses, *FStrength, *FAmplitude)
BakeTrain(myTerrain, 3, 0.5, 1.5)

Passes is how many times the blur is done, normally once

Strength is how much the surrounding points affect final
output. AKA strength of the blur, normally 1.0 / no change.

Amplitude is multiplied by the final output to amplify.
Normally 1.0 / no change.
'''

# Emitters:
#
# Emitters spawn particles, and store info about them.
#

class Emitter():
    def __init__(self, position=[0, 0, 0], template=None, max=0, velocity=[0, -1, 0], lifetime=2.0, gravity=[0, 9.8, 0], randomness=0.0):
        self.particles = ()
        self.position = position
        self.template = template
        self.max = max
        self.velocity = velocity
        self.lifetime = lifetime
        self.gravity = gravity
        self.active = True
        self.randomness = randomness
        self.user = 0

# Usage:
'''
# Creating an emitter
# Emitter(position, template, max, velocity, lifetime, gravity)
myEmitter = z3dpy.Emitter([0, 0, 0], myMesh, 150, [0, 0, 0], 15.0, [0, 9.8, 0])

# Add it to the emitters list to be drawn
z3dpy.emitters.append(myEmitter)

# During the draw loop, TickEmitters()

while True:

    z3dpy.TickEmitters()

    for tri in z3dpy.Render():
'''


# Particle:
#
# Not meant to be created manually, they are automatically
# created during 
# TickEmitters().
#
# [0] is the time left
# [1] is the position
# [2] is the velocity
#

def Part(vPosition, vVelocity, fTime):
    return [fTime, vPosition, vVelocity]


# For decoding dae and x3d files
class XMLScript:
    def __init__(self, script):
        self.script = script

    def __repr__(self):
        return self.script
    
    def TagExists(self, tag):
        return "<" + tag + ">" in self.script

    def GetInnerXML(self, tag):
        startTag = "<" + tag
        return XMLScript(self.script[self.script.index(">", self.script.index(startTag)) + 1:self.script.index("</" + tag + ">")])
    
    def GetAttr(self, tag, attr):
        attrLen = len(attr)
        startTag = "<" + tag
        attributes = self.script[self.script.index(startTag) + len(startTag):self.script.index(">", self.script.index(startTag))].replace("\n", "").replace("\t", "").split("\" ")
        for attrb in attributes:
            if attrb.strip()[:attrLen] == attr:
                return attrb.strip()[attrLen + 2:]
        return ""
    
    def CountTags(self, tag):
        return self.script.count("<" + tag + " ")
    
    def GetInnerXMLById(self, id):
        dex = 0
        while (self.script.find("<", dex) != -1):
            trueDex = self.script.index("<", dex)
            if self.script[trueDex + 1] != "/":
                tagName = self.script[trueDex + 1:self.script.index(" ", trueDex)]
                attributes = self.script[self.script.index(" ", trueDex) + 1:self.script.index(">", trueDex)].split(" ")
                for attr in attributes:
                    #print(attr[4:-1])
                    if attr[:2] == "id":
                        if attr[4:-1] == id:
                            return XMLScript(self.script[self.script.index(">", trueDex) + 1:self.script.index("</" + tagName + ">", trueDex)])
            dex = self.script.index(">", dex) + 1
            #print(dex)
        print(id, "was not found!", self.script)
        return ""

# For decoding glTF files
class JSONScript:
    def __init__(self, script):
        self.script = script
    
    def __repr__(self):
        return self.script

    def GetItem(self, name):
        itemName = "\"" + name + "\"" + ":"
        start = self.script.index(itemName) + len(itemName)
        dex = start
        level = -1

        match self.script[start]:
            case "{":
                startTag = "{"
                endTag = "}"
            case "[":
                startTag = "["
                endTag = "]"
            case "\"":
                return self.script[start + 1:StringSweepUntil(self.script, start + 1, "\"")]
            case _:
                return self.script[start:StringSweepUntil(self.script, start, "]},")]

        while True:
            char = self.script[dex]

            if char == endTag:
                if not level:
                    break
                else:
                    level -= 1

            if char == startTag: level += 1

            dex += 1
        return JSONScript(self.script[start:dex + 1])

    def GetOuter(self, name, value):
        itemName = "\"" + name + "\"" + ":"
        print(type(value))
        if type(value) is str:
            itemName += "\"" + value + "\""
        else:
            itemName += str(value)
        if itemName not in self.script:
            print(itemName, "was not found in the JSON Script")
            return ""
        return JSONScript(self.script[StringSweepUntil(self.script, self.script.index(itemName), "{", -1):StringSweepUntil(self.script, self.script.index(itemName), "}") + 1])

    def GetList(self, name):
        fullName = "\"" + name + "\":"
        return self.GetItem(name).script[len(fullName):].strip().replace("{", "")[1:-2].split("},")

    def GetValue(self, name):
        itemName = "\"" + name + "\"" + ":"
        start = self.script.index(itemName) + len(itemName)
        if len(self.script) > start:
            if self.script[start] == "\"":
                return self.script[start:self.script.index("\"", start + 1)]
            if self.script[start] == "{":
                return self.script[start:StringSweepUntil(self.script, start, ",}]", 1) + 1]
        return self.script[start:StringSweepUntil(self.script, start, ",}]", 1) + 1]


# StringSweepUntil is like index, with multiple options. It'll return the first occurence of any of the characters in the symbols string
# If the symbols are not found it'll return either 0 or the length of the string, depending on which way the step goes.
'''
    myString[:z3dpy.StringSweepUntil(myString, 0, ",.!;?")]
'''
def StringSweepUntil(string, start, symbols, step=1):
    dex = start
    length = len(string)
    while -1 < dex < length:
        if string[dex] in symbols: break
        dex += step
    return dex

# Textures:
#
# Textures are a matrix/list of lists, to form a grid of
# colours.
# Transparency is a bool. It won't draw pixels that are
# False.

# Pixels can be accessed or changed with myTexture[x][y].

def TestTexture():
    # A red and blue 4x4 checker texture
    return (
            ((255, 0, 0, True), (255, 20, 0, True), (0, 38, 255, True), (0, 62, 255, True)),
            ((213, 4, 24, True), (255, 20, 47, True), (16, 39, 225, True), (28, 62, 255, True)), 
            ((0, 38, 255, True), (0, 62, 255, True), (255, 0, 0, True), (255, 20, 0, True)), 
            ((16, 39, 225, True), (28, 62, 255, True), (213, 4, 24, True), (255, 20, 47, True))
            )

# PyGame can be used to open quite a few different image formats.
def PgLoadTexture(filename, pygame):
    img = pygame.image.load(filename)
    surf = pygame.surfarray.array2d(img)
    fnSurf = []
    for x in range(len(surf)):
        fnSurf.append([])
        for y in range(len(surf[0])):
            col = img.get_at((y, x))
            col = col[:3] + (col[3] > 0,)
            fnSurf[x].append(col)
    return fnSurf

# Working on a BMP Loader for textures.
def LoadTexture(filename):
    match filename[-3:]:
        case "bmp":
            file = open(filename, 'rb')
            if file.read1(2) == b'BM':
                fileSize = unpack('I', file.read1(4))[0]
                file.read1(4)
                bitmapOffset = unpack('I', file.read1(4))[0]
                # Reading Header
                sizeOfHeader = unpack('I', file.read1(4))[0]
                width = unpack('l', file.read1(4))[0]
                height = unpack('l', file.read1(4))[0]
                
                if height > 0:
                    print("Bottom-Left Origin")
                else:
                    print("Top-Left Origin")

                texture = [[(0, 0, 0, False) for x in range(height)] for y in range(width)]
                planes = unpack('h', file.read1(2))[0]
                if planes != 1:
                    print("LoadTexture(): Bitplanes are wrong, is this a BMP file?")
                else:
                    bits = unpack('h', file.read1(2))[0]
                    compression = unpack('I', file.read1(4))[0]
                    if compression:
                        print("LoadTexture(): Does not support compressed BMPs")
                    else:
                        sizeImage = unpack('I', file.read1(4))[0]
                        XPelsPerMeter = unpack('l', file.read1(4))[0]
                        YPelsPerMeter = unpack('l', file.read1(4))[0]

                        clrUsed = unpack('I', file.read1(4))[0]
                        if not clrUsed:
                            clrUsed = 2 ** bits

                        clrImportant = unpack('I', file.read1(4))[0]
                        colours = []
                        
                        print("BMP File:")
                        print("Size:", fileSize, "bytes")
                        print("Width:", width)
                        print("Height:", height)
                        print("Bit Depth:", bits)
                        print("Compression:", compression)
                        print("sizeImage:", sizeImage)
                        print("PPM:", str([XPelsPerMeter, YPelsPerMeter]))
                        print("Colours Used:", clrUsed)
                        print("Important Colours:", clrImportant if clrImportant else "All")

                        for c in range(clrUsed):
                            colours.append(hex(unpack('I', file.read1(bits))[0])[2:])
                            print(colours[-1])

                        for pixel in range(width * height):
                            colIndex = unpack('B', file.read1(1))[0] // 16
                            print(colIndex)
                            colour = colours[colIndex]
                            print(colour)
                            texture[pixel % width][pixel // width] = BMPHexToRGB(colour) + (True,)

                        file.close()
                        return texture

            file.close()
        case _:
            print("LoadTexture() only supports BMP files.")

    
    return TestTexture()



def BMPHexToRGB(hex_string):
    if hex_string[0] == '#':
        hex_string = hex_string[1:]
    return (int(hex_string[2:4], 16), int(hex_string[4:6], 16), int(hex_string[6:8], 16))


#==========================================================================
#
# Object Functions
#
# Several objects are still lists, so these functions are
# human-friendly ways to set and retrieve 'properties'
#
#==========================================================================

# TRIANGLES


# Functions for each point
def TriGetP1(tri): return tri[0]

def TriGetP2(tri): return tri[1]

def TriGetP3(tri): return tri[2]

# TriGetNormal() will calculate a new normal
def TriGetNormal(tri): return VectorNormalize(CrossProduct(VectorSub(tri[1], tri[0]), VectorSub(tri[2], tri[0])))

def TriGetColour(tri): return tri[4]

# Colour is determined by the associated mesh's shader.
def TriSetColour(tri, vColour):
    tri[4] = vColour

def TriGetShade(tri): return tri[3]

def TriSetShade(tri, FShade):
    tri[3] = FShade

def TriGetId(tri): return tri[5]

# Id is automatically calculated during the render process,
# and by default will be the id of the associated mesh.
def TriSetId(tri, id):
    tri[5] = id


# THINGS


def AddThing(thing, iLayer=2):
    thing.internalid = (len(layers[iLayer]), iLayer)
    layers[iLayer].append(thing)

def AddThings(things, iLayer=2):
    for thing in things:
        AddThing(thing, iLayer)

def AddDupe(thing, position, rotation, iLayer=2):
    dupe = Dupe(thing.internalid[0], position, rotation)
    layers[iLayer].append(dupe)
    return dupe


def GatherThings():
    output = []
    for layer in layers:
        output += layer
    return output


# If you don't specify the layer, looks for it in the
# default layer.
def RemoveThing(thing):
    global layers
    iLayer = thing.internalId[1]
    if len(layers[iLayer]) == 1:
        layers[iLayer] = []
        return
    dex = thing.internalId[0]
    layers[iLayer] = layers[iLayer][:dex] + layers[iLayer][dex + 1:]




# RAYS

def RayGetStart(ray):
    return ray[1]

def RaySetStart(ray, vector):
    ray[1] = vector

def RayGetDirection(ray):
    return VectorNormalize(VectorSub(ray[2], ray[1]))

def RayGetLength(ray):
    return VectorGetLength(VectorSub(ray[2], ray[1]))

def RayGetEnd(ray):
    return ray[2]

def RaySetEnd(ray, vector):
    ray[2] = vector

def RayGetIsArrow(ray):
    return ray[0]

def RaySetIsArrow(ray, bIsArrow):
    ray[0] = bIsArrow


# PARTICLES

def PartGetTime(particle):
    return particle[0]

def PartSetTime(particle, fTime):
    particle[0] = fTime

def PartGetPos(particle):
    return particle[1]

def PartSetPos(particle, vector):
    particle[1] = vector

def PartGetVelocity(particle):
    return particle[2]

def PartSetVelocity(particle, vector):
    particle[2] = vector


# HITS

def HitCheck(hit):
    return hit[0]

def HitGetDistance(hit):
    return hit[2]

def HitGetPos(hit):
    return hit[1]

def HitGetTri(hit):
    return hit[3]




#==========================================================================
#  
# Vectors
#
#==========================================================================


# These vector functions return new vectors, not modifying the original.

def VectorAdd(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def VectorAddF(v, f):
    return [v[0] + f, v[1] + f, v[2] + f]

def VectorSub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def VectorMul(v1, v2):
    return [v1[0] * v2[0], v1[1] * v2[1], v1[2] * v2[2]]

def VectorMulF(v, f):
    return [v[0] * f, v[1] * f, v[2] * f]

def VectorDiv(v1, v2):
    return [v1[0] / v2[0], v1[1] / v2[1], v1[2] / v2[2]]

def VectorDivF(v, f):
    return [v[0] / f, v[1] / f, v[2] / f]

def VectorMod(v1, v2):
    return [v1[0] % v2[0], v1[1] % v2[1], v1[2] % v2[2]]

def VectorModI(v, i):
    return [v[0] % i, v[1] % i, v[2] % i]

def VectorComb(v):
    return v[0] + v[1] + v[2]

def VectorNormalize(v):
    l = VectorGetLength(v)
    return [v[0] / l, v[1] / l, v[2] / l] if l else v

def VectorMinF(v, f):
    return [min(v[0], f), min(v[1], f), min(v[2], f)]

def VectorMaxF(v, f):
    return [max(v[0], f), max(v[1], f), max(v[2], f)]

def VectorMax(v1, v2):
    return [max(v1[0], v2[0]), max(v1[1], v2[1]), max(v1[2], v2[2])]

def VectorMin(v1, v2):
    return [min(v1[0], v2[0]), min(v1[1], v2[1]), min(v1[2], v2[2])]

# Vector Compare returns wether or not v1 is greater than v2
def VectorCompare(v1, v2):
    vO = VectorABS(v1)
    vT = VectorABS(v2)
    return VectorComb(vO) > VectorComb(vT)
    
def VectorFloor(v):
    return [floor(v[0]), floor(v[1]), floor(v[2])]
    
# Cross Product gives you the direction perpendicular to both input vectors, so given an X and Y it would output a Z direction.
def CrossProduct(v1, v2):
    return [(v1[1] * v2[2]) - (v1[2] * v2[1]), (v1[2] * v2[0]) - (v1[0] * v2[2]), (v1[0] * v2[1]) - (v1[1] * v2[0])]

def VectorGetLength(v):
    return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

# Vector Dot Product compares 2 directions. 1 is the same, -1 is apposing.
# Useful for lighting calculations.
def DotProduct(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def VectorEqual(v1, v2, threshold=0.0):
    return (v1[0] + -v2[0]) + (v1[1] + -v2[1]) + (v1[2] + -v2[2]) <= threshold

def DistanceBetweenVectors(v1, v2):
    d1 = v2[0] - v1[0]
    d2 = v2[1] - v1[1]
    d3 = v2[2] - v1[2]
    output = d1 * d1 + d2 * d2 + d3 * d3
    return sqrt(output)

def VectorNegate(v):
    return [-v[0], -v[1], -v[2]]

def VectorABS(v):
    return [abs(v[0]), abs(v[1]), abs(v[2])]

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))

# Returns a vector where the strongest axis is 1 and the others are 0
def VectorPureDirection(v):
    return VectorZero(VectorNormalize(v), 1.0)

def VectorRotateX(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotZ(deg))

'''
    # To get the forward, up, or right vector of a Thing or Mesh:
    forward = VectorRotate([0, 0, 1], myThing.rotation)
    right = VectorRotate([1, 0, 0], myThing.rotation)
    up = VectorRotate([0, 1, 0], myThing.rotation)
'''
def VectorRotate(vector, vRot):
    nRot = WrapRot(vRot)
    nV = VectorRotateX(vector, nRot[0])
    nV = VectorRotateZ(nV, nRot[2])
    return VectorRotateY(nV, nRot[1])

# Returns a vector where all axis below the threshold are 0
def VectorZero(vec, thresh):
    return [axis if axis >= thresh else 0 for axis in vec]

def WrapRot(vRot):
    newRot = [vRot[0], vRot[1], vRot[2]]

    if newRot[0] < 0:
        newRot[0] = newRot[0] % -360 + 360
    if newRot[1] < 0:
        newRot[1] = newRot[1] % -360 + 360
    if newRot[2] < 0:
        newRot[2] = newRot[2] % -360 + 360

    return VectorModI(newRot, 360)

def VectorAverage(list_of_vectors):
    out = [0, 0, 0]
    for v in list_of_vectors:
        out = VectorAdd(out, v)
    return VectorDivF(out, len(list_of_vectors))

def VectorIntersectPlane(pPos, pNrm, lSta, lEnd):
    pNrm = VectorNormalize(pNrm)
    plane_d = -DotProduct(pNrm, pPos)
    ad = DotProduct(lSta, pNrm)
    bd = DotProduct(lEnd, pNrm)
    t = (-plane_d - ad) / (bd - ad)
    lineStartToEnd = VectorSub(lEnd, lSta)
    lineToIntersect = VectorMulF(lineStartToEnd, t)
    return VectorAdd(lSta, lineToIntersect)

def ShortestPointToPlane(point, plNrm, plPos):
    return DotProduct(plNrm, point) - DotProduct(plNrm, plPos)




#==========================================================================
#  
# Vector UVs
#
#==========================================================================


# In VectorUV functions, the first vector's UV and normal are carried. The second vector does not have to be a VectorUV.

def VectorUVAdd(v1, v2):
    return VectorAdd(v1, v2) + [v1[3], v1[4]]

def VectorUVSub(v1, v2):
    return VectorSub(v1, v2) + [v1[3], v1[4]]

def VectorUVMul(v1, v2):
    return VectorMul(v1, v2) + [v1[3], v1[4]]

def VectorUVMulF(v1, f):
    return VectorMulF(v1, f) + [v1[3], v1[4]]

def VectorUVDiv(v1, v2):
    return VectorDiv(v1, v2) + [v1[3], v1[4]]

def VectorUVDivF(v1, f):
    return VectorDivF(v1, f) + [v1[3], v1[4]]

def VectorUVIntersectPlane(pPos, pNrm, lSta, lEnd):
    pNrm = VectorNormalize(pNrm)
    plane_d = -DotProduct(pNrm, pPos)
    ad = DotProduct(lSta, pNrm)
    bd = DotProduct(lEnd, pNrm)
    t = (-plane_d - ad) / (bd - ad)
    lineStartToEnd = VectorUVSub(lEnd, lSta)
    lineToIntersect = VectorUVMulF(lineStartToEnd, t)
    newLine = [lSta[0], lSta[1], lSta[2], lSta[3], (((lEnd[4][0] - lSta[4][0]) * t) + lSta[4][0], ((lEnd[4][1] - lSta[4][1]) * t) + lSta[4][1])]
    return VectorUVAdd(newLine, lineToIntersect)

def VectorUVFloor(vectorUV): return VectorFloor(vectorUV) + vectorUV[3:]




#==========================================================================
#  
# Triangle Functions
#
#==========================================================================


def TriAdd(t, v): return [VectorUVAdd(t[0], v), VectorUVAdd(t[1], v), VectorUVAdd(t[2], v), t[3], t[4], t[5], t[6]]

def TriSub(t, v): return [VectorUVSub(t[0], v), VectorUVSub(t[1], v), VectorUVSub(t[2], v), t[3], t[4], t[5], t[6]]

def TriMul(t, v): return [VectorUVMul(t[0], v), VectorUVMul(t[1], v), VectorUVMul(t[2], v), t[3], t[4], t[5], t[6]]

def TriMulF(t, f): return [VectorUVMulF(t[0], f), VectorUVMulF(t[1], f), VectorUVMulF(t[2], f), t[3], t[4], t[5], t[6]]

def TriDiv(t, v): return [VectorUVDiv(t[0], v), VectorUVDiv(t[1], v), VectorUVDiv(t[2], v), t[3], t[4], t[5], t[6]]

def TriDivF(t, f): return [VectorUVDivF(t[0], f), VectorUVDivF(t[1], f), VectorUVDivF(t[2], f), t[3], t[4], t[5], t[6]]

def TriClipAgainstPlane(tri, pPos, pNrm):
    test = [ShortestPointToPlane(tri[0], pNrm, pPos) >= 0, ShortestPointToPlane(tri[1], pNrm, pPos) >= 0, ShortestPointToPlane(tri[2], pNrm, pPos) >= 0]
    match test.count(True):
        case 0:
            return []
        case 3:
            yield tri
            
        case 1:
            first = test.index(True)
            second = test.index(False)
            third = test.index(False, second + 1)
            outT1 = [tri[first], VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[third]), VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[second]), tri[3], tri[4], tri[5], tri[6]]
            yield outT1

        case 2:
            first = test.index(True)
            second = test.index(True, first + 1)
            third = test.index(False)
            outT1 = [tri[first], tri[second], VectorUVIntersectPlane(pPos, pNrm, tri[second], tri[third]), tri[3], tri[4], tri[5], tri[6]]
            outT2 = [tri[first], outT1[2], VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[third]), tri[3], tri[4], tri[5], tri[6]]
            yield outT1
            yield outT2

def TriAverage(tri):
    return [(tri[0][0] + tri[1][0] + tri[2][0]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.33333]


# Triangle Sorting functions
def TriSortAverage(n):
    return (n[0][2] + n[1][2] + n[2][2]) * 0.3333333

def TriSortFurthest(n):
    return max(n[0][2], n[1][2], n[2][2])

def TriSortClosest(n):
    return min(n[0][2], n[1][2], n[2][2])

def TriClipAgainstZ(tri, distance=iC[4]):
    return TriClipAgainstPlane(tri, (0.0, 0.0, distance), (0.0, 0.0, 1.0))

def TriClipAgainstScreenEdges(tri):
    output = []
    for t in TriClipAgainstPlane(tri, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        for r in TriClipAgainstPlane(t, (0.0, screenSize[1] - 1.0, 0.0), (0.0, -1.0, 0.0)):
            for i in TriClipAgainstPlane(r, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)):
                output += TriClipAgainstPlane(i, (screenSize[0] - 1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    return output


# I don't know what the algorithm is actually called
# I'll call it the Monkey Bars Method.
def Triangulate(list_of_vectors):
    output = []
    points = [0, 1]
    for n in range(2, len(list_of_vectors)):
        points.append(n)
        p1 = list_of_vectors[points[0]]
        p2 = list_of_vectors[points[1]]
        p3 = list_of_vectors[points[2]]
        output.append(Tri(p1, p2, p3))
        points = [points[0], points[2]]
    return output




#==========================================================================
#  
# Mesh Functions
#
#==========================================================================

def LoadMesh(filename, position=(0.0, 0.0, 0.0), rotation=[0.0, 0.0, 0.0], scale=(1.0, 1.0, 1.0), colour=(255, 255, 255), id=0, material=MATERIAL_UNLIT, cull=True, visible=True):
    try:
        file = open(filename)
    except FileNotFoundError:
        if filename.count("/"):
            while filename.count("/") > 0:
                filename = filename[filename.index("/") + 1:]
            if filename == "error.obj":
                raise FileNotFoundError("Can't load placeholder mesh. (Is the z3dpy folder missing?)")
            else:
                print(filename[:-4], "was not found, replacing...")
                return LoadMesh("z3dpy/mesh/error.obj", position, rotation, scale, colour, id, material, cull, visible)

    match filename[-3:]:
        case "obj":
            with file:
                # Object Format
                verts = []
                uvs = []
                output = []
                matoutputs = []
                colours = [(255, 255, 255)]
                gathered = []
                triangles = []
                mat = -1
                storedUVs = []
                currentMat = ""

                while (currentLine := file.readline()):
                    if currentLine == "a\n": break
                    match currentLine[0]:
                        case 'v':
                            if currentLine[1] != 'n':
                                if currentLine[1] == 't':
                                    currentLine = currentLine[3:].strip().split(' ')
                                    uvs.append([float(currentLine[0]), float(currentLine[1])])
                                else:
                                    currentLine = currentLine[2:].strip().split(' ')
                                    verts.append([float(currentLine[0]) * scale[0], float(currentLine[1]) * scale[1], float(currentLine[2]) * scale[2], [0, 0, 0], [0, 0], 0])
                        case 'f':
                            currentLine = currentLine[2:]
                            bUV = '/' in currentLine
                            if bUV:
                                # Face includes UVs
                                preUV = [int(l.split("/")[1]) for l in currentLine.strip().split(' ')]
                                currentLine = [l.split("/")[0] for l in currentLine.strip().split(' ')]
                            else:
                                currentLine = currentLine.split(' ')

                            p1 = int(currentLine[0]) - 1
                            p2 = int(currentLine[1]) - 1
                            p3 = int(currentLine[2]) - 1

                            if len(currentLine) < 4:
                                normal = TriGetNormal([verts[p1], verts[p2], verts[p3]])
                                verts[p1][3] = VectorAdd(verts[p1][3], normal)
                                verts[p2][3] = VectorAdd(verts[p2][3], normal)
                                verts[p3][3] = VectorAdd(verts[p3][3], normal)

                                verts[p1][5] += 1
                                verts[p2][5] += 1
                                verts[p3][5] += 1
                                triangles.append([p1, p2, p3])
                                if bUV:
                                    storedUVs.append(preUV)
                            else:
                                points = [0, 1]
                                for n in range(2, len(currentLine)):
                                    points.append(n)
                                    p1 = int(currentLine[points[0]]) - 1
                                    p2 = int(currentLine[points[1]]) - 1
                                    p3 = int(currentLine[points[2]]) - 1
                                    normal = TriGetNormal([verts[p1], verts[p2], verts[p3]])
                                    verts[p1][3] = VectorAdd(verts[p1][3], normal)
                                    verts[p2][3] = VectorAdd(verts[p2][3], normal)
                                    verts[p3][3] = VectorAdd(verts[p3][3], normal)
                                    verts[p1][5] += 1
                                    verts[p2][5] += 1
                                    verts[p3][5] += 1
                                    triangles.append([p1, p2, p3])
                                    if bUV:
                                        storedUVs.append([preUV[points[0]], preUV[points[1]], preUV[points[2]]])
                                    points = [points[0], points[2]]
                                

                    if currentLine[:6] == "usemtl":
                        if currentLine[7:] != currentMat:
                            currentMat = currentLine[7:]
                            # Accounting for different materials
                            if mat == 0:
                                try:
                                    mtlname = filename[:-4] + ".mtl"
                                    mtlFile = open(mtlname)
                                except:
                                    print("Couldn't open file: " + mtlname)

                                else:
                                    while (mtlLine := mtlFile.readline()):
                                        if mtlLine[:2] == "Kd":
                                                colour = [float(c) for c in mtlLine[3:].split(" ")]
                                                colours.append(VectorMulF(colour, 255))
                            gathered.append(triangles)
                            triangles = []
                            mat += 1

                # Averaging normals
                for v in verts:
                    # ?
                    if v[5]:
                        v[3] = VectorDivF(v[3], v[5])
                    v.pop()

                uvLen = len(storedUVs)
                if mat == -1:
                    for tr in range(len(triangles)):
                        nt = Tri(verts[triangles[tr][0]], verts[triangles[tr][1]], verts[triangles[tr][2]])
                        if uvLen:
                            nt[0][4] = uvs[storedUVs[tr][0] - 1]
                            nt[1][4] = uvs[storedUVs[tr][1] - 1]
                            nt[2][4] = uvs[storedUVs[tr][2] - 1]
                        output.append(nt)

                    return Mesh(tuple(output), position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
                else:

                    gathered.append(triangles)
                    for trL in gathered:
                        output.append([])
                        for tr in range(len(trL)):
                            nt = Tri(verts[trL[tr][0]], verts[trL[tr][1]], verts[trL[tr][2]])
                            output[-1].append(nt)
                            if uvLen:
                                nt[0][4] = uvs[storedUVs[tr][0] - 1]
                                nt[1][4] = uvs[storedUVs[tr][1] - 1]
                                nt[2][4] = uvs[storedUVs[tr][2] - 1]

                    meshes = [Mesh(tuple(trS), position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible) for trS in matoutputs]
                    colours = colours[1:]
                    colours.reverse()

                    map(MeshSetColour, meshes, colours)
                    return meshes

        case "dae":
            with file:
                # Collada
                xml = XMLScript(file.read())
                daeVer = xml.GetAttr("COLLADA", "version")

                if daeVer != "1.4.1":
                    print("Collada version is not 1.4.1, hopefully this works...")
                    
                geomId = xml.GetAttr("geometry", "id")

                geom = xml.GetInnerXML("geometry")

                verts = [float(v) for v in geom.GetInnerXMLById(geomId + "-positions").GetInnerXML("float_array").script.split(" ")]

                # UVs
                uvs = [float(v) for v in geom.GetInnerXMLById(geomId + "-map-0-array").script.strip().split(" ")]
                uvs = [(uvs[v], uvs[v + 1]) for v in range(0, len(uvs), 2)]
                normals = geom.GetInnerXMLById(geomId + "-normals-array").script.strip().split(" ")
                normals = [[normals[n], normals[n + 1], normals[n + 2]] for n in range(0, len(normals), 3)]
                verts = [[verts[v], verts[v + 1], verts[v + 2]] for v in range(0, len(verts), 3)]

                try:
                    # Triangle
                    trixml = geom.GetInnerXML("triangles")
                except ValueError:
                    # Ngon
                    trixml = geom.GetInnerXML("polylist")
                    triLength = trixml.CountTags("input")
                    triCounts = trixml.GetInnerXML("vcount").script.strip().split(" ")
                    faces = [int(f) for f in trixml.GetInnerXML("p").script.strip().split(" ")]
                    indexes = [-1, -1, -1]

                    ngon = []
                    
                    n = []
                    u = []

                    tris = []
                    for i in range(triLength):
                        match trixml.GetAttr('input', 'semantic'):
                            case "VERTEX":
                                indexes[0] = i
                            case "NORMAL":
                                indexes[1] = i
                            case "TEXCOORD":
                                indexes[2] = i
                        trixml.script = trixml.script[trixml.script.index("/>") + 2:]
                    
                    f = 0
                    g = 0
                    length = len(faces)
                    while f < length:
                        for i in range(int(triCounts[g])):
                            p1 = verts[faces[f + indexes[0]]]
                            n1 = [0, 0, 0]
                            u1 = [0, 0]
                            if indexes[1] != -1:
                                n1 = normals[faces[f + indexes[1]]]
                            if indexes[2] != -1:
                                u1 = uvs[faces[f + indexes[2]]]
                            ngon.append(VectorUV(p1[0], p1[1], p1[2], n1, u1))
                        tris += Triangulate(ngon)
                        f += int(triCounts[g]) * triLength
                        g += 1

                else:
                    faces = trixml.GetInnerXML("p").script.strip().split(" ")
                    triLength = trixml.CountTags("input")
                    tris = []
                    double = triLength * 2
                    indexes = [-1, -1, -1]
                        
                    for i in range(triLength):
                        match trixml.GetAttr('input', 'semantic'):
                            case "VERTEX":
                                indexes[0] = i
                            case "NORMAL":
                                indexes[1] = i
                            case "TEXCOORD":
                                indexes[2] = i
                        trixml.script = trixml.script[trixml.script.index("/>") + 2:]
                        
                    for f in range(0, len(faces), triLength * 3):
                        v1 = verts[int(faces[f + indexes[0]])]
                        v2 = verts[int(faces[f + triLength + indexes[0]])]
                        v3 = verts[int(faces[f + double + indexes[0]])]
                        n1 = [0, 0, 0]
                        n2 = [0, 0, 0]
                        n3 = [0, 0, 0]
                        uv1 = [0, 0]
                        uv2 = [0, 0]
                        uv3 = [0, 0]
                            
                        if indexes[1] != -1:
                            n1 = normals[int(faces[f + indexes[1]])]
                            n2 = normals[int(faces[f + triLength + indexes[1]])]
                            n3 = normals[int(faces[f + double + indexes[1]])]
                        if indexes[2] != -1:
                            uv1 = uvs[int(faces[f + indexes[2]])]
                            uv2 = uvs[int(faces[f + triLength + indexes[2]])]
                            uv3 = uvs[int(faces[f + double + indexes[2]])]


                        tris.append(Tri(VectorUV(v1[0], v1[1], v1[2], n1, uv1), VectorUV(v2[0], v2[1], v2[2], n2, uv2), VectorUV(v3[0], v3[1], v3[2], n3, uv3)))

            return Mesh(tris, position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
            
        case "x3d":
            # Extensible 3D
            with file:
                    xml = XMLScript(file.read())
                    scene = xml.GetInnerXML("Scene")
                    #print(scene.GetAttr("Coordinate", "point").strip())
                    verts = [float(v) for v in scene.GetAttr("Coordinate", "point").strip().split(" ")]
                    verts = [VectorUV(verts[v], verts[v + 1], verts[v + 2]) for v in range(0, len(verts), 3)]
                    faces = scene.GetAttr("IndexedFaceSet", "coordIndex").split(" ")
                    tris = []
                    tries = [[]]
                    for f in faces:
                        if f == "-1":
                            if len(tries[-1]) > 3:
                                ngon = [verts[t] for t in tries[-1]]
                                tries.pop()
                                tris += Triangulate(ngon)
                            tries.append([])
                        else:
                            tries[-1].append(int(f))
                    tries.pop()
                    tris += [Tri(verts[t[0]], verts[t[1]], verts[t[2]]) for t in tries]
            return Mesh(tris, position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
            
        case "stl":
            # STL
            with file:
                points = []
                tris = []

                if file.read(5) == "solid":
                    
                    # ASCII
                    file.readline()
                    while (line := file.readline()):
                        line = line[:-1]

                        while line[0] == '\t' or line[0] == ' ':
                            line = line[1:]

                        if line[:5] == "facet":
                            normal = [float(l) for l in line.split(" ")[2:]]
                        
                        if line[:6] == "vertex":
                            points.append([float(l) for l in line.split(" ")[1:]])
                        
                        if line == "endfacet":
                            # It's not within spec to put ngons in there but just in case.
                            if len(points) > 3:
                                ngon = [VectorUV(p[0], p[1], p[2], normal) for p in points]
                                tris += Triangulate(ngon)
                            else:
                                tris.append(Tri(VectorUV(points[0][0], points[0][1], points[0][2], normal), VectorUV(points[1][0], points[1][1], points[1][2], normal), VectorUV(points[2][0], points[2][1], points[2][2], normal)))
                            points = []

                else:
                    # Binary
                    file.close()
                    file = open(filename, 'rb')
                    header = file.read1(80)
                    numTris = unpack("L", file.read1(4))[0]
                    print(numTris)
                    for t in range(numTris):
                        normal = [unpack('f', file.read1(4))[0] for i in range(3)]
                        p1 = [unpack('f', file.read1(4))[0] for i in range(3)]
                        p2 = [unpack('f', file.read1(4))[0] for i in range(3)]
                        p3 = [unpack('f', file.read1(4))[0] for i in range(3)]
                        file.read1(2)
                        tris.append(Tri(VectorUV(p1[0], p1[1], p1[2], normal), VectorUV(p2[0], p2[1], p2[2], normal), VectorUV(p3[0], p3[1], p3[2], normal)))

            return Mesh(tris, position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
            
        case "ply":
            # Stanford PLY
            with file:
                if file.readline() != "ply\n":
                    print("Does not have a ply header. Is this a ply file?")

                vertCount = 0
                faceCount = 0

                properties = []
                verts = []
                faces = []
                tris = []

                format = file.readline()[:-1].split(" ")
                file.readline()
                while (line := file.readline()[:-1]) != "end_header":
                    if " " in line:
                        split = line.split(" ")
                        if len(split) == 3:
                            match split[0]:
                                case "element":
                                    if split[1] == "vertex":
                                        vertCount = int(split[2])
                                    else:
                                        faceCount = int(split[2])

                                case "property":
                                    properties.append(split[2])

                if format[1] == "ascii":
                    # ASCII
                    for i in range(vertCount):
                        newVert = VectorUV(0, 0, 0)
                        split = file.readline()[:-1].split(" ")
                        for s, p in zip(split, properties):
                            match p:
                                case "x":
                                    newVert[0] = float(s)

                                case "y":
                                    newVert[1] = float(s)
                            
                                case "z":
                                    newVert[2] = float(s)

                                case "nx":
                                    newVert[3][0] = float(s)

                                case "ny":
                                    newVert[3][1] = float(s)
                                    
                                case "nz":
                                    newVert[3][2] = float(s)

                                case "s":
                                    newVert[4] = (float(s), newVert[4][1])

                                case "t":
                                    newVert[4] = (newVert[4][0], float(s))
                        verts.append(newVert)
                    
                    for i in range(faceCount):
                        split = file.readline()[:-1].split(" ")
                        if split[0] != '3':
                            # Triangulating N-gons
                            ngon = [verts[int(v)] for v in split[1:]]
                            tris += Triangulate(ngon)
                        else:
                            tris += [Tri(verts[int(split[1])], verts[int(split[2])], verts[int(split[3])])]

                else:
                    # Binary
                    file.close()
                    file = open(filename, 'rb')
                    while (line := file.read1(4)) != b'der\n': pass
                    for v in range(vertCount):
                        newVert = VectorUV(0, 0, 0)
                        for s, p in zip([unpack("f", file.read1(4))[0] for i in range(len(properties))], properties):
                            match p:
                                case "x":
                                    newVert[0] = s

                                case "y":
                                    newVert[1] = s
                            
                                case "z":
                                    newVert[2] = s

                                case "nx":
                                    newVert[3][0] = s

                                case "ny":
                                    newVert[3][1] = s
                                    
                                case "nz":
                                    newVert[3][2] = s

                                case "s":
                                    newVert[4] = (s, newVert[4][1])

                                case "t":
                                    newVert[4] = (newVert[4][0], s)
                        verts.append(newVert)

                    for i in range(faceCount):
                        size = unpack("B", file.read1(1))[0]
                        if size != 3:
                            ngon = [verts[unpack("I", file.read1(4))[0]] for i in range(size)]
                            tris += Triangulate(ngon)
                        else:
                            tris.append(Tri(verts[unpack("I", file.read1(4))[0]], verts[unpack("I", file.read1(4))[0]], verts[unpack("I", file.read1(4))[0]]))
            return Mesh(tris, position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
                
            
        case "glb":
            # glTF 2.0
            # Still working out the bugs on it
            file.close()
            with open(filename, 'rb') as file:
                    file.read1(0x14)
                    json = ""
                    while ((bits := file.read1(4)) != b'BIN\x00'):
                        json += str(bits)[2:-1]
                    
                    binaryOffset = file.tell()
                    
                    json = JSONScript(json)

                    triLength = int(json.GetItem("meshes").GetItem("indices"))

                    triOrder = [-1, -1, -1]

                    for val in json.GetItem("attributes").script[1:-1].strip().split(","):
                        split = val.split(":")
                        match split[0][1:-1]:
                            case "POSITION":
                                triOrder[0] = int(split[1].replace("}", ""))
                            case "NORMAL":
                                triOrder[1] = int(split[1].replace("}", ""))
                            case "TEXCOORD_0":
                                triOrder[2] = int(split[1].replace("}", ""))

                    flip = True
                    buffers = [-1, -1, -1, -1]

                    for buffer in json.GetItem("accessors").script[1:-2].strip().replace("{", "").split("},"):
                            script = JSONScript(buffer)
                            match script.GetItem("type"):
                                case "VEC3":
                                    buffers[0 if flip else 1] = [int(script.GetItem("count")), int(script.GetItem("bufferView")), int(script.GetItem("componentType"))]
                                    flip = False
                                case "VEC2":
                                    buffers[2] = [int(script.GetItem("count")), int(script.GetItem("bufferView")), int(script.GetItem("componentType"))]
                                case "SCALAR":
                                    buffers[3] = [int(script.GetItem("count")), int(script.GetItem("bufferView")), int(script.GetItem("componentType"))]
                    
                    data = [[], [], [], []]
                    
                    for index, bufferView in enumerate(json.GetList("bufferViews")):
                        view = JSONScript(bufferView)
                        file.seek(int(view.GetItem("byteOffset")) + binaryOffset)
                        for i in range(4):
                            if buffers[i] != -1:
                                if index == buffers[i][1]:
                                    byteType = GlTFComponentTypeToUnpackParameters(buffers[i][2])
                                    data[index] += [unpack(byteType[0], file.read1(byteType[1]))[0] for i in range(buffers[i][0])]
                    
                    data[0] = [(data[0][v], data[0][v + 1], data[0][v + 2]) for v in range(0, len(data[0]), 3)]

                    data[1] = [(data[1][v], data[1][v + 1], data[1][v + 2]) for v in range(0, len(data[1]), 3)]

                    data[2] = [(data[2][v], data[2][v + 1]) for v in range(0, len(data[2]), 2)]

                    print(triOrder, len(data[0]), len(data[1]), len(data[2]), len(data[3]))
                    print(data[3])
                    input(">")
                    tries = data[3]
                    tris = []

                    double = triLength * 2
            
                    # The numbers, what do they mean? Where are they broadcast from?
                    for t in range(0, len(tries), triLength * 3):
                        p1 = data[0][tries[t + triOrder[0]]]
                        p2 = data[0][tries[t + triLength + triOrder[0]]]
                        
                        p3 = data[0][tries[t + double + triOrder[0]]]
                        n1 = [0, 0, 0]
                        n2 = [0, 0, 0]
                        n3 = [0, 0, 0]
                        uv1 = [0, 0]
                        uv2 = [0, 0]
                        uv3 = [0, 0]
                        if data[1]:
                            print(tries[t + triLength + triOrder[1]] - 1)
                            n1 = data[1][tries[t + triOrder[1]] - 1]
                            n2 = data[1][tries[t + triLength + triOrder[1]] - 1]
                            n3 = data[1][tries[t + double + triOrder[1]] - 1]
                        if data[2]:
                            uv1 = data[2][tries[t + triOrder[2]] - 1]
                            uv2 = data[2][tries[t + triLength + triOrder[2]] - 1]
                            uv3 = data[2][tries[t + double + triOrder[2]] - 1]
                        
                        tris = Tri(VectorUV(p1[0], p1[1], p1[2], n1, uv1), VectorUV(p2[0], p2[1], p2[2], n2, uv2), VectorUV(p3[0], p3[1], p3[2], n3, uv3))

                    return Mesh(tris, position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible)
            

def MeshSetColour(mesh, colour):
    mesh.SetColour(colour)

def LoadAniMesh(filename, position=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0], scale=(1.0, 1.0, 1.0), colour=(255, 255, 255), material=MATERIAL_UNLIT, id=0, cull=True, visible=True):
    if filename[-4:] == 'aobj':
        # AOBJ Format
        file = open(filename)
        newMsh = Mesh([], position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible, frame=0)
        points = []
        tries = []
        obj = True

        for line in file.read().split('\n'):
            if line:
                if line == 'a':
                    newMsh.tris.append([Tri(points[tri[0]], points[tri[1]], points[tri[2]]) for tri in tries])
                    obj = False
                    continue
                if ' ' in line:
                    vs = line[line.index(' ') + 1:].strip().split(" ")
                if obj:
                    match line[:2]:
                        case 'v ':
                            newvs = vs
                            points.append(VectorUV(float(newvs[0]), float(newvs[1]), float(newvs[2])))
                        case 'f ':
                            tries.append([(int(vert) - 1) if '/' not in vert else (int(vert[:vert.index('/')]) - 1) for vert in vs])
                else:
                    if line == "new":
                        newMsh.tris.append([Tri(points[tri[0]], points[tri[1]], points[tri[2]]) for tri in tries])
                        points = []
                        tries = []
                        obj = True
                        continue

                    if line == "next":
                        newMsh.tris.append([Tri(points[tri[0]], points[tri[1]], points[tri[2]]) for tri in tries])
                        continue

                    newpoint = [float(vert) for vert in vs]
                    points[int(line[:line.index(' ')])] = VectorUV(newpoint[0], newpoint[1], newpoint[2])

        return newMsh

    else:
        # OBJ Format
        try:
            exists = open(filename[:-4] + ".aobj", 'r')
        except:
            CreateAOBJ(filename)
        else:
            exists.close()
        looking = True
        a = 0
        st = 0
        nd = 0
        # Looking for first frame
        while looking:
            try:
                test = open(filename[:-4] + str(a) + ".obj")
            except:
                a += 1
                if a > 100:
                    print("Could not find any frames. Is the obj exported as an animation?")
            else:
                test.close()
                st = a
                looking = False
        looking = True
        # Looking for last frame
        while looking:
            try:
                test = open(filename[:-4] + str(a + 1) + ".obj")
            except:
                nd = a
                looking = False
            else:
                test.close()
                a += 1
                
        newMsh = Mesh([], position=position, rotation=rotation, scale=scale, colour=colour, id=id, cull=cull, material=material, visible=visible, frame=0)
        for f in range(st, nd):
            newMsh.tris.append(LoadMesh(filename[:-4] + str(f) + ".obj", position, rotation, scale, colour, id, material, cull, visible).tris)

        return newMsh

def GlTFComponentTypeToUnpackParameters(value):
    match value:
        case 5120:
            # Signed Byte
            return ('b', 1)
        case 5121:
            # Unsigned Byte
            return ('B', 1)
        case 5122:
            # Signed Short
            return ('h', 2)
        case 5123:
            # Unsigned Short
            return ('H', 2)
        case 5125:
            # Unsigned Int
            return ('I', 4)
        case 5126:
            # Float
            return ('f', 4)

try:
    lightMesh = LoadMesh("z3dpy/mesh/light.obj")
    lightMesh.id = -1
    lightMesh.SetColour([255, 0, 0])

    dotMesh = LoadMesh("z3dpy/mesh/dot.obj")
    dotMesh.id = -1
    dotMesh.SetColour([255, 0, 0])

    arrowMesh = LoadMesh("z3dpy/mesh/axisZ.obj")
    arrowMesh.id = -1
    arrowMesh.SetColour([255, 0, 0])
except:
    print("Failed to load built-in meshes. (is the z3dpy folder missing?)")

def MeshUniqPoints(mesh):
    buffer = ()
    for tri in mesh.tris:
        for point in tri[:3]:
            if point not in buffer:
                buffer += (point,)
                yield point




#==========================================================================
#  
# Animated OBJ Format
#
#==========================================================================

def CreateAOBJ(filename):
    count = 1
    verts = 0
    while True:
        try:
            file = open(filename[:-4] + str(count) + filename[-4:], 'r')
            file.close()
            count += 1
        except:
            break

    def Compare(v, string):
        return v[0] == string[0] and v[1] == string[1] and v[2] == string[2]

    output = ""
    vertis = []
    start = True

    for f in range(1, count):
        file = open(filename[:-4] + str(f) + filename[-4:], 'r')
        verts = 0
        buffer = ""
        while (line := file.readline()):
            if line:
                if start:
                    buffer += line
                if line[:2] == "v ":
                    strip = line[2:].strip()
                    split = strip.split(' ')
                    if start:
                        vertis.append(split)
                    else:
                        verts += 1
                        if verts > len(vertis):
                            break
                        if not Compare(vertis[verts - 1], split):
                            buffer += str(verts - 1) + ' ' + strip + "\n"
                            vertis[verts - 1] = split

        if verts and verts != len(vertis):
            buffer = ""
            f -= 1
            start = True
            vertis = []
            output += "new\n"
            continue

        output += buffer + ("a\n" if start else "next\n")
        start = False
        file.close()

    file = open(filename[:-4] + ".aobj", 'w')
    file.write(output)
    file.close()
    print("Your OBJ sequence has been converted to an animated obj.")




#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def MatrixMakeRotX(deg):
    rad = deg * 0.0174
    

def MatrixMakeRotY(deg):
    rad = deg * 0.0174
    

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174
    

def RotationMatrix(axis, degrees):
    rad = degrees * 0.0174
    match axis.index(1):
        case 0:
            return ((1, 0, 0, 0), (0, cos(rad), sin(rad), 0), (0, -sin(rad), cos(rad), 0), (0, 0, 0, 1))
        case 1:
            return ((cos(rad), 0, sin(rad), 0), (0, 1, 0, 0), (-sin(rad), 0, cos(rad), 0), (0, 0, 0, 1))
        case 2:
            return ((cos(rad), sin(rad), 0, 0), (-sin(rad), cos(rad), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

def TriMatrixMul(t, m):
    return [Vec3MatrixMul(t[0], m) + [t[0][3], t[0][4]], Vec3MatrixMul(t[1], m) + [t[1][3], t[1][4]], Vec3MatrixMul(t[2], m) + [t[2][3], t[2][4]], t[3], t[4], t[5], t[6]]

def Vec3MatrixMul(v, m):
    return [v[0] * m[0][0] + v[1] * m[1][0] + v[2] * m[2][0] + m[3][0], v[0] * m[0][1] + v[1] * m[1][1] + v[2] * m[2][1] + m[3][1], v[0] * m[0][2] + v[1] * m[1][2] + v[2] * m[2][2] + m[3][2]]

def MatrixMatrixMul(m1, m2):
    output = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for c in range(0, 3):
        for r in range(0, 3):
            output[r][c] = m1[r][0] * m2[0][c] + m1[r][1] * m2[1][c] + m1[r][2] * m2[2][c] + m1[r][3] * m2[3][c]
    return tuple(output)

# Stuff for the PointAt and View Matrix
def MatrixStuff(pos, target, up):
    newForward = VectorSub(target, pos)
    newForward = VectorNormalize(newForward)

    a = VectorMulF(newForward, DotProduct(up, newForward))
    newUp = VectorSub(up, a)
    newUp = VectorNormalize(newUp)

    newRight = CrossProduct(newUp, newForward)

    return (newForward, newUp, newRight)

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[2][1], temp[2][2], 0), (temp[1][0], temp[1][1], temp[1][2], 0), (temp[0][0], temp[0][1], temp[0][2], 0), (pos[0], pos[1], pos[2], 1))

def ViewMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[1][0], temp[0][0], 0.0), (temp[2][1], temp[1][1], temp[0][1], 0.0), (temp[2][2], temp[1][2], temp[0][2], 0.0), (-DotProduct(pos, temp[2]), -DotProduct(pos, temp[1]), -DotProduct(pos, temp[0]), 1.0))

def ProjectionMatrix(fov):
    a = screenSize[0] / screenSize[1]
    f = fov * 0.5
    f = tan(f)
    return [[a * f, 0, 0, 0], [0, f, 0, 0], [0, 0, iC[5] / (iC[5] - iC[4]), 1], [0, 0, (-iC[5] * iC[4]) / (iC[5] - iC[4]), 0]]




#==========================================================================
#  
# Ray Functions
#
#==========================================================================

def RayIntersectTri(ray, tri):
    deadzone = 0.1
    rayDr = RayGetDirection(ray)
    raySt = ray[1]

    e1 = VectorSub(tri[1], tri[0])
    e2 = VectorSub(tri[2], tri[0])
    h = CrossProduct(rayDr, e2)
    a = DotProduct(e1, h)
    if a < -deadzone or a > deadzone:
        f = 1 / a
        o = VectorSub(raySt, tri[0])
        ds = DotProduct(o, h) * f
        
        if 0.0 < ds < 1.0:
        
            q = CrossProduct(o, e1)
            v = DotProduct(rayDr, q) * f

            if v > 0.0 and ds + v < 1.0:

                l = DotProduct(e2, q) * f
                if 0.0 < l < RayGetLength(ray):
                    # Hit
                    #
                    # [0] is wether or not it hit
                    #
                    # [1] is location
                    #
                    # [2] is distance
                    #
                    # [3] is the tri that was hit
                    
                    return (True, VectorAdd(raySt, VectorMulF(rayDr, l)), l, tri)
    return (False,)

def RayIntersectMesh(ray, mesh):
    for t in TransformTris(mesh.tris, mesh.position, RotTo(mesh.rotation, (0, 0, 1)), (0, 1, 0)):
        hit = RayIntersectTri(ray, t)
        if hit[0]:
            return hit
    return (False,)

# Does a ray intersection test with the hitbox
def RayIntersectThingSimple(ray, thing):
    hit = RayIntersectMesh(ray, thing.hitbox.mesh.tris)
    if hit[0]:
        return hit
    return (False,)

# Does a ray intersection test with each triangle
def RayIntersectThingComplex(ray, thing):
    for m in thing.meshes:
        if thing.internalid == -2:
            trg = thing.rotation
        else:
            fullRot = VectorAdd(m.rotation, thing.rotation)
            trg = RotTo(fullRot, (0.0, 0.0, 1.0))
            up = RotTo(fullRot, (0.0, 1.0, 0.0))
        for t in TransformTris(m.tris, VectorAdd(m.position, thing.position), trg, up, m.scale, m.cull, m.material):
            inrts = RayIntersectTri(ray, t)
            if inrts[0]:
                return inrts
    return (False,)

def TriToRays(tri):
    return [Ray(tri[0], tri[1]), Ray(tri[1], tri[2]), Ray(tri[2], tri[0])]




#==========================================================================
#  
# Trains
#
#==========================================================================

def BakeTrain(train, passes=1, strength=1.0, amplitude=1.0):
    print("Baking Train...")
    lenX = len(train) - 1
    lenY = len(train[0])
    # Blurring to smooth
    for p in range(passes):
        for x in range(1, lenX):
            for y in range(1, lenY - 1):
                mx = x + 1
                my = y + 1
                mn = x - 1
                ny = y - 1

                # Doing a gaussian blur by de-valuing edges
                # manually
                edgeStrength = 0.8 * strength
                cornerStrength = 0.6 * strength

                p0 = train[x][y]
                p1 = train[mx][y] * edgeStrength
                p2 = train[mn][y] * edgeStrength
                p3 = train[x][my] * edgeStrength
                p4 = train[x][ny] * edgeStrength
                p5 = train[mx][my] * cornerStrength
                p6 = train[mx][ny] * cornerStrength
                p7 = train[mn][my] * cornerStrength
                p8 = train[mn][ny] * cornerStrength
                h = sum((p0, p1, p2, p3, p4, p5, p6, p7, p8)) / 9
                train[x][y] = h * amplitude

    trainMesh.tris = ()
    
    # Creating the mesh from the train.
    for point in range(0, lenX * (lenY - 2), 1):
        x = point % lenX
        y = point // lenX
        trainMesh.tris += (Tri([x, train[x][y + 1], y + 1], [x, train[x][y], y], [x + 1, train[x + 1][y], y]),)
        trainMesh.tris += (Tri([x + 1, train[x + 1][y + 1], y + 1], [x, train[x][y + 1], y + 1], [x + 1, train[x + 1][y], y]),)

    print("Done!")

def TrainInterpolate(train, fX, fY):
    x = max(fX, 0.0)
    y = max(fY, 0.0)
    x = min(x, len(train))
    y = min(y, len(train[0]))
    first = ListInterpolate(train[floor(fX)], fY)
    second = ListInterpolate(train[ceil(fX)], fY)
    difference = fX - floor(fX)
    return (second - first) * difference + first




#==========================================================================
#  
# Collisions and Physics
#
#==========================================================================

# GatherCollisions()
# Returns a list of lists, containing the two things that are colliding.
# Makes sure that there are no repeats in the list.

# Usage:
'''
myCharacter.hitbox = z3dpy.Hitbox()
thatTree.hitbox = z3dpy.Hitbox()
david.hitbox = z3dpy.Hitbox()

for collision in GatherCollisions([myCharacter, thatTree, david]):
    thing1 = collision[0]
    thing2 = collision[1]

'''

def GatherCollisions(thingList):
    results = []
    for me in range(len(thingList)):
        if thingList[me].hitbox:
            for thm in ListExclude(thingList, me):
                if thm.hitbox:
                    if thm.hitbox.id == thingList[me].hitbox.id:
                        if DistanceBetweenVectors(thm.position, thingList[me].position) < thm.hitbox.radius + thingList[me].hitbox.radius:
                            if [thm, thingList[me]] not in results:

                                myPos = thingList[me].position
                                thPos = thm.position
                                match thingList[me].hitbox.type:
                                    case 0:
                                        # Sphere
                                        # If the distance is within range, it's a hit.
                                        distance = DistanceBetweenVectors(myPos, thPos)
                                        if distance < thm.hitbox.radius:
                                            results.append([thingList[me], thm])
                                    case 2:
                                        # Cube
                                        # Just a bunch of range checks
                                        rad = thingList[me].hitbox.radius + thm.hitbox.radius
                                        hgt = thingList[me].hitbox.height + thm.hitbox.height
                                        if abs(myPos[0] - thPos[0]) <= rad:
                                            if abs(myPos[1] - thPos[1]) <= hgt:
                                                if abs(myPos[2] - thPos[2]) <= rad:
                                                    results.append([thingList[me], thm])
    return results

# BasicHandleCollisions()
# Takes 2 things: the other, and the pivot. The other will get manually placed outside of the pivot's hitbox.

# Physics Collisions will define the pivot as the Thing with the most velocity.

# Usage:
'''
myCharacter.hitbox = z3dpy.Hitbox()
thatTree.hitbox = z3dpy.Hitbox()
david.hitbox = z3dpy.Hitbox()

for collision in GatherCollisions([myCharacter, thatTree, david]):
    BasicHandleCollisions(collision)

'''

def BasicHandleCollisions(other, pivot):
    match other.hitbox.type:
        case 0:
            # Sphere Collisions
            # Simple offset the direction away from pivot.
            other.position = VectorMulF(DirectionBetweenVectors(other.position, pivot.position), other.hitbox.radius + pivot.hitbox.radius)
        case 2:
            # Cube Collisions

            if other.position[0] + other.hitbox.radius < (pivot.position[0] - pivot.hitbox.radius) + 0.5:
                # +X Wall Collision
                other.position[0] = pivot.position[0] - pivot.hitbox.radius - other.hitbox.radius
                return
            
            if other.position[0] - other.hitbox.radius > (pivot.position[0] + pivot.hitbox.radius) - 0.5:
                # -X Wall Collision
                other.position[0] = pivot.position[0] + pivot.hitbox.radius + other.hitbox.radius
                return
            
            if other.position[2] + other.hitbox.radius < (pivot.position[2] - pivot.hitbox.radius) + 0.5:
                # +Z Wall Collision
                other.position[2] = pivot.position[2] - pivot.hitbox.radius - other.hitbox.radius    
                return
            
            if other.position[2] - other.hitbox.radius > (pivot.position[2] + pivot.hitbox.radius) - 0.5:
                # -Z Wall Collision
                other.position[2] = pivot.position[2] + pivot.hitbox.radius + other.hitbox.radius
                return

            if other.position[1] > pivot.position[1]:
                # Ceiling Collision
                other.position[1] = pivot.position[1] + pivot.hitbox.height + other.hitbox.height
                if other.physics:
                    other.physics.velocity[1] = 0
                return

            # Floor Collision
            other.position[1] = pivot.position[1] - pivot.hitbox.height - other.hitbox.height
            if other.physics:
                GroundBounce(other)


# HandlePhysics()
# Updates the position of each thing based on it's physics properties.

# Usage:
'''
myCharacter.physics = z3dpy.PhysicsBody()

while True:
    z3dpy.GetDelta()

    HandlePhysics([myCharacter])

'''

def HandlePhysics(thing, floorHeight=0):
    if thing.movable and thing.physics:
        thing.physics.velocity = VectorAdd(thing.physics.velocity, thing.physics.acceleration)
        # Drag
        thing.physics.velocity = VectorSub(thing.physics.velocity, [airDrag * Sign(thing.physics.velocity[0]), airDrag * Sign(thing.physics.velocity[1]), airDrag * Sign(thing.physics.velocity[2])])
        thing.physics.rotVelocity = VectorSub(thing.physics.rotVelocity, [airDrag * Sign(thing.physics.rotVelocity[0]), airDrag * Sign(thing.physics.rotVelocity[1]), airDrag * Sign(thing.physics.rotVelocity[2])])
        
        # Gravity
        thing.physics.velocity = VectorAdd(thing.physics.velocity, VectorMulF(VectorMulF(gravity, 5), delta))

        # Applying Velocities
        thing.position = VectorAdd(thing.position, VectorMulF(thing.physics.velocity, delta))
        thing.rotation = VectorAdd(thing.rotation, VectorMulF(thing.physics.rotVelocity, delta))

        flr = floorHeight - (thing.hitbox.height * 0.5)
        
        if thing.position[1] >= flr:
            thing.position[1] = flr
            if thing.physics.velocity[1] > 6:
                GroundBounce(thing)
            else:
                thing.physics.velocity[1] = 0

def HandlePhysicsFloor(things, f_floor_height=0):
    for t in things:
        HandlePhysics(t, f_floor_height)

def HandlePhysicsTrain(things, train):
    for t in things:
        if t.position[0] > 0.0 and t.position[0] < len(train) - 1:
            if t.position[2] > 0.0 and t.position[2] < len(train[0]) - 1:
                h4 = TrainInterpolate(train, t.position[0], t.position[2])
                HandlePhysics(t, h4)
                continue
        HandlePhysics(t, 0.0)

def PhysicsBounce(thing):
    d = VectorPureDirection(thing.physics.velocity)
    thing.physics.velocity = VectorMul(thing.physics.velocity, VectorMulF(d, -thing.physics.bounciness))

def GroundBounce(thing):
    newVel = thing.physics.velocity[1] * -thing.physics.bounciness
    if abs(newVel) < 0.001:
        thing.physics.velocity[1] = 0
        return
    thing.physics.velocity[1] = newVel

# PhysicsCollisions()
# Does GatherCollisions() and BasicHandleCollisions() automatically, with some
# velocity manipulation when a physics body is involved.
# Will only push things that have physics bodies, so static things can be put in as well, as long as they have a hitbox.

# Usage:
'''
myCharacter.physics = z3dpy.PhysicsBody()
myCharacter.hitbox = z3dpy.Hitbox()

joe.physics = z3dpy.PhysicsBody()
joe.hitbox = z3dpy.Hitbox()

thatTree.hitbox = z3dpy.Hitbox()
thatOtherTree.hitbox = z3dpy.Hitbox()

# Then during the draw loop...

        z3dpy.GetDelta()

        HandlePhysics([myCharacter, joe])

        PhysicsCollisions([myCharacter, thatTree, thatOtherTree, joe])

'''

def PhysicsCollisions(thing_list):
    for cols in GatherCollisions(thing_list):
        if cols[0].physics:
            if cols[1].physics:
                # Start with a BasicHandleCollisions(), the pivot is the Thing with higher velocity
                if VectorCompare(cols[0].physics.velocity, cols[1].physics.velocity):
                    BasicHandleCollisions(cols[0], cols[1])
                else:
                    BasicHandleCollisions(cols[1], cols[0])

                # If the velocities aren't strong enough, skip the physics part.
                if max(cols[0].physics.velocity) >= 0.1 and max(cols[1].physics.velocity) >= 0.1:
                    myforce = VectorMulF(cols[0].physics.velocity, cols[0].physics.mass)
                    thforce = VectorMulF(cols[1].physics.velocity, cols[1].physics.mass)
                    # Add together the force, and apply it to both Things, so if one object is flung at another, the force should carry.
                    toforce = VectorAdd(myforce, thforce)
                    cols[0].physics.velocity = toforce
                    cols[1].physics.velocity = toforce
            else:
                BasicHandleCollisions(cols[0], cols[1])
        else:
            BasicHandleCollisions(cols[1], cols[0])

def Sign(f):
    return 0 if f == 0 else 1 if f > 0 else -1




#==========================================================================
#  
# Rendering
#
#==========================================================================

# Render()
# Uses the internal lists

# Usage:
'''
myCharacter = z3dpy.Thing([myMesh], [0, 0, 0])

z3dpy.AddThing(myCharacter)

def OnDeath():
    z3dpy.RemoveThing(myCharacter)

while True:
    for tri in z3dpy.Render():
        # Draw code here

'''

# Returns a formatted version for third-party draw functions.
def FormatTri(tri, is_1D):
    if is_1D:
        # Kivy, Tkinter
        return (tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1])
    else:
        # Pygame
        return ((tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1]))


def Render(sort_key=TriSortAverage, b_reverse=True):
    finished = []
    llen = len(layers)
    llayer = min(llen - 1, 2)
    finished += RenderMeshList([trainMesh])
    for l in range(llen):
        finished += RenderThings(layers[l], emitters if l == llayer else [], sort_key, b_reverse)
    
    return finished


# RenderThings()
# Specify your own list of things to render.

def RenderThings(things, emitters=[], sortKey=TriSortAverage, bReverse=True):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rendering.")
        return []
    else:
        viewed = []
        for t in things:
            if type(t) is list:
                # Dupe
                if things[t[0]].visible:
                    for m in things[t[0]].meshes:
                        if m.visible:
                            if m.cull:
                                viewed += RasterPt1(m.tris, VectorAdd(m.position, t[1]), VectorAdd(m.rotation, t[2]), m.material, VectorMul(m.scale, things[t[0]].scale))
                            else:
                                viewed += RasterPt1NoCull(m.tris, VectorAdd(m.position, t[1]), VectorAdd(m.rotation, t[2]), m.material, VectorMul(m.scale, things[t[0]].scale))
            else:
                if t.visible:
                    if t.movable:
                        # bMovable
                        for m in t.meshes:
                            if m.visible:
                                if m.frame == -1:
                                    # Standard Mesh
                                    if m.cull:
                                        viewed += RasterPt1(m.tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.material, VectorMul(m.scale, t.scale))
                                    else:
                                        viewed += RasterPt1NoCull(m.tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.material, VectorMul(m.scale, t.scale))
                                else:
                                    # AniMesh
                                    length = len(m.tris)
                                    if m.frame >= length:
                                        m.frame -= length
                                    if m.cull:
                                        viewed += RasterPt1(m.tris[m.frame], VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.material, VectorMul(m.scale, t.scale))
                                    else:
                                        viewed += RasterPt1NoCull(m.tris[m.frame], VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.material, VectorMul(m.scale, t.scale))
                    else:
                        # not bMovable
                        for m in t.meshes:
                            if m.visible:
                                if m.cull:
                                    viewed += RasterPt1Static(m.tris, VectorAdd(m.position, t.position), m.material)
                                else:
                                    viewed += RasterPt1StaticNoCull(m.tris, VectorAdd(m.position, t.position), m.material)

        for em in emitters:
            for p in em.particles:
                viewed += RasterPt1(em.template.tris, p[1], p[2], em.template.material, em.template.scale)

        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)
    

# RenderMeshList()
# Supply your own list of meshes to draw.

def RenderMeshList(meshList, sortKey=TriSortAverage, bReverse=True):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rendering.")
    else:
        viewed = []
        for mesh in meshList:
            viewed += RasterPt1(mesh.tris, mesh.position, mesh.rotation, mesh.material, mesh.scale)
        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)

# Draws things, as well as hitboxes, and any lights/rays you give it. 
# Triangles from debug objects will have an id of -1
def DebugRender(train=[], sortKey=TriSortAverage, bReverse=True, clearRays=False):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rendering.")
        return []
    else:
        global rays
        viewed = []
        things = GatherThings()
        for t in things:
            if type(t) is list:
                if things[t[0]].hitbox:
                    viewed += RasterPt1Static(things[t[0]].hitbox.mesh.tris, things[t[0]].position, things[t[0]].hitbox.mesh.material)
            else:
                if t.hitbox:
                    viewed += RasterPt1Static(t.hitbox.mesh.tris, t.position, t.hitbox.mesh.material)

        viewed.sort(key = sortKey, reverse=bReverse)
        
        for l in lights:
            match l.type:
                case 0:
                    viewed += RasterPt1Static(lightMesh.tris, l.position, lightMesh.material)
                case 1:
                    viewed += RasterPt1PointAt(arrowMesh.tris, (0, 0, 0), l.position, (0, 1, 0), MATERIAL_UNLIT, arrowMesh.scale)

        for d in dots:
            viewed += RasterPt1Static(dotMesh.tris, d, dotMesh.material)

        for r in rays:
            if r[0]:
                viewed += RasterPt1PointAt(arrowMesh.tris, r[1], r[2], iC[7], MATERIAL_UNLIT, arrowMesh.scale)
            else:
                viewed += RasterPt2NoPos([[r[1] + [[0, 0, 0], [0, 0]], VectorAdd(r[1], [0, 0.01, 0]) + [[0, 0, 0], [0, 0]], r[2] + [[0, 0, 0], [0, 0]], (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), -1]], MATERIAL_UNLIT)

        if train:
            for x in range(len(train)):
                for y in range(len(train[0])):
                    viewed += RasterPt1Static(dotMesh.tris, [x, train[x][y], y], dotMesh.shader)

        for e in emitters:
            viewed += RasterPt1Static(dotMesh.tris, e.position, dotMesh.shader)

        if clearRays:
            rays = []
        
        return RasterPt3(viewed)

def RasterPt1(tris, pos, rot, material, scale=(1.0, 1.0, 1.0)):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
    return RasterPt2NoPos(TransformTris(tris, pos, trg, up, scale, False, material), material)

def RasterPt1PointAt(tris, pos, target, up, material, scale=(1.0, 1.0, 1.0)):
    return RasterPt2NoPos(TransformTris(tris, pos, target, up, scale, False, material), material)

def RasterPt1NoCull(tris, pos, rot, material, scale=(1.0, 1.0, 1.0)):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
    return RasterPt2NoPos(TransformTris(tris, pos, trg, up, scale, True, material), material)

def RasterPt1StaticNoCull(tris, pos, material):
    return RasterPt2(tris, pos, material)


def RasterPt1Static(tris, pos, material):
    return RasterPt2([tri[:4] + [material.Local(tri)] + tri[5:] for tri in tris if DotProduct(VectorMul(tri[3], (-1, 1, 1)), iC[6]) > -0.4], pos, material)

def RasterPt2(tris, pos, material):
    output = []
    for tri in ViewTris(TranslateTris(tris, pos)):
        tri[4] = material.View(tri)
        output += TriClipAgainstPlane(tri, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output

def RasterPt2NoPos(tris, material):
    output = []
    for t in ViewTris(tris):
        t[4] = material.View(t)
        output += TriClipAgainstPlane(t, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output


def RasterPt3(tris):
    return (tri for i in ProjectTris(tris) for tri in TriClipAgainstScreenEdges(i))

# Lowest-Level Raster Functions
# Rastering is based on Javidx9's C++ series, although
# the resemblance is drifting further.
#
# My version has 3 stages: Transform, View, and Project.
#
#
# Transform takes a list of triangles and moves/rotates them in world space, given the position, and target direction.
#
# View takes a list of triangles and moves them to their position relative to the camera, as if the camera was the one moving/rotating.
#
# Project takes a list of triangles and flattens them to produce 2D triangles.
#
# The stages should be done in that order.
#

def TransformTris(tris, pos, trg, up=(0.0, 1.0, 0.0), scale=(1, 1, 1), noCull=False, material=MATERIAL_UNLIT):
    mW = PointAtMatrix(pos, trg, up)
    for t in tris:
        col = material.Local(t)
        nt = TriMatrixMul(TriMul(t, scale), mW)
        nt[4] = col
        if DotProduct(TriGetNormal(nt), iC[6]) < 0.4 or noCull:
            nt[4] = material.World(nt)
            yield nt

def ViewTris(tris):
    return (TriMatrixMul(tri, intMatV) for tri in tris)
                    
def ProjectTris(tris):
    return (TriMul(TriAdd(ProjectTri(tri), [1, 1, 0]), [iC[3], iC[2], 1]) for tri in tris)


# The World Matrix method of Transforming, requires TranslateTris() afterwards
def WTransformTris(tris, rot, material=MATERIAL_UNLIT):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotZ(rot[2]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotY(rot[1]))
    for t in tris:
        col = material.Local(nt)
        nt = TriMatrixMul(t, mW)
        nt[4] = col
        nt[4] = material.World(nt)
        yield nt
        
def TranslateTris(tris, pos):
    for tri in tris:
        yield TriAdd(tri, pos)


# Single triangle functions in the hopes I can eventually figure out multi-processing.

def TransformTri(tri, rot):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotY(rot[1]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotZ(rot[2]))
    nt = TriMatrixMul(tri, mW)
    return nt

def TranslateTri(tri, pos):
    return TriAdd(tri, pos)

def ViewTri(tri):
    return TriMatrixMul(tri, intMatV)




#==========================================================================
#  
# Lighting
#
#==========================================================================

# CheapLighting() and ExpensiveLighting()
# Returns the colour of all lighting. 

# Usage:
'''
def MyShader(tri):
    # Multiply the lighting with the tri's colour
    return z3dpy.VectorMul(z3dpy.TriGetColour(tri), CheapLighting(tri))
'''

# CheapLighting takes the direction towards the light source, no shadow checks or anything.
def CheapLighting(tri, lights=lights):
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    triPos = TriAverage(tri)
    num = 0
    if not len(lights):
        return (0, 0, 0)
    for l in lights:
        match l.type:
            case 0:
                # LIGHT_POINT
                dist = DistanceBetweenVectors(triPos, l.position)
                if dist <= l.radius:
                    lightDir = DirectionBetweenVectors(l.position, triPos)
                    if (dot := DotProduct(lightDir, TriGetNormal(tri))) < 0:
                        d = dist/l.radius
                        intensity = (1 - (d * d)) * l.strength
                        colour = VectorAdd(colour, VectorMulF(l.colour, intensity * -dot))
                        num += 1

            case 1:
                # LIGHT_SUN
                if (dot := DotProduct(l.position, TriGetNormal(tri))) < 0:
                    intensity = -dot * l.strength
                    colour = VectorAdd(colour, VectorMulF(l.colour, intensity))
                    num += 1
            
            case 2:
                # LIGHT_SPOT
                dist = DistanceBetweenVectors(triPos, l.position)
                if dist < l.radius:
                    if ShortestPointToPlane(triPos, l.direction, l.position) > 0:
                        if (dot := DotProduct(l.direction, VectorNormalize(VectorSub(l.position, triPos)))) < 0:
                            d = dist / l.radius
                            intensity = (1 - (d * d)) * l.strength
                            colour = VectorAdd(colour, VectorMulF(l.colour, intensity * -dot))


    inverse = 1/max(num, 1)
    return VectorMax(VectorMinF(VectorMulF(colour, inverse), 1.0), worldColour)

# ExpensiveLighting uses the direction towards the light source, and tests for ray collisions to create shadows.
def ExpensiveLighting(tri, shadow_casters=GatherThings(), lights=lights):
    if shadow_casters == []:
        shadow_casters = GatherThings()
    num = 0
    normal = TriGetNormal(tri)
    shading = 0.0
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    pos = TriAverage(tri)
    if not len(lights):
        return (0, 0, 0)
    for l in lights:
            match l.type:
                # LIGHT_POINT
                case 0:
                    dist = DistanceBetweenVectors(pos, l.position)
                    if dist <= l.radius:
                        lightDir = DirectionBetweenVectors(l.position, pos)
                        shade = DotProduct(lightDir, normal)
                        if shade < 0:
                            testRay = Ray(pos, l.position)

                            # Checking for shadows
                            for th in shadow_casters:
                                inters = RayIntersectThingComplex(testRay, th)
                                if inters[0]:
                                    # Making sure it's not this triangle by comparing world position
                                    if not VectorEqual(TriAverage(tri), pos):
                                        break
                            else:
                                shading += shade
                                d = (dist / l.radius)
                                intensity += (1 - (d * d)) * l.strength
                                colour = VectorAdd(colour, VectorMulF(l.colour, intensity))
                                num += 1
                # LIGHT_SUN
                case 1:
                    if (shade := DotProduct(l.direction, normal)) > 0:
                        testRay = Ray(pos, VectorAdd(pos, VectorMulF(VectorNegate(l.direction), 25)))
                        rays.append(testRay)
                        for th in shadow_casters:
                            intersection = RayIntersectThingComplex(testRay, th)
                            if intersection[0]:
                                if not VectorEqual(intersection[4], pos):
                                    break
                        else:
                            shading += shade
                            num += 1
                
                # LIGHT_SPOT
                case 2:
                    if ShortestPointToPlane(pos, l.direction, l.position) > 0:
                        if (shade := DotProduct(l.rotation, normal)) > 0:
                            for th in shadow_casters:
                                intersection = RayIntersectThingComplex(testRay, th)
                                if intersection[0]:
                                    if not VectorEqual(intersection[4], pos):
                                        break
                            else:
                                shading += shade
                                intensity += (1 - (d * d)) * l.strength
                                colour = VectorAdd(colour, VectorMulF(l.colour, intensity))
                                num += 1

    colour = VectorDivF(colour, max(num, 1))
    return VectorMax(VectorMinF(VectorMulF(colour, shading), 1.0), worldColour)


# BakeLighting() and FlatLightingBaked()

# BakeLighting() saves the FlatLighting() calculation to the triangle's shade value, for cheaply referencing later.

# Usage:
'''
myLight = z3dpy.Light(z3dpy.LIGHT_POINT, [0.0, 0.0, 0.0], 0.8, 50, [255, 0, 0])

# If you add the light to the internal list, BakeLighting() doesn't need the lights argument.
z3dpy.lights.append(myLight)

# BakeLighting(things, *expensive, *lights, *thingsThatWillCastShadowsIfExpensive)
BakeLighting([myThing, myOtherThing])

# Then, during the draw loop...

for tri in RenderThings([myThing, myOtherThing]):
    # Draw Code

'''

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shade variable
def BakeLighting(things, expensive=False, lights=lights, shadow_casters=-1):
    print("Baking Lighting...")
    if shadow_casters == -1:
        shadow_casters = things
    for th in things:
        for m in th.meshes:
            for t in m.tris:
                if expensive:
                    calc = ExpensiveLighting(TranslateTri(TransformTri(t, VectorAdd(m.rotation, th.rotation)), VectorAdd(m.position, th.position)), shadow_casters, lights)
                else:
                    calc = CheapLighting(TranslateTri(TransformTri(t, VectorAdd(m.rotation, th.rotation)), VectorAdd(m.position, th.position)), lights)
                t[3] = tuple(calc)
    print("Lighting Baked!")




#==========================================================================
#  
# Rastering
#
#==========================================================================

def FillSort(n):
    return n[0]

# TriToLines()
# Converts a triangle to lines, calling a given draw function as they are calculated.

# Usage:
'''
def MyLineDraw(sx, sy, ex, ey):
    # Draw code here
    pass

for tri in RenderThings(things):
    z3dpy.TriToLines(tri, MyLineDraw)
'''

# Part One: From P1 to P2

def TemplateLineDraw(sx, sy, ex, ey, tri):
    return

def TriToLines(tri, draw=TemplateLineDraw):
    list = [VectorFloor(tri[0]), VectorFloor(tri[1]), VectorFloor(tri[2])]
    list.sort(key=FillSort)
    if list[2][0] != list[0][0]:
        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])

        diff = floor(list[1][0] - list[0][0])
        if diff:

            diff3 = (list[1][1] - list[0][1]) / diff
            for x in range(0, diff + 1, Sign(diff)):
                rX = x + list[0][0]
                draw(rX, diff3 * x + list[0][1], rX, slope * x + list[0][1])

        FillTriangleLinePt2(list, slope, draw)

# Part Two: From P2 to P3

def FillTriangleLinePt2(list, fSlope, draw):
    # If this side is flat, no need.
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        diff4 = list[1][0] - list[0][0]
        slope2 = (list[2][1] - list[1][1]) / diff2
        for x in range(0, int(diff2) + 1, Sign(diff2)):
            rX = x + list[1][0]
            draw(rX, (slope2 * x) + list[1][1], rX, (fSlope * (x + diff4)) + list[0][1])

# TriToPixels()
# Converts a triangle to pixels, and calls a given draw function as they are calculated.

# Usage:
'''
def MyPixelDraw(x, y):
    # Draw code here
    pass


for tri in z3dpy.Render():
    z3dpy.TriToPixels(tri, MyPixelDraw)

'''

def TemplatePixelDraw(x, y):
    return

def TriToPixels(tri, draw=TemplatePixelDraw):
    list = [VectorFloor(tri[0]), VectorFloor(tri[1]), VectorFloor(tri[2])]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX:
        slope = (list[2][1] - list[0][1]) / diffX
        diff = list[1][0] - list[0][0]

        # If this side's flat, no need.
        if diff:
            diffY = list[1][1] - list[0][1]
            diff3 = diffY / diff

            for x in range(floor(diff) + 1):

                ranges = [floor(diff3 * x + list[0][1]), floor(slope * x + list[0][1])]

                fX = floor(x + list[0][0])

                ranges.sort()

                for y in range(ranges[0], ranges[1] + 1):
                    draw(fX, y)

        TriToPixelsPt2(list, slope, diff, draw)

def TriToPixelsPt2(list, fSlope, diff, draw):
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        slope2 = (list[2][1] - list[1][1]) / diff2

        for x in range(floor(diff2)):
            # Repeat the same steps except for this side now.
            ranges = [floor(slope2 * x + list[1][1]), floor(fSlope * (x + diff) + list[0][1])]
            if ranges[0] == ranges[1]:
                continue

            ranges.sort()
            fX = floor(x + list[1][0])
            for y in range(ranges[0], ranges[1] + 1):
                draw(fX, y)

# TriToTexels()
# Converts a triangle into pixels with UV coordinates, and calls a given draw function as they are calculated.

# Usage:
'''
def MyTexelDraw(x, y, u, v):
    # UVs are normalized so they will need to be multiplied and modulo'd by the size of the applied texture.
    scaleX = len(myTexture[0])
    scaleY = len(myTexture)
    # Using abs() to mirror in the negatives
    actualU = abs(u * scaleX) % scaleX
    actualV = abs(v * scaleY) % scaleY

for tri in Render():
    TriToTexels(tri, myTexelDraw)

'''

def TemplateTexelDraw(x, y, u, v):
    return

def TriToTexels(tri, draw=TemplateTexelDraw):
    list = [VectorFloor(tri[0]) + tri[0][3:], VectorFloor(tri[1]) + tri[1][3:], VectorFloor(tri[2]) + tri[2][3:]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX:
        slope = (list[2][1] - list[0][1]) / diffX

        diff = list[1][0] - list[0][0]

        if diff:

            diffY = list[1][1] - list[0][1]
            diff3 = diffY / diff

            diffF = floor(diff) + 1

            for x in range(diffF):

                fX = x + floor(list[0][0])

                if fX < screenSize[0]:

                    ranges = [floor(diff3 * x + list[0][1]), floor(slope * x + list[0][1])]

                    rangD = ranges[1] - ranges[0]

                    if rangD:
                        sgn = Sign(rangD)

                        UVs = UVCalcPt1(list[0][4], list[1][4], list[2][4], x / diffF, x / diffX, True)

                        for y in range(max(ranges[0], 0), ranges[1] + sgn, sgn):
                            if y < screenSize[1]:
                                fUVs = UVCalcPt2((y - ranges[0]) / rangD, UVs[0], UVs[1], UVs[2], UVs[3])
                                draw(fX, y, fUVs[0], fUVs[1])
                            
        TriToTexelsPt2(list, slope, diff, diffX, draw)

def TriToTexelsPt2(list, fSlope, diff, diffX, draw):
    # Repeat the same steps except for this side now.
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        if diff2:
            slope2 = (list[2][1] - list[1][1]) / diff2

            diffF = floor(diff2) + 1

            for x in range(diffF):

                fX = x + floor(list[1][0])

                if fX < screenSize[0]:
                    
                    ranges = [floor(slope2 * x + list[1][1]), floor(fSlope * (x + diff) + list[0][1])]

                    rangd = ranges[1] - ranges[0]

                    if rangd:
                        sgn = Sign(rangd)

                        UVs = UVCalcPt1(list[0][4], list[1][4], list[2][4], x / diffF, (x + diff) / diffX, False)

                        for y in range(max(ranges[0], 0), min(ranges[1] + sgn, screenSize[1]), sgn):
                            fUVs = UVCalcPt2((y - ranges[0]) / rangd, UVs[0], UVs[1], UVs[2], UVs[3])  
                            draw(fX, y, fUVs[0], fUVs[1])

# UVCalcPt1()
# Fx is normalized X from either P1 - P2 or P2 - P3 depending on stage
# Fx2 is normalized X from P1 to P3
# stage is a bool, determines which side of the triangle is
# being drawn.

def UVCalcPt1(uv1, uv2, uv3, Fx, Fx2, bStage1):
    if bStage1:
        # From P1 to P2
        UVstX = Fx * (uv2[0] - uv1[0]) + uv1[0]
        UVstY = Fx * (uv2[1] - uv1[1]) + uv1[1]
    else:
        # From P2 to P3
        UVstX = Fx * (uv3[0] - uv2[0]) + uv2[0]
        UVstY = Fx * (uv3[1] - uv2[1]) + uv2[1]
    
    # From P1 to P3

    UVndX = Fx2 * (uv3[0] - uv1[0]) + uv1[0]
    UVndY = Fx2 * (uv3[1] - uv1[1]) + uv1[1]

    return (UVndX - UVstX, UVndY - UVstY, UVstX, UVstY)

def UVCalcPt2(Fy, uvDx, uvDy, UVstX, UVstY):
    return (Fy * uvDx + UVstX, Fy * uvDy + UVstY)


#==========================================================================
#  
# Projection Functions
#
#==========================================================================

def Projection(vector):
    if vector[2]:
        return [(vector[0] * howX) / vector[2], (vector[1] * howY) / vector[2], vector[2], vector[3], vector[4]]
    return vector
        
def ProjectTri(t):
    return [Projection(t[0]), Projection(t[1]), Projection(t[2]), t[3], t[4], t[5], t[6]]




#==========================================================================
#  
# Calculating How Projection
#
#==========================================================================

# Wrote code to brute-force finding a single multiplier that could do most of
# the projection.
# I call it: How-Does-That-Even-Work Projection
# I realize now that it's basically just pre-multiplying the matrix, but let me have this.

# Instead of a matrix, it's now [ (x * howX) / Z, (y * howY) / Z, 1 ]

# It's still gotta divide by Z to get perspective, without is orthographic.

# The current settings are FOV of 90, and aspect ratio of 16:9.
# To recalculate, use SetFOV(f_fov) or SetAspectRatio(f_aspect_ratio).


howX = 0.56249968159
howY = 1.0

fov = 90
aspectRatio = 9/16


def SetFOV(f_fov):
    global howX
    global howY
    global fov
    found = CalculateCam(f_fov, 500, aspectRatio)
    howX = found[0]
    howY = found[1]
    fov = f_fov

# Aspect Ratio: put height over width as a fraction, so
# 16:9 is 9/16, 4:3 is 3/4, and so on.
# It also accepts raw resolution for unusual aspect ratios
def SetAspectRatio(f_aspect_ratio):
    global howX
    global howY
    global aspectRatio
    found = CalculateCam(fov, 500, f_aspect_ratio)
    howX = found[0]
    howY = found[1]
    aspectRatio = f_aspect_ratio

def SetCameraConstants(x, y):
    global howX
    global howY
    howX = x
    howY = y

def ComplexX(x, f, how):
    return how * f * x

def ComplexY(x, f):
    return f * x

def SimpleFormula(x, m):
    return m * x

def Compare(m, fullGraph):
    score = 0
    for x in range(len(fullGraph)):
        realY = fullGraph[x]
        guessY = SimpleFormula(x, m)
        score += abs(realY - guessY)
    return score

calc = True

# Calculating Camera Variables
#
# Takes the full formula, graphs it, then tries to replicate that graph as
# closely as possible with m * x

# m starts at 1, then randomly guesses within a continually shrinking radius
# to find a better and better solution.
#
# It's a bit like gradient descent but I was hoping the randomness would help it
# avoid false peaks.
#

def CalculateCam(foV, farClip, aspectRatio):
    print("Calculating Camera Constants")
    fov = foV * 0.0174533
    print("Graphing real formulas...")
    fullXGraph = []
    fullYGraph = []
    f = 1 / tan(fov* 0.5)
    for x in range(farClip):
        fullXGraph.append(ComplexX(x, f, aspectRatio))
        fullYGraph.append(ComplexY(x, f))
    print("Calculating slopes...")
    finished = []
    
    for z in range(0, 2):
        currentScore = 9999999
        bestM = 1
        noImp = 0
        srchRad = 12
        guessM = 1
        calc = True
        while calc:
            match z:
                case 0:
                    Score = Compare(guessM, fullXGraph)
                case 1:
                    Score = Compare(guessM, fullYGraph)
            if Score < currentScore:
                bestM = guessM
                currentScore = Score
            else:
                noImp += 1
                guessM = bestM
            if noImp > 50:
                srchRad /= 2
                noImp = 0
            if srchRad < 0.00001:
                calc = False
                finished.append(bestM)
            guessM = bestM + ((rand() - 0.5) * srchRad)
    print("Done!")
    print("z3dpy.SetCameraConstants(" + str(finished[0]) + ", " + str(finished[1]) + ")")
    return finished




#==========================================================================
#  
# Emitter/Particle Functions
#
#==========================================================================

# HandleEmitters()
# Takes a list of emitters (or the global list if no input),
# and updates the currently active particles, getting rid of
# expired ones, before creating more if below the max.

# Usage:
'''
# Load a mesh to serve as the template
myMesh = z3dpy.LoadMesh("z3dpy/mesh/cube.obj")

# Emitter(vPos, meshTemplate, iMax, vVelocity, fLifetime, vGravity)
myEmitter = z3dpy.Emitter([1.0, 2.0, 3.0], myMesh, 150, [5.0, 0.0, 0.0], 15.0, [0.0, 9.8, 0.0])


# Internal List
#


# append to the global list
z3dpy.emitters.append(myEmitter)

while True:

    z3dpy.HandleEmitters()

    # Emitters in the global list will be drawn with Render()
    for tri in zp.Render():


# Your own list
#

while True:

    z3dpy.HandleEmitters([myEmitter])

    # Emitters is an argument in RenderThings()
    for tri in z3dpy.RenderThings([myThing, thatTree], [myEmitter])

'''

def ParticleFilter(pt): return pt[0] > delta

def HandleEmitters(emitters=emitters):
    for emitter in emitters:
        emitter.particles = list(filter(ParticleFilter, emitter.particles))
        for pt in emitter.particles:
            pt[0] -= delta
            # Basic version of physics for particles
            pt[2] = VectorSub(pt[2], [airDrag * Sign(pt[2][0]), airDrag * Sign(pt[2][1]), airDrag * Sign(pt[2][2])])
            pt[2] = VectorAdd(pt[2], VectorMulF(VectorMulF(emitter.gravity, 5), delta))
            pt[1] = VectorAdd(VectorMulF(pt[2], delta), pt[1])
        
        if emitter.active:
            if len(emitter.particles) < emitter.max:
                if emitter.randomness:
                    emitter.particles += (Part(emitter.position, VectorAdd(emitter.velocity, ((rand() - 0.5) * emitter.randomness, (rand() - 0.5) * emitter.randomness, (rand() - 0.5) * emitter.randomness)), emitter.lifetime),)
                else:
                    emitter.particles += (Part(emitter.position, emitter.velocity, emitter.lifetime),)

#==========================================================================
#  
# Utilities
#
#==========================================================================

# WhatIs() will take a list and figure out what object it is

def WhatIs(list_object):
    if type(list_object) is not list:
        return type(list_object).__name__

    match len(list_object):
        case 2:
            return "Vector2"
        case 3:
            if type(list_object[1]) is list:
                return "Particle"
            return "Vector"
        case 4:
            if type(list_object[0]) is list:
                return "Ray"
            return "Vector4"
        case 5:
            return "VectorUV"
        case 7:
            return "Triangle"
                    
def RGBToHex(vColour):
    def intToHex(int):
        int = min(int, 255)
        return hex(max(int, 0))[2:].rjust(2, "0")
    return "#" + intToHex(floor(vColour[0])) + intToHex(floor(vColour[1])) + intToHex(floor(vColour[2]))

# Triple Equals, because I think Python should have that feature. Compares the locations of their pointers instead of value.
# I guess it's good for knowing wether you've got a reference or copy.
# I've heard that this might not work depending on the interpreter.
def TripleEquals(a, b):
    return id(a) == id(b)

# List Utilities

def ListInterpolate(lst, fIndex):
    flr = floor(fIndex)
    if fIndex > 0:
        if fIndex < len(lst):
            first = lst[flr]
            difference = lst[ceil(fIndex)] - first
            return difference * (fIndex - flr) + first
        return lst[-1]
    return lst[flr]

# My solution to the built-in remove()
def ListExclude(lst, index): return lst[:index] + lst[index+1:]

# My own list flattener, as it seems NumPy is the only other option.
def ListNDFlatten(list_of_lists):
    test = list_of_lists
    while type((test := [item for sublist in test for item in sublist])[0]) is list: pass
    return test


#==========================================================================
#  
# Z3dPyFast
#
#==========================================================================

try:
    import z3dpyfast
except:
    def Fast(): print("z3dpyfast was not found, defaulting to pure Python.")
else:
    def Fast():
        global DistanceBetweenVectors
        global DirectionBetweenVectors
        global ShortestPointToPlane
        global VectorUVIntersectPlane
        global RotTo
        global TriGetNormal
        global MatrixStuff
        global PointAtMatrix
        #global TriToLines
        DistanceBetweenVectors = z3dpyfast.DistanceBetweenVectors
        DirectionBetweenVectors = z3dpyfast.DirectionBetweenVectors
        ShortestPointToPlane = z3dpyfast.ShortestPointToPlane
        VectorUVIntersectPlane = z3dpyfast.VectorUVIntersectPlane
        RotTo = z3dpyfast.RotTo
        TriGetNormal = z3dpyfast.GetNormal
        MatrixStuff = z3dpyfast.MatrixStuff
        PointAtMatrix = z3dpyfast.MatrixMakePointAt
        #TriToLines = z3dpyfast.TriToLines
        
        print("z3dpyfast loaded.")
    # Not yet
    '''
    class Z3dPyScreen():
        def __init__(self):
            # [&hWnd, &Factory, &wcex, &RenderTarget]
            self.data = [0, 0, 0, 0]

        def Init(self, width, height):
            self.data = z3dpyfast.NewWindow(width, height, self.data)
                    
        #def SetBackgroundColour(self, vColour): z3dpyfast.SetBackgroundColour(vColour)

        def Clear(self): z3dpyfast.ClearScreen(self.data)
                    
        #def Draw(self, tri): z3dpyfast.DrawTri(tri)
                    
        #def Update(self): z3dpyfast.UpdateScreen()
                    
        def Release(self): z3dpyfast.DestroyWindow(self.data)
    
    screen = Z3dPyScreen()
    '''
def fast():
    Fast()

## Deprecated
    
def SetHowVars(x, y):
    SetCameraConstants(x, y)

def FindHowVars(f_fov, f_aspect_ratio):
    fov = f_fov
    SetAspectRatio(f_aspect_ratio)

def RotTo(vRot, VTarget):
    return VectorRotate(VTarget, vRot)

def VectorDoP(v1, v2):
    return DotProduct(v1, v2)

def VectorCrP(v1, v2):
    return CrossProduct(v1, v2)

def Raster(sortKey=TriSortAverage, bReverse=True):
    return Render(sortKey, bReverse)

def RasterThings(things, emitters=[], sortKey=TriSortAverage, bReverse=True):
    return RenderThings(things, emitters, sortKey, bReverse)

def RasterMeshList(meshList, sortKey=TriSortAverage, bReverse=True):
    return RenderMeshList(meshList, sortKey, bReverse)

def DebugRaster(train=[], sortKey=TriSortAverage, bReverse=True, clearRays=False):
    return DebugRender(train, sortKey, bReverse, clearRays)
##