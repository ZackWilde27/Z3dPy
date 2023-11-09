# -zw
'''
Z3dPy v0.3.9
THE COMPLETE OVERHAUL UPDATE

*Nightly version, wiki/examples are based on the release version

LEGEND:
- Parameters marked with * are optional

- Most parameters have a starting letter denoting type.
Capitals mean normalized.

- Functions are CapitalizedCamelCase, variables are regularCamelCase.


Change Notes:


THE RETURN OF OBJECTS

- The larger objects have now been converted to classes, this includes:
Meshes
AniMeshes (which are now just meshes)
Emitters
Cameras
Things

All object functions for these are either redundant and thus removed, or are now functions inside the objects.

Smaller objects like Vectors, Rays, Tris, Dupes, Hits, and Particles are still the same for max speed

- Removed WhatIs().


RENDERING

- Raster functions have been renamed to Render functions.
This includes:
Render()
DebugRender()
RenderThings()
RenderMeshList()

The old functions will still be there for backwards compatibility


SHADERS

- Instead of having a separate draw function
for each shade, I'm introducing a shader system.

Each mesh now has a shader property. It's a function
that returns the colour for a given triangle.

For example:

    myMesh = z3dpy.LoadMesh("z3dpy/mesh/suzanne.obj")

    myMesh.shader = SHADER_SIMPLE

    then during the draw loop...

    for tri in z3dpy.RenderMeshList([myMesh]):
        # Now the colour is pre-set.
        pygame.draw.polygon(mySurface, z3dpy.TriGetColour(tri), ...)

        # You may need a VectorFloor() or VectorCeil() to keep things integer-only.


shader has 5 built-in options:

SHADER_UNLIT (default)
    Tri's colour is unchanged

SHADER_SIMPLE
    Basic direction shading.

SHADER_STATIC
    Baked lighting

SHADER_DYNAMIC
    Dynamic lighting

For example:

    def MyShader(tri):
        return z3dpy.TriGetColour(tri)

    myMesh = z3dpy.LoadMesh("mesh/cube.obj")

    myMesh.shader = MyShader


DRAWING

- Completely changed how TriTo__() works, instead of a for loop, the functions take
a draw method.

    def MyDraw(x, y):
        pixelArray[x][y] = z3dpy.TriGetColour(tri)

    while True:
        for tri in z3dpy.Raster():
            z3dpy.TriToPixels(tri, MyDraw)

TriToPixels(tri, draw)
    draw function is given 2 parameters, x, y

TriToLines(tri, draw)
    draw function is given 4 parameters, sx, sy, ex, ey

The current triangle in the draw function can be accessed as 'tri', without having to pass it in.

- Fixed TriToPixels() and TriToLines() visual glitches.

- Added TriToTexels(), which will convert a triangle into pixels with UV coordinates.
    UVs are normalized, so you'll have to multiply and modulo by the size of the texture.

    TriToTexels(tri, draw)
        draw function is given 4 parameters, x, y, u, v


- Removed PgPixelShader() and TkPixelShader(), as there's no longer overhead with
TriToTexels().

- PgDrawTri__() and TkDrawTri__() are now deprecated, though can still be used.

- Added FormatTri(tri, Is1D), which will take a tri and turn it into a list of 2D points for
drawing libraries. Tkinter and Kivy use a 1D array, while PyGame uses a 2D array.

- Working on the texture code, I narrowed down a couple issues to the mesh importer
rather than the interpolator, so the error is at least more consistent, though
there are still a few problems.


ANIMATED MESHES

- Fixed broken animated meshes

- Created my own Animated OBJ format (.aobj) because the standard method is
inefficient. My method only stores locations of verticies when they change, and
combines it all into one file.
(It may be case-dependent, but in my testing it's a lot smaller than
an OBJ sequence.)

It starts with the first OBJ file as normal, before an 'a' on it's own line, then
it switches to a format of "(vert number) x y z" for each vert that moves, and
a "next" on it's own line when a new frame begins. If the amount of verticies changes
from one frame to the next, there will be a 'new' instead of 'next', followed by
the OBJ file of the next frame, before switching back after an 'a'.

OBJ sequences will automatically be converted to an aobj file on loading, with
a printed message about it. I've also included a separate script for converting.


MESHES

- Fixed LoadMesh() throwing an error when the file wasn't found, and a "/" was not in the filename.

- Renamed suzanne.obj after realizing my mistake.


Z3DPYFAST

- z3dpyfast is no longer enabled by default. Initialize it with z3dpy.fast()
Though once the functions are replaced, you can't go back to pure Python without resetting.


MISC

- Forgot to convert the rotation to direction when defining a sun light in the new lights object,
it's now fixed.

- UVCalc() returns [y, x] when I meant for it to return [x, y], but somehow it looks more correct that way,
so I'm leaving it for now.

- BakedLighting() now requires the list of things. To get the original default behaviour,
put in z3dpy.GatherThings() as the argument.

- Hit functions have been renamed to better match other functions, this includes
HitGetDistance()
HitGetPos()
HitGetNormal()
HitGetWorldPos()

- SetInternalCam() error message displays again, I optimized it too far last time.

- Added ListNDFlatten(list), as looking online it seems like NumPy is the only other option

- Renamed Vec3MatrixMulOneLine() to just Vec3MatrixMul().

- Renamed sign() to Sign(), to fit the rules.

- Optimizations, but I mean that's a given.

'''

# Time for delta-time calculations
from time import time

# Rand for finding projection constants
from random import random as rand

# Math for, well...
from math import sqrt, floor, ceil, sin, cos, tan

# z3dpyfast is imported at the bottom of the script to replace functions.

print("Z3dPy v0.3.9")

#==========================================================================
#  
# Variables
#
#==========================================================================

def SHADER_UNLIT(tri): return TriGetColour(tri)
def SHADER_SIMPLE(tri): return VectorMulF(tri[6], max(-tri[3][2], 0))
def SHADER_DYNAMIC(tri): return VectorMul(tri[6], CheapLighting(tri))
def SHADER_STATIC(tri): return VectorMul(tri[6], tri[5])
def debugShader(tri): return [255, 0, 0]

# Delta calculations
timer = time()

delta = 0.016666

def GetDelta():
    global delta
    global timer
    delta = time() - timer
    timer = time()
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
# [3] is the normal
# [4] is the center point in world space
# [5] is the baked shade
# [6] is colour
# [7] is Id

def Tri(vector1, vector2, vector3):
    return [vector1, vector2, vector3, GetNormal([vector1, vector2, vector3]), TriAverage([vector1, vector2, vector3]), (0.0, 0.0, 0.0), (255, 255, 255), 0]

'''
class Tri():
    def __init__(self, vector1, vector2, vector3):
        self.p1 = vector1
        self.p2 = vector2
        self.p3 = vector3
        self.normal = GetNormal([vector1, vector2, vector3])
        self.wpos = TriAverage([vector1, vector2, vector3])
        self.shade = (0.0, 0.0, 0.0)
        self.colour = (255, 255, 255)
        self.id = 0
'''

# Meshes:
#
# Colour is copied to triangles, used when drawing.
#
# Id is copied to triangles, as a way to check
# where a tri came from.
#

class Mesh():
    def __init__(self, tris, vPos=[0.0, 0.0, 0.0], vRot=[0.0, 0.0, 0.0], vColour=(255, 255, 255), iId=0, bCull=True, shader=SHADER_UNLIT, shaderFunction=None):
        self.tris = tris
        self.position = vPos
        self.rotation = vRot
        self.colour = (255, 255, 255)
        self.id = iId
        self.cull = bCull
        self.shader = shader
        self.frame = -1

    def SetColour(self, vColour):
        self.colour = vColour
        if self.frame == -1:
            for tri in self.tris:
                TriSetColour(tri, vColour)
        else:
            for frame in self.tris:
                for tri in frame:
                    TriSetColour(tri, vColour)
    
    def __repr__(self):
        return "Z3dPy Mesh:\n\tPos: " + str(self.position) + "\n\tRot: " + str(self.rotation) + "\n\tColour: " + str(self.colour) + "\n\tId: " + str(self.id) + "\n\tFrame: " + str(self.frame)

# Usage:
'''

# The mesh will be exported as numbered frames, remove the number from the name.
# So, if my list of OBJs was anim1.obj, anim2.obj, and so on:
enemyMesh = LoadAniMesh("mesh/anim.obj")

enemy = z3dpy.Thing([enemyMesh], 0, 5, 2)

while True:

    # Then during the draw loop, increment the animation.

    # ThingIncFrames() will increment the frame counter of all animeshes in a thing.
    z3dpy.ThingIncFrames(enemy)

'''

# Hitbox Object:
#
# Stores all the needed info regarding collisions, the type
# of hitbox, it's scale, and collision id.
#
# [0] is type
# [1] is id
# [2] is radius
# [3] is height
# [4] is hitbox mesh for drawing.
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

#def Hitbox(type = 2, id = 0, radius = 1, height = 1):
    #return [type, id, radius, height, LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [radius, height, radius])]

class Hitbox():
    def __init__(self, tyype = 2, id = 0, radius = 1, height = 1):
        self.type = tyype
        self.id = id
        self.radius = radius
        self.height = height
        self.mesh = LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [radius, height, radius])
    
    def UpdateVis(self):
        match self.type:
            case 2:
                self.mesh = LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [self.radius, self.height, self.radius])
            case _:
                self.mesh = LoadMesh("z3dpy/mesh/sphere.obj", [0, 0, 0], [self.radius, self.height, self.radius])
        self.mesh.colour = (255, 0, 0)
        self.mesh.id = -1
        


# OldPhysics Body:
#
# Enable physics with z3dpy.ThingSetupPhysics(myThing)
#
# [0] is pos velocity
# [1] is pos acceleration
# [2] is mass
# [3] is friction
# [4] is bounciness
# [5] is rot velocity
# [6] is rot acceleration
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

#def PhysicsBody():
    #return [[0, 0, 0], [0, 0, 0], 0.5, 15, 0.5, [0, 0, 0], [0, 0, 0]]

class PhysicsBody():
    def __init__(self):
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.mass = 0.5
        self.friction = 15
        self.bounciness = 0.5
        self.rotVelocity = [0, 0, 0]
        self.rotAcceleration = [0, 0, 0]

# Things:
#
# The Thing is what you would typically refer to as an 
# object, it has a collection of meshes, and collision data.
#
#
# [0] is the list of meshes
# [1] is position
# [2] is rotation
# [3] is hitbox
# [4] is physics body
# [5] is isMovable
# [6] is internal id
# [7] is user variable.
#
# Hitbox and Physics body are empty till you assign them.
#
# Internal id is usually the index for RemoveThing().
# -1 means it's a Dupe.
# -2 means the rotation value is the PointAt target

#def Thing(meshList, vPos):
    #return [meshList, vPos, [0, 0, 0], [], [], True, 0, 0]

class Thing():
    def __init__(self, meshList, vPos):
        self.meshes = meshList
        self.position = vPos
        self.rotation = [0, 0, 0]
        self.hitbox = None
        self.physics = None
        self.movable = True
        self.internalid = 0
        self.user = 0
    
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
#

def Dupe(iIndex, vPos, vRot):
    return [iIndex, vPos, vRot, -1]

# Cameras:
#
# Cameras hold info about where the screen is located in the world, and where it's pointing.
# Rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
#
# For a third person camera, set yourCam.target
# For a first person camera, call yourCam.SetTargetDir() or yourCam.SetTargetFP()
#
# To change the FOV, use FindHowVars()

# [0] is user variable
# [1] is position
# [2] is rotation
# [3] is near clip
# [4] is far clip
# [5] is target location
# [6] is up vector
#
    
class Cam():
    def __init__(self, vPosition, screenWidth=0, screenHeight=0):
        if screenWidth and screenHeight:
            global screenSize
            screenSize = (screenWidth, screenHeight)
        self.position = vPosition
        self.rotation = [0, 0, 0]
        self.nearClip = 0.1
        self.farClip = 1500
        self.target = [0, 0, 1]
        self.up = [0, 1, 0]
        self.user = 0

    def GetTargetDir(self):
        return VectorNormalize(VectorSub(self.target, self.position))

    def SetTargetDir(self, vector):
        self.target = VectorAdd(self.position, VectorNormalize(vector))

    def SetTargetFP(self):
        dir = RotTo(self.rotation, [0, 0, 1])
        self.target = VectorAdd(self.position, dir)
    
    def GetRightVector(self):
        return VectorCrP(self.GetTargetDir(), self.up)
    
    def Chase(self, location, speed):
        dspeed = speed * delta
        line = VectorMulF((self.position[0] - location[0], self.position[1] - location[1], self.position[2] - location[2]), dspeed)
        if VectorGetLength(line) < dspeed:
            self.position = location
            return True
        self.position = VectorSub(self.position, line)
        return False

# Internal Camera
#
# the internal camera is used to store info for various functions
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
    intMatV = LookAtMatrix(camera.position, camera.target, camera.up)

# Lights:
#
# Point lights use a combination of comparing directions and distance to light triangles.
#
# Sun lights use a simple static direction to light triangles.
#

#
# [0] is type
# [1] is position
# [2] is strength
# [3] is radius
# [4] is colour
# [5] is internal id
# [6] is user variable
#

LIGHT_POINT = 0
LIGHT_SUN = 1
LIGHT_SPOT = 2

class Light():
    def __init__(self, tyype, vPos, FStrength, fRadius, vColour=(255, 255, 255)):
        self.type = tyype
        if tyype:
            self.position = RotTo(vPos, [0, 0, 1])
        else:
            self.position = vPos
        self.rotation = [0, 0, 0]
        self.strength = FStrength
        self.radius = fRadius
        self.colour = VectorDivF(vColour, 255)

# Rays:
#
# Used for debug drawing rays in world space, or ray
# collisions.
#
# [0] is wether or not it's drawn as an arrow
# [1] is ray start location
# [2] is ray end location

def Ray(vRaySt, vRayNd, bIsArrow=False):
    return [bIsArrow, vRaySt, vRayNd]

# Usage:
'''

myRay = z3dpy.Ray(myCam.position, thatTree.position)

# Add the ray to the global list to get drawn with DebugRaster()
z3dpy.rays.append(myRay)

# and/or you could do a collision check
hit = zp.RayIntersectThingComplex(myRay, myCharacter)

if hit[0]:
    location = hit[1]
    distance = hit[2]
    normal = hit[3]
    wPosOfTri = hit[4]
    print(location, distance, normal, wPosOfTri)
else:
    print("Nope")
'''



# Dots:
#
# Dots is a list of vectors that will be drawn as points
# with DebugRaster().
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

# Now when debug rastering, it'll be drawn as a small trigon, with an id of -1.


for tri in DebugRaster():
    match z3dpy.TriGetId(tri):
        case -1:
            # Debug things
            z3dpy.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        case _:
            # Everything else
            z3dpy.PgDrawTriFLB(tri, screen, pygame)
            
'''


# Terrains / Trains:
#
# Z3dPy's terrain system to easily replace the flat floor
# of HandlePhysics(). Needs to be baked beforehand.
#
# [x][y] is the height at that particular location.
#
# Keep in mind it's an invisible floor, meant to match the
# environment rather than being drawn.

def Train(x, y):
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
# [0] is the list of currently active particles
# [1] is position
# [2] is the template mesh
# [3] is particle start velocity
# [4] is max number of particles
# [5] is particle lifetime
# [6] is particle gravity
# [7] is wether or not it's active.
# [8] is randomness of particle start velocity
#

class Emitter():
    def __init__(self, vPos, templateMesh, iMax, vVelocity, fLifetime, vGravity, fRandomness):
        self.particles = ()
        self.position = vPos
        self.template = templateMesh
        self.max = iMax
        self.velocity = vVelocity
        self.lifetime = fLifetime
        self.gravity = vGravity
        self.randomness = fRandomness

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

    for tri in z3dpy.Raster():
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

# PyGame came in clutch, because right now it's the only
# way to avoid writing the texture manually.
# Pixels above 0 alpha will be opaque.
def PgLoadTexture(filename, pygame):
    try:
        img = pygame.image.load(filename)
    except:
        return TestTexture()
    else:
        surf = pygame.surfarray.array2d(img)
        fnSurf = []
        for x in range(len(surf)):
            fnSurf.append([])
            for y in range(len(surf[0])):
                col = img.get_at((x, y))
                col = col[:3] + (col[3] > 0,)
                fnSurf[x].append(col)
        return fnSurf




#==========================================================================
#
# Object Functions
#
# Several objects are still lists, so these functions are
# human-friendly ways to set and retrieve variables
#
#==========================================================================

# TRIANGLES


# Functions for each point
def TriGetP1(tri):
    return tri[0]

def TriGetP2(tri):
    return tri[1]

def TriGetP3(tri):
    return tri[2]

# TriGetNormal() will return the current normal, while
# GetNormal() will calculate a new one.
def TriGetNormal(tri):
    return tri[3]

# Normals are automatically calculated during the raster
# process, and by default will be the world space normal.
def TriSetNormal(tri, vector):
    tri[3] = vector

def TriGetColour(tri):
    return tri[6]

# Colour is determined by the associated mesh's shader.
def TriSetColour(tri, vColour):
    tri[6] = vColour

def TriGetWPos(tri):
    return tri[4]

# World position is automatically calculated during the
# raster process, and by default will be the center point
# of the triangle in world space.
def TriSetWPos(tri, vector):
    tri[4] = vector

def TriGetShade(tri):
    return tri[5]

def TriSetShade(tri, FShade):
    tri[5] = FShade

def TriGetId(tri):
    return tri[7]

# Id is automatically calculated during the raster process,
# and by default will be the id of the associated mesh.
def TriSetId(tri, id):
    tri[7] = id


# THINGS


def AddThing(thing, iLayer=2):
    # Setting the internal id to the length of the list, which
    # corrosponds to it's new index
    thing.internalId = len(layers[iLayer])
    layers[iLayer].append(thing)

def AddThings(things, iLayer=2):
    for thing in things:
        AddThing(thing, iLayer)

def AddDupe(thing, position, rotation, iLayer=2):
    dupe = Dupe(thing.internalId, position, rotation)
    layers[iLayer].append(dupe)
    return dupe


def GatherThings():
    output = []
    for layer in layers:
        output += layer
    return output


# If you don't specify the layer, looks for it in the
# default layer.
def RemoveThing(thing, iLayer=2):
    global layers
    if len(layers[iLayer]) == 1:
        layers[iLayer] = []
        return
    dex = thing.internalId
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

def HitGetNormal(hit):
    return hit[3]

def HitGetTriPos(hit):
    return hit[4]




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

def VectorModF(v, f):
    return [v[0] % f, v[1] % f, v[2] % f]

def VectorComb(v):
    return v[0] + v[1] + v[2]

def VectorNormalize(v):
    l = VectorGetLength(v)
    return [v[0] / l, v[1] / l, v[2] / l] if l != 0 else v

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
    return vO[0] + vO[1] + vO[2] > vT[0] + vT[1] + vT[2]
    
def VectorFloor(v):
    return [floor(v[0]), floor(v[1]), floor(v[2])]
    
# Vector Cross Product gives you the direction of the 3rd dimension, given 2 Vectors. If you give it an X and a Y direction, it will give you the Z direction.
def VectorCrP(v1, v2):
    return [(v1[1] * v2[2]) - (v1[2] * v2[1]), (v1[2] * v2[0]) - (v1[0] * v2[2]), (v1[0] * v2[1]) - (v1[1] * v2[0])]

def VectorGetLength(v):
    return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

# Vector Dot Product compares 2 directions. 1 is the same, -1 is apposing.
# Useful for lighting calculations.
def VectorDoP(v1, v2):
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

    return VectorModF(newRot, 360)

# Rotation To Direction, relative to the target.
# Usage:
'''
    # To get the forward, up, or right vector of a Thing or Mesh:
    forward = RotTo(myThing.rot, [0, 0, 1])
    right = RotTo(myThing.rot, [1, 0, 0])
    up = RotTo(myThing.rot, [0, 1, 0])
'''
def RotTo(vRot, VTarget):
    nRot = WrapRot(vRot)
    nV = VectorRotateX(VTarget, nRot[0])
    nV = VectorRotateZ(nV, nRot[2])
    return VectorRotateY(nV, nRot[1])

def VectorIntersectPlane(pPos, pNrm, lSta, lEnd):
    pNrm = VectorNormalize(pNrm)
    plane_d = -VectorDoP(pNrm, pPos)
    ad = VectorDoP(lSta, pNrm)
    bd = VectorDoP(lEnd, pNrm)
    t = (-plane_d - ad) / (bd - ad)
    lineStartToEnd = VectorSub(lEnd, lSta)
    lineToIntersect = VectorMulF(lineStartToEnd, t)
    return VectorAdd(lSta, lineToIntersect)

def ShortestPointToPlane(point, plNrm, plPos):
    return VectorDoP(plNrm, point) - VectorDoP(plNrm, plPos)




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
    plane_d = -VectorDoP(pNrm, pPos)
    ad = VectorDoP(lSta, pNrm)
    bd = VectorDoP(lEnd, pNrm)
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


def TriAdd(t, v): return [VectorUVAdd(t[0], v), VectorUVAdd(t[1], v), VectorUVAdd(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriSub(t, v): return [VectorUVSub(t[0], v), VectorUVSub(t[1], v), VectorUVSub(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriMul(t, v): return [VectorUVMul(t[0], v), VectorUVMul(t[1], v), VectorUVMul(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriMulF(t, f): return [VectorUVMulF(t[0], f), VectorUVMulF(t[1], f), VectorUVMulF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

def TriDivF(t, f): return [VectorUVDivF(t[0], f), VectorUVDivF(t[1], f), VectorUVDivF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

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
            outT1 = [tri[first], VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[third]), VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[second]), tri[3], tri[4], tri[5], tri[6], tri[7]]
            yield outT1

        case 2:
            first = test.index(True)
            second = test.index(True, first + 1)
            third = test.index(False)
            outT1 = [tri[first], tri[second], VectorUVIntersectPlane(pPos, pNrm, tri[second], tri[third]), tri[3], tri[4], tri[5], tri[6], tri[7]]
            outT2 = [tri[first], outT1[2], VectorUVIntersectPlane(pPos, pNrm, tri[first], tri[third]), tri[3], tri[4], tri[5], tri[6], tri[7]]
            yield outT1
            yield outT2

def GetNormal(tri): return VectorNormalize(VectorCrP(VectorSub(tri[1], tri[0]), VectorSub(tri[2], tri[0])))

def TriAverage(tri):
    return [(tri[0][0] + tri[1][0] + tri[2][0]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.33333]


# Triangle Sorting functions
def triSortAverage(n):
    return (n[0][2] + n[1][2] + n[2][2]) * 0.3333333

def triSortFurthest(n):
    return max(n[0][2], n[1][2], n[2][2])

def triSortClosest(n):
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
# but I'm going to call it the Monkey Bars Method.

def Triangulate(listOfVectors):
    # Triangulating n-gon
    output = []
    points = [0, 1]
    for n in range(2, len(listOfVectors)):
        points.append(n)
        p1 = listOfVectors[points[0]]
        p2 = listOfVectors[points[1]]
        p3 = listOfVectors[points[2]]
        output.append(Tri(p1, p2, p3))
        points = [points[0], points[2]]
    return output




#==========================================================================
#  
# Mesh Functions
#
#==========================================================================

# Load OBJ File
def LoadMesh(filename, vPos=(0.0, 0.0, 0.0), VScale=(1.0, 1.0, 1.0)):
    try:
        file = open(filename)
    except:
            if filename.count("/") != 0:
                while filename.count("/") > 0:
                    filename = filename[filename.index("/") + 1:]
            if filename == "error.obj":
                raise Exception("Can't load placeholder mesh. (Is the z3dpy folder missing?)")
            else:
                print(filename[:-4], "was not found, replacing...")
                return LoadMesh("z3dpy/mesh/error.obj", vPos, VScale)
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
                        verts.append([float(currentLine[0]) * VScale[0], float(currentLine[1]) * VScale[1], float(currentLine[2]) * VScale[2], [0, 0, 0], [0, 0], 0])
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
                    normal = GetNormal([verts[p1], verts[p2], verts[p3]])
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
                        normal = GetNormal([verts[p1], verts[p2], verts[p3]])
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

    file.close()
    uvslen = len(storedUVs)
    if mat == -1:
        for tr in range(len(triangles)):
            nt = Tri(verts[triangles[tr][0]], verts[triangles[tr][1]], verts[triangles[tr][2]])
            if tr < uvslen:
                nt[0][4] = uvs[storedUVs[tr][0] - 1]
                nt[1][4] = uvs[storedUVs[tr][1] - 1]
                nt[2][4] = uvs[storedUVs[tr][2] - 1]
            output.append(nt)

        return Mesh(tuple(output), vPos)
    else:

        gathered.append(triangles)
        for trL in gathered:
            output.append([])
            for tr in range(len(trL)):
                nt = Tri(verts[trL[tr][0]], verts[trL[tr][1]], verts[trL[tr][2]])
                output[-1].append(nt)
                if tr < uvslen:
                    nt[0][4] = uvs[storedUVs[tr][0] - 1]
                    nt[1][4] = uvs[storedUVs[tr][1] - 1]
                    nt[2][4] = uvs[storedUVs[tr][2] - 1]

        meshes = [Mesh(tuple(trS), vPos) for trS in matoutputs]
        colours = colours[1:]
        colours.reverse()

        map(MeshSetColour, meshes, colours)
        return meshes

def MeshSetColour(mesh, colour):
    mesh.SetColour(colour)

def LoadAniMesh(filename, vPos=[0.0, 0.0, 0.0], VScale=(1.0, 1.0, 1.0)):
    if filename[-4:] == 'aobj':
        # AOBJ Format
        file = open(filename)
        newMsh = Mesh([], vPos)
        newMsh.frame = 0
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

                    #print(vs)
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
                
        newMsh = Mesh([], vPos)
        newMsh.frame = 0
        for f in range(st, nd):
            newMsh.tris.append(LoadMesh(filename[:-4] + str(f) + ".obj", [0, 0, 0], VScale).tris)

        return newMsh

try:
    lightMesh = LoadMesh("z3dpy/mesh/light.obj")
    lightMesh.id = -1
    lightMesh.colour = (255, 0, 0)

    dotMesh = LoadMesh("z3dpy/mesh/dot.obj")
    dotMesh.id = -1
    dotMesh.colour = (255, 0, 0)

    arrowMesh = LoadMesh("z3dpy/mesh/axisZ.obj")
    arrowMesh.id = -1
    arrowMesh.colour = (255, 0, 0)
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
    print("Your mesh has been converted to a .aobj")




#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def MatrixMakeRotX(deg):
    rad = deg * 0.0174
    return ((1, 0, 0, 0), (0, cos(rad), sin(rad), 0), (0, -sin(rad), cos(rad), 0), (0, 0, 0, 1))

def MatrixMakeRotY(deg):
    rad = deg * 0.0174
    return ((cos(rad), 0, sin(rad), 0), (0, 1, 0, 0), (-sin(rad), 0, cos(rad), 0), (0, 0, 0, 1))

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174
    return ((cos(rad), sin(rad), 0, 0), (-sin(rad), cos(rad), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

def TriMatrixMul(t, m):
    return [Vec3MatrixMul(t[0], m) + [t[0][3], t[0][4]], Vec3MatrixMul(t[1], m) + [t[1][3], t[1][4]], Vec3MatrixMul(t[2], m) + [t[2][3], t[2][4]], t[3], t[4], t[5], t[6], t[7]]

def Vec3MatrixMul(v, m):
    return [v[0] * m[0][0] + v[1] * m[1][0] + v[2] * m[2][0] + m[3][0], v[0] * m[0][1] + v[1] * m[1][1] + v[2] * m[2][1] + m[3][1], v[0] * m[0][2] + v[1] * m[1][2] + v[2] * m[2][2] + m[3][2]]

def MatrixMatrixMul(m1, m2):
    output = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for c in range(0, 3):
        for r in range(0, 3):
            output[r][c] = m1[r][0] * m2[0][c] + m1[r][1] * m2[1][c] + m1[r][2] * m2[2][c] + m1[r][3] * m2[3][c]
    return tuple(output)

# Stuff for the PointAt and LookAt Matrix
def MatrixStuff(pos, target, up):
    newForward = VectorSub(target, pos)
    newForward = VectorNormalize(newForward)

    a = VectorMulF(newForward, VectorDoP(up, newForward))
    newUp = VectorSub(up, a)
    newUp = VectorNormalize(newUp)

    newRight = VectorCrP(newUp, newForward)

    return (newForward, newUp, newRight)

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[2][1], temp[2][2], 0), (temp[1][0], temp[1][1], temp[1][2], 0), (temp[0][0], temp[0][1], temp[0][2], 0), (pos[0], pos[1], pos[2], 1))

def LookAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[1][0], temp[0][0], 0.0), (temp[2][1], temp[1][1], temp[0][1], 0.0), (temp[2][2], temp[1][2], temp[0][2], 0.0), (-VectorDoP(pos, temp[2]), -VectorDoP(pos, temp[1]), -VectorDoP(pos, temp[0]), 1.0))

def MatrixMakeProjection(fov):
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
    h = VectorCrP(rayDr, e2)
    a = VectorDoP(e1, h)
    if a < -deadzone or a > deadzone:
        f = 1 / a
        o = VectorSub(raySt, tri[0])
        ds = VectorDoP(o, h) * f
        
        if 0.0 < ds < 1.0:
        
            q = VectorCrP(o, e1)
            v = VectorDoP(rayDr, q) * f

            if v > 0.0 and ds + v < 1.0:

                l = VectorDoP(e2, q) * f
                if 0.0 < l < RayGetLength(ray):
                    # Hit
                    #
                    # [0] is wether or not it hit
                    #
                    # [1] is location
                    #
                    # [2] is distance
                    #
                    # [3] is normal of hit tri
                    #
                    # [4] is wpos of hit tri
                    
                    return (True, VectorAdd(raySt, VectorMulF(rayDr, l)), l, tri[3], tri[4])
    return (False,)

def RayIntersectMesh(ray, mesh):
    for t in TranslateTris(TransformTris(mesh.tris, mesh.rotation), mesh.position):
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
        if thing.internalId == -2:
            trg = thing.rotation
        else:
            fullRot = VectorAdd(m.rotation, thing.rotation)
            trg = RotTo(fullRot, (0.0, 0.0, 1.0))
            up = RotTo(fullRot, (0.0, 1.0, 0.0))
        for t in TransformTris(m.tris, VectorAdd(m.position, thing.position), trg, up):
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
    # Blurring to smooth
    for p in range(passes):
        for x in range(1, len(train) - 1):
            for y in range(1, len(train[0]) - 1):
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
#
#   myCharacter.hitbox = z3dpy.Hitbox()
#   thatTree.hitbox = z3dpy.Hitbox()
#   david.hitbox = z3dpy.Hitbox()
#
#   for collision in GatherCollisions([myCharacter, thatTree, david]):
#       thing1 = collision[0]
#       thing2 = collision[1]
#

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
#
#   myCharacter.hitbox = z3dpy.Hitbox()
#   thatTree.hitbox = z3dpy.Hitbox()
#   david.hitbox = z3dpy.Hitbox()
#
#   for collision in GatherCollisions([myCharacter, thatTree, david]):
#       BasicHandleCollisions(collision)
#

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
                other.position[1] = pivot.position[1] - pivot.hitbox.height - other.hitbox.height
                if other.physics:
                    # Set vertical velocity to 0
                    other.physics.velocity[1] = 0
                return

            # Floor Collision
            other.position[1] = pivot.position[1] - pivot.hitbox.height - other.hitbox.height
            if other.physics:
                GroundBounce(other)


# HandlePhysics()
# Updates the position of each thing based on it's physics properties.

# Usage:
#
#   myCharacter.physics = z3dpy.PhysicsBody()
#
#   while True:
#       HandlePhysics([myCharacter])
#

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

def HandlePhysicsFloor(things, fFloorHeight=0):
    for t in things:
        HandlePhysics(t, fFloorHeight)

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
#
#   myCharacter.physics = z3dpy.PhysicsBody()
#   myCharacter.hitbox = z3dpy.Hitbox()
#
#   joe.physics = z3dpy.PhysicsBody()
#   joe.hitbox = z3dpy.Hitbox()
#
#   thatTree.hitbox = z3dpy.Hitbox()
#   thatOtherTree.hitbox = z3dpy.Hitbox()
#
#   while True:
#       HandlePhysics([myCharacter, joe])
#
#       PhysicsCollisions([myCharacter, thatTree, thatOtherTree, joe])
#

def PhysicsCollisions(thingList):
    for cols in GatherCollisions(thingList):
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
#
# myCharacter = z3dpy.Thing([myMesh], [0, 0, 0])
#
# z3dpy.AddThing(myCharacter)
#
# def OnDeath():
#   z3dpy.RemoveThing(myCharacter)
#
# while True:
#   for tri in z3dpy.Render():
#       # Draw code here
#

# Returns a formatted version for third-party draw functions.
def FormatTri(tri, is1D):
    if is1D:
        # Kivy, Tkinter
        return (tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1])
    else:
        # Pygame
        return ((tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1]))


def Render(sortKey=triSortAverage, bReverse=True):
    finished = []
    llen = len(layers)
    llayer = min(llen - 1, 2)
    for l in range(llen):
        finished += RenderThings(layers[l], emitters if l == llayer else [], sortKey, bReverse)
    return finished


# RenderThings()
# Specify your own list of things to render.

# Usage:
#
# for tri in z3dpy.RenderThings([myCharacter]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#

def RenderThings(things, emitters=[], sortKey=triSortAverage, bReverse=True):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        viewed = []
        for t in things:
            if type(t) is list:
                # Dupe
                for m in things[t[0]].meshes:
                    if m.cull:
                        viewed += RasterPt1(m.tris, VectorAdd(m.position, t[1]), VectorAdd(m.rotation, t[2]), m.shader)
                    else:
                        viewed += RasterPt1NoCull(m.tris, VectorAdd(m.position, t[1]), VectorAdd(m.rotation, t[2]), m.shader)
            else:
                    if t.movable:
                        # bMovable
                        for m in t.meshes:
                            if m.frame == -1:
                                # Standard Mesh
                                if m.cull:
                                    viewed += RasterPt1(m.tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)
                                else:
                                    viewed += RasterPt1NoCull(m.tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)
                            else:
                                # AniMesh
                                length = len(m.tris)
                                if m.frame >= length:
                                    m.frame -= length
                                if m.cull:
                                    viewed += RasterPt1(m.tris[m.frame], VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)
                                else:
                                    viewed += RasterPt1NoCull(m.tris[m.frame], VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)
                    else:
                        # not bMovable
                        for m in t.meshes:
                            if m.cull:
                                viewed += RasterPt1Static(m.tris, VectorAdd(m.position, t.position), m.shader)
                            else:
                                viewed += RasterPt1StaticNoCull(m.tris, VectorAdd(m.position, t.position), m.shader)

        for em in emitters:
            for p in em.particles:
                viewed += RasterPt1(em.template[0], p[1], p[2])

        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)
    

# RenderMeshList()
# Supply your own list of meshes to draw.

# Usage:
#
# for tri in z3dpy.RenderMeshList([cube]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RenderMeshList(meshList, sortKey=triSortAverage, bReverse=True):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
    else:
        viewed = []
        for m in meshList:
            viewed += RasterPt1(m.tris, m.position, m.rotation, m.shader)
        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)

# Draws things, as well as hitboxes, and any lights/rays you give it. 
# Triangles from debug objects will have an id of -1
def DebugRender(train=[], sortKey=triSortAverage, bReverse=True, clearRays=False):
    try:
        intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        global rays
        viewed = []
        for t in GatherThings():
            for m in t[0]:
                if m.frame == -1:
                    # Static Mesh
                    viewed += RasterPt1(m.tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)
                else:
                    # AniMesh
                    cap = len(m.tris)
                    if m.frame >= cap:
                        m.frame -= cap
                    viewed += RasterPt1(m.tris[m.frame].tris, VectorAdd(m.position, t.position), VectorAdd(m.rotation, t.rotation), m.shader)

            if t[3]:
                viewed += RasterPt1Static(t.hitbox.mesh.tris, t.position, SHADER_UNLIT)

        viewed.sort(key = sortKey, reverse=bReverse)
        
        for l in lights:
            match l.type:
                case 0:
                    viewed += RasterPt1Static(lightMesh.tris, l.position, SHADER_UNLIT)
                case 1:
                    viewed += RasterPt1PointAt(arrowMesh.tris, (0, 0, 0), l.position, (0, 1, 0), SHADER_UNLIT)

        for d in dots:
            viewed += RasterPt1Static(dotMesh.tris, d, SHADER_UNLIT)

        for r in rays:
            if r[0]:
                viewed += RasterPt1PointAt(arrowMesh.tris, r[1], r[2], iC[7], SHADER_UNLIT)
            else:
                viewed += RasterPt2NoPos([[r[1] + [[0, 0, 0], [0, 0]], VectorAdd(r[1], [0, 0.01, 0]) + [[0, 0, 0], [0, 0]], r[2] + [[0, 0, 0], [0, 0]], (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), -1]], SHADER_UNLIT, None)

        if train:
            for x in range(len(train)):
                for y in range(len(train[0])):
                    viewed += RasterPt1Static(dotMesh.tris, [x, train[x][y], y], SHADER_UNLIT)

        for e in emitters:
            viewed += RasterPt1Static(dotMesh.tris, e.position, SHADER_UNLIT)

        if clearRays:
            rays = []
        
        return RasterPt3(viewed)

def RasterPt1(tris, pos, rot, shader):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
    return RasterPt2NoPos(TransformTris(tris, pos, trg, up), shader)

def RasterPt1PointAt(tris, pos, target, up, shader):
    return RasterPt2NoPos(TransformTris(tris, pos, target, up), shader)

def RasterPt1NoCull(tris, pos, rot, shader):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
    return RasterPt2(TransformTris(tris, pos, trg, up), pos, shader)

def RasterPt1StaticNoCull(tris, pos, shader):
    return RasterPt2(tris, pos, shader)


def RasterPt1Static(tris, pos, shader):
    return RasterPt2([tri for tri in tris if VectorDoP(VectorMul(tri[3], (-1, 1, 1)), iC[6]) > -0.4], pos, shader)

# Lots of repeating myself but there's less computation this way.
def RasterPt2(tris, pos, shader):
    output = []
    for tri in ViewTris(TranslateTris(tris, pos)):
        tri[6] = shader(tri)
        output += TriClipAgainstPlane(tri, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output

def RasterPt2NoPos(tris, shader):
    output = []
    for t in ViewTris(tris):
        t[6] = shader(t)
        output += TriClipAgainstPlane(t, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output


def RasterPt3(tris):
    output = []
    for i in ProjectTris(tris):
        output += TriClipAgainstScreenEdges(i)
    return output

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

def TransformTris(tris, pos, trg, up=(0.0, 1.0, 0.0)):
    mW = PointAtMatrix(pos, trg, up)
    for t in tris:
        nt = TriMatrixMul(t, mW)
        nt[3] = GetNormal(nt)
        if VectorDoP(nt[3], iC[6]) < 0.4:
            nt[4] = TriAverage(nt)
            nt[4][2] += pos[2]
            nt[4][1] += pos[1]
            yield nt

def WTransformTris(tris, rot):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotZ(rot[2]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotY(rot[1]))
    for t in tris:
        nt = TriMatrixMul(t, mW)
        nt[3] = GetNormal(nt)
        nt[4] = TriAverage(nt)
        yield nt

def TransformTri(tri, rot):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotY(rot[1]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotZ(rot[2]))
    nt = TriMatrixMul(tri, mW)
    return nt[:3] + [GetNormal(nt)] + nt[4:]
        
def TranslateTris(tris, pos):
    for tri in tris:
        ntri = TriAdd(tri, pos)
        ntri[4] = VectorAdd(tri[4], pos)
        yield ntri

def TranslateTri(tri, pos):
    newTri = TriAdd(tri, pos)
    return newTri[:4] + [VectorAdd(TriAverage(newTri), pos)] + newTri[5:]

def ViewTris(tris):
    return (TriMatrixMul(tri, intMatV) for tri in tris)

def ViewTri(tri):
    return TriMatrixMul(tri, intMatV)
                    
def ProjectTris(tris):
    return (TriMul(TriAdd(ProjectTri(tri), [1, 1, 0]), [iC[3], iC[2], 1]) for tri in tris)

def ProjectTri(tri):
    return TriMul(TriAdd(ProjectTri(tri), [1, 1, 0]), [iC[3], iC[2], 1])


#==========================================================================
#  
# Drawing/Shaders
#
#==========================================================================

# CheapLighting() and ExpensiveLighting()
# Returns the colour of all lighting. 

# Usage:
#
# def MyShader(tri):
    # Multiply with the lighting with the tri's colour
#   return z3dpy.VectorMul(z3dpy.TriGetColour(tri), CheapLighting(tri))
#

# CheapLighting takes the direction towards the light source, no shadow checks or anything.
def CheapLighting(tri, lights=lights):
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    num = 0
    if not len(lights):
        return (0, 0, 0)
    for l in lights:
        match l.type:
            case 0:
                # LIGHT_POINT
                dist = DistanceBetweenVectors(tri[4], l.position)
                if dist <= l.radius:
                    lightDir = DirectionBetweenVectors(l.position, tri[4])
                    if (dot := VectorDoP(lightDir, tri[3])) < 0:
                        d = dist/l.radius
                        intensity = (1 - (d * d)) * l.strength
                        colour = VectorAdd(colour, VectorMulF(l.colour, intensity * -dot))
                        num += 1
            case 1:
                # LIGHT_SUN
                if (dot := VectorDoP(l.position, tri[3])) < 0:
                    intensity = -dot * l.strength
                    colour = VectorAdd(colour, VectorMulF(l.colour, intensity))
                    num += 1
    inverse = 1/max(num, 1)
    return VectorMax(VectorMinF(VectorMulF(colour, inverse), 1.0), worldColour)

# ExpensiveLighting uses the direction towards the light source, and tests for ray collisions to create shadows.
def ExpensiveLighting(tri, shadowcasters=GatherThings(), lights=lights):
    if shadowcasters == []:
        shadowcasters = GatherThings()
    shading = 0.0
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    pos = tri[4]
    if not len(lights):
        return (0, 0, 0)
    for l in lights:
            match l.type:
                # LIGHT_POINT
                case 0:
                    dist = DistanceBetweenVectors(pos, l.position)
                    if dist <= l.radius:
                        lightDir = DirectionBetweenVectors(l.position, pos)
                        shade = VectorDoP(lightDir, tri[3])
                        if shade < 0:
                            testRay = Ray(pos, l.position)

                            # Checking for shadows
                            for th in shadowcasters:
                                inters = RayIntersectThingComplex(testRay, th)
                                if inters[0]:
                                    # Making sure it's not this triangle, by comparing world position
                                    if not VectorEqual(inters[4], tri[4]):
                                        break
                            else:
                                shading += shade
                                d = (dist / l.radius)
                                intensity += (1 - (d * d)) * l.strength
                                colour = VectorAdd(colour, VectorMulF(l.colour, intensity))
                # LIGHT_SUN
                case 1:
                    if (shade := VectorDoP(l.rotation, tri[3])) > 0:
                        testRay = Ray(tri[4], VectorAdd(tri[4], VectorMulF(VectorNegate(l.rotation), 25)))
                        rays.append(testRay)
                        for th in shadowcasters:
                            intersection = RayIntersectThingComplex(testRay, th)
                            if intersection[0]:
                                if not VectorEqual(intersection[4], tri[4]):
                                    break
                        else:
                            shading += shade

                    


    colour = VectorDivF(colour, len(lights))
    return VectorMax(VectorMinF(VectorMulF(colour, shading), 1.0), worldColour)


# BakeLighting() and FlatLightingBaked()

# BakeLighting() saves the FlatLighting() calculation to the triangle's shade value, for cheaply referencing later.
# FlatLightingBaked() retrives a triangle's shade value.

# Usage:
'''
# At the start of the script, call BakeLighting() after defining the lights
BakeLighting()

# Then, during the draw loop...

for tri in RasterThings(things):

    PgDrawTriFLB(tri, screen, pygame)

    # or

    TkDrawTriFLB(tri, canvas)

'''

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shader variable
def BakeLighting(things, expensive=False, lights=lights, shadowcasters=-1):
    print("Baking Lighting...")
    if shadowcasters == -1:
        shadowcasters = things
    for th in things:
        for m in th.meshes:
            for t in m.tris:
                if expensive:
                    calc = ExpensiveLighting(TranslateTri(TransformTri(t, VectorAdd(m.rotation, th.rotation)), VectorAdd(m.position, th.position)), shadowcasters, lights)
                else:
                    calc = CheapLighting(TranslateTri(TransformTri(t, VectorAdd(m.rotation, th.rotation)), VectorAdd(m.position, th.position)), lights)
                t[5] = tuple(calc)
    print("Lighting Baked!")

def FillSort(n):
    return int(n[0])

# TriToLines()
# Returns a tuple of lines to draw on the screen, given a triangle.

# Usage:
#
# for tri in RasterThings(things):
#   for line in TriToLines(tri):
#
#       start = line[0]
#       sX = start[0]
#       sY = start[1]
#
#       end = line[1]
#       eX = end[0]
#       eY = end[1]
#

# Part One: From P1 to P2

def TemplateLineDraw(sx, sy, ex, ey, tri):
    return

def TriToLines(tri, draw=TemplateLineDraw):
    list = [VectorFloor(tri[0]), VectorFloor(tri[1]), VectorFloor(tri[2])]
    list.sort(key=FillSort)
    if list[2][0] != list[0][0]:
        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])

        diff = floor(list[1][0] - list[0][0])
        if diff != 0:

            diff3 = (list[1][1] - list[0][1]) / diff
            for x in range(0, diff + 1, Sign(diff)):
                draw(x + list[0][0], (diff3 * x) + list[0][1], x + list[0][0], (slope * x) + list[0][1])

        FillTriangleLinePt2(list, slope, draw)

# Part Two: From P2 to P3

def FillTriangleLinePt2(list, fSlope, draw):
    # If this side is flat, no need.
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        diff4 = list[1][0] - list[0][0]
        slope2 = (list[2][1] - list[1][1]) / diff2
        for x in range(0, int(diff2) + 1, Sign(diff2)):
            draw(x + list[1][0], (slope2 * x) + list[1][1], x + list[1][0], (fSlope * (x + diff4)) + list[0][1])

# TriToPixels()
# Returns a tuple of pixels to draw on the screen, given a triangle.

# Usage:
#
# for tri in Raster():
#   for pixel in TriToPixels(tri):
#       x = pixel[0]
#       y = pixel[1]
#

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

                # Pixel:
                # [0] is the screen x, [1] is the screen y
                for y in range(ranges[0], ranges[1] + 1):
                    draw(fX, y)

        FillTrianglePixelPt2(list, slope, diff, draw)

def FillTrianglePixelPt2(list, fSlope, diff, draw):
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
    return (Fy * uvDy + UVstY, Fy * uvDx + UVstX)

def TemplateTexelDraw(x, y, u, v):
    return

def TriToTexels(tri, draw=TemplateTexelDraw):
    list = [VectorFloor(tri[0]) + tri[0][3:], VectorFloor(tri[1]) + tri[1][3:], VectorFloor(tri[2]) + tri[2][3:]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX:
        slope = (list[2][1] + -list[0][1]) / diffX

        diff = list[1][0] + -list[0][0]

        if diff:

            diffY = list[1][1] + -list[0][1]
            diff3 = diffY / diff

            diffF = floor(diff) + 1

            for x in range(diffF):

                fX = x + floor(list[0][0])

                if 0 < fX < screenSize[0]:

                    ranges = [floor(diff3 * x + list[0][1]), floor(slope * x + list[0][1])]

                    rangD = ranges[1] - ranges[0]

                    if rangD:
                        sgn = Sign(rangD)

                        UVs = UVCalcPt1(list[0][4], list[1][4], list[2][4], x / diffF, x / diffX, True)

                        for y in range(ranges[0], ranges[1] + sgn, sgn):
                            if 0 < y < screenSize[1]:
                                # "Texel":
                                # [0] is the screen x, [1] is the screen y, [2] is u, and [3] is v
                                fUVs = UVCalcPt2((y - ranges[0]) / rangD, UVs[0], UVs[1], UVs[2], UVs[3])
                                draw(fX, y, fUVs[0], fUVs[1])
                            
        TriToTexelsPt2(list, slope, diff, diffX, draw)

def TriToTexelsPt2(list, fSlope, diff, diffX, draw):
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        if diff2:
            slope2 = (list[2][1] - list[1][1]) / diff2

            diffF = floor(diff2) + 1

            for x in range(diffF):

                fX = x + floor(list[1][0])

                if 0 < fX < screenSize[0]:
                    # Repeat the same steps except for this side now.
                    ranges = [floor(slope2 * x + list[1][1]), floor(fSlope * (x + diff) + list[0][1])]

                    rangd = ranges[1] - ranges[0]

                    if rangd:
                        sgn = Sign(rangd)

                        UVs = UVCalcPt1(list[0][4], list[1][4], list[2][4], x / diffF, (x + diff) / diffX, False)

                        for y in range(max(ranges[0], 0), min(ranges[1] + sgn, screenSize[1]), sgn):
                            fUVs = UVCalcPt2((y - ranges[0]) / rangd, UVs[0], UVs[1], UVs[2], UVs[3])  
                            draw(fX, y, fUVs[0], fUVs[1])




#==========================================================================
#  
# Projection Functions
#
#==========================================================================

def Projection(vector):
    if vector[2] != 0:
        return [(vector[0] * howX) / vector[2], (vector[1] * howY) / vector[2], 1, vector[3], vector[4]]
    return vector
        
def ProjectTri(t):
    return [Projection(t[0]), Projection(t[1]), Projection(t[2]), t[3], t[4], t[5], t[6], t[7]]




#==========================================================================
#  
# Calculating How Projection
#
#==========================================================================

# Wrote code to brute-force finding a single multiplier that could do most of
# the projection.
# I call it: How-Does-That-Even-Work Projection

# Instead of a matrix, it's now [(X * howX) / Z, (Y * howY) / Z, 1]

# It's still gotta divide by Z to get perspective, without is orthographic.

# The current settings are FOV of 90, and aspect ratio of 16:9.
# To recalculate, use FindHowVars(fFov, *aspectRatio).
# FindHowVars(90, 9/16)


howX = 0.56249968159
howY = 1.0

# Optional aspect ratio argument: put height over width as a fraction, so
# 16:9 is 9/16, 4:3 is 3/4, and so on.
# It also accepts raw resolution for unusual aspect ratios
def FindHowVars(fFov, asp=9/16):
    global howX
    global howY
    found = CalculateCam(fFov, 500, asp)
    howX = found[0]
    howY = found[1]

def SetHowVars(x, y):
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
#
# I've had success replacing the projection

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
    print("z3dpy.SetHowVars(" + str(finished[0]) + ", " + str(finished[1]) + ")")
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

# Emitter(vPos, mshTemplate, iMax, vVelocity, fLifetime, vGravity)
myEmitter = z3dpy.Emitter([1.0, 2.0, 3.0], myMesh, 150, [5.0, 0.0, 0.0], 15.0, [0.0, 9.8, 0.0])


# Internal List
#


# append to the global list
z3dpy.emitters.append(myEmitter)

while True:

    z3dpy.HandleEmitters()

    # Emitters in the global list will be drawn with Raster()
    for tri in zp.Raster():


# Your own list
#

while True:

    z3dpy.HandleEmitters([myEmitter])

    # Emitters is an argument in RasterThings()
    for tri in z3dpy.RasterThings([myThing, thatTree], [myEmitter])

'''

def HandleEmitters(emitters=emitters):
    for emitter in emitters:
        emitter.particles = [pt for pt in emitter.particles if pt[0] > delta]
        for pt in emitter.particles:
            pt[0] -= delta
            # Basic version of physics for particles
            pt[2] = VectorSub(pt[2], [airDrag * Sign(pt[2][0]), airDrag * Sign(pt[2][1]), airDrag * Sign(pt[2][2])])
            pt[2] = VectorAdd(pt[2], VectorMulF(VectorMulF(emitter.gravity, 5), delta))
            pt[1] = VectorAdd(VectorMulF(pt[2], delta), pt[1])
        if emitter.active:
            if len(emitter.particles) < emitter.max:
                if emitter.randomness > 0.0:
                    emitter.particles += (Part(emitter.position, VectorAdd(emitter.velocity, ((rand() - 0.5) * emitter.randomness, (rand() - 0.5) * emitter.randomness, (rand() - 0.5) * emitter.randomness)), emitter.lifetime),)
                else:
                    emitter.particles += (Part(emitter.position, emitter.velocity, emitter.lifetime),)




#==========================================================================
#  
# Utilities
#
#==========================================================================
                    
def RGBToHex(vColour):
    def intToHex(int):
        int = min(int, 255)
        return hex(max(int, 0))[2:].rjust(2, "0")
    return "#" + intToHex(floor(vColour[0])) + intToHex(floor(vColour[1])) + intToHex(floor(vColour[2]))

# My own list utilities

def ListInterpolate(lst, fIndex):
    floor = floor(fIndex)
    first = lst[floor]
    difference = lst[ceil(fIndex)] - first
    return difference * (fIndex - floor) + first

def ListExclude(lst, index): return lst[:index] + lst[index+1:]

# My own list flattener, as it seems NumPy is the only other option.
def ListNDFlatten(listOfLists):
    test = listOfLists
    while isinstance((test := [item for sublist in test for item in sublist])[0], list):
        pass
    return test

try:
    import z3dpyfast
except:
    def fast(): print("z3dpyfast could not be found.")
else:
    def fast():
        global DistanceBetweenVectors
        global DirectionBetweenVectors
        global ShortestPointToPlane
        global VectorUVIntersectPlane
        global RotTo
        global GetNormal
        global MatrixStuff
        global PointAtMatrix
        DistanceBetweenVectors = z3dpyfast.DistanceBetweenVectors
        DirectionBetweenVectors = z3dpyfast.DirectionBetweenVectors
        ShortestPointToPlane = z3dpyfast.ShortestPointToPlane
        VectorUVIntersectPlane = z3dpyfast.VectorUVIntersectPlane
        RotTo = z3dpyfast.RotTo
        GetNormal = z3dpyfast.GetNormal
        MatrixStuff = z3dpyfast.MatrixStuff
        PointAtMatrix = z3dpyfast.MatrixMakePointAt
        print("z3dpyfast loaded.")

## Deprecated
def Raster(sortKey=triSortAverage, bReverse=True):
    return Render(sortKey, bReverse)

def RasterThings(things, emitters=[], sortKey=triSortAverage, bReverse=True):
    return RenderThings(things, emitters, sortKey, bReverse)

def RasterMeshList(meshList, sortKey=triSortAverage, bReverse=True):
    return RenderMeshList(meshList, sortKey, bReverse)

def DebugRaster(train=[], sortKey=triSortAverage, bReverse=True, clearRays=False):
    return DebugRender(train, sortKey, bReverse, clearRays)

def PgDrawTriRGB(tri, colour, surface, pygame):
    pygame.draw.polygon(surface, colour, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriRGBF(tri, colour, surface, pygame):
    ncolour = VectorMaxF(colour, 0)
    ncolour = VectorMinF(ncolour, 1)
    pygame.draw.polygon(surface, VectorMulF(ncolour, 255), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriF(tri, f, surface, pygame):
    f = max(f, 0)
    f = min(f, 1) * 255
    pygame.draw.polygon(surface, (f, f, f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriOutl(tri, colour, surface, pygame):
    ncolour = VectorMaxF(colour, 0)
    ncolour = VectorMinF(ncolour, 255)
    pygame.draw.lines(surface, colour, True, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriS(tri, f, surface, pygame):
    f = max(f, 0)
    f = min(f, 1)
    pygame.draw.polygon(surface, VectorMulF(tri[6], f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriFL(tri, surface, pygame, lights=lights):
    pygame.draw.polygon(surface, VectorMul(tri[6], CheapLighting(tri, lights)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriFLB(tri, surface, pygame):
    pygame.draw.polygon(surface, VectorMul(tri[6], tri[5]), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def TkDrawTriRGB(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(colour))

def TkDrawTriRGBF(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMulF(colour, 255)))

def TkDrawTriF(tri, f, canvas):
    f = str(floor(max(f, 0) * 100))
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill="gray" + f)

def TkDrawTriOutl(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], outline=RGBToHex(colour))

def TkDrawTriS(tri, f, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMulF(tri[6], f)))

def TkDrawTriFL(tri, canvas, lights=lights):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorFloor(VectorMul(tri[6], CheapLighting(tri, lights)))))

def TkDrawTriFLB(tri, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMul(tri[6], tri[5])))
##