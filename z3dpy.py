# -zw
'''
Z3dPy v0.3.2

LEGEND:
- Parameters marked with * are optional
- Most parameters have a starting letter denoting type.
Capitals mean normalized.

Change Notes:

PATCH 2

- Fixed MeshAddRot(), MeshSubRot(), MeshMulRot() and MeshDivRot()

- World position on the y axis has been fixed.

C++

- z3dpyfast now also replaces MatrixStuff(), and
PointAtMatrix()

- Applied the clipping texture fix to z3dpyfast as well.


LIGHTING

- Applied a more robust fix to Tri World Position.

- Expensive lighting now compares world position to reject
self intersections, so there should be fewer lighting bugs.

- Light_Sun(vRot, FStrength, unused, *vColour) now uses
rot instead of direction.


DRAW TRI OUTLINE

- TkDrawTriOutl() used to fill, that has been fixed.

- PgDrawTriOutl() and TkDrawTriOutl() now take raw RGB,
not normalized.


RASTERING

- DebugRaster(*train, *sortKey, *reverseSort, *clearRays)
now has clearRays, which if True, will clear the rays list
before returning.


MESHES

- LoadMesh()'s per-vertex normals weren't being calculated
correctly for P1, this has been fixed.

- AniMesh functions are now just Mesh functions.
Such as:
MeshGetFrame()
MeshSetFrame()

- Removed frame functions and iNext from animesh frames,
as the same functionality can be achieved with a match/case
before incrementing.


HITS

- Added object functions for hits:

HitCheck(hit) -> bool - wether or not it hit
HitPos(hit) -> vector - location of hit
HitDistance(hit) -> float - distance of hit
HitNormal(hit) -> vector - normal of hit tri.
HitTriPos(hit) -> vector - world position of hit tri

- Hits now have world position of the hit triangle,
at index [4]


NORMALS

- After some debugging, triangle normals have been
corrected.


YET MORE STREAMLINING

- Removed deprecated TickEmitters(), use
HandleEmitters() instead.

- Removed deprecated Camera(), use Cam() instead.

- Almost every function with separated x, y,
and z is now vPos. This includes:

Thing(meshes, vPos)
Cam(vPos, *scW, *scH)
Mesh(tris, *vPos, ...)
AniMesh(tris, *vPos, ...)


PIXEL SHADERS

- UVs are set per-triangle instead of per-vertex.


MISC

- More optimizations in
TriToLines(), LoadMesh(), Raster(), CamChase(), etc.

- RGBToHex() has been fixed, meant to use rjust instead of ljust.

- DebugRaster() now visualizes emitters as dots.

- Updated the documentation inside the script. I realized
some of it is very outdated.

- Removed unused indexes from Dupes.

'''

# Time for delta-time calculations
import time

# Rand for finding projection constants
import random as rand

# Math for, well...
import math

# z3dpyfast is imported at the bottom of the script to replace functions.

print("Z3dPy v0.3.2")

#==========================================================================
#  
# Variables
#
#==========================================================================

# Delta calculations
timer = time.time()

delta = 0.016666

def GetDelta():
    global delta
    global timer
    delta = time.time() - timer
    timer = time.time()
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
# "Objects"
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

# Meshes:
# [0] is the tuple of triangles
# [1] is the position
# [2] is the rotation
# [3] is the colour
# [4] is the id
# [5] is always -1
# [6] is the user variable
# [7] is wether or not back-faces are culled
#
# Colour is copied to triangles, used when drawing.
#
# Id is copied to triangles, as a way to check
# where a tri came from.
#

def Mesh(tris, vPos=[0.0, 0.0, 0.0], vRot=[0.0, 0.0, 0.0], vColour=[255, 255, 255], iId=0, bCull=True):
    return [tris, vPos, vRot, vColour, iId, -1, 0, bCull]

# AniMeshes:
# Same as Mesh except animated:
# [0] is a list of frames
# [5] is frame number.
#
def AniMesh(frames, vPos=[0.0, 0.0, 0.0], vRot=[0.0, 0.0, 0.0], vColour=[255, 255, 255], iId=0, bCull=True):
    return [frames, vPos, vRot, vColour, iId, 0, 0, bCull]

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

def Hitbox(type = 2, id = 0, radius = 1, height = 1):
    return [type, id, radius, height, LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [radius, height, radius])]

# Physics Body:
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

def PhysicsBody():
    return [[0, 0, 0], [0, 0, 0], 0.5, 15, 0.5, [0, 0, 0], [0, 0, 0]]

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

def Thing(meshList, vPos):
    return [meshList, vPos, [0, 0, 0], [], [], True, 0, 0]

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
# For a third person camera, use CamSetTargetLoc()
# For a first person camera, use CamSetTargetDir()
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

def Cam(vPos, scW=0, scH=0):
    global screenSize
    if scW and scH:
        screenSize = (scW, scH)
    return [0, vPos, [0, 0, 0], 0.1, 1500, [0, 0, 1], [0, 1, 0]]

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
    iC = [CamGetPos(camera), CamGetRot(camera), screenSize[1] * 0.5, screenSize[0] * 0.5, CamGetNCl(camera), CamGetFCl(camera), CamGetTargetDir(camera), CamGetUpVector(camera)]
    # Storing the look at matrix, since it doesn't need to be updated as long as
    # the camera hasn't moved.
    intMatV = LookAtMatrix(CamGetPos(camera), CamGetTargetLoc(camera), CamGetUpVector(camera))

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

def Light_Point(vPos, FStrength, fRadius, vColour=(255, 255, 255)):
    return [0, vPos, FStrength, fRadius, VectorDivF(vColour, 255), 0, 0]

# Unique to Sun:
# [1] is direction

def Light_Sun(vRot, FStrength, fRadius, vColour=(255, 255, 255)):
    return [1, RotTo(vRot, (0, 0, 1)), FStrength, fRadius, VectorDivF(vColour, 255), 0, 0]

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
# Assuming imported as zp

myRay = zp.Ray(zp.CamGetPos(myCam), zp.ThingGetPos(thatTree))

# Add the ray to the global list to get drawn with DebugRaster()
zp.rays.append(myRay)

# and/or you could do a collision check
hit = zp.RayIntersectThingComplex(myRay, myCharacter)

if hit[0]:
    # Hit
    location = hit[1]
    distance = hit[2]
    normal = hit[3]
    wPosOfTri = hit[4]
    print(location, distance, normal, wPosOfTri)
else:
    # No Hit
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

z3dpy.dots.append(z3dpy.ThingGetPos(myCharacter))

# This may or may not update depending on wether it's a 
# reference,
# so I'd recommend setting the list before drawing.

z3dpy.dots = [myVector, z3dpy.ThingGetPos(myCharacter)]

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
    output = []
    for g in range(0, x):
        output.append([])
        for h in range(0, y):
            output[g].append(0.0)
    return output

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

def Emitter(position, template, maximum, velocity=[0.0, 0.0, 0.0], lifetime=15.0, vGravity=(0, 9.8, 0), randomness=0.0):
    return [(), position, template, velocity, maximum, lifetime, vGravity, False, randomness]

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
# Everything is a list, so these functions are
# human-friendly ways to set and retrieve variables
#
#==========================================================================


# UNIVERSAL
# Well, almost universal


# These work with Things, Cameras, Meshes/AniMeshes, Frames,
# Lights, Rays, Emitters, and Particles
def GetPos(any):
    return any[1]

def SetPos(any, vector):
    any[1] = vector

# These work with Things, Cameras, Meshes/AniMeshes, and
# Frames
def GetRot(any):
    return any[2]

def SetRot(any, vector):
    any[2] = vector


# Get/SetList()
# Works with Things, Meshes/AniMeshes, Frames, and Emitters
# for Things, it's a list of meshes,
# for Meshes and Frames, it's a tuple of tris,
# for AniMeshes, it's a list of frames,
# for Emitters, it's a list of currently active particles

def GetList(any):
    return any[0]

def SetList(any, lst):
    any[0] = lst


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

# Colour is automatically calculated during the raster
# process, and by default will be the colour of the
# associated mesh.
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


# MESHES


def MeshSetTris(mesh, lTris):
    mesh[0] = lTris

def MeshGetTris(mesh):
    return mesh[0]

def MeshSetPos(mesh, vPos):
    mesh[1] = vPos

def MeshGetPos(mesh):
    return mesh[1]

def MeshSetRot(mesh, vRot):
    mesh[2] = vRot

def MeshAddRot(mesh, vector):
    mesh[2][0] += vector[0]
    mesh[2][1] += vector[1]
    mesh[2][2] += vector[2]

def MeshSubRot(mesh, vector):
    mesh[2][0] -= vector[0]
    mesh[2][1] -= vector[1]
    mesh[2][2] -= vector[2]

def MeshMulRot(mesh, vector):
    mesh[2][0] *= vector[0]
    mesh[2][1] *= vector[1]
    mesh[2][2] *= vector[2]

def MeshDivRot(mesh, vector):
    mesh[2][0] /= vector[0]
    mesh[2][1] /= vector[1]
    mesh[2][2] /= vector[2]

def MeshGetRot(mesh):
    return mesh[2]

def MeshSetColour(mesh, vColour):
    mesh[3] = vColour
    if mesh[5] == -1:
        for t in mesh[0]:
            t[6] = vColour
    else:
        for frm in mesh[0]:
            for t in frm:
                t[6] = vColour

def MeshGetColour(mesh):
    return mesh[3]

def MeshSetId(mesh, iId):
    mesh[4] = iId
    for t in mesh[0]:
        t[7] = iId

def MeshGetId(mesh):
    return mesh[4]

def MeshGetCull(mesh):
    return mesh[7]

def MeshSetCull(mesh, bCull):
    mesh[7] = bCull

def MeshGetFrame(mesh):
    return mesh[5]

def MeshSetFrame(mesh, iFrame):
    mesh[5] = iFrame

def MeshIncFrame(mesh):
    mesh[5] = (mesh[5] + 1) % len(mesh[0])

def MeshDecFrame(mesh):
    mesh[5] -= 1

## Deprecated
def AniMeshGetFrame(animesh):
    return MeshGetFrame(animesh)

def AniMeshSetFrame(animesh):
    return MeshSetFrame(animesh)

def AniMeshIncFrame(animesh):
    return MeshIncFrame(animesh)

def AniMeshDecFrame(animesh):
    return AniMeshDecFrame(animesh)
##

# THINGS


def AddThing(thing, iLayer=2):
    # Setting the internal id to the length of the list, which
    # corrosponds to it's new index
    thing[6] = len(layers[iLayer])
    layers[iLayer].append(thing)

def AddThings(things, iLayer=2):
    for thing in things:
        AddThing(thing, iLayer)

def AddDupe(thing, position, rotation, iLayer=2):
    dupe = Dupe(thing[6], position, rotation)
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
    dex = thing[6]
    layers[iLayer] = layers[iLayer][:dex] + layers[iLayer][dex + 1:]


def ThingSetPos(thing, vector):
    thing[1] = vector

def ThingAddPos(thing, vector):
    thing[1][0] += vector[0]
    thing[1][1] += vector[1]
    thing[1][2] += vector[2]

def ThingSubPos(thing, vector):
    thing[1][0] -= vector[0]
    thing[1][1] -= vector[1]
    thing[1][2] -= vector[2]

def ThingSetPosX(thing, x):
    thing[1][0] = x

def ThingSetPosY(thing, y):
    thing[1][1] = y

def ThingSetPosZ(thing, z):
    thing[1][2] = z

def ThingAddPosX(thing, x):
    thing[1][0] += x

def ThingAddPosY(thing, y):
    thing[1][1] += y

def ThingAddPosZ(thing, z):
    thing[1][2] += z

def ThingGetPos(thing):
    return thing[1]

def ThingGetPosX(thing):
    return thing[1][0]

def ThingGetPosY(thing):
    return thing[1][1]

def ThingGetPosZ(thing):
    return thing[1][2]

def ThingSetRot(thing, vRot):
    thing[2] = vRot

def ThingAddRot(thing, vector):
    thing[2][0] += vector[0]
    thing[2][1] += vector[1]
    thing[2][2] += vector[2]

def ThingSubRot(thing, vector):
    thing[2][0] -= vector[0]
    thing[2][1] -= vector[1]
    thing[2][2] -= vector[2]

def ThingMulRot(thing, vector):
    thing[2][0] *= vector[0]
    thing[2][1] *= vector[1]
    thing[2][2] *= vector[2]

def ThingDivRot(thing, vector):
    thing[2][0] /= vector[0]
    thing[2][1] /= vector[1]
    thing[2][2] /= vector[2]

def ThingSetPitch(thing, fDeg):
    thing[2][0] = fDeg

def ThingSetRoll(thing, fDeg):
    thing[2][1] = fDeg

def ThingSetYaw(thing, fDeg):
    thing[2][2] = fDeg

def ThingGetRot(thing):
    return thing[2]

def ThingGetPitch(thing):
    return thing[2][0]

def ThingGetRoll(thing):
    return thing[2][2]

def ThingGetYaw(thing):
    return thing[2][1]

# ThingIncFrames will increment frame counter of each
# AniMesh in the Thing.
def ThingIncFrames(thing):
    for m in thing[0]:
        if MeshGetFrame(m) != -1:
            MeshIncFrame(m)

def ThingDecFrames(thing):
    for m in thing[0]:
        if MeshGetFrame(m) != -1:
            MeshDecFrame(m)

def ThingGetFrames(thing):
    for m in thing[0]:
        if (frame := MeshGetFrame(m)) != -1:
            return frame
        
def ThingSetColour(thing, vColour):
    for m in thing[0]:
        MeshSetColour(m, vColour)

def ThingSetupHitbox(thing, iType = 2, iId = 0, fRadius = 1.0, fHeight = 1.0):
    thing[3] = Hitbox()
    ThingSetCollision(thing, iType, iId, fRadius, fHeight)

# ThingSetCollision() will set the collision data and
# update the hitbox mesh.
# Type: 0 = Sphere, 2 = Cube
# Radius: radius of the sphere, or length/width of
# the cube
# Height: height of the cube.
# Id: Objects with the same ID will check for collisions.
# Everything is 0 by default, so if unsure, use that.

def ThingSetCollision(thing, iType, iId, fRadius, fHeight):
        thing[3][2] = fRadius
        thing[3][3] = fHeight
        thing[3][0] = iType
        thing[3][1] = iId
        match iType:
            case 0:
                thing[3][4] = LoadMesh("z3dpy/mesh/sphere.obj", [0, 0, 0], [fRadius, fRadius, fRadius])
            case 2:
                thing[3][4] = LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [fRadius, fHeight, fRadius])
        MeshSetId(thing[3][4], -1)
        MeshSetColour(thing[3][4], [255, 0, 0])

# Hitbox functions will return either an empty list or -1 if the input does not have a hitbox

def ThingGetHitboxMesh(thing):
    if thing[3] != []:
        return thing[3][4]
    return []

def ThingGetHitboxHeight(thing):
    if thing[3] != []:
        return thing[3][3]
    return 0

def ThingSetHitboxHeight(thing, fHeight):
    thing[3][3] = fHeight

def ThingGetHitboxRadius(thing):
    if thing[3] != []:
        return thing[3][2]
    return 0

def ThingSetHitboxRadius(thing, fRadius):
    thing[3][2] = fRadius

def ThingGetHitboxId(thing):
    if thing[3] != []:
        return thing[3][1]
    return -1

def ThingSetHitboxId(thing, iId):
    thing[3][1] = iId

def ThingGetHitboxType(thing):
    if thing[3] != []:
        return thing[3][0]
    return -1

def ThingGetMovable(thing):
    return thing[5]

def ThingSetMovable(thing, bMovable):
    thing[5] = bMovable

def ThingGetUserVar(thing):
    return thing[7]

def ThingSetUserVar(thing, any):
    thing[7] = any

def ThingSetupPhysics(thing):
    thing[4] = PhysicsBody()

def ThingGetPhysics(thing):
    return thing[4]

def ThingSetVelocity(thing, vVelocity):
    thing[4][0] = vVelocity

def ThingSetVelocityX(thing, x):
    thing[4][0][0] = x

def ThingSetVelocityY(thing, y):
    thing[4][0][1] = y

def ThingSetVelocityZ(thing, z):
    thing[4][0][2] = z

def ThingGetVelocity(thing):
    return thing[4][0]

def ThingGetVelocityX(thing):
    return thing[4][0][0]

def ThingGetVelocityY(thing):
    return thing[4][0][1]

def ThingGetVelocityZ(thing):
    return thing[4][0][2]

def ThingAddVelocity(thing, vector):
    thing[4][0][0] += vector[0]
    thing[4][0][1] += vector[1]
    thing[4][0][2] += vector[2]

def ThingSubVelocity(thing, vector):
    thing[4][0][0] -= vector[0]
    thing[4][0][1] -= vector[1]
    thing[4][0][2] -= vector[2]

def ThingSetAcceleration(thing, vector):
    thing[4][1] = vector

def ThingGetAcceleration(thing):
    return thing[4][1]

def ThingSetMass(thing, mass):
    thing[4][2] = mass

def ThingGetMass(thing):
    return thing[4][2]

def ThingSetFriction(thing, frc):
    thing[4][3] = frc

def ThingGetFriction(thing):
    return thing[4][3]

def ThingSetBounciness(thing, bnc):
    thing[4][4] = bnc

def ThingGetBounciness(thing):
    return thing[4][4]

def ThingSetRotVelocity(thing, vector):
    thing[4][5] = vector

def ThingAddRotVelocity(thing, vector):
    thing[4][5][0] += vector[0]
    thing[4][5][1] += vector[1]
    thing[4][5][2] += vector[2]

def ThingGetRotVelocity(thing):
    return thing[4][5]

def ThingSetRotAccel(thing, vector):
    thing[4][6] = vector

def ThingAddRotAccel(thing, vector):
    thing[4][6][0] += vector[0]
    thing[4][6][1] += vector[1]
    thing[4][6][2] += vector[2]

def ThingGetRotAccel(thing):
    return thing[4][6]

# ThingStop resets velocity, acceleration, rot velocity, and rot acceleration to 0. 
def ThingStop(thing):
    thing[4][1] = [0, 0, 0]
    thing[4][0] = [0, 0, 0]
    thing[4][5] = [0, 0, 0]
    thing[4][6] = [0, 0, 0]


# CAMERAS


def CamSetPosX(cam, x):
    cam[1][0] = x

def CamSetPosY(cam, y):
    cam[1][1] = y

def CamSetPosZ(cam, z):
    cam[1][2] = z

def CamSetPos(cam, vector):
    cam[1] = vector

def CamAddPos(cam, vector):
    cam[1][0] += vector[0]
    cam[1][1] += vector[1]
    cam[1][2] += vector[2]

def CamSubPos(cam, vector):
    cam[1][0] -= vector[0]
    cam[1][1] -= vector[1]
    cam[1][2] -= vector[2]

def CamMulPos(cam, vector):
    cam[1][0] *= vector[0]
    cam[1][1] *= vector[1]
    cam[1][2] *= vector[2]

def CamDivPos(cam, vector):
    cam[1][0] /= vector[0]
    cam[1][1] /= vector[1]
    cam[1][2] /= vector[2]

def CamGetPos(cam):
    return cam[1]

def CamGetPosX(cam):
    return cam[1][0]

def CamGetPosY(cam):
    return cam[1][1]

def CamGetPosZ(cam):
    return cam[1][2]

def CamGetPitch(cam):
    return cam[2][0]

def CamGetRoll(cam):
    return cam[2][2]

def CamGetYaw(cam):
    return cam[2][1]

def CamSetPitch(cam, deg):
    cam[2][0] = deg

def CamSetRoll(cam, deg):
    cam[2][2] = deg

def CamSetYaw(cam, deg):
    cam[2][1] = deg

def CamSetRot(cam, vector):
    cam[2] = vector

def CamAddRot(cam, v):
    cam[2] = VectorAdd(cam[2], v)

def CamSubRot(cam, v):
    cam[2] = VectorSub(cam[2], v)

def CamMulRot(cam, v):
    cam[2] = VectorMul(cam[2], v)

def CamDivRot(cam, v):
    cam[2] = [cam[2][0] / v[0], cam[2][1] / v[1], cam[2][2] / v[2]]

def CamDivRotF(cam, v):
    cam[2] = VectorDivF(cam[2], v)

def CamGetRot(cam):
    return cam[2]

def CamSetNCl(cam, nc):
    cam[3] = nc

def CamGetNCl(cam):
    return cam[3]

def CamSetFCl(cam, fc):
    cam[4] = fc

def CamGetFCl(cam):
    return cam[4]

def CamSetTargetLoc(cam, vector):
    cam[5] = vector

def CamGetTargetLoc(cam):
    return cam[5]

def CamSetTargetDir(cam, vector):
    cam[5] = VectorAdd(cam[1], VectorNormalize(vector))

def CamGetTargetDir(cam):
    return VectorNormalize(VectorSub(cam[5], cam[1]))


# SetTargetFP: Takes the camera rotation and figures out the
# target vector
def CamSetTargetFP(cam):
    dir = RotTo(CamGetRot(cam), [0, 0, 1])
    CamSetTargetDir(cam, dir)


def CamSetUpVector(cam, vector):
    cam[6] = vector

def CamGetUpVector(cam):
    return cam[6]

def CamGetRightVector(cam):
    return VectorCrP(CamGetTargetDir(cam), CamGetUpVector(cam))

def CamChase(cam, location, speed=0.25):
    dspeed = speed * delta
    line = (cam[1][0] - location[0], cam[1][1] - location[1], cam[1][2] - location[2])
    if VectorGetLength(line) < 0.05:
        CamSetPos(cam, location)
        return True
    CamSubPos(cam, VectorMulF(line, dspeed))
    return False

def CamGetUserVar(cam):
    return cam[0]

def CamSetUserVar(cam, any):
    cam[0] = any


# LIGHTS


def LightGetType(light):
    return light[0]

def LightGetPos(light):
    return light[1]

def LightSetPos(light, vector):
    light[1] = vector

def LightSetPosX(light, x):
    light[1][0] = x

def LightSetPosY(light, y):
    light[1][1] = y

def LightSetPosZ(light, z):
    light[1][2] = z

def LightAddPos(light, vector):
    light[1][0] += vector[0]
    light[1][1] += vector[1]
    light[1][2] += vector[2]

def LightGetStrength(light):
    return light[2]

def LightSetStrength(light, FStrength):
    light[2] = FStrength

def LightGetRadius(light):
    return light[3]

def LightSetRadius(light, fRadius):
    light[3] = fRadius

def LightGetColour(light):
    return light[4]

def LightSetColour(light, vColour):
    light[4] = VectorDivF(vColour, 255)

def LightSetUserVar(light, any):
    light[5] = any

def LightGetUserVar(light):
    return light[5]


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


# EMITTERS


def EmitterGetPos(emitter):
    return emitter[1]

def EmitterSetPos(emitter, vector):
    emitter[1] = vector

def EmitterGetTemplate(emitter):
    return emitter[2]

def EmitterSetTemplate(emitter, mesh):
    emitter[2] = mesh

def EmitterGetVelocity(emitter):
    return emitter[3]

def EmitterSetVelocity(emitter, vector):
    emitter[3] = vector

def EmitterGetMax(emitter):
    return emitter[4]

def EmitterSetMax(emitter, iMax):
    emitter[4] = iMax

def EmitterSetLifetime(emitter, fLifetime):
    emitter[5] = fLifetime

def EmitterGetLifetime(emitter):
    return emitter[5]

def EmitterGetActive(emitter):
    return emitter[7]

def EmitterSetActive(emitter, bActive):
    emitter[7] = bActive

def EmitterGetGravity(emitter):
    return emitter[6]

def EmitterSetGravity(emitter, vector):
    emitter[6] = vector


# HITS


def HitCheck(hit):
    return hit[0]

def HitDistance(hit):
    return hit[2]

def HitPos(hit):
    return hit[1]

def HitNormal(hit):
    return hit[3]

def HitTriPos(hit):
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
    return [math.floor(v[0]), math.floor(v[1]), math.floor(v[2])]
    
# Vector Cross Product gives you the direction of the 3rd dimension, given 2 Vectors. If you give it an X and a Y direction, it will give you the Z direction.
def VectorCrP(v1, v2):
    return [(v1[1] * v2[2]) - (v1[2] * v2[1]), (v1[2] * v2[0]) - (v1[0] * v2[2]), (v1[0] * v2[1]) - (v1[1] * v2[0])]

def VectorGetLength(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

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
    return math.sqrt(output)

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
    return Vec3MatrixMulOneLine(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return Vec3MatrixMulOneLine(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return Vec3MatrixMulOneLine(vec, MatrixMakeRotZ(deg))

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


#==========================================================================
#  
# Triangle Functions
#
#==========================================================================


def TriAdd(t, v):
    return [VectorUVAdd(t[0], v), VectorUVAdd(t[1], v), VectorUVAdd(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriSub(t, v):
    return [VectorUVSub(t[0], v), VectorUVSub(t[1], v), VectorUVSub(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriMul(t, v):
    return [VectorUVMul(t[0], v), VectorUVMul(t[1], v), VectorUVMul(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriMulF(t, f):
    return [VectorUVMulF(t[0], f), VectorUVMulF(t[1], f), VectorUVMulF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

def TriDivF(t, f):
    return [VectorUVDivF(t[0], f), VectorUVDivF(t[1], f), VectorUVDivF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

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

def GetNormal(tri):
    return VectorNormalize(VectorMulF(VectorCrP(VectorSub(tri[1], tri[0]), VectorSub(tri[2], tri[0])), 1))

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
    for t in TriClipAgainstPlane(tri, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        for r in TriClipAgainstPlane(t, (0.0, screenSize[1] - 1.0, 0.0), (0.0, -1.0, 0.0)):
            for i in TriClipAgainstPlane(r, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)):
                for s in TriClipAgainstPlane(i, (screenSize[0] - 1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)):
                    yield s

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
            while filename.count("/") > 1:
                filename = filename[filename.index("/") + 1:]
            if (name := filename[filename.index("/") + 1:]) == "error.obj":
                raise Exception("Can't load placeholder mesh. (Is the z3dpy folder missing?)")
            else:
                print(name, "was not found, replacing...")
                return LoadMesh("z3dpy/mesh/error.obj", vPos, VScale)
    verts = []
    uvs = []
    output = []
    matoutputs = []
    colours = [(255, 255, 255)]
    triangles = []
    mattriangles = []
    mat = -1
    storedUVs = []
    currentMat = ""

    while (currentLine := file.readline()):
        match currentLine[0]:
            case 'v':
                if currentLine[1] == 't':
                    currentLine = currentLine[3:].split(' ')
                    uvs.append([float(currentLine[0]), float(currentLine[1])])
                else:
                    currentLine = currentLine[2:].split(' ')
                    verts.append([float(currentLine[0]) * VScale[0], float(currentLine[1]) * VScale[1], float(currentLine[2]) * VScale[2], [0, 0, 0], [0, 0], 0])
            case 'f':
                currentLine = currentLine[2:]
                if '/' in currentLine:
                    # Face includes UVs
                    newLine = ""
                    storedUVs.append([])
                    currentLine = currentLine.split(' ')
                    for cl in currentLine:
                        cl = cl.split('/')
                        storedUVs[-1].append(uvs[int(cl[1]) - 1])
                        newLine += cl[0]
                    currentLine = newLine
                else:
                    currentLine = currentLine.split(' ')

                if len(currentLine) < 4:
                    p1 = int(currentLine[0]) - 1
                    p2 = int(currentLine[1])- 1
                    p3 = int(currentLine[2]) - 1
                    qTri = [verts[p1], verts[p2], verts[p3]]
                    
                    # Adding the normals, to be averaged
                    normal = GetNormal(qTri)
                    verts[p1][3] = VectorAdd(verts[p1][3], normal)
                    verts[p2][3] = VectorAdd(verts[p2][3], normal)
                    verts[p3][3] = VectorAdd(verts[p3][3], normal)

                    # Counting triangles per vertex, for averaging
                    verts[p1][5] += 1
                    verts[p2][5] += 1
                    verts[p3][5] += 1
                    if mat != -1:
                        mattriangles[mat].append([p1, p2, p3])
                    else:
                        triangles.append([p1, p2, p3])
                else:
                    # Triangulating n-gon
                    # Starts with the first 3 points, and sweeps through, connecting triangles.
                    points = [0, 1]
                    for n in range(2, len(currentLine)):
                        points.append(n)
                        v1 = verts[int(currentLine[points[0]]) - 1]
                        v2 = verts[int(currentLine[points[1]]) - 1]
                        v3 = verts[int(currentLine[points[2]]) - 1]
                        qTri = [v1, v2, v3]
                        normal = GetNormal(qTri)
                        v1[3] = VectorAdd(v1[3], normal)
                        v2[3] = VectorAdd(v2[3], normal)
                        v3[3] = VectorAdd(v3[3], normal)
                        v1[5] += 1
                        v2[5] += 1
                        v3[5] += 1
                        if mat != -1:
                            mattriangles[mat].append([int(currentLine[points[0]]) - 1, int(currentLine[points[1]]) - 1, int(currentLine[points[2]]) - 1])
                        else:
                            triangles.append([int(currentLine[points[0]]) - 1, int(currentLine[points[1]]) - 1, int(currentLine[points[2]]) - 1])
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
                mattriangles.append([])
                mat += 1

    # Averaging normals
    for v in verts:
        # ?
        if v[5] != 0:
            v[3] = VectorDivF(v[3], v[5])
        v.pop()

    file.close()
    if mat == -1:
        for tr in range(len(triangles)):
            output.append(Tri(verts[triangles[tr][0]], verts[triangles[tr][1]], verts[triangles[tr][2]]))
            if tr < len(storedUVs):
                output[-1][0][4] = storedUVs[tr][0]
                output[-1][1][4] = storedUVs[tr][1]
                output[-1][2][4] = storedUVs[tr][2]

        return Mesh(tuple(output), vPos)
    else:
        for trL in mattriangles:
            index = len(matoutputs)
            matoutputs.append([])
            for tr in range(len(trL)):
                nt = Tri(verts[trL[tr][0]], verts[trL[tr][1]], verts[trL[tr][2]])
                matoutputs[index].append(nt)
                if tr < len(storedUVs):
                    matoutputs[-1][0][4] = storedUVs[tr][0]
                    matoutputs[-1][1][4] = storedUVs[tr][1]
                    matoutputs[-1][2][4] = storedUVs[tr][2]

        meshes = [Mesh(tuple(trS), vPos) for trS in matoutputs]
        colours = colours[1:]
        colours.reverse()

        for m in range(len(meshes)):
            MeshSetColour(meshes[m], colours[m])
        return meshes

def LoadAniMesh(filename, vPos=(0.0, 0.0, 0.0), VScale=(1.0, 1.0, 1.0)):
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
                print("Could not find any frames. Is the obj exported as animation?")
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
            
    newMsh = AniMesh([], vPos)
    for f in range(st, nd):
        newMsh[0].append(LoadMesh(filename[:-4] + str(f) + ".obj", vPos, VScale)[0])

    return newMsh

try:
    lightMesh = LoadMesh("z3dpy/mesh/light.obj")
    MeshSetId(lightMesh, -1)
    MeshSetColour(lightMesh, (255, 0, 0))

    dotMesh = LoadMesh("z3dpy/mesh/dot.obj")
    MeshSetId(dotMesh, -1)
    MeshSetColour(dotMesh, (255, 0, 0))

    arrowMesh = LoadMesh("z3dpy/mesh/axisZ.obj")
    MeshSetId(arrowMesh, -1)
    MeshSetColour(arrowMesh, (255, 0, 0))
except:
    print("Failed to load debug meshes. (is the z3dpy folder missing?)")

def MeshUniqPoints(mesh):
    buffer = ()
    for tri in MeshGetTris(mesh):
        for point in tri[:3]:
            if point not in buffer:
                buffer += (point,)
                yield point


#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def MatrixMakeRotX(deg):
    rad = deg * 0.0174
    return ((1, 0, 0, 0), (0, math.cos(rad), math.sin(rad), 0), (0, -math.sin(rad), math.cos(rad), 0), (0, 0, 0, 1))

def MatrixMakeRotY(deg):
    rad = deg * 0.0174
    return ((math.cos(rad), 0, math.sin(rad), 0), (0, 1, 0, 0), (-math.sin(rad), 0, math.cos(rad), 0), (0, 0, 0, 1))

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174
    return ((math.cos(rad), math.sin(rad), 0, 0), (-math.sin(rad), math.cos(rad), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

def TriMatrixMul(t, m):
    return [VecMatrixMul(t[0], m), VecMatrixMul(t[1], m), VecMatrixMul(t[2], m), t[3], t[4], t[5], t[6], t[7]]

def VecMatrixMul(v, m):
    output = Vec3MatrixMulOneLine(v, m)
    return output + [v[3], v[4]]

def Vec3MatrixMulOneLine(v, m):
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
    f = math.tan(f)
    return [[a * f, 0, 0, 0], [0, f, 0, 0], [0, 0, iC[5] / (iC[5] - iC[4]), 1], [0, 0, (-iC[5] * iC[4]) / (iC[5] - iC[4]), 0]]


#==========================================================================
#  
# Ray Functions
#
#==========================================================================


def RayIntersectTri(ray, tri):
    # Using the Moller Trumbore algorithm
    # Credit to whoever decided to include code on the
    # wikipedia page.
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
        
        if ds > 0.0 and ds < 1.0:
        
            q = VectorCrP(o, e1)
            v = VectorDoP(rayDr, q) * f

            if v > 0.0 and ds + v < 1.0:

                l = VectorDoP(e2, q) * f
                if l >= 0.0 and l < RayGetLength(ray):
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
    for t in TranslateTris(TransformTris(mesh[0], mesh[2]), mesh[1]):
        hit = RayIntersectTri(ray, t)
        if hit[0]:
            return hit
    return (False,)

# Does a ray intersection test with the hitbox
def RayIntersectThingSimple(ray, thing):
    hit = RayIntersectMesh(ray, thing[4][4][0])
    if hit[0]:
        return hit
    return (False,)

# Does a ray intersection test with each triangle
def RayIntersectThingComplex(ray, thing):
    for m in thing[0]:
        if thing[6] == -2:
            trg = thing[2]
        else:
            fullRot = VectorAdd(m[2], thing[2])
            trg = RotTo(fullRot, (0.0, 0.0, 1.0))
            up = RotTo(fullRot, (0.0, 1.0, 0.0))
        for t in TransformTris(m[0], VectorAdd(m[1], thing[1]), trg, up):
            inrts = RayIntersectTri(ray, t)
            if inrts[0]:
                return inrts
    return (False,)

def TriToRays(tri):
    return [Ray(tri[0], tri[1]), Ray(tri[1], tri[2]), Ray(tri[2], tri[0])]

# Honestly, I have no idea how this is will perform, but
# Most Complex Collision Method:
# Tests against collisions between every tri of every mesh, leading to hopefully accurate collisions.
def ThingIntersectThingComplex(thing1, thing2):
    for m in thing1[0]:
        fullRot = VectorAdd(m[2], thing1[2])
        trg = RotTo(fullRot, (0.0, 0.0, 1.0))
        up = RotTo(fullRot, (0.0, 1.0, 0.0))
        for t in TransformTris(m[0], VectorAdd(m[1], thing1[1]), trg, up):
            for ray in TriToRays(t):
                RayIntersectThingComplex(ray, thing2)


#==========================================================================
#  
# Trains
#
#==========================================================================

def BakeTrain(train, passes=1, strength=1.0, amplitude=1.0):
    scX = len(train)
    scY = len(train[0])
    print("Baking Train...")
    # Blurring to smooth
    for p in range(passes):
        for x in range(scX):
            for y in range(scY):
                mx = min(x + 1, scX - 1)
                mn = max(x - 1, 1)
                my = min(y + 1, scY - 1)
                ny = max(y - 1, 1)

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
    if fX > 0.0 and fY > 0.0:
        if fX < len(train) - 1 and fY < len(train[0]) - 1:
            first = ListInterpolate(train[math.floor(fX)], fY)
            second = ListInterpolate(train[math.ceil(fX)], fY)
            difference = fX - math.floor(fX)
            return (second - first) * difference + first
    return 0




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
#   ThingSetupHitbox(myCharacter)
#   ThingSetupHitbox(thatTree)
#   ThingSetupHitbox(david)
#
#   for collision in GatherCollisions([myCharacter, thatTree, david]):
#       thing1 = collision[0]
#       thing2 = collision[1]
#

def GatherCollisions(thingList):
    results = []
    for me in range(len(thingList)):
        if thingList[me][3] != []:
            for thm in range(len(thingList)):

                if thm != me:
                    if thingList[thm][3] != []:
                        if ThingGetHitboxId(thingList[thm]) == ThingGetHitboxId(thingList[me]):
                            if DistanceBetweenVectors(thingList[thm][1], thingList[me][1]) < ThingGetHitboxRadius(thingList[thm]) + ThingGetHitboxRadius(thingList[me]):
                                if [thingList[thm], thingList[me]] not in results:

                                    myPos = ThingGetPos(thingList[me])
                                    thPos = ThingGetPos(thingList[thm])
                                    match ThingGetHitboxType(thingList[me]):
                                        case 0:
                                            # Sphere
                                            # If the distance is within range, it's a hit.
                                            distance = DistanceBetweenVectors(myPos, thPos)
                                            if distance < ThingGetHitboxRadius(thingList[thm]):
                                                results.append([thingList[me], thingList[thm]])
                                        case 2:
                                            # Cube
                                            # Just a bunch of range checks
                                            rad = ThingGetHitboxRadius(thingList[me]) + ThingGetHitboxRadius(thingList[thm])
                                            hgt = ThingGetHitboxHeight(thingList[me]) + ThingGetHitboxHeight(thingList[thm])
                                            if abs(myPos[0] - thPos[0]) <= rad:
                                                if abs(myPos[1] - thPos[1]) <= hgt:
                                                    if abs(myPos[2] - thPos[2]) <= rad:
                                                        results.append([thingList[me], thingList[thm]])
    return results

# BasicHandleCollisions()
# Takes 2 things: the other, and the pivot. The other will get manually placed out of the pivot's hitbox.

# Usage:
#
#   ThingSetupHitbox(myCharacter)
#   ThingSetupHitbox(thatTree)
#   ThingSetupHitbox(david)
#
#   for collision in GatherCollisions([myCharacter, thatTree, david]):
#       BasicHandleCollisions(collision)
#

def BasicHandleCollisions(oth, pivot):
    
    match oth[3][0]:
        case 0:
            # Sphere Collisions
            # Simple offset the direction away from pivot.
            oth[1] = VectorMulF(DirectionBetweenVectors(oth[1], pivot[1]), oth[3][2] + pivot[3][2])
        case 2:
            # Cube Collisions

            if oth[1][0] + oth[3][2] < (pivot[1][0] - pivot[3][2]) + 0.5:
                # +X Wall Collision
                oth[1][0] = pivot[1][0] - pivot[3][2] - oth[3][2]
                return
            
            if oth[1][0] - oth[3][2] > (pivot[1][0] + pivot[3][2]) - 0.5:
                # -X Wall Collision
                oth[1][0] = pivot[1][0] + pivot[3][2] + oth[3][2]
                return
            
            if oth[1][2] + oth[3][2] < (pivot[1][2] - pivot[3][2]) + 0.5:
                # +Z Wall Collision
                oth[1][2] = pivot[1][2] - pivot[3][2] - oth[3][2]    
                return
            
            if oth[1][2] - oth[3][2] > (pivot[1][2] + pivot[3][2]) - 0.5:
                # -Z Wall Collision
                oth[1][2] = pivot[1][2] + pivot[3][2] + oth[3][2]
                return

            if oth[1][1] > pivot[1][1]:
                # Ceiling Collision
                oth[1][1] = pivot[1][1] + pivot[3][3] + oth[3][3]
                if oth[4] != []:
                    # Set vertical velocity to 0
                    oth[4][0][1] = 0
                return

            # Floor Collision
            oth[1][1] = pivot[1][1] - pivot[3][3] - oth[3][3]
            if oth[4] != []:
                GroundBounce(oth)


# HandlePhysics()
# Sets the position of each thing based on it's physics calculations.

# Usage:
#
#   ThingSetupPhysics(myCharacter)
#
#   while True:
#       HandlePhysics([myCharacter])
#

def HandlePhysics(thing, floorHeight=0):
    if ThingGetMovable(thing) and ThingGetPhysics(thing) != []:
        ThingAddVelocity(thing, ThingGetAcceleration(thing))
        # Drag
        ThingSetVelocity(thing, VectorSub(ThingGetVelocity(thing), [airDrag * sign(ThingGetVelocityX(thing)), airDrag * sign(ThingGetVelocityY(thing)), airDrag * sign(ThingGetVelocityZ(thing))]))
        ThingSetRotVelocity(thing, VectorSub(ThingGetRotVelocity(thing), [airDrag * sign(ThingGetRotVelocity(thing)[0]), airDrag * sign(ThingGetRotVelocity(thing)[1]), airDrag * sign(ThingGetRotVelocity(thing)[2])]))
        
        # Gravity
        ThingAddVelocity(thing, VectorMulF(VectorMulF(gravity, 5), delta))

        # Applying Velocities
        ThingAddPos(thing, VectorMulF(ThingGetVelocity(thing), delta))
        ThingAddRot(thing, VectorMulF(ThingGetRotVelocity(thing), delta))
        
        if ThingGetPosY(thing) >= floorHeight - (ThingGetHitboxHeight(thing) * 0.5):
            ThingSetPosY(thing, floorHeight - (ThingGetHitboxHeight(thing) * 0.5))
            if ThingGetVelocityY(thing) > 6:
                GroundBounce(thing)
            else:
                ThingSetVelocityY(thing, 0)

def HandlePhysicsFloor(things, fFloorHeight=0):
    for t in things:
        HandlePhysics(t, fFloorHeight)

def HandlePhysicsTrain(things, train):
    for t in things:
        if ThingGetPosX(t) > 0.0 and ThingGetPosX(t) < len(train) - 1:
            if ThingGetPosZ(t) > 0.0 and ThingGetPosZ(t) < len(train[0]) - 1:
                h4 = TrainInterpolate(train, ThingGetPosX(t), ThingGetPosZ(t))
                HandlePhysics(t, h4)
                continue
        HandlePhysics(t, 0.0)

def PhysicsBounce(thing):
    d = VectorPureDirection(ThingGetVelocity(thing))
    ThingSetVelocity(thing, VectorMul(ThingGetVelocity(thing), VectorMulF(d, -ThingGetBounciness(thing))))

def GroundBounce(thing):
    newVel = ThingGetVelocityY(thing) * -ThingGetBounciness(thing)
    if abs(newVel) < 0.001:
        ThingSetVelocityY(thing, 0)
        return
    ThingSetVelocityY(thing, newVel)

# PhysicsCollisions()
# Does GatherCollisions() and BasicHandleCollisions() automatically, with some
# velocity manipulation when a physics body is involved.
# Will only push things that have physics bodies, so static things can be put in as well, as long as they have a hitbox.

# Usage:
#
#   ThingSetupPhysics(myCharacter)
#   ThingSetupHitbox(myCharacter)
#
#   ThingSetupPhysics(joe)
#   ThingSetupHitbox(joe)
#
#   ThingSetupHitbox(thatTree)
#   ThingSetupHitbox(thatOtherTree)
#
#   while True:
#       HandlePhysics([myCharacter, joe])
#
#       PhysicsCollisions([myCharacter, thatTree, thatOtherTree, joe])
#

def PhysicsCollisions(thingList):
    for cols in GatherCollisions(thingList):
        if cols[0][4] != []:
            if cols[1][4] != []:
                # Start with a BasicHandleCollisions(), the pivot is the Thing with higher velocity
                if VectorCompare(cols[0][4][0], cols[1][4][0]):
                    BasicHandleCollisions(cols[0], cols[1])
                else:
                    BasicHandleCollisions(cols[1], cols[0])

                # If the velocities aren't strong enough, skip the physics part.
                if max(cols[0][4][0]) >= 0.1 and max(cols[1][4][0]) >= 0.1:
                    myforce = VectorMulF(cols[0][4][0], cols[0][4][2])
                    thforce = VectorMulF(cols[1][4][0], cols[1][4][2])
                    # Add together the force, and apply it to both Things, so if one object is flung at another, the force should carry.
                    toforce = VectorAdd(myforce, thforce)
                    cols[0][4][0] = toforce
                    cols[1][4][0] = toforce
            else:
                BasicHandleCollisions(cols[0], cols[1])
        else:
            BasicHandleCollisions(cols[1], cols[0])

def sign(f):
    return 0 if f == 0 else 1 if f > 0 else -1

#==========================================================================
#  
# Rastering
#
#==========================================================================

# Raster functions return new triangles. Will not overwrite the old triangles.

# Raster()
# Uses the internal lists

# Usage:
#
# def OnDeath():
#   z3dpy.RemoveThing(myCharacter)
#
# z3dpy.AddThing(myCharacter)
#
# for tri in z3dpy.Raster():
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#

def Raster(fnSortKey=triSortAverage, bReverse=True):
    finished = []
    llen = len(layers)
    llayer = min(llen - 1, 2)
    for l in range(llen):
        finished += RasterThings(layers[l], emitters if l == llayer else [], fnSortKey, bReverse)
    return finished

# RasterThings()
# Specify your own list of things to raster.

# Usage:
#
# for tri in z3dpy.RasterThings([myCharacter]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RasterThings(things, emitters=[], sortKey=triSortAverage, bReverse=True):
    try:
        intMatV
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        viewed = []
        for t in things:
            if t[3] == -1:
                # Dupe
                for m in things[t[0]][0]:
                    if m[7]:
                        viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                    else:
                        viewed += RasterPt1NoCull(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
            else:
                    if t[5]:
                        # bMovable
                        for m in t[0]:
                            if m[5] == -1:
                                # Standard Mesh
                                if m[7]:
                                    viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                                else:
                                    viewed += RasterPt1NoCull(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                            else:
                                # AniMesh
                                if m[7]:
                                    viewed += RasterPt1(m[0][m[5]], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                                else:
                                    viewed += RasterPt1NoCull(m[0][m[5]], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                    else:
                        # not bMovable
                        for m in t[0]:
                            if m[7]:
                                viewed += RasterPt1Static(m[0], VectorAdd(m[1], t[1]))
                            else:
                                viewed += RasterPt1StaticNoCull(m[0], VectorAdd(m[1], t[1]))

        for em in emitters:
            for p in em[0]:
                viewed += RasterPt1(EmitterGetTemplate(em)[0], p[1], p[2])

        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)
    

# RasterMeshList()
# Supply your own list of meshes to draw.

# Usage:
#
# for tri in z3dpy.RasterMeshList([cube]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RasterMeshList(meshList, sortKey=triSortAverage, bReverse=True):
    try:
        intMatV
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        viewed = []
        for m in meshList:
            viewed += RasterPt1(m[0], m[1], m[2])
        viewed.sort(key=sortKey, reverse=bReverse)
        return RasterPt3(viewed)



# Draws things, as well as hitboxes, and any lights/rays you give it. 
# Triangles from debug objects will have an id of -1
def DebugRaster(train=[], sortKey=triSortAverage, bReverse=True, clearRays=False):
    try:
        intMatV
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        global rays
        finished = []
        viewed = []
        for t in GatherThings():
            for m in t[0]:
                if MeshGetFrame(m) == -1:
                    # Static Mesh
                    viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                else:
                    # AniMesh
                    viewed += RasterPt1(m[0][MeshGetFrame(m)][0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))

            if t[3] != []:
                viewed += RasterPt1Static(t[3][4][0], t[1])

        viewed.sort(key = sortKey, reverse=bReverse)
        
        for l in lights:
            match l[0]:
                case 0:
                    viewed += RasterPt1Static(lightMesh[0], l[1])
                case 1:
                    viewed += RasterPt1PointAt(arrowMesh[0], (0, 0, 0), l[1], (0, 1, 0))

        for d in dots:
            viewed += RasterPt1Static(dotMesh[0], d)

        for r in rays:
            if r[0]:
                viewed += RasterPt1PointAt(arrowMesh[0], r[1], r[2], iC[7])
            else:
                viewed += RasterPt2NoPos([[r[1] + [[0, 0, 0], [0, 0]], VectorAdd(r[1], [0, 0.01, 0]) + [[0, 0, 0], [0, 0]], r[2] + [[0, 0, 0], [0, 0]], (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), -1]])

        if clearRays:
            rays = []

        if train != []:
            for x in range(len(train)):
                for y in range(len(train[0])):
                    viewed += RasterPt1Static(dotMesh[0], [x, train[x][y], y])

        for e in emitters:
            viewed += RasterPt1Static(dotMesh[0], e[1])
        
        finished += RasterPt3(viewed)
        return finished

def RasterPt1(tris, pos, rot):
    trg = VectorAdd(pos, RotTo(rot, [0.0, 0.0, 1.0]))
    up = RotTo(rot, [0.0, 1.0, 0.0])
    return RasterPt2NoPos(TransformTris(tris, pos, trg, up))

def RasterPt1PointAt(tris, pos, target, up):
    return RasterPt2NoPos(TransformTris(tris, pos, target, up))

def RasterPt1NoCull(tris, pos, rot):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
    return RasterPt2(TransformTris(tris, pos, trg, up), pos)

def RasterPt1StaticNoCull(tris, pos):
    return RasterPt2(tris, pos)


def RasterPt1Static(tris, pos):
    prepared = [tri for tri in tris if VectorDoP(VectorMul(tri[3], (-1, 1, 1)), iC[6]) > -0.4]
    return RasterPt2(prepared, pos)

def RasterPt2(tris, pos):
    output = []
    for t in ViewTris(TranslateTris(tris, pos)):
        output += TriClipAgainstPlane(t, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output

def RasterPt2NoPos(tris):
    output = []
    for t in ViewTris(tris):
        output += TriClipAgainstPlane(t, (0.0, 0.0, 0.1), (0.0, 0.0, 1.0))
    return output


def RasterPt3(tris):
    output = []
    for i in ProjectTris(tris):
        for s in TriClipAgainstScreenEdges(i):
            output.append(s)
    return output

# Low-Level Raster Functions
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
    nt[3] = GetNormal(nt)
    return nt
        
def TranslateTris(tris, pos):
    for tri in tris:
        ntri = TriAdd(tri, pos)
        ntri[4] = VectorAdd(tri[4], pos)
        yield ntri

def TranslateTri(tri, pos):
    newTri = TriAdd(tri, pos)
    newTri[4] = VectorAdd(TriAverage(newTri), pos)
    return newTri

def ViewTris(tris):
    return (TriMatrixMul(tri, intMatV) for tri in tris)

def ViewTri(tri):
    return TriMatrixMul(tri, intMatV)
                    
def ProjectTris(tris):
    return (TriMul(TriAdd(ProjectTri(tri), [1, 1, 0]), [iC[3], iC[2], 1]) for tri in tris)

#==========================================================================
#  
# Drawing/Shaders
#
#==========================================================================

# Drawing Functions
# Handy shortcuts for drawing to a PyGame or Tkinter screen.

# Usage:
'''
for tri in z3dpy.Raster():

    # PyGame:

    z3dpy.PgDrawTriRGB(tri, [255, 213, 0], surface, pygame)
    # or
    z3dpy.PgDrawTriRGBF(tri, [1, 0.75, 0], surface, pygame)
    # or
    z3dpy.PgDrawTriS(tri, 0.8, surface, pygame)
    # or
    z3dpy.PgDrawTriFL(tri, surface, pygame)
    # or
    z3dpy.PgDrawTriFLB(tri, surface, pygame)

    # Tkinter:

    z3dpy.TkDrawTriRGB(tri, [255, 213, 0], canvas)
    # or
    z3dpy.TkDrawTriRGBF(tri, [1, 0.75, 0], canvas)
    # or
    z3dpy.TkDrawTriS(tri, 0.8, canvas)
    # or
    z3dpy.TkDrawTriFL(tri, canvas)
    # or
    z3dpy.TkDrawTriFLB(tri, canvas)

    # So for example:
    z3dpy.PgDrawTriRGBF(tri, z3dpy.TriGetNormal(tri), screen, pygame)
'''

# Pygame
# Pygame is the fastest at drawing, but installed separately.

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

# Tkinter
# Slower, but almost always pre-installed

def TkDrawTriRGB(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(colour))

def TkDrawTriRGBF(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMulF(colour, 255)))

def TkDrawTriF(tri, f, canvas):
    f = str(math.floor(max(f, 0) * 100))
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill="gray" + f)

def TkDrawTriOutl(tri, colour, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], outline=RGBToHex(colour))

def TkDrawTriS(tri, f, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMulF(tri[6], f)))

def TkDrawTriFL(tri, canvas, lights=lights):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorFloor(VectorMul(tri[6], CheapLighting(tri, lights)))))

def TkDrawTriFLB(tri, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=RGBToHex(VectorMul(tri[6], tri[5])))

# CheapLighting() and ExpensiveLighting()
# Returns the colour of all lighting. 

# Usage:
#
# for tri in RasterThings(things):
#
#   triColour = z3dpy.VectorMul(z3dpy.TriGetColour(tri), CheapLighting(tri))
#
#   PgDrawTriRGB(tri, triColour, surface, pygame)
#
#   or
#
#   TkDrawTriRGB(tri, triColour, canvas)
#

# Lighting shaders, meant to be plugged into DrawTriRGB(), after multiplying by tri's colour.
# Takes the direction towards the light and compares that to it's normal.

# CheapLighting takes the direction towards the light source, no shadow checks or anything.
def CheapLighting(tri, lights=lights):
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    num = 0
    if not len(lights):
        return (0, 0, 0)
    for l in lights:
        match l[0]:
            case 0:
                dist = DistanceBetweenVectors(tri[4], l[1])
                if dist <= l[3]:
                    lightDir = DirectionBetweenVectors(l[1], tri[4])
                    if (dot := VectorDoP(lightDir, tri[3])) < 0:
                        d = dist/l[3]
                        intensity = (1 - (d * d)) * l[2]
                        colour = VectorAdd(colour, VectorMulF(l[4], intensity * -dot))
                        num += 1
            case 1:
                if (dot := VectorDoP(l[1], tri[3])) < 0:
                    intensity = -dot * l[2]
                    colour = VectorAdd(colour, VectorMulF(l[4], intensity))
                    num += 1
    return VectorMax(VectorMinF(VectorDivF(colour, max(num, 1)), 1.0), worldColour)

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
            match l[0]:
                case 0:
                    dist = DistanceBetweenVectors(pos, l[1])
                    if dist <= l[3]:
                        lightDir = DirectionBetweenVectors(l[1], pos)
                        shade = VectorDoP(lightDir, tri[3])
                        if shade < 0:
                            testRay = Ray(pos, l[1])

                            # Checking for shadows
                            for th in shadowcasters:
                                inters = RayIntersectThingComplex(testRay, th)
                                if inters[0]:
                                    # Making sure it's not this triangle, by comparing world position
                                    if not VectorEqual(inters[4], tri[4]):
                                        break
                            else:
                                shading += shade
                                d = (dist / l[3])
                                intensity += (1 - (d * d)) * l[2]
                                colour = VectorAdd(colour, VectorMulF(l[4], intensity))
                case 1:
                    lightDir = l[1]
                    if (shade := VectorDoP(lightDir, tri[3])) > 0:
                        testRay = Ray(tri[4], VectorAdd(tri[4], VectorMulF(VectorNegate(lightDir), 25)))
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

def FlatLightingBaked(tri):
    return tri[5]

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shader variable
def BakeLighting(things=-1, expensive=False, lights=lights, shadowcasters=-1):
    print("Baking Lighting...")
    if things == -1:
        things = GatherThings()
        shadowcasters = GatherThings()
    if shadowcasters == -1:
        shadowcasters = things
    for th in things:
        for m in th[0]:
            for t in m[0]:
                if expensive:
                    calc = ExpensiveLighting(TranslateTri(TransformTri(t, VectorAdd(MeshGetRot(m), ThingGetRot(th))), VectorAdd(MeshGetPos(m), ThingGetPos(th))), shadowcasters, lights)
                else:
                    calc = CheapLighting(TranslateTri(TransformTri(t, VectorAdd(MeshGetRot(m), ThingGetRot(th))), VectorAdd(MeshGetPos(m), ThingGetPos(th))), lights)
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

def TriToLines(tri):
    output = []

    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)
    if list[2][0] != list[0][0]:
        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])

        diff = int(list[1][0] - list[0][0])
        if diff != 0:

            diff3 = (list[1][1] - list[0][1]) / diff
            for x in range(0, diff + 1, sign(diff)):

                lStart = (x + list[0][0], (diff3 * x) + list[0][1])
                lEnd = (x + list[0][0], (slope * x) + list[0][1])

                output.append((lStart, lEnd))

        output += FillTriangleLinePt2(list, slope)
    return tuple(output)

# Part Two: From P2 to P3

def FillTriangleLinePt2(list, fSlope):
    # If this side is flat, no need.
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        diff4 = list[1][0] - list[0][0]
        slope2 = (list[2][1] - list[1][1]) / diff2
    return [((x + list[1][0], (slope2 * x) + list[1][1]), (x + list[1][0], (fSlope * (x + diff4)) + list[0][1])) for x in range(0, int(diff2) + 1, sign(diff2))]

# TriToPixels()
# Returns a tuple of pixels to draw on the screen, given a triangle.

# Usage:
#
# for tri in Raster():
#   for pixel in TriToPixels(tri):
#       x = pixel[0]
#       y = pixel[1]
#

def TriToPixels(tri):
    output = []
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX != 0:
        slope = (list[2][1] - list[0][1]) / diffX
        diff = list[1][0] - list[0][0]

        # If this side's flat, no need.
        if diff != 0:
            diffY = list[1][1] - list[0][1]
            diff3 = diffY / diff

            for x in range(int(diff) + 1):

                ranges = [int(diff3 * x + list[0][1]), int(slope * x + list[0][1])]

                fX = int(x + list[0][0])

                ranges.sort()

                # Pixel:
                # [0] is the screen x, [1] is the screen y
                output += [(fX, y) for y in range(ranges[0], ranges[1] + 1)]

        output += FillTrianglePixelPt2(list, slope, diff)
    return tuple(output)

def FillTrianglePixelPt2(list, fSlope, diff):
    output = []
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        if diff2 != 0:
            slope2 = (list[2][1] - list[1][1]) / diff2

            for x in range(int(diff2)):
                # Repeat the same steps except for this side now.
                ranges = [int(slope2 * x + list[1][1]), int(fSlope * (x + diff) + list[0][1])]
                if ranges[0] == ranges[1]:
                    continue

                ranges.sort()
                fX = int(x + list[1][0])

                output += [(fX, y) for y in range(ranges[0], ranges[1] + 1)]
    return output

# PgPixelShader()
# Calculates texturing, converts the triangle to pixels, then draws them to the screen via a PyGame PixelArray.

# Usage:
#
# screenArray = pygame.PixelArray(screen)
#
# for tri in RasterThings(things):
#   PgPixelShader(tri, screenArray)
#
txtr = TestTexture()

# UVCalcPt1()
# Fx is normalized X from either P1 - P2 or P2 - P3 depending on stage
# Fx2 is normalized X from P1 to P3
# stage is a bool, determines which side of the triangle is
# being drawn.

def UVCalcPt1(uv1, uv2, uv3, Fx, Fx2, bStage1):
    if bStage1:
        # Meant to be multiplied by 0-1 for interpolation
        # From P1 to P2
        uvD1 = uv2[0] - uv1[0]
        uvD2 = uv2[1] - uv1[1]
        # Figure out the UV points for the vertical line we are about to draw
        UVstX = Fx * uvD1 + uv1[0]
        UVstY = Fx * uvD2 + uv1[1]
    else:
        # From P2 to P3
        uvD1 = uv3[0] - uv2[0]
        uvD2 = uv3[1] - uv2[1]
        UVstX = Fx * uvD1 + uv2[0]
        UVstY = Fx * uvD2 + uv2[1]
    
    # From P1 to P3
    uvD3 = uv3[0] - uv1[0]
    uvD4 = uv3[1] - uv1[1]

    UVndX = Fx2 * uvD3 + uv1[0]
    UVndY = Fx2 * uvD4 + uv1[1]
                
    # differences for interpolation
    uvDy = UVndY - UVstY
    uvDx = UVndX - UVstX
    return (uvDx, uvDy, UVstX, UVstY)


def UVCalcPt2(Fy, uvDx, uvDy, UVstX, UVstY):
    return (Fy * uvDy + UVstY, Fy * uvDx + UVstX)


# PixelShader() is just TriToPixels(), but also calculates 
# UV coordinates, and does the drawing to minimize overhead.

# Uses Affine texture mapping, which means textures will warp
# like a PS1

# Usage:
'''

# You'll need to convert the screen to a pygame pixel array
screen = pygame.display.set_mode((1280, 720))
screenArray = pygame.PixelArray(screen)

# Next, load a texture or create one
myTexture = z3dpy.PgLoadTexture("z3dpy/textures/test.png", pygame)

# or

myTexture = (
            ((255, 255, 255, True), (0, 0, 0, True)),
            ((0, 0, 0, True), (255, 255, 255, True))
            )

# Then, during the draw loop, replace PgDrawTri* with PgPixelShader(tri, pixelArray, texture)
for tri in z3dpy.Raster():
    z3dpy.PgPixelShader(tri, screenArray, myTexture)

'''

def PgPixelShader(tri, pixelArray, texture=txtr):
    tX = len(texture)
    tY = len(texture[0])
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX != 0:
        # x * slope takes a screen X and turns it into a screen Y, along the P1-P3 line
        slope = (list[2][1] - list[0][1]) / diffX

        # multiplied by 0-1 to get a screen X, along the P1-P2 line (normalized, make 
        # sure to add back P1's X)
        diff = list[1][0] - list[0][0]

        # If this side's flat, no need.
        if diff != 0:

            uv1 = list[0][4]
            uv2 = list[1][4]
            uv3 = list[2][4]

            diffY = list[1][1] - list[0][1]
            # x * diff3 takes a screen x and results in a screen y, on the P1-P2 line 
            # (normalized, make sure to add back P1's Y)
            diff3 = diffY / diff

            for x in range(math.floor(diff) + 1):

                ranges = [math.floor(diff3 * x + list[0][1]), math.floor(slope * x + list[0][1])]

                rangD = ranges[1] - ranges[0]                

                if rangD == 0:
                    continue

                sgn = sign(rangD)

                # Converting x to 0-1
                # Normalized between P1 and P2
                nX = (x / (diff + 1))
                # Normalized between P1 and P3
                nX2 = (x / diffX)

                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, True)

                # Final X coordinate (pre-calculating instead of in the for loop)
                fX = math.floor(x + list[0][0])

                if fX > 0 and fX < screenSize[0]:

                    for y in range(ranges[0], ranges[1] + sgn, sgn):

                        # Convering y to 0-1
                        nY = (y - ranges[0]) / rangD
                            
                        # Pixel:
                        # [0] is the screen x, [1] is the screen y, [2] is the UV
                        if y > 0 and y < screenSize[1]:
                            if pixelArray[fX, y] == 0:
                                fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                                u = fUVs[0] * tX
                                v = fUVs[1] * tY
                                u = math.floor(abs(u)) % tX
                                v = math.floor(abs(v)) % tY
                                colour = texture[u][v]
                                if colour[3]:
                                    pixelArray[fX, y] = colour

        PgPixelShaderPt2(list, slope, diff, diffX, pixelArray, texture, tX, tY)

def PgPixelShaderPt2(list, fSlope, diff, diffX, pixelArray, texture, tX, tY):
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        if diff2 != 0:
            slope2 = (list[2][1] - list[1][1]) / diff2
            uv1 = list[0][4]
            uv2 = list[1][4]
            uv3 = list[2][4]

            for x in range(math.floor(diff2) + 1):
                # Repeat the same steps except for this side now.
                ranges = [math.floor(slope2 * x + list[1][1]), math.floor(fSlope * (x + diff) + list[0][1])]

                rangd = ranges[1] - ranges[0]

                if rangd == 0:
                    continue

                sgn = sign(rangd)
                
                nX = x / (diff2 + 1)
                nX2 = (x + diff) / diffX
                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, False)
                fX = math.floor(x + list[1][0])

                for y in range(ranges[0], ranges[1] + sgn, sgn):

                    nY = (y - ranges[0]) / rangd

                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            if pixelArray[fX, y] == 0:
                                fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                                rU = fUVs[0] * tX
                                rV = fUVs[1] * tY
                                u = math.floor(abs(rU)) % tX
                                v = math.floor(abs(rV)) % tY
                                colour = texture[u][v]
                                if colour[3]:
                                    pixelArray[fX, y] = colour

# Tkinter is slow, so this is not meant for real time.
def TkPixelShader(tri, canvas, texture=txtr):
    tX = len(texture)
    tY = len(texture[0])
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX != 0:
        # x * slope takes a screen X and turns it into a screen Y, along the P1-P3 line
        slope = (list[2][1] - list[0][1]) / diffX

        # multiplied by 0-1 to get a screen X, along the P1-P2 line (normalized, make 
        # sure to add back P1's X)
        diff = list[1][0] - list[0][0]

        # If this side's flat, no need.
        if diff != 0:

            uv1 = list[0][4]
            uv2 = list[1][4]
            uv3 = list[2][4]

            diffY = list[1][1] - list[0][1]
            # x * diff3 takes a screen x and results in a screen y, on the P1-P2 line 
            # (normalized, make sure to add back P1's Y)
            diff3 = diffY / diff

            for x in range(math.floor(diff) + 1):

                range1 = math.floor(diff3 * x + list[0][1])
                range2 = math.floor(slope * x + list[0][1])

                if range2 - range1 == 0:
                    continue

                # Converting x to 0-1
                # Normalized between P1 and P2
                nX = (x / (diff + 1))
                # Normalized between P1 and P3
                nX2 = (x / diffX)

                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, True)

                # Final X coordinate (pre-calculating instead of in the for loop)
                fX = math.floor(x + list[0][0])

                sgn = 1 if range1 < range2 else -1
                for y in range(range1, range2 + sgn, sgn):

                    # Convering y to 0-1
                    nY = (y - range1) / (range2 - range1)
                        
                    # Pixel:
                    # [0] is the screen x, [1] is the screen y, [2] is the UV
                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                            rU = fUVs[0] * tX
                            rV = fUVs[1] * tY
                            u = math.floor(abs(rU)) % tX
                            v = math.floor(abs(rV)) % tY
                            colour = texture[u][v]
                            if colour[3]:
                                canvas.create_line(fX, y, fX + 1, y, fill=RGBToHex(colour))

        TkPixelShaderPt2(list, slope, diff, diffX, canvas, texture, tX, tY)

def TkPixelShaderPt2(list, fSlope, diff, diffX, canvas, texture, tX, tY):
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        if diff2 != 0:
            slope2 = (list[2][1] - list[1][1]) / diff2
            uv1 = list[0][4]
            uv2 = list[1][4]
            uv3 = list[2][4]

            for x in range(math.floor(diff2) + 1):
                # Repeat the same steps except for this side now.
                range1 = math.floor(slope2 * x + list[1][1])
                range2 = math.floor(fSlope * (x + diff) + list[0][1])

                if range2 - range1 == 0:
                    continue
                
                nX = x / (diff2 + 1)
                nX2 = (x + diff) / diffX
                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, False)
                fX = math.floor(x + list[1][0])

                sgn = 1 if range1 < range2 else -1

                for y in range(range1, range2 + sgn, sgn):

                    nY = (y - range1) / (range2 - range1)

                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                            rU = fUVs[0] * tX
                            rV = fUVs[1] * tY
                            u = math.floor(abs(rU)) % tX
                            v = math.floor(abs(rV)) % tY
                            colour = texture[u][v]
                            if colour[3]:
                                canvas.create_line(fX, y, fX + 1, y, fill=RGBToHex(colour))

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

def CalculateCam(foV, farClip, aspectRatio):
    print("Calculating Camera Constants")
    fov = foV * 0.0174533
    print("Graphing real formulas...")
    fullXGraph = []
    fullYGraph = []
    f = 1 / math.tan(fov* 0.5)
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
            guessM = bestM + ((rand.random() - 0.5) * srchRad)
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
    for em in emitters:
        for p in range(len(em[0])):
            if p >= len(em[0]):
                break
            pt = em[0][p]
            pt[0] -= delta
            if pt[0] <= 0:
                # Removal from list
                em[0] = em[0][:p] + em[0][p+1:]
                p -= 1
                continue
            # Basic version of physics for particles
            pt[2] = VectorSub(pt[2], [airDrag * sign(pt[2][0]), airDrag * sign(pt[2][1]), airDrag * sign(pt[2][2])])
            pt[2] = VectorAdd(pt[2], VectorMulF(VectorMulF(EmitterGetGravity(em), 5), delta))
            pt[1] = VectorAdd(VectorMulF(pt[2], delta), pt[1])
        if em[6]:
            if len(em[0]) < EmitterGetMax(em):
                if em[8] > 0.0:
                    em[0] += (Part(EmitterGetPos(em), VectorAdd(EmitterGetVelocity(em), ((rand.random() - 0.5) * em[8], (rand.random() - 0.5) * em[8], (rand.random() - 0.5) * em[8])), EmitterGetLifetime(em)),)
                else:
                    em[0] += (Part(EmitterGetPos(em), EmitterGetVelocity(em), EmitterGetLifetime(em)),)

#==========================================================================
#  
# Misc Functions
#
#==========================================================================

# WhatIs()
# Takes a list and figures out what "object" it is.
# meant to be used with print() for debugging. Speed is not a priority

# Usage:
#
# print(WhatIs(hopefullyATriangle))
#
    
def WhatIs(any):
    try:
        length = len(any)
    except:
        return str(type(any))
    else:
        match length:
            case 2:
                try:
                    test = any[0][0]
                    return "Ray"
                except:
                    return "Vector2"
            case 3:
                try:
                    test = any[0] + 1
                    return "Vector"
                except:
                    try:
                        test = any[0][0] + 1
                        # S for shortened triangle, it only includes the points, and no other information.
                        return "STriangle"
                    except:
                        return "Particle"
            case 4:
                try:
                    test = any[0][0]
                    return "PhysicsBody"
                except:
                    return "Vector4"
            case 5:
                try:
                    test = any[4][0][0]
                    return "Hitbox"
                except:
                    try:
                        test = any[4][2]
                        return "VectorUV"
                    except:
                        return "Light_Point"
            case 6:
                return "Triangle"
            case 7:
                try:
                    test = any[5][0]
                    return "Camera"
                except:
                    if any[5] == -1:
                        return "Mesh"
                    else:
                        return "AniMesh"
            case 8:
                try:
                    test = any[4] + 1
                    return "Emitter"
                except:
                    try:
                        test = any[6][0]
                        return "Triangle"
                    except:
                        return "Thing"
                    
def RGBToHex(vColour):
    def intToHex(int):
        int = min(int, 255)
        return hex(max(int, 0))[2:].rjust(2, "0")
    #print("#" + intToHex(int(vector[0])) + intToHex(int(vector[1])) + intToHex(int(vector[2])))
    return "#" + intToHex(math.floor(vColour[0])) + intToHex(math.floor(vColour[1])) + intToHex(math.floor(vColour[2]))
                    
def PgScreen(width, height, bgCol, pygame):
    global screenSize
    screenSize = (width, height)
    screen = pygame.display.set_mode((width, height))
    screen.fill(bgCol)
    return screen

def TkScreen(width, height, bgCol, tkinter):
    global screenSize
    screenSize = (width, height)
    canvas = tkinter.Canvas(width=width, height=height, background=bgCol)
    canvas.pack()
    return canvas

# My own list interpolator
def ListInterpolate(list, fIndex):
    floor = math.floor(fIndex)
    first = list[floor]
    difference = list[math.ceil(fIndex)]
    difference -= first
    difference *= fIndex - floor
    return difference + first

def ListExclude(list, index):
    return list[:index] + list[index+1:]

try:
    import z3dpyfast
except:
    pass
else:
    DistanceBetweenVectors = z3dpyfast.DistanceBetweenVectors
    DirectionBetweenVectors = z3dpyfast.DirectionBetweenVectors
    ShortestPointToPlane = z3dpyfast.ShortestPointToPlane
    VectorUVIntersectPlane = z3dpyfast.VectorUVIntersectPlane
    RotTo = z3dpyfast.RotTo
    GetNormal = z3dpyfast.GetNormal
    MatrixStuff = z3dpyfast.MatrixStuff
    PointAtMatrix = z3dpyfast.MatrixMakePointAt
    print("z3dpyfast loaded.")
