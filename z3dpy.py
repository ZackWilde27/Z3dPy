# -zw
'''
Z3dPy v0.2.8 - The Fixes/Streamlining Update

Change Notes:

LIGHTS

- Added Light_Sun(VDirection, FStrength, fRadius, *vColour).
DebugRaster() will draw these lights as arrows located
at 0, 0, 0

- Added worldColour, acts as ambient light in flat lighting.
It's normalized, so white is (1.0, 1.0, 1.0)

- Fixed lighting bug where the Z direction had a much
larger radius

- Reworked colour system, lights are more vibrant.

- ExpensiveLighting() now calculates colour like
CheapLighting().

- ExpensiveLighting() only checks for shadows against
Things in it's shadowcasters argument.
I would recommend using low poly models for shadows.

- GetPos() and SetPos() are now compatible with lights and
rays (I just assumed they were compatible before, sorry
about that.)

- [0] is now type, everything else has been shifted over.

- Fixed LightGetUserVar() and LightSetUserVar().

- BakeLighting() doesn't require any arguments. By default
it'll bake everything in the layers, using everything as
shadowcasters

Argument list is now BakeLighting(things, bExpensive, lights, shadowCasters)


RASTERING

- RasterParts() is now in
RasterThings(thingList, emitterList, *sortingMethod, *reverseSorting)
so they can be sorted alongside the Things.

- Remade the transformation stage: instead of a rotation
matrix + position, everything uses the PointAt matrix.

It allows for skipping the translation stage entirely,
speeding things up a bit.

TransformTris(tris, pos, target, *up) now takes those
arguments

WTransformTris(tris, rot) does the old rotation matrix
method

- Renamed RasterPt1BF() to RasterPt1NoCull(), makes more
sense than BackFace

- Added RasterPt1StaticNoCull(tris, pos)

- Raster Pipeline no longer needs id and colour, as it
now carries through.


TRIS

- Fixed world position offset.

- Put colour and id back in Triangles from the start,
because adding them afterwards just makes things complicated.


RAYS

- Rays now have bIsArrow, which if True will DebugRaster()
the ray as an arrow, pointing at the end location

- Added RayGetIsArrow(ray) and RaySetIsArrow(ray, bIsArrow).


DELTA TIME

- Added GetDelta(). Call it at the start of the loop to
calculate delta time.
It updates the global, so returning the delta is
for your code, if you need it.

- gravity now takes delta into account


CAM CHASE

- CamChase() now uses delta time.

- CamChase() now returns wether or not the camera is at
the target location. This can be used for things like
blending between cameras or transitions and stuff.


PHYSICS

- Ceiling hitbox now scales with Y velocity, so it should
be harder to clip through regardless of speed.

- Reworked HandlePhysicsTrain() to improve interpolation.


EMITTERS

- TickEmitters() has been renamed to HandleEmitters(), to
match HandlePhysics().

- If you have fewer than 3 layers, Raster() will draw emitters on the last layer.


THINGS

- If a Thing's id is -2, it's rotation value becomes the
target location for all meshes.

- Removed cylinder hitboxes, as they didn't have much support


C++

- z3dpyfast is being scaled down to just a vector math
library.
I'm still figuring out the bugs, it's not ready yet.


MISC

- Added ListInterpolate(list, fIndex) which will interpolate between numbers in a list based on fIndex

- Fixed MeshUniqPoints()

- Removed WhatIsInt()

- Fixed GatherThings()

- Remade VectorMin(v1, v2) and VectorMax(v1, v2). It'll min/max each axis individually.
I meant to do this in the last update
To get the original functionality, use VectorCompare(v1, v2) which returns wether or not v1 is greater in magnitude than v2.

- Fixed texture rotation with pixel shaders

- Made general optimizations
'''

# Time for delta-time calculations related to physics
import time

# Rand for finding projection constants
import random as rand

# Math for, well...
import math

print("Z3dPy v0.2.8")

#==========================================================================
#  
# Variables
#
#==========================================================================


# You can reference these at any time to get a global axis.
x = (1, 0, 0)
y = (0, -1, 0)
z = (0, 0, 1)

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

# Internal list of lights, for both FlatLighting(), and
# DebugRaster()
lights = []

# Internal list of emitters, for HandleEmitters() and Raster()
emitters = []

# Internal list of rays for drawing with DebugRaster()
rays = []

# Global things list, now in layers
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

def VectorUV(x, y, z):
    return [x, y, z, [0, 0, 0], [0, 0]]

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

def Mesh(tris, x, y, z):
    return [tris, [x, y, z], [0, 0, 0], [255, 255, 255], 0, -1, 0, True]


def NOP():
    return

# Frames:
# a simplified mesh, for AniMeshes
#
# Each Frame has a function, which is normally NOP
#
# To define AI tied to animations, replace NOP with your own function
#
# Frames also have an index indicating the next frame to go to, which is normally -1 for no change.
#

def Frame(tris, iNext=-1, Function=NOP):
    return [tris, iNext, Function]

# AniMeshes:
# Same as Mesh except animated:
# [0] is a list of frames
# [5] is frame number.
#
def AniMesh(frames, x, y, z):
    return [frames, [x, y, z], [0, 0, 0], [255, 255, 255], 0, 0, 0]

def AnimMesh(frames, x, y, z):
    return [frames, [x, y, z], [0, 0, 0], [255, 255, 255], 0, 0, 0]

# Usage:
'''
# Assuming that frame 0-30 is a walk animation and 31-60 is an attack animation

def AIFunction():
    # I'll make up some AI function real quick:
    if PlayerIsTHEGordanFreeman():
        return
    else:
        AniMeshSetFrame(enemyMesh, 31)
        AttackPlayer()


enemyMesh = z3dpy.LoadAniMesh("filename.obj")


# On the 29th frame of animation, it'll perform AIFunction().
AniMeshSetFrameFunc(enemyMesh, 29, AIFunction)

# FrameNext is well, the frame that comes next.
# Keep in mind it will override anything the function does.
AniMeshSetFrameNext(enemyMesh, 30, 0)

AniMeshSetFrameNext(enemyMesh, 60, 31)

# If the function doesn't set the frame to 31, the frame 30 will loop back to 0.
# and once it's in the attack animation, frame 60 will loop back to 31

# Inspired by Doom.


enemy = z3dpy.Thing([enemyMesh], 0, 5, 2)


# Then during the draw loop, increment the animation.
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
    return [type, id, radius, height, LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, radius, height, radius)]

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

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], [], [], True, 0, 0]

# Dupes:
#
# A Dupe is a duplicate of a thing, reusing it's properties
# with a unique position and rotation
#
# [0] is the index of the thing to copy from
# [1] is position
# [2] is rotation
# [6] is -1 to indicate it's a dupe
# [3] - [5] are unused, so they're user variables now
#

def Dupe(iIndex, vPos, vRot):
    return [iIndex, vPos, vRot, 0, 0, 0, -1]

# Cameras:
#
# In order to render the triangles, we need information
# about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
#
# For a third person camera, use CamSetTargetLocation()
# For a first person camera, use CamSetTargetVector()
#
# To change the FOV, call FindHowVars(fov)

# [0] is user variable
# [1] is position
# [2] is rotation
# [3] is near clip
# [4] is far clip
# [5] is target location
# [6] is up vector
#

def Cam(x, y, z, scW=-1, scH=-1):
    global screenSize
    if scW + scH != -2:
        screenSize = (scW, scH)
    return [0, [x, y, z], [0, 0, 0], 0.1, 1500, [0, 0, 1], [0, 1, 0]]


def Camera(x, y, z, scW=-1, scH=-1):
    global screenSize
    if scW + scH != -2:
        screenSize = (scW, scH)
    return [0, [x, y, z], [0, 0, 0], 0.1, 1500, [0, 0, 1], [0, 1, 0]]

# Internal Camera
#
# the internal camera used for rendering. 
# Set the internal camera to one of your cameras when you want to render from it.
#
# [0] is location
# [1] is rotation
# [2] is screen height / 2
# [3] is screen width / 2
# [4] is near clip
# [5] is far clip
# [6] is target vector
# [7] is up vector
#

iC = [[0, 0, 0], [0, 0, 0], 360, 640, 0.1, 1500, [0, 0, 1], [0, 1, 0]]

intMatV = ()

intMatP = ()

def SetInternalCam(camera):
    global intMatV
    global iC
    iC = [CamGetPos(camera), CamGetRot(camera), screenSize[1] * 0.5, screenSize[0] * 0.5, CamGetNCl(camera), CamGetFCl(camera), CamGetTargetVector(camera), CamGetUpVector(camera)]
    # doing all these calculations once so we can hold on 
    # to them for the rest of calculations
    intMatV = LookAtMatrix(camera)

# Lights:
#
# Point lights will light up triangles that are inside the
# radius and facing towards it's location
#
# Used for the FlatLighting() shader, which outputs a colour
# to be plugged into DrawTriS() or DrawTriF()
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

def Light_Point(x, y, z, FStrength, fRadius, vColour=(255, 255, 255)):
    return [0, [x, y, z], FStrength, fRadius, VectorDivF(vColour, 255), 0, 0]

# Unique to Sun:
# [1] is direction

def Light_Sun(VDirection, FStrength, fRadius, vColour=(255, 255, 255)):
    return [1, VDirection, FStrength, fRadius, VectorDivF(vColour, 255), 0, 0]

# My own list interpolator
def ListInterpolate(list, fIndex):
    first = list[math.floor(fIndex)]
    second = list[math.ceil(fIndex)]
    difference = fIndex - math.floor(fIndex)
    return (second - first) * difference + first

def TrainInterpolate(train, fX, fY):
    if fX > 0.0 and fY > 0.0:
        if fX < len(train) - 1 and fY < len(train[0]) - 1:
            first = ListInterpolate(train[math.floor(fX)], fY)
            second = ListInterpolate(train[math.ceil(fX)], fY)
            difference = fX - math.floor(fX)
            return (second - first) * difference + first
    return 0

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

# Add the ray to the global list to get drawn
zp.rays.append(myRay)

# and/or you could do a collision check
hit = zp.RayIntersectThingComplex(myRay, myCharacter)

if hit[0]:
    # Hit
    location = hit[1]
    distance = hit[2]
    normal = hit[3]
    print(location, distance, normal)
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

# Now when debug rastering, it'll be drawn as a small trigon.


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

# Optional passes, strength, and amplitude argument
# (by default, 1, 1.0, and 1.0)
BakeTrain(myTerrain, 3, 0.5, 1.5)

Passes is how many times the blur is done, normally once

Strength is how much the surrounding points affect final
output. AKA strength of the blur, normally 1.0 / no change.

Amplitude is multiplied by the final output to amplify.
Normally 1.0 / no change.
'''

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
                p0 = train[x][y]
                p1 = train[mx][y] * 0.8 * strength
                p2 = train[mn][y] * 0.8 * strength
                p3 = train[x][my] * 0.8 * strength
                p4 = train[x][ny] * 0.8 * strength
                p5 = train[mx][my] * 0.6 * strength
                p6 = train[mx][ny] * 0.6 * strength
                p7 = train[mn][my] * 0.6 * strength
                p8 = train[mn][ny] * 0.6 * strength
                h = sum((p0, p1, p2, p3, p4, p5, p6, p7, p8)) / 9
                train[x][y] = h * amplitude

    print("Done!")



# Emitters:
#
# Emitters spawn particles, and store info about them.
#
# [0] is the list of currently active particles
# [1] is position
# [2] is the template mesh
# [3] is velocity
# [4] is max #
# [5] is lifetime
# [6] is particle gravity
# [7] is wether or not it's active.
#

def Emitter(position, template, maximum, velocity=[0, 0, 0], lifetime=15.0, vGravity=[0, 9.8, 0]):
    return [(), position, template, velocity, maximum, lifetime, vGravity, False]

# Usage:
'''
# Creating an emitter
# Emitter(position, template, max, velocity, lifetime, gravity)
myEmitter = z3dpy.Emitter([0, 0, 0], myMesh, 150, [0, 0, 0], 15.0, [0, 9.8, 0])

# Add it to the emitters list to be drawn, if using Raster()
z3dpy.emitters.append(myEmitter)

# During the draw loop, TickEmitters()

while True:

    z3dpy.TickEmitters()

    # You can also specify your own list
    z3dpy.TickEmitters([myEmitter, myOtherEmitter])
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
# False transparency.

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
    mesh[2] = VectorAdd(MeshGetRot(mesh), vector)

def MeshSubRot(mesh, vector):
    mesh[2] = VectorSub(MeshGetRot(mesh), vector)

def MeshMulRot(mesh, vector):
    mesh[2] = VectorMul(MeshGetRot(mesh), vector)

def MeshDivRot(mesh, vector):
    mesh[2] = VectorDiv(MeshGetRot(mesh), vector)

def MeshGetRot(mesh):
    return mesh[2]

def MeshSetColour(mesh, vColour):
    mesh[3] = vColour
    if AniMeshGetFrame(mesh) == -1:
        for t in mesh[0]:
            t[6] = vColour
    else:
        for frm in mesh[0]:
            for t in frm[0]:
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

def AniMeshGetFrame(animesh):
    return animesh[5]

def AniMeshSetFrame(animesh, iFrame):
    animesh[5] = iFrame

def AniMeshIncFrame(animesh):
    animesh[5] = (animesh[5] + 1) % len(animesh[0])

def AniMeshDecFrame(animesh):
    animesh[5] -= 1

# AniMeshSetFrameFunc sets the function to be executed on a
# particular frame of animation
# iFrame is the frame that the function should be run on.
# Keep in mind that there can only be one function per frame.
def AniMeshSetFrameFunc(animesh, iFrame, function):
    animesh[0][iFrame][2] = function

# AniMeshSetFrameNext sets the frame that will come
# after iFrame
def AniMeshSetFrameNext(animesh, iFrame, iNext):
    animesh[0][iFrame][1] = iNext

## Deprecated
def AnimMeshGetFrame(animesh):
    return AniMeshGetFrame(animesh)

def AnimMeshSetFrame(animesh, iFrame):
    AniMeshSetFrame(animesh, iFrame)

def AnimMeshIncFrame(animesh):
    AniMeshIncFrame(animesh)

def AnimMeshDecFrame(animesh):
    AniMeshDecFrame(animesh)

def AnimMeshSetFrameFunc(animesh, iFrame, function):
    AniMeshSetFrameFunc(animesh, iFrame, function)

def AnimMeshSetFrameNext(animesh, iFrame, iNext):
    AniMeshSetFrameNext(animesh, iFrame, iNext)
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
        output += [thing for thing in layer]
    return tuple(output)


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
    thing[1] = VectorAdd(ThingGetPos(thing), vector)

def ThingSubPos(thing, vector):
    thing[1] = VectorSub(ThingGetPos(thing), vector)

def ThingSetPosX(thing, x):
    thing[1] = [x] + thing[1][1:]

def ThingSetPosY(thing, y):
    thing[1] = [thing[1][0], y, thing[1][2]]

def ThingSetPosZ(thing, z):
    thing[1] = thing[1][:-1] + [z]

def ThingAddPosX(thing, x):
    oPos = ThingGetPos(thing)
    thing[1] = [oPos[0] + x, oPos[1], oPos[2]]

def ThingAddPosY(thing, y):
    thing[1] = [thing[1][0], thing[1][1] + y, thing[1][2]]

def ThingAddPosZ(thing, z):
    thing[1] = [thing[1][0], thing[1][1], thing[1][2] + z]

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
    thing[2] = VectorAdd(ThingGetRot(thing), vector)

def ThingSubRot(thing, vector):
    thing[2] = VectorSub(ThingGetRot(thing), vector)

def ThingMulRot(thing, vector):
    thing[2] = VectorMul(ThingGetRot(thing), vector)

def ThingDivRot(thing, vector):
    thing[2] = VectorDiv(ThingGetRot(thing), vector)

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
        if AniMeshGetFrame(m) != -1:
            AniMeshIncFrame(m)

# ThingSetFrameFunc(thing, 0, 30, AIFunction)
# iAniMesh is the index of the animesh to change
# iFrame is the frame that the function should be run on.
def ThingSetFrameFunc(thing, iAniMesh, iFrame, function):
    thing[0][iAniMesh][iFrame][2] = function

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
                thing[3][4] = LoadMesh("z3dpy/mesh/sphere.obj", 0, 0, 0, fRadius, fRadius, fRadius)
            case 2:
                thing[3][4] = LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, fRadius, fHeight, fRadius)
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
    thing[4][0] = [x, thing[4][0][1], thing[4][0][2]]

def ThingSetVelocityY(thing, y):
    thing[4][0] = [thing[4][0][0], y, thing[4][0][2]]

def ThingSetVelocityZ(thing, z):
    thing[4][0] = [thing[4][0][0], thing[4][0][1], z]

def ThingGetVelocity(thing):
    return thing[4][0]

def ThingGetVelocityX(thing):
    return thing[4][0][0]

def ThingGetVelocityY(thing):
    return thing[4][0][1]

def ThingGetVelocityZ(thing):
    return thing[4][0][2]

def ThingAddVelocity(thing, vector):
    thing[4][0] = VectorAdd(ThingGetVelocity(thing), vector)

def ThingSubVelocity(thing, vector):
    thing[4][0] = VectorSub(ThingGetVelocity(thing), vector)

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
    thing[4][5] = VectorAdd(thing[4][5], vector)

def ThingGetRotVelocity(thing):
    return thing[4][5]

def ThingSetRotAccel(thing, vector):
    thing[4][6] = vector

def ThingAddRotAccel(thing, vector):
    thing[4][6] = VectorAdd(thing[4][6], vector)

def ThingGetRotAccel(thing):
    return thing[4][6]

# ThingStop resets velocity and acceleration to 0. 
def ThingStop(thing):
    thing[4][1] = [0, 0, 0]
    thing[4][0] = [0, 0, 0]


# CAMERAS


def CamSetPosX(cam, x):
    cam[1] = [x, cam[1][1], cam[1][2]]

def CamSetPosY(cam, y):
    cam[1] = [cam[1][0], y, cam[1][2]]

def CamSetPosZ(cam, z):
    cam[1] = [cam[1][0], cam[1][1], z]

def CamSetPos(cam, vector):
    cam[1] = vector

def CamAddPos(cam, vector):
    cam[1] = VectorAdd(cam[1], vector)

def CamSubPos(cam, vector):
    cam[1] = VectorSub(cam[1], vector)

def CamMulPos(cam, vector):
    cam[1] = VectorMul(cam[1], vector)

def CamDivPos(cam, x, y, z):
    cam[1] = [cam[1][0] / x, cam[1][1] / y, cam[1][2] / z]

def CamDivPosF(cam, f):
    cam[1] = VectorDivF(cam[1], f)

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
    CamSetTargetVector(cam, dir)


## Deprecated
def CamSetTargetLocation(cam, vector):
    CamSetTargetLoc(cam, vector)

def CamGetTargetLocation(cam):
    return CamGetTargetLoc(cam)

def CamSetTargetVector(cam, vector):
    CamSetTargetDir(cam, vector)

def CamGetTargetVector(cam):
    return CamGetTargetDir(cam)
##


def CamSetUpVector(cam, vector):
    cam[6] = vector

def CamGetUpVector(cam):
    return cam[6]

def CamGetRightVector(cam):
    return VectorCrP(CamGetTargetDir(cam), CamGetUpVector(cam))

def CamChase(cam, location, speed=0.25):
    line = VectorSub(CamGetPos(cam), location)
    if VectorComb(VectorABS(line)) < 0.05:
        CamSetPos(cam, location)
        return True
    CamSubPos(cam, VectorMulF(line, speed * delta))
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
    light[1] = [x, light[0][1], light[0][2]]

def LightSetPosY(light, y):
    light[1] = [light[0][0], y, light[0][2]]

def LightSetPosZ(light, z):
    light[1] = [light[0][0], light[0][1], z]

def LightAddPos(light, vector):
    light[1] = VectorAdd(light[0], vector)

def LightGetStrength(light):
    return light[2]

def LightSetStrength(light, str):
    light[2] = str

def LightGetRadius(light):
    return light[3]

def LightSetRadius(light, radius):
    light[3] = radius

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


#==========================================================================
#  
# Vector UV Functions
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

#==========================================================================
#  
# Vector functions
#
#==========================================================================

# These vector functions return new vectors, not modifying the original. (Except for VectorMin() and VectorMax(), which returns one of the given vectors.)

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
    l = abs(VectorGetLength(v))
    if l != 0:
        return [v[0] / l, v[1] / l, v[2] / l]
    return v

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
    return math.sqrt((v[0] * v[0]) + (v[1] * v[1]) + (v[2] * v[2]))

# Vector Dot Product compares 2 directions. 1 is apposing, -1 is facing the same direction. (or the other way around, not too sure)
# Useful for lighting calculations.
def VectorDoP(v1, v2):
    return (v1[0] * v2[0]) + (v1[1] * v2[1]) + (v1[2] * v2[2])

def VectorEqual(v1, v2):
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def DistanceBetweenVectors(v1, v2):
    d1 = v2[0] - v1[0]
    d2 = v2[1] - v1[1]
    d3 = v2[2] - v1[2]
    output = (d1 * d1) + (d2 * d2) + (d3 * d3)
    return math.sqrt(output)

def VectorNegate(v):
    return [-v[0], -v[1], -v[2]]

def VectorABS(v):
    return [abs(v[0]), abs(v[1]), abs(v[2])]

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))

# Give it a vector and it'll return a vector where the strongest axis is 1 and the others are 0
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

# WrapRot() takes a rot and converts it to 0-359
def WrapRot(vRot):
    # Constructing new rot, not modifying the original.
    nRot = [vRot[0], vRot[1], vRot[2]]

    if nRot[0] < 0:
        nRot[0] = (nRot[0] % -360) + 360
    if nRot[1] < 0:
        nRot[1] = (nRot[1] % -360) + 360
    if nRot[2] < 0:
        nRot[2] = (nRot[2] % -360) + 360

    return VectorModF(nRot, 360)

# Now I know the definitive order of operations:
# RotateX -> RotateZ -> RotateY
def RotTo(vRot, VTarget):
    nRot = WrapRot(vRot)
    nV = VectorRotateX(VTarget, nRot[0])
    nV = VectorRotateZ(nV, nRot[2])
    return VectorRotateY(nV, nRot[1])


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

def VectorIntersectPlane(pPos, pNrm, lSta, lEnd, uv1, uv2):
    pNrm = VectorNormalize(pNrm)
    plane_d = -VectorDoP(pNrm, pPos)
    ad = VectorDoP(lSta, pNrm)
    bd = VectorDoP(lEnd, pNrm)
    t = (-plane_d - ad) / (bd - ad)
    lineStartToEnd = VectorUVSub(lEnd, lSta)
    lineToIntersect = VectorUVMulF(lineStartToEnd, t)
    lSta[4] = ((uv2[0] - uv1[0]) * t + uv1[0], (uv2[1] - uv1[1]) * t + uv1[1])
    return VectorUVAdd(lSta, lineToIntersect)

def ShortestPointToPlane(point, plNrm, plPos):
    return VectorDoP(plNrm, point) - VectorDoP(plNrm, plPos)

def TriClipAgainstPlane(tri, pPos, pNrm):
    pNrm = VectorNormalize(pNrm)
    insideP = []
    outsideP = []
    d1 = ShortestPointToPlane(tri[0], pNrm, pPos)
    d2 = ShortestPointToPlane(tri[1], pNrm, pPos)
    d3 = ShortestPointToPlane(tri[2], pNrm, pPos)
    if d1 >= 0:
        insideP.append(tri[0])
    else:
        outsideP.append(tri[0])
    if d2 >= 0:
        insideP.append(tri[1])
    else:
        outsideP.append(tri[1])
    if d3 >= 0:
        insideP.append(tri[2])
    else:
        outsideP.append(tri[2])

    if len(insideP) == 0:
        return []

    if len(insideP) == 3:
        return [tri]

    if len(insideP) == 1 and len(outsideP) == 2:
        outT1 = [insideP[0], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[1], insideP[0][4], outsideP[1][4]), VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0], insideP[0][4], outsideP[0][4]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        return [outT1]

    if len(insideP) == 2 and len(outsideP) == 1:
        outT1 = [insideP[0], insideP[1], VectorIntersectPlane(pPos, pNrm, insideP[1], outsideP[0], insideP[1][4], outsideP[0][4]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        outT2 = [insideP[0], outT1[2], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0], insideP[0][4], outsideP[0][4]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        return [outT1, outT2]

def GetNormal(tri):
    triLine1 = VectorSub(tri[1], tri[0])
    triLine2 = VectorSub(tri[2], tri[0])
    normal = VectorCrP(triLine1, triLine2)
    return VectorNormalize(VectorMul(normal, [1, -1, -1]))

def TriAverage(tri):
    return [(tri[0][0] + tri[1][0] + tri[2][0]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.33333]


# Triangle Sorting functions
def triSortAverage(n):
    return (n[0][2] + n[1][2] + n[2][2]) * 0.3333333

def triSortFurthest(n):
    return max(n[0][2], n[1][2], n[2][2])

def triSortClosest(n):
    return min(n[0][2], n[1][2], n[2][2])

def TriClipAgainstZ(tri):
    return TriClipAgainstPlane(tri, [0.0, 0.0, 0.1], [0.0, 0.0, 1.0])

def TriClipAgainstScreenEdges(tri):
    output = []
    for t in TriClipAgainstPlane(tri, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]):
        for r in TriClipAgainstPlane(t, [0.0, screenSize[1] - 1.0, 0.0], [0.0, -1.0, 0.0]):
            for i in TriClipAgainstPlane(r, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]):
                for s in TriClipAgainstPlane(i, [screenSize[0] - 1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]):
                    output.append(s)
    return tuple(output)


#==========================================================================
#  
# Mesh Functions
#
#==========================================================================


# Load OBJ File
def LoadMesh(filename, x = 0, y = 0, z = 0, sclX = 1, sclY = 1, sclZ = 1):
    try:
        file = open(filename)
    except:
        if filename == "z3dpy/mesh/error.obj":
            raise Exception("Can't load placeholder mesh. (Is the z3dpy folder missing?)")
        else:
            return LoadMesh("z3dpy/mesh/error.obj", x, y, z, sclX, sclY, sclZ)
    verts = []
    uvs = []
    output = []
    matoutputs = []
    triangles = []
    mattriangles = []
    mat = -1

    while (currentLine := file.readline()):
        if currentLine[0] == 'v':
            if currentLine[1] == 't':
                currentLine = currentLine[3:].split(' ')
                uvs.append([float(currentLine[0]), float(currentLine[1])])
            else:
                currentLine = currentLine[2:].split(' ')
                verts.append([float(currentLine[0]) * sclX, float(currentLine[1]) * sclY, float(currentLine[2]) * sclZ, [0, 0, 0], [float(currentLine[0]) * sclX, float(currentLine[1]) * sclY], 0])
            
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            if '/' in currentLine:
                newLine = []
                currentLine = currentLine.split(' ')
                for cl in currentLine:
                    cl = cl.split('/')
                    verts[int(cl[0]) - 1][4] = uvs[int(cl[1]) - 1]
                    newLine.append(cl[0])
                currentLine = newLine
            else:
                currentLine = currentLine.split(' ')
            if len(currentLine) < 4:
                qTri = [verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1]]
                normal = GetNormal(qTri)
                v1 = qTri[0]
                v2 = qTri[1]
                v3 = qTri[2]
                verts[int(currentLine[1])- 1][3] = VectorAdd(verts[int(currentLine[1])- 1][3], normal)
                verts[int(currentLine[2]) - 1][3] = VectorAdd(verts[int(currentLine[2]) - 1][3], normal)

                verts[int(currentLine[0]) - 1][5] += 1
                verts[int(currentLine[1]) - 1][5] += 1
                verts[int(currentLine[2]) - 1][5] += 1
                if mat != -1:
                    mattriangles[mat].append([int(currentLine[0]) - 1, int(currentLine[1])- 1, int(currentLine[2]) - 1])
                else:
                    triangles.append([int(currentLine[0]) - 1, int(currentLine[1])- 1, int(currentLine[2]) - 1])
            else:
                # Triangulating n-gon
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
            # Accounting for different materials
            mattriangles.append([])
            mat += 1

    for v in verts:
        v[3] = VectorDivF(v[3], v[5])

    for tr in triangles:
        nt = Tri(verts[tr[0]], verts[tr[1]], verts[tr[2]])
        output.append(nt)

    for trL in mattriangles:
        index = len(matoutputs)
        matoutputs.append([])
        for tr in trL:
            nt = Tri(verts[tr[0]], verts[tr[1]], verts[tr[2]])
            matoutputs[index].append(nt)

    file.close()
    if mat == -1:
        return Mesh(tuple(output), x, y, z)
    else:
        return [Mesh(tuple(trS), x, y, z) for trS in matoutputs]

def LoadAniMesh(filename, x=0, y=0, z=0, sclX=1, sclY=1, sclZ=1):
    looking = True
    a = 0
    st = 0
    nd = 0
    # Looking for first frame
    while looking:
        try:
            test = open(filename[:-4] + str(a) + ".obj", 'r')
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
            test = open(filename[:-4] + str(a + 1) + ".obj", 'r')
        except:
            nd = a
            looking = False
        else:
            test.close()
            a += 1
            
    newMsh = AniMesh([], x, y, z)
    for f in range(st, nd):
        newFrm = Frame(LoadMesh(filename[:-4] + str(f) + ".obj", 0, 0, 0, sclX, sclY, sclZ)[0])
        
        newMsh[0].append(newFrm)

    return newMsh


## Deprecated
def LoadAnimMesh(filename, x=0, y=0, z=0, sclX=1, sclY=1, sclZ=1):
    return LoadAniMesh(filename, x, y, z, sclX, sclY, sclZ)
##

lightMesh = LoadMesh("z3dpy/mesh/light.obj")

MeshSetId(lightMesh, -1)
MeshSetColour(lightMesh, (255, 0, 0))

dotMesh = LoadMesh("z3dpy/mesh/dot.obj")
MeshSetId(dotMesh, -1)
MeshSetColour(dotMesh, (255, 0, 0))

arrowMesh = LoadMesh("z3dpy/mesh/axisZ.obj")
MeshSetId(arrowMesh, -1)
MeshSetColour(arrowMesh, (255, 0, 0))

def NewCube(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/cube.obj", x, y, z)

def NewCylinder(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/cylinder.obj", x, y, z)

def NewSusanne(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/susanne.obj", x, y, z)

def NewZ3dPy(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/zack.obj", x, y, z)

def NewArrow(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/axisZ.obj", x, y, z)

def NewSphere(x=0, y=0, z=0):
    return LoadMesh("z3dpy/mesh/sphere.obj", x, y, z)

def MeshUniqPoints(mesh):
    buffer = []
    for tri in MeshGetTris(mesh):
        for point in tri[:3]:
            if (x := VectorComb(point)) not in buffer:
                buffer.append(x)
                yield point


#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def TriMatrixMul(t, m):
    return [VecMatrixMul(t[0], m), VecMatrixMul(t[1], m), VecMatrixMul(t[2], m), t[3], t[4], t[5], t[6], t[7]]

def VecMatrixMul(v, m):
    output = Vec3MatrixMulOneLine(v, m)
    output.pop()
    return output + [v[3], v[4]]

def Vec3MatrixMulOneLine(v, m):
    return [v[0] * m[0][0] + v[1] * m[1][0] + v[2] * m[2][0] + m[3][0], v[0] * m[0][1] + v[1] * m[1][1] + v[2] * m[2][1] + m[3][1], v[0] * m[0][2] + v[1] * m[1][2] + v[2] * m[2][2] + m[3][2], v[0] * m[0][3] + v[1] * m[1][3] + v[2] * m[2][3] + m[3][3]]

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

    return [newForward, newUp, newRight]

def MatrixMakeRotX(deg):
    rad = deg * 0.0174
    return ((1, 0, 0, 0), (0, math.cos(rad), math.sin(rad), 0), (0, -math.sin(rad), math.cos(rad), 0), (0, 0, 0, 1))


def MatrixMakeRotY(deg):
    rad = deg * 0.0174
    return ((math.cos(rad), 0, math.sin(rad), 0), (0, 1, 0, 0), (-math.sin(rad), 0, math.cos(rad), 0), (0, 0, 0, 1))

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174
    return ((math.cos(rad), math.sin(rad), 0, 0), (-math.sin(rad), math.cos(rad), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[2][1], temp[2][2], 0), (temp[1][0], temp[1][1], temp[1][2], 0), (temp[0][0], temp[0][1], temp[0][2], 0), (pos[0], pos[1], pos[2], 1))

def LookAtMatrix(camera):
    temp = MatrixStuff(CamGetPos(camera), CamGetTargetLocation(camera), CamGetUpVector(camera))
    return ((temp[2][0], temp[1][0], temp[0][0], 0.0), (temp[2][1], temp[1][1], temp[0][1], 0.0), (temp[2][2], temp[1][2], temp[0][2], 0.0), (-VectorDoP(CamGetPos(camera), temp[2]), -VectorDoP(CamGetPos(camera), temp[1]), -VectorDoP(CamGetPos(camera), temp[0]), 1.0))

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
    # wikipedia page
    deadzone = 0.1
    rayDr = RayGetDirection(ray)
    raySt = ray[1]

    e1 = VectorSub(tri[1], tri[0])
    e2 = VectorSub(tri[2], tri[0])
    h = VectorCrP(rayDr, e2)
    a = VectorDoP(e1, h)
    if a < -deadzone or a > deadzone:
        f = 1.0 / a
        o = VectorSub(raySt, tri[0])
        ds = VectorDoP(o, h) * f
        
        if ds < 0.0 or ds > 1.0:
            return (False,)
        
        q = VectorCrP(o, e1)
        v = VectorDoP(rayDr, q) * f

        if v < 0.0 or ds + v > 1.0:
            return (False,)

        l = VectorDoP(e2, q) * f
        if l > deadzone and l < RayGetLength(ray):
            # Hit
            #
            # [0] is wether or not it hit
            #
            # [1] is location
            #
            # [2] is distance
            #
            # [3] is hit normal
            #
            
            return (True, VectorAdd(raySt, VectorMulF(rayDr, l)), l, tri[3])
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
            trg = RotTo(VectorAdd(m[2], thing[2]), (0.0, 0.0, 1.0))
        for t in TransformTris(m[0], VectorAdd(m[1], thing[1]), trg, (0.0, 1.0, 0.0)):
            inrts = RayIntersectTri(ray, t)
            if inrts[0]:
                return inrts
    return (False,)



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
    for me in range(0, len(thingList)):
        if thingList[me][3] != []:
            for thm in range(0, len(thingList)):
                if thingList[thm][3] != []:

                    # In order of speed
                    if thm != me:
                        if ThingGetHitboxId(thingList[thm]) == ThingGetHitboxId(thingList[me]):
                        
                            if [thingList[thm], thingList[me]] not in results:
                                myPos = ThingGetPos(thingList[me])
                                thPos = ThingGetPos(thingList[thm])
                                match ThingGetHitboxType(thingList[me]):
                                    case 0:
                                        # Sphere
                                        # If the distance
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

# Floors are handled just like the 

def BasicHandleCollisions(oth, pivot):
    
    match ThingGetHitboxType(oth):
        case 0:
            # Sphere Collisions
            # Simple offset the direction away from pivot.
            ThingSetPos(oth, VectorMulF(DirectionBetweenVectors(ThingGetPos(oth), ThingGetPos(pivot)), ThingGetHitboxRadius(oth) + ThingGetHitboxRadius(pivot)))
        case 2:
            # Cube Collisions

            if ThingGetPosX(oth) + ThingGetHitboxRadius(oth) < (ThingGetPosX(pivot) - ThingGetHitboxRadius(pivot)) + 0.5:
                # +X Wall Collision
                ThingSetPosX(oth, ThingGetPosX(pivot) - ThingGetHitboxRadius(pivot) - ThingGetHitboxRadius(oth))
                return
            
            if ThingGetPosX(oth) - ThingGetHitboxRadius(oth) > (ThingGetPosX(pivot) + ThingGetHitboxRadius(pivot)) - 0.5:
                # -X Wall Collision
                ThingSetPosX(oth, ThingGetPosX(pivot) + ThingGetHitboxRadius(pivot) + ThingGetHitboxRadius(oth))
                return
            
            if ThingGetPosZ(oth) + ThingGetHitboxRadius(oth) < (ThingGetPosZ(pivot) - ThingGetHitboxRadius(pivot)) + 0.5:
                # +Z Wall Collision
                ThingSetPosZ(oth, ThingGetPosZ(pivot) - ThingGetHitboxRadius(pivot) - ThingGetHitboxRadius(oth))    
                return
            
            if ThingGetPosZ(oth) - ThingGetHitboxRadius(oth) > (ThingGetPosZ(pivot) + ThingGetHitboxRadius(pivot)) - 0.5:
                # -Z Wall Collision
                ThingSetPosZ(oth, ThingGetPosZ(pivot) + ThingGetHitboxRadius(pivot) + ThingGetHitboxRadius(oth))
                return

            if ThingGetPosY(oth) > ThingGetPosY(pivot):
                # Ceiling Collision
                ThingSetPosY(oth, ThingGetPosY(pivot) + ThingGetHitboxHeight(pivot) + ThingGetHitboxHeight(oth))
                ThingSetVelocityY(oth, 0)
                return

            # Floor Collision
            ThingSetPosY(oth, ThingGetPosY(pivot) - ThingGetHitboxHeight(pivot) - ThingGetHitboxHeight(oth))
            if ThingGetPhysics(oth) != []:
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
# Does GatherCollisions(), and if two things are colliding, set their velocities accordingly.
# Will only push things that have physics bodies, so static things can be put in as well.

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
        if ThingGetPhysics(cols[0]) != []:
            if ThingGetPhysics(cols[1]) != []:
                myforce = VectorMulF(VectorMulF(ThingGetVelocity(cols[0]), ThingGetMass(cols[0])), ThingGetFriction(cols[1]))
                thforce = VectorMulF(VectorMulF(ThingGetVelocity(cols[1]), ThingGetMass(cols[1])), ThingGetFriction(cols[0]))
                toforce = VectorAdd(myforce, thforce)
                ThingAddVelocity(cols[0], toforce)
                ThingAddVelocity(cols[1], VectorNegate(toforce))
            else:
                # Non-physics things use BasicHandleCollisions()
                BasicHandleCollisions(cols[0], cols[1])
        else:
            BasicHandleCollisions(cols[1], cols[0])

def sign(f):
    if f == 0:
        return 0
    return 1 if f > 0 else -1

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

def Raster(fnSortKey=triSortAverage, bSortReverse=True):
    finished = []
    llen = len(layers)
    llayer = min(llen - 1, 2)
    for l in range(llen):
        finished += RasterThings(layers[l], emitters if l == llayer else [], fnSortKey, bSortReverse)
    return finished

# RasterThings()
# Specify your own list of things to raster.

# Usage:
#
# for tri in z3dpy.RasterThings([myCharacter]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RasterThings(things, emitters=[], sortKey=triSortAverage, sortReverse=True):
    try:
        test = intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        viewed = []
        for t in things:
            match t[6]:
                case -2:
                    # Custom Target
                    for m in t[0]:
                        if m[5] == -1:
                            # Static Mesh
                            viewed += RasterPt1PointAt(m[0], VectorAdd(m[1], t[1]), t[2], iC[7])
                        else:
                            # AniMesh
                            viewed += RasterPt1PointAt(m[0][AniMeshGetFrame(m)[0]][0], VectorAdd(m[1], t[1]), t[2], iC[7])
                            # Call the function for that frame
                            m[0][m[5][2]]()
                            # If iNext is not -1, set the current frame.
                            if m[0][m[5]][1] != -1:
                                m[5] = m[0][m[5]][1]
                case -1:
                    # Dupe
                    for m in things[t[0]][0]:
                        viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                case _:
                    if t[5]:
                        for m in t[0]:
                            if m[5] == -1:
                                # Static Mesh
                                viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                            else:
                                # AniMesh
                                viewed += RasterPt1(m[0][m[5]][0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))
                                # Call the function for that frame
                                m[0][m[5]][2]()
                                if m[0][m[5]][1] != -1:
                                    m[5] = m[0][m[5]][1]
                    else:
                        # Static Thing
                        for m in t[0]:
                            viewed += RasterPt1Static(m[0], VectorAdd(m[1], t[1]))

        for em in emitters:
            for p in em[0]:
                viewed += RasterPt1(EmitterGetTemplate(em)[0], p[1], p[2])

        viewed.sort(key=sortKey, reverse=sortReverse)
        return RasterPt3(viewed)
    

# RasterMeshList()
# Supply your own list of meshes to draw.

# Usage:
#
# for tri in z3dpy.RasterMeshList([cube]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RasterMeshList(meshList, sortKey=triSortAverage, sortReverse=True):
    try:
        test = intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        viewed = []
        for m in meshList:
            viewed += RasterPt1(m[0], m[1], m[2])
        viewed.sort(key=sortKey, reverse=sortReverse)
        return RasterPt3(viewed)



# Draws things, as well as hitboxes, and any lights/rays you give it. 
# Triangles from debug objects will have an id of -1
def DebugRaster(train=[], sortKey=triSortAverage, sortReverse=True):
    try:
        test = intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCam(yourCamera) before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in GatherThings():
            for m in t[0]:
                viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]))

            if t[3] != []:
                viewed += RasterPt1Static(t[3][4][0], t[1])
        
        viewed.sort(key = sortKey, reverse=sortReverse)

        

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
                viewed += RasterPt2NoPos([[RayGetStart(r) + [[0, 0, 0], [0, 0]], VectorAdd(RayGetStart(r), [0, 0.01, 0]) + [[0, 0, 0], [0, 0]], RayGetEnd(r) + [[0, 0, 0], [0, 0]], (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), -1]])

        if train != []:
            for x in range(len(train)):
                for y in range(len(train[0])):
                    viewed += RasterPt1Static(dotMesh[0], [x, train[x][y], y])

        finished += RasterPt3(viewed)
        return finished

def RasterPt1(tris, pos, rot):
    trg = VectorAdd(pos, RotTo(rot, (0.0, 0.0, 1.0)))
    up = RotTo(rot, (0.0, 1.0, 0.0))
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
        output += TriClipAgainstZ(t)
    return output

def RasterPt2NoPos(tris):
    output = []
    for t in ViewTris(tris):
        output += TriClipAgainstZ(t)
    return output


def RasterPt3(tris):
    output = []
    for i in ProjectTris(tris):
        for s in TriClipAgainstScreenEdges(i):
            output.append(s)
    return output

# Low-Level Raster Functions
# Rastering is based on Javidx9's C++ series, although
# the resemblance might be 
#
# My version has 4 stages: Transform, Translate, View, and Project.
#
# The original triangles are all located relative to 0, 0, 0, according to the OBJ file.
#
# Each frame, each mesh is rotated by it's own matrix around the origin, before being moved to it's position in world space.
# then the triangles are moved to their relative position as if the camera was the one moving/rotating, before being flattened into screen space.
#

#
# Transform takes a list of triangles and rotates them in world space, given the angles.
#
# Translate takes a list of triangles and moves them in world space.
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
        if VectorDoP(VectorMul(nt[3], (-1, 1, 1)), iC[6]) > -0.4:
            nt[4] = TriAverage(nt)
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
    return [TriMatrixMul(tri, intMatV) for tri in tris]

def ViewTri(tri):
    return TriMatrixMul(tri, intMatV)
                    
def ProjectTris(tris):
    return [TriMul(TriAdd(ProjectTri(tri), [1, 1, 0]), [iC[3], iC[2], 1]) for tri in tris]

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

    # Tkinter:

    z3dpy.TkDrawTriRGB(tri, [255, 213, 0], canvas)
    # or
    z3dpy.TkDrawTriRGBF(tri, [1, 0.75, 0], canvas)
    # or
    z3dpy.TkDrawTriS(tri, 0.8, canvas)
    # or
    z3dpy.TkDrawTriFL(tri, canvas)

    # So for example:
    z3dpy.PgDrawTriRGBF(tri, z3dpy.TriGetNormal(tri), screen, pygame)
'''

# Pygame
# Pygame is the fastest at drawing, but installed separately.

def PgDrawTriRGB(tri, colour, surface, pygame):
    ncolour = VectorMaxF(colour, 0)
    ncolour = VectorMinF(ncolour, 255)
    pygame.draw.polygon(surface, ncolour, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

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
    ncolour = VectorMinF(ncolour, 1)
    pygame.draw.lines(surface, VectorMulF(colour, 255), True, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriS(tri, f, surface, pygame):
    f = max(f, 0)
    f = min(f, 1)
    pygame.draw.polygon(surface, VectorMulF(TriGetColour(tri), f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriFL(tri, surface, pygame):
    pygame.draw.polygon(surface, VectorMul(TriGetColour(tri), FlatLighting(tri)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriFLB(tri, surface, pygame):
    pygame.draw.polygon(surface, VectorMul(TriGetColour(tri), FlatLightingBaked(tri)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Tkinter
# Slower, but almost always pre-installed

def TkDraw(tri, fillCol, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=fillCol)

def TkDrawTriRGB(tri, colour, canvas):
    fillCol = RGBToHex(colour)
    TkDraw(tri, fillCol, canvas)

def TkDrawTriRGBF(tri, colour, canvas):
    fillCol = RGBToHex(VectorMulF(colour, 255))
    TkDraw(tri, fillCol, canvas)

def TkDrawTriF(tri, f, canvas):
    f = str(math.floor(max(f, 0) * 100))
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill="gray" + f)

def TkDrawTriOutl(tri, colour, canvas):
    fillCol = RGBToHex(colour)
    TkDraw(tri, fillCol, canvas)

def TkDrawTriS(tri, f, canvas):
    fillCol = RGBToHex(VectorMulF(TriGetColour(tri), f))
    TkDraw(tri, fillCol, canvas)

def TkDrawTriFL(tri, canvas):
    fillCol = RGBToHex(VectorMul(TriGetColour(tri), VectorMinF(FlatLighting(tri), 1)))
    TkDraw(tri, fillCol, canvas)

def TkDrawTriFLB(tri, canvas):
    fillCol = RGBToHex(VectorMulF(TriGetColour(tri), FlatLightingBaked(tri)))
    TkDraw(tri, fillCol, canvas)

# FlatLighting()
# Returns a float indicating how much light the triangle recieves.

# Usage:
#
# for tri in RasterThings(things):
#
#   PgDrawTriS(tri, FlatLighting(tri), screen, pygame)
#
#   TkDrawTriS(tri, FlatLighting(tri), canvas)
#

# Flat lighting shader, meant to be put into DrawTriS's shade
# Takes the direction towards the light and compares that to a corrected normal.
def FlatLighting(tri, lights=lights):
    return CheapLighting(tri, lights)

# CheapLighting takes the direction towards the light source, no shadow checks or anything.
def CheapLighting(tri, lights=lights):
    # Shading is the direction based, Intensity is the distance based.
    shading = 0.0
    colour = (0.0, 0.0, 0.0)
    intensity = 0.0
    nNormal = VectorMul(tri[3], (-1, 1, 1))
    pos = tri[4]
    num = 0
    for l in lights:
        match l[0]:
            case 0:
                dist = DistanceBetweenVectors(pos, l[1])
                if dist <= l[3]:
                    lightDir = DirectionBetweenVectors(l[1], pos)
                    if (dot := VectorDoP(lightDir, nNormal)) > 0:
                        d = dist/l[3]
                        intensity = (1 - (d * d)) * l[2]
                        shading += dot
                        colour = VectorAdd(colour, VectorMulF(l[4], intensity))
                        num += 1
            case 1:
                if (dot := VectorDoP(l[1], nNormal)) > 0:
                    shading += dot
                    intensity = dot * l[2]
                    colour = VectorAdd(colour, VectorMulF(l[4], intensity))
                    num += 1
    if num != 0:
        colour = VectorDivF(colour, num)
    else:
        colour = (0, 0, 0)
    return VectorMax(VectorMinF(VectorMulF(colour, shading), 1.0), worldColour)

# ExpensiveLighting uses the direction towards the light source, and tests for ray collisions to create shadows.
def ExpensiveLighting(tri, shadowcasters=GatherThings(), lights=lights):
    shading = 0.0
    colour = (1.0, 1.0, 1.0)
    intensity = 0.0
    pos = tri[4]
    for l in lights:
        match l[0]:
            case 0:
                dist = DistanceBetweenVectors(pos, l[1])
                if dist <= l[3]:
                    lightDir = DirectionBetweenVectors(l[1], pos)
                    shade = VectorDoP(lightDir, VectorMul(tri[3], (-1, 1, 1)))
                    if shade > 0:
                        testRay = Ray(pos, l[1])

                        # Checking for shadows
                        for th in shadowcasters:
                            inters = RayIntersectThingComplex(testRay, th)
                            if inters[0]:
                                # Making sure it's not this triangle, by comparing normals
                                if not VectorEqual(inters[3], tri[3]):
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

                    for th in shadowcasters:
                        intersection = RayIntersectThingComplex(testRay, th)
                        if intersection[0]:
                            if not VectorEqual(intersection[3], tri[3]):
                                break
                    else:
                        shading += shade
                        intensity += (1 - ((dist / l[3])))

    colour = VectorDivF(colour, len(lights))
    return VectorMax(VectorMinF(VectorMulF(colour, shading), 1.0), worldColour)

## Deprecated
def CheapLightingCalc(tri, lights=lights):
    return CheapLighting(tri, lights)

def ExpensiveLightingCalc(tri, lights=lights):
    return ExpensiveLighting(tri, lights)
##


# BakeLighting() and FlatLightingBaked()

# BakeLighting() saves the FlatLighting() calculation to the triangle's shade value, for cheaply referencing later.
# FlatLightingBaked() retrives a triangle's shade value.

# Usage:
#
# BakeLighting(things)
#
# for tri in RasterThings(things):
#
#   PgDrawTriFLB(tri, screen, pygame)
#
#   or
#
#   TkDrawTriFLB(tri, canvas)
#

def FlatLightingBaked(tri):
    return tri[5]

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shader variable
def BakeLighting(things, expensive=False, lights=lights, shadowcasters=GatherThings()):
    print("Baking Lighting...")
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

# My own filling triangle routines so I can move beyond single-colour flat shading and single-triangle depth sorting.

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
#       pygame.draw.line(screen, (255, 255, 255), sX, sY, eX, eY)
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
                if (lStart, lEnd) not in output:
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
        #for x in range(0, int(diff2) + 1, sign(diff2)):
            #lStart = 
            #lEnd = (x + list[1][0], (fSlope * (x + diff4)) + list[0][1])
            #output.append((lStart, lEnd))
    return [((x + list[1][0], (slope2 * x) + list[1][1]), (x + list[1][0], (fSlope * (x + diff4)) + list[0][1])) for x in range(0, int(diff2) + 1, sign(diff2))]

# TriToPixels()
# Returns a tuple of pixels to draw on the screen, given a triangle.

# Usage:
#
# for tri in Raster():
#   for pixel in TriToPixels(tri):
#       x = pixel[0]
#       y = pixel[1]
#       uv = pixel[2]
#       u = uv[0]
#       v = uv[1]
#

def TriToPixels(tri):
    output = []
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX != 0:
        # x * slope takes a screen X and turns it into a screen Y, along the P1-P3 line
        slope = (list[2][1] - list[0][1]) / diffX

        # multiplied by 0-1 to get a screen X, along the P1-P2 line (normalized, make sure to add back P1's X)
        diff = list[1][0] - list[0][0]

        # If this side's flat, no need.
        if diff != 0:
            diffY = list[1][1] - list[0][1]
            # x * diff3 takes a screen x and results in a screen y, on the P1-P2 line (normalized, make sure to add back P1's Y)
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
# stage is a bool, determines which side of the triangle is being drawn,

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

# Uses Affine texture mapping, which means textures warp
# like a PS1

# Lots of comments because something is broken, and
# so far I haven't found the issue, maybe there's someone who can.
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

            for x in range(int(diff) + 1):

                ranges = [int(diff3 * x + list[0][1]), int(slope * x + list[0][1])]

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
                fX = int(x + list[0][0])

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
                                u = int(abs(u)) % tX
                                v = int(abs(v)) % tY
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

            for x in range(int(diff2) + 1):
                # Repeat the same steps except for this side now.
                ranges = [int(slope2 * x + list[1][1]), int(fSlope * (x + diff) + list[0][1])]

                rangd = ranges[1] - ranges[0]

                if rangd == 0:
                    continue

                sgn = sign(rangd)
                
                nX = x / (diff2 + 1)
                nX2 = (x + diff) / diffX
                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, False)
                fX = int(x + list[1][0])

                for y in range(ranges[0], ranges[1] + sgn, sgn):

                    nY = (y - ranges[0]) / rangd

                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            if pixelArray[fX, y] == 0:
                                fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                                rU = fUVs[0] * tX
                                rV = fUVs[1] * tY
                                u = int(abs(rU)) % tX
                                v = int(abs(rV)) % tY
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

            for x in range(int(diff) + 1):

                range1 = int(diff3 * x + list[0][1])
                range2 = int(slope * x + list[0][1])

                if range2 - range1 == 0:
                    continue

                # Converting x to 0-1
                # Normalized between P1 and P2
                nX = (x / (diff + 1))
                # Normalized between P1 and P3
                nX2 = (x / diffX)

                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, True)

                # Final X coordinate (pre-calculating instead of in the for loop)
                fX = int(x + list[0][0])

                sgn = 1 if range1 < range2 else -1
                for y in range(range1, range2 + sgn, sgn):

                    # Convering y to 0-1
                    nY = (y - range1) / (range2 - range1)
                        
                    # Pixel:
                    # [0] is the screen x, [1] is the screen y, [2] is the UV
                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                            rU = int(fUVs[0] * tX)
                            rV = int(fUVs[1] * tY)
                            u = int(abs(rU)) % tX
                            v = int(abs(rV)) % tY
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

            for x in range(int(diff2) + 1):
                # Repeat the same steps except for this side now.
                range1 = int(slope2 * x + list[1][1])
                range2 = int(fSlope * (x + diff) + list[0][1])

                if range2 - range1 == 0:
                    continue
                
                nX = x / (diff2 + 1)
                nX2 = (x + diff) / diffX
                UVs = UVCalcPt1(uv1, uv2, uv3, nX, nX2, False)
                fX = int(x + list[1][0])

                sgn = 1 if range1 < range2 else -1

                for y in range(range1, range2 + sgn, sgn):

                    nY = (y - range1) / (range2 - range1)

                    if fX > 0 and fX < screenSize[0]:
                        if y > 0 and y < screenSize[1]:
                            fUVs = UVCalcPt2(nY, UVs[0], UVs[1], UVs[2], UVs[3])
                            rU = int(fUVs[0] * tX)
                            rV = int(fUVs[1] * tY)
                            u = int(abs(rU)) % tX
                            v = int(abs(rV)) % tY
                            colour = texture[u][v]
                            if colour[3]:
                                canvas.create_line(fX, y, fX + 1, y, fill=RGBToHex(colour))

#==========================================================================
#  
# Projection Functions
#
#==========================================================================

def Projection(vector):
    vector += [[], []]
    if vector[2] != 0:
        # 
        return [(vector[0] * howX) / vector[2], (vector[1] * howY) / vector[2], 1, vector[3], vector[4]]
    return vector
        
def ProjectTri(t):
    return [Projection(t[0]), Projection(t[1]), Projection(t[2]), t[3], t[4], t[5], t[6], t[7]]

def RGBToHex(vector):
    def intToHex(int):
        return hex(max(int, 0))[2:].ljust(2, "0")
    return "#" + intToHex(int(vector[0])) + intToHex(int(vector[1])) + intToHex(int(vector[2]))

#==========================================================================
#  
# Calculating How Projection
#
#==========================================================================

# Wrote code to brute-force finding a single multiplier that could do most of
# the projection.
# I call it: How-Does-That-Even-Work Projection

# Instead of a matrix, it's now [(X * howX) / Z, (Y * howY) / Z, 1]

# I've already calculated the constants for an FOV of 90, at 16:9: 
# To recalculate, use FindHowVars(fFov). It's quite speedy now, but nevertheless 
# should be done once at the start.

howX = 0.56249968159
howY = 1.0

# Optional aspect ratio argument: put height over width as a fraction, so for 16:9 
# put in 9/16, 4:3 is 3/4, 21:9 is 9/21, and so on.
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
        rY = fullGraph[x]
        aY = SimpleFormula(x, m)
        # More difference is bad.
        score += abs(rY - aY)
    return score

calc = True

# Calculating Camera Variables
# Starts at 1, then randomly guesses to find a better and better solution.

# What it's really doing is taking the full projection formula, and graphing it,
# then trying to replicate that graph as closely as possible with m * x
#
# Written as a brute-forcer because it's meant to find a constant for any formula

def CalculateCam(foV, farClip, aspectRatio):
    print("")
    print("Calculating Camera Constants")
    print("")
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
        aiM = 1
        calc = True
        while calc:
            match z:
                case 0:
                    Score = Compare(aiM, fullXGraph)
                case 1:
                    Score = Compare(aiM, fullYGraph)
            if Score < currentScore:
                bestM = aiM
                currentScore = Score
            else:
                noImp += 1
                aiM = bestM
            if noImp > 50:
                srchRad /= 2
                noImp = 0
            if srchRad < 0.00001:
                calc = False
                finished.append(bestM)
            aiM = bestM + ((rand.random() - 0.5) * srchRad)
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
myMesh = z3dpy.LoadMesh("mesh/template.obj")

# Emitter(vPos, mshTemplate, iMax, vVelocity, fLifetime, vGravity)
myEmitter = z3dpy.Emitter([1.0, 2.0, 3.0], myMesh, 150, [5.0, 0.0, 0.0], 15.0, [0.0, 9.8, 0.0])

# Now, from here you can append to the internal list, or put your own list in.

z3dpy.emitters.append(myEmitter)

# then, during the draw loop...

z3dpy.HandleEmitters()

# or

z3dpy.HandleEmitters([myEmitter])

'''

def HandleEmitters(emitters=emitters):
    for em in emitters:
        for p in range(len(em[0])):
            if p == len(em[0]):
                break
            pt = em[0][p]
            pt[0] -= delta
            if pt[0] <= 0:
                # Removal from list
                em[0] = em[0][:p] + em[0][p+1:]
                # Accounting for the removal
                p -= 1
                continue
            # Basic version of physics for particles
            pt[2] = VectorMul(pt[2], [airDrag * sign(pt[2][0]), airDrag * sign(pt[2][1]), airDrag * sign(pt[2][2])])
            pt[2] = VectorAdd(pt[2], VectorMulF(VectorMulF(EmitterGetGravity(em), 5), delta))
            pt[1] = VectorAdd(VectorMulF(pt[2], delta), pt[1])
        if em[6]:
            if len(em[0]) < EmitterGetMax(em):
                em[0] = em[0] + (Part(EmitterGetPos(em), EmitterGetVelocity(em), EmitterGetLifetime(em)),)

## Deprecated
def TickEmitters(emitters=emitters):
    HandleEmitters(emitters)
##

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