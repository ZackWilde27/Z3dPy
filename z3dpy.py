# -zw

# Z3dPy v0.2.0

# Change Notes:
#
# TRIANGLES or should I say TRIS
#
# - Renamed all functions with Triangle or Triangles to Tri or Tris. PgDrawTriF(), TransformTris(), and TriAdd() just to name a few.
#
# - Fixed bug where tris sometimes had extra or missing components.
#
# RENDERING
#
# - Added Raster(). It doesn't require any arguments since it uses the global things list (see THINGS section).
#
# - Changed DebugRasterThings() to DebugRaster(), and it uses the global things list, like Raster()
#
# - Removed RasterThingsStatic() because RasterThings() will automatically decide based on isMovable
#
# - Tweaked raster functions for optimization. Functionality is still the same.
#
# - PgPixelShader no longer needs a buffer array.
#
# - Experimental: PgPixelShader now does textures... sort of. I'm still working on it.
#
# LIGHTING
#
# - Fixed lighting bug when moving things away from origin
#
# - Added LightSetPosX(light, x), LightSetPosY(light, y), LightSetPosZ(light, z), and LightAddPos(light, vector)
#
# - Added DrawTriFL(tri, surface, pygame) and DrawTriFLB(tri, surface, pygame) so flat-lit triangles can be rendered just like RGB, F and S.
#
# THINGS
#
# - Added global things list, and functions to go along with it: AddThing(thing) and RemoveThing(thing)
#
# - ThingSetupHitbox now has optional arguments for setting hitbox parameters
#
# - Rotations are different
#
# PHYSICS
#
# - Physics now uses bounciness: When a physics thing hits the ground or a non-physics thing, the strongest velocity direction is inverted
# with the new magnitude determined by bounciness.
#
# - Drag is now a global variable: airDrag. Representing air resistance.
#
# OBJECTS
#
# - LoadMesh()'s x, y, and z are now optional, since they would usually be left at 0 when combining into things.
#
# - Added CameraGetPosX(camera), CameraGetPosY(camera), and CameraGetPosZ(camera)
#
# - Some objects now have a dedicated user variable. Due to the loose nature of python, this user variable can be any type (int by default).
#
# MISC
#
# - Added prefix letters to function parameters to denote the type of variable expected.
# Integers start with i, floats start with f, lists start with an l, and so on. Capital letters mean normalized, for floats and vectors and stuff.
#
# - Updated WhatIs() and WhatIsInt() to reflect changes to objects, functionality is still the same.
#
# - Added more documentation in the comments.
#

import math
import random as rand
import time

print("Z3dPy v0.2.0")

#==========================================================================
#  
# Variables
#
#==========================================================================


# You can reference these at any time to get a global axis.
globalX = (1, 0, 0)
globalY = (0, 1, 0)
globalZ = (0, 0, 1)

physTime = time.time()

gravityDir = [0, 9.8, 0]

airDrag = 0.02

# Internal list of lights, for both FlatLighting(), and DebugRaster()
lights = []

# Global Things List

things = []

def AddThing(thing):
    # Setting the internal id to the length of the list, which
    # corrosponds to it's index
    thing[6] = len(things)
    things.append(thing)

# Made so that if there's only one thing in the list, you don't need an argument.
def RemoveThing(thing=[]):
    global things
    if len(things) == 1:
        things = []
        return
    dex = thing[6]
    things = things[:dex] + things[dex + 1:]

# Global list of rays for drawing with DebugRaster()
rays = []

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
# [3] is W

def Vector4(x, y, z, w):
    return [x, y, z, w]

# VectorUV:
# Complicated Vectors for rendering.
# [0] - [2] are the x y and z, [3] is normal, [4] is UV

def VectorUV(x, y, z):
    return [x, y, z, [0, 0, 0], [0, 0]]

# Triangles:
#[0] - [2] are the 3 points, [3] is the normal, [4] is the center point in world space, [5] is the baked shade, [6] is colour (added during rastering), ,
# and [7] is Id (added during rastering)

def Tri(vector1, vector2, vector3):
    return [vector1, vector2, vector3, GetNormal([vector1, vector2, vector3]), TriAverage([vector1, vector2, vector3]), 0.0]

# Meshes:
# [0] is the tuple of triangles, [1] is the position, [2] is the rotation, [3] is the colour, [4] is the id, and [5] is the user variable

def Mesh(tris, x, y, z):
    return [tris, [x, y, z], [0, 0, 0], (255, 255, 255), 0, 0]

# Some stuff I need to declare before the Thing class

# Hitbox Object:
#
# Stores all the needed info regarding collisions, the type of hitbox, it's scale, and collision id.
# Only hitboxes with the same collision id will collide.
#
# [0] is type, [1] is id, [2] is radius, [3] is height, [4] is hitbox mesh for drawing.
#
# Enable collisions with myThing[4] = z3dpy.Hitbox()

def Hitbox(type = 2, id = 0, radius = 1, height = 1):
    return [type, id, radius, height, LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, radius, height, radius)]

# Physics Body:
#
# Enable physics with myThing[6] = z3dpy.PhysicsBody()
#
# [0] is velocity, [1] is acceleration, [2] is mass, [3] is friction, [4] is bounciness
#
# Mass does not have to be 0-1, but I've found small values work better.
#
# Friction controls how quickly the velocity falls off when hitting the ground. Also, when other
# things collide, their new velocity scales by the friction.
#
# Bounciness is supposed to be 0-1, 1 means it'll bounce with no loss of speed, 0 means it won't bounce.
# this applies when hitting the ground, or hitting things that don't have physics.
#
# Drag is now a global variable, representing general air resistance.

def PhysicsBody():
    return [[0, 0, 0], [0, 0, 0], 0.2, 0.2, 0.5]

# Things:
#
# The Thing is what you would typically refer to as an object, it has a collection of meshes, and collision data.
#
#
# [0] is the list of meshes, [1] is position, [2] is rotation, [3] is hitbox, [4] is physics body, and [5] is isMovable, [6] is internal id, and [7] is user variable.
#
# Hitbox and Physics body are empty till you assign them.
# Internal id should not be changed, it's for storing the index in the global things list.

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], [], [], True, 0, 0]

# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
#
# For a third person camera, use CameraSetTargetLocation()
# For a first person camera, use CameraSetTargetVector()
#
# To change the FOV, call FindHowVars(fov)

# [0] is position, [1] is rotation, [2] is screenHeight, [3] is screenWidth, [4] is near clip, [5] is far clip
# [6] is target location, and [7] is up vector, [8] is user variable

def Camera(x, y, z, iScrW, iScrH):
    return [[x, y, z], [0, 0, 0], iScrH, iScrW, 0.1, 1500, [0, 0, 1], [0, 1, 0], 0]

# Lights:
#
# Point lights will light up triangles that are inside the radius and facing towards it's location
#
# Used for the FlatLighting() shader, which outputs a colour to be plugged into DrawTriangleS() or DrawTriangleF()
#

# [0] is position, [1] is strength, [2] is radius, [3] is colour, and [4] is user variable

def Light_Point(x, y, z, FStrength, fRadius, vColour=(255, 255, 255)):
    return [[x, y, z], FStrength, fRadius, vColour, 0]

# Rays:
#
# Used for drawing rays to the screen.
#
# [0] is ray start location, [1] is ray end location

def Ray(raySt, rayNd):
    return [raySt, rayNd]

# Textures:
#
# Textures are a matrix/list of lists, to form a grid of colours.

# Pixels can be accessed or changed with myTexture[x][y].

def TestTexture():
    # A red and blue 2x2 checker texture
    return (((255, 0, 0), (0, 0, 255)), ((0, 0, 255), (255, 0, 0)))

#==========================================================================
#
# Object Functions
#
# Everything is a list, so these functions are human-friendly ways to set and retrieve variables
#
#==========================================================================

# The majority of these functions have no speed cost.

# TRIANGLES

# TriGetNormal() will return the current normal, while GetNormal() will calculate a new one.
def TriGetNormal(tri):
    return tri[3]

# Normals are automatically calculated during the raster process, and by default will be the world space normal.
def TriSetNormal(tri, vector):
    tri[3] = vector

def TriGetColour(tri):
    return tri[6]

# Colour is automatically calculated during the raster process, and by default will be the colour of the associated mesh.
def TriSetColour(tri, vColour):
    tri[6] = vColour

def TriGetWPos(tri):
    return tri[4]

# World position is automatically calculated during the raster process, and by default will be the center point of the triangle in world space.
def TriSetWPos(tri, vector):
    tri[4] = vector

def TriGetShade(tri):
    return tri[5]

def TriSetShade(tri, FShade):
    tri[5] = FShade

def TriGetId(tri):
    return tri[7]

# Id is automatically calculated during the raster process, and by default will be the id of the associated mesh.
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

def MeshGetColour(mesh):
    return mesh[3]

def MeshSetId(mesh, iId):
    mesh[4] = iId

def MeshGetId(mesh):
    return mesh[4]



# THINGS


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

# Object Id is meant for the draw loop, so you can check a triangle's id to see what mesh it came from.

def ThingSetupHitbox(thing, iType = 2, iId = 0, fRadius = 1, fHeight = 1):
    thing[3] = Hitbox(iType, iId, fRadius, fHeight)

# ThingSetCollision() will set the collision data and update the hitbox mesh.
# Type: 0 = Sphere, 1 = Cylinder, 2 = Cube
# Radius: radius of the sphere/cylinder, or length of the cube
# Height: height of the cylinder/cube.
# Id: Objects with the same ID will check for collisions. Everything is 0 by default, so if unsure, use that.

def ThingSetCollision(thing, iType, iId, fRadius, fHeight):
        thing[3][2] = fRadius
        thing[3][3] = fHeight
        thing[3][0] = iType
        thing[3][1] = iId
        match type:
            case 0:
                thing[3][4] = LoadMesh("z3dpy/mesh/sphere.obj", 0, 0, 0, fRadius, fRadius, fRadius)
            case 1:
                thing[3][4] = LoadMesh("z3dpy/mesh/cylinder.obj", 0, 0, 0, fRadius, fHeight, fRadius)
            case 2:
                thing[3][4] = LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, fRadius, fHeight, fRadius)

def ThingGetHitboxMesh(thing):
    if thing[3] != []:
        return thing[3][4]
    return []

def ThingGetHitboxHeight(thing):
    if thing[3] != []:
        return thing[3][3]
    return -1

def ThingGetHitboxRadius(thing):
    if thing[3] != []:
        return thing[3][2]
    return -1

def ThingGetHitboxId(thing):
    if thing[3] != []:
        return thing[3][1]
    return -1

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


# CAMERAS


def CameraSetPosX(cam, x):
    cam[0] = [x, cam[0][1], cam[0][2]]

def CameraSetPosY(cam, y):
    cam[0] = [cam[0][0], y, cam[0][2]]

def CameraSetPosZ(cam, z):
    cam[0] = [cam[0][0], cam[0][1], z]

def CameraSetPos(cam, vector):
    cam[0] = vector

def CameraAddPos(cam, vector):
    cam[0] = VectorAdd(cam[0], vector)

def CameraSubPos(cam, vector):
    cam[0] = VectorSub(cam[0], vector)

def CameraMulPos(cam, vector):
    cam[0] = VectorMul(cam[0], vector)

def CameraDivPos(cam, x, y, z):
    cam[0] = [cam[0][0] / x, cam[0][1] / y, cam[0][2] / z]

def CameraDivPosF(cam, f):
    cam[0] = VectorDivF(cam[0], f)

def CameraGetPos(cam):
    return cam[0]

def CameraGetPosX(cam):
    return cam[0][0]

def CameraGetPosY(cam):
    return cam[0][1]

def CameraGetPosZ(cam):
    return cam[0][2]

def CameraGetPitch(cam):
    return cam[1][0]

def CameraGetRoll(cam):
    return cam[1][2]

def CameraGetYaw(cam):
    return cam[1][1]

def CameraSetPitch(cam, deg):
    cam[1][0] = deg

def CameraSetRoll(cam, deg):
    cam[1][2] = deg

def CameraSetYaw(cam, deg):
    cam[1][1] = deg

def CameraSetRot(cam, vector):
    cam[1] = vector

def CameraAddRot(cam, v):
    cam[1] = VectorAdd(cam[1], v)

def CameraSubRot(cam, v):
    cam[1] = VectorSub(cam[1], v)

def CameraMulRot(cam, v):
    cam[1] = VectorMul(cam[1], v)

def CameraDivRot(cam, v):
    cam[1] = [cam[1][0] / v[0], cam[1][1] / v[1], cam[1][2] / v[2]]

def CameraDivRotF(cam, v):
    cam[1] = VectorDivF(cam[1], v)

def CameraGetRot(cam):
    return cam[1]

def CameraSetScH(cam, h):
    cam[2] = h

def CameraGetScH(cam):
    return cam[2]

def CameraSetScW(cam, w):
    cam[3] = w

def CameraGetScW(cam):
    return cam[3]

def CameraSetNCl(cam, nc):
    cam[4] = nc

def CameraGetNCl(cam):
    return cam[4]

def CameraSetFCl(cam, fc):
    cam[5] = fc

def CameraGetFCl(cam):
    return cam[5]

# Backwards Compatibility / Direction is easier to understand
def CameraSetTargetDirection(cam, vector):
    CameraSetTargetVector(cam, vector)
def CameraGetTargetDirection(cam):
    return CameraGetTargetVector(cam)

def CameraSetTargetLocation(cam, vector):
    cam[6] = vector

def CameraSetTargetVector(cam, vector):
    cam[6] = VectorAdd(cam[0], VectorNormalize(vector))

# SetTargetFP: Takes care of rotating vectors based on camera's rotation.
def CameraSetTargetFP(cam):
    dir = VectorRotateX([0, 0, 1], CameraGetPitch(cam))
    dir = VectorRotateY(dir, CameraGetYaw(cam))
    CameraSetTargetVector(cam, dir)

def CameraGetTargetLocation(cam):
    return cam[6]

def CameraGetTargetVector(cam):
    return VectorNormalize(VectorSub(cam[6], cam[0]))

def CameraSetUpVector(cam, vector):
    cam[7] = vector

def CameraGetUpVector(cam):
    return cam[7]

def CameraGetRightVector(cam):
    return VectorCrP(CameraGetTargetVector(cam), cam[7])

def CameraGetUserVar(cam):
    return cam[8]

def CameraSetUserVar(cam, any):
    cam[8] = any


# LIGHTS


def LightGetPos(light):
    return light[0]

def LightSetPos(light, vector):
    light[0] = vector

def LightSetPosX(light, x):
    light[0] = [x, light[0][1], light[0][2]]

def LightSetPosY(light, y):
    light[0] = [light[0][0], y, light[0][2]]

def LightSetPosZ(light, z):
    light[0] = [light[0][0], light[0][1], z]

def LightAddPos(light, vector):
    light[0] = VectorAdd(light[0], vector)

def LightGetStrength(light):
    return light[1]

def LightSetStrength(light, str):
    light[1] = str

def LightGetRadius(light):
    return light[2]

def LightSetRadius(light, radius):
    light[2] = radius

def LightSetUserVar(light, any):
    light[3] = any

def LightGetUserVar(light):
    return light[3]


# RAYS


def RayGetStart(ray):
    return ray[0]

def RaySetStart(ray, vector):
    ray[0] = vector

def RayGetDirection(ray):
    return VectorNormalize(VectorSub(ray[1], ray[0]))

def RayGetEnd(ray):
    return ray[1]

def RaySetEnd(ray, vector):
    ray[1] = vector

#==========================================================================
#  
# Misc Functions
#
#==========================================================================

# WhatIs()
# Takes a list and figures out what "object" it is.
# meant to be used with print() for debugging. Speed was not a priority

# Usage:
#
# print(WhatIs(hopefullyATriangle))
#

def WhatIs(any):
    try:
        test = len(any)
    except:
        return str(type(any))
    else:
        match len(any):
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
                        return "Unknown"
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
                        test = any[2][0] + 1
                        return "Triangle"
                    except:
                        try:
                            test = any[4][2]
                            return "VectorUV"
                        except:
                            return "Light_Point"
            case 6:
                return "Mesh"
            case 8:
                return "Thing"
            case 9:
                return "Camera"
            
# WhatIsInt():
# Same as WhatIs(), except instead of a string it's a number
# -1 is Unknown
# 0 is Vector
# 1 is Vector2
# 2 is Vector4
# 3 is VectorUV
# 4 is Triangle
# 5 is STriangle
# 6 is Mesh
# 7 is Ray
# 8 is Light_Point
# 9 is Thing
# 10 is Hitbox
# 11 is PhysicsBody
# 12 is Camera
            
def WhatIsInt(any):
    try:
        test = len(any)
    except:
        return -1
    else:
        match len(any):
            case 2:
                try:
                    test = any[0][0]
                    return 7
                except:
                    return 1
            case 3:
                try:
                    test = any[0] + 1
                    return 0
                except:
                    try:
                        test = any[0][0] + 1
                        # S for shortened triangle, it only includes the points, and no other information.
                        return 5
                    except:
                        return -1
            case 4:
                try:
                    test = any[0][0]
                    return 11
                except:
                    return 2
            case 5:
                try:
                    test = any[4][0][0]
                    return 10
                except:
                    try:
                        test = any[2][0] + 1
                        return 4
                    except:
                        try:
                            test = any[4][2]
                            return 3
                        except:
                            return 8
            case 6:
                return 6
            case 8:
                return 9
            case 9:
                return 12

def Projection(vector, a, f, fc, nc):
    # At the start I went the full formula route instead of matrix form, and
    # I kept it because it works.
    q = fc / (fc - nc)
    if vector[2] != 0:
        return [(a * f * vector[0]) / vector[2], (f * vector[1]) / vector[2], (q * vector[2]) - (q * nc), vector[3], vector[4]]
    else:
        return vector

# Wrote a script to brute-force finding a single multiplier that could do most of the projection.
# I call it: How-Does-That-Even-Work Projection

# I've already calculated the constants for an FOV of 90: 
# To recalculate, use FindHowVars(). Although it's VERY slow, so do this once at the start.
howX = 1.0975459978374298
howY = 0.6173470654658898

def HowProjection(vector):
    vector += [[], []]
    # Assumes 16/9 aspect ratio, because of this 3.
    return [(vector[0] * howX) / (vector[2] * 3), (vector[1] * howY) / vector[2], vector[2], vector[3], vector[4]]

def ProjectTri(t, a, f, fc, nc):
    return [Projection(t[0], a, f, fc, nc), Projection(t[1], a, f, fc, nc), Projection(t[2], a, f, fc, nc), t[3], t[4], t[5]]
        
def HowProjectTri(t):
    return [HowProjection(t[0]), HowProjection(t[1]), HowProjection(t[2]), t[3], t[4], t[5]]

def RGBToHex(vector):
    def floatToHex(flt):
        return hex(flt)[2:].ljust(2, "0")
    return "#" + floatToHex(vector[0]) + floatToHex(vector[1]) + floatToHex(vector[2])

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

def VectorMod(v, f):
    return [v[0] % f, v[1] % f, v[2] % f]

def VectorNormalize(v):
    l = abs(VectorGetLength(v))
    if l != 0:
        return [v[0] / l, v[1] / l, v[2] / l]
    return [v[0], v[1], v[2]]

def VectorMinF(v, f):
    return [min(v[0], f), min(v[1], f), min(v[2], f)]

def VectorMaxF(v, f):
    return [max(v[0], f), max(v[1], f), max(v[2], f)]

# Vector Compare returns wether or not v1 is greater than v2
def VectorCompare(v1, v2):
    vO = VectorABS(v1)
    vT = VectorABS(v2)
    return vO[0] + vO[1] + vO[2] > vT[0] + vT[1] + vT[2]
    
def VectorMin(v1, v2):
    if VectorCompare(v1, v2):
        return v2
    else:
        return v1
    
def VectorMax(v1, v2):
    if VectorCompare(v1, v2):
        return v1
    else:
        return v2
    
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
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def VectorEqual(v1, v2):
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def DistanceBetweenVectors(v1, v2):
    output = ((v2[0] - v1[0]) ** 2) + ((v2[1] - v1[1]) ** 2) + ((v2[2] - v1[2]) ** 2)
    return math.sqrt(output)

def VectorNegate(v):
    return [v[0] * -1, v[1] * -1, v[2] * -1]

def VectorABS(v):
    return [abs(v[0]), abs(v[1]), abs(v[2])]

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))

# Give it a vector and it'll return a vector where the strongest axis is 1 and the others are 0
def VectorPureDirection(v):
    output = []
    for axis in VectorNormalize(v):
        output.append(1.0 if axis == 1.0 else 0.0)
    return output

def VectorRotateX(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return Vec3MatrixMul(vec, MatrixMakeRotZ(deg))


#==========================================================================
#  
# Triangle Functions
#
#==========================================================================


def TriAdd(t, v):
    return [VectorUVAdd(t[0], v), VectorUVAdd(t[1], v), VectorUVAdd(t[2], v), t[3], t[4], t[5]]

def TriSub(t, v):
    return [VectorUVSub(t[0], v), VectorUVSub(t[1], v), VectorUVSub(t[2], v), t[3], t[4], t[5]]

def TriMul(t, v):
    return [VectorUVMul(t[0], v), VectorUVMul(t[1], v), VectorUVMul(t[2], v), t[3], t[4], t[5]]

def TriMulF(t, f):
    return [VectorUVMulF(t[0], f), VectorUVMulF(t[1], f), VectorUVMulF(t[2], f), t[3], t[4], t[5]]

def TriDivF(t, f):
    return [VectorUVDivF(t[0], f), VectorUVDivF(t[1], f), VectorUVDivF(t[2], f), t[3], t[4], t[5]]

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
    n = VectorNormalize(point)
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
        if len(tri) == 6:
            return [tri]
        else:
            return [tri[:-2]]

    if len(insideP) == 1 and len(outsideP) == 2:
        outT = [insideP[0], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[1]), VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri[3], tri[4], tri[5]]
        return [outT]

    if len(insideP) == 2 and len(outsideP) == 1:
        outT1 = [insideP[0], insideP[1], VectorIntersectPlane(pPos, pNrm, insideP[1], outsideP[0]), tri[3], tri[4], tri[5]]
        outT2 = [insideP[0], outT1[2], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri[3], tri[4], tri[5]]
        return [outT1, outT2]

def GetNormal(tri):
    triLine1 = VectorSub(tri[1], tri[0])
    triLine2 = VectorSub(tri[2], tri[0])
    normal = VectorCrP(triLine1, triLine2)
    return VectorNormalize(VectorMul(normal, [1, -1, -1]))

def TriAverage(tri):
    return Vector((tri[0][0] + tri[1][0] + tri[2][0]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.333333, (tri[0][1] + tri[1][1] + tri[2][1]) * 0.33333)


# Triangle Sorting functions
def triSortAverage(n):
    return (n[0][2] + n[1][2] + n[2][2]) * 0.3333333

def triSortFurthest(n):
    return max(n[0][2], n[1][2], n[2][2])

def triSortClosest(n):
    return min(n[0][2], n[1][2], n[2][2])


def TriClipAgainstZ(tri):
    return TriClipAgainstPlane(tri, [0, 0, iC[6]], [0, 0, 1])

def TriClipAgainstScreenEdges(tri):
    output = []
    for t in TriClipAgainstPlane(tri, [0, 0, 0], [0, 1, 0]):
        for r in TriClipAgainstPlane(t, [0, iC[2] - 1, 0], [0, -1, 0]):
            for i in TriClipAgainstPlane(r, [0, 0, 0], [1, 0, 0]):
                for s in TriClipAgainstPlane(i, [iC[3] - 1, 0, 0], [-1, 0, 0]):
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
    currentLine = ""
    scaped = True
    output = []
    triangles = []

    while scaped:
        currentLine = file.readline()
        if currentLine == '':
            scaped = False
            break
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
                    triangles.append([int(currentLine[points[0]]) - 1, int(currentLine[points[1]]) - 1, int(currentLine[points[2]]) - 1])
                    points = [points[0], points[2]]
    for v in verts:
        v[3] = VectorDivF(v[3], v[5])
    for tr in triangles:
        nt = Tri(verts[tr[0]], verts[tr[1]], verts[tr[2]])
        output.append(nt)
    file.close()
    return Mesh(tuple(output), x, y, z)

def LoadAnimMesh(filename, x=0, y=0, z=0, sclX=1, sclY=1, sclZ=1):
    meshes = []
    # Calculating how many frames
    looking = True
    a = 1
    while looking:
        try:
            test = open(filename[:-4] + str(a) + ".obj", 'r')
        except:
            a -= 1
            looking = False
        else:
            test.close()
            a += 1
    print("Frames: " + str(a))
    for f in range(0, a):
        meshes.append(LoadMesh(filename[:-4] + str(f) + ".obj", x, y, z, sclX, sclY, sclZ))
    return meshes

lightMesh = LoadMesh("z3dpy/mesh/light.obj", 0, 0, 0)

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


#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def TriMatrixMul(t, m):
    return [VecMatrixMul(t[0], m), VecMatrixMul(t[1], m), VecMatrixMul(t[2], m), t[3], t[4], t[5]]

def VecMatrixMul(v, m):
    output = Vec3MatrixMulOneLine(v, m)
    output.pop()
    return output + [v[3], v[4]]

def Vec3MatrixMul(v, m):
    output = [0.0, 0.0, 0.0, 0.0]
    for i in range(0, 3):
        output[0] += v[i] * m[i][0]
        output[1] += v[i] * m[i][1]
        output[2] += v[i] * m[i][2]
        output[3] += v[i] * m[i][3]
    output[0] += m[3][0]
    output[1] += m[3][1]
    output[2] += m[3][2]
    output[3] += m[3][3]
    return output

def Vec3MatrixMulOneLine(v, m):
    return [v[0] * m[0][0] + v[1] * m[1][0] + v[2] * m[2][0] + m[3][0], v[0] * m[0][1] + v[1] * m[1][1] + v[2] * m[2][1] + m[3][1], v[0] * m[0][2] + v[1] * m[1][2] + v[2] * m[2][2] + m[3][2], v[0] * m[0][3] + v[1] * m[1][3] + v[2] * m[2][3] + m[3][3]]

def MatrixMatrixMul(m1, m2):
    output = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for c in range(0, 3):
        for r in range(0, 3):
            output[r][c] = m1[r][0] * m2[0][c] + m1[r][1] * m2[1][c] + m1[r][2] * m2[2][c] + m1[r][3] * m2[3][c]
    return output

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
    rad = math.radians(deg)
    return [[1, 0, 0, 0], [0, math.cos(rad), math.sin(rad), 0], [0, -math.sin(rad), math.cos(rad), 0], [0, 0, 0, 1]]


def MatrixMakeRotY(deg):
    rad = math.radians(deg)
    return [[math.cos(rad), 0, math.sin(rad), 0], [0, 1, 0, 0], [-math.sin(rad), 0, math.cos(rad), 0], [0, 0, 0, 1]]

def MatrixMakeRotZ(deg):
    rad = math.radians(deg)
    return [[math.cos(rad), math.sin(rad), 0, 0], [-math.sin(rad), math.cos(rad), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

# Here me out:
# Pre-Making Rotation Matrixes

matRotX = []
matRotY = []
matRotZ = []

for deg in range(0, 360):
    matRotX.append(MatrixMakeRotX(deg))
    matRotY.append(MatrixMakeRotY(deg))
    matRotZ.append(MatrixMakeRotZ(deg))


matRotX = tuple(matRotX)
matRotY = tuple(matRotY)
matRotZ = tuple(matRotZ)

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[2][1], temp[2][2], 0), (temp[1][0], temp[1][1], temp[1][2], 0), (temp[0][0], temp[0][1], temp[0][2], 0), (pos[0], pos[1], pos[2], 1))

def LookAtMatrix(camera):
    temp = MatrixStuff(CameraGetPos(camera), CameraGetTargetLocation(camera), CameraGetUpVector(camera))
    return ((temp[2][0], temp[1][0], temp[0][0], 0), (temp[2][1], temp[1][1], temp[0][1], 0), (temp[2][2], temp[1][2], temp[0][2], 0), (-VectorDoP(CameraGetPos(camera), temp[2]), -VectorDoP(CameraGetPos(camera), temp[1]), -VectorDoP(CameraGetPos(camera), temp[0]), 1))

def MatrixMakeProjection(fov):
    a = iC[2] / iC[3]
    f = fov * 0.5
    f = math.tan(f)
    return [[a * f, 0, 0, 0], [0, f, 0, 0], [0, 0, iC[7] / (iC[7] - iC[6]), 1], [0, 0, (-iC[7] * iC[6]) / (iC[7] - iC[6]), 0]]


#==========================================================================
#  
# Ray Functions
#
#==========================================================================


def RayIntersectTri(ray, tri):
    # Using the Moller Trumbore algorithm
    if len(rays) < 100:
        rays.append(ray)
    rayDr = RayGetDirection(ray)
    raySt = RayGetStart(ray)

    e1 = VectorSub(tri[1], tri[0])
    e2 = VectorSub(tri[2], tri[0])
    o = VectorSub(raySt, tri[0])
    h = VectorCrP(o, rayDr)
    
    d = -VectorDoP(rayDr, Tri(tri))
    f = 1 / d

    ds = VectorDoP(o, Tri(tri)) * f
    u = VectorDoP(e2, h) * f
    v = -VectorDoP(e1, h) * f
    q = 1 - u - v
    
    if d >= 0.00001 and ds >= 0 and u >= 0 and v >= 0 and q >= 0:
        # Hit
        #
        # [0] is wether or not it hit
        #
        # [1] is location
        #
        # [2] is distance
        #
        Hit = [True, VectorAdd(raySt, VectorMulF(rayDr, ds)), ds]
        return Hit
        
    else:
        return [False]

def RayIntersectMesh(ray, mesh):
    for t in mesh[0]:
        hit = RayIntersectTri(ray, t)
        if hit[0]:
            return hit
    return [False]

# Does a ray intersection test with the hitbox
def RayIntersectThingSimple(ray, thing):
    for t in thing[4][0]:
        hit = RayIntersectMesh(ray, t)
        if hit[0]:
            return hit
    return [False]

# Does a ray intersection test with each triangle
def RayIntersectThingComplex(ray, thing):
    for m in thing[0]:
        for t in TranslateTris(TransformTris(MeshGetTris(m), VectorAdd(MeshGetRot(m), ThingGetRot(thing))), VectorAdd(MeshGetPos(m), ThingGetPos(thing))):
            inrts = RayIntersectTri(ray, t)
            if inrts[0]:
                return inrts
    return [False]

# Internal Camera
#
# the internal camera used for rendering. 
# Set the internal camera to one of your cameras when you want to render from it.
#
# [0] is location, [1] is rotation, [2] is screen height, [3] is screen width, [4] is screen width / 2, [5] is screen height / 2
# [6] is near clip, [7] is far clip, [8] is target vector, [9] is up vector
#

iC = [[0, 0, 0], [0, 0, 0], 720, 1280, 360, 640, 0.1, 1500, [0, 0, 1], [0, 1, 0]]

intMatV = []
intMatP = []

def SetInternalCamera(camera):
    global intMatV
    global intMatP
    global iC
    iC = [CameraGetPos(camera), CameraGetRot(camera), CameraGetScH(camera), CameraGetScW(camera), CameraGetScH(camera) * 0.5, CameraGetScW(camera) * 0.5, CameraGetNCl(camera), CameraGetFCl(camera), CameraGetTargetVector(camera), CameraGetUpVector(camera)]
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intMatV = LookAtMatrix(camera)

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
        if thingList[me][4] != []:
            for thm in range(0, len(thingList)):
                if thingList[thm][4] != []:

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
                                    case 1:
                                        # Cylinder
                                        # The distance is measured with no vertical in mind, and a check to make sure it's within height
                                        if abs(thPos[2] - myPos[2]) <= ThingGetHitboxHeight(thingList[thm]):
                                            if DistanceBetweenVectors(Vector(myPos[0], 0, myPos[2]), Vector(thPos[0], 0, thPos[2])) < ThingGetHitboxRadius(thingList[thm]):
                                                results.append([thingList[me], thingList[thm]])
                                    case 2:
                                        # Cube
                                        # Just a bunch of range checks
                                        thR = ThingGetHitboxRadius(thingList[thm])
                                        thH = ThingGetHitboxHeight(thingList[thm])
                                        if abs(myPos[0] - thPos[0]) <= thR:
                                            if abs(myPos[1] - thPos[1]) <= thH:
                                                if abs(myPos[2] - thPos[2]) <= thR:
                                                    results.append([thingList[me], thingList[thm]])
    return results

# BasicHandleCollisions()
# Takes a list of two things colliding, and moves the one that isMovable away from the second.

# Usage:
#
#   ThingSetupHitbox(myCharacter)
#   ThingSetupHitbox(thatTree)
#   ThingSetupHitbox(david)
#
#   for collision in GatherCollisions([myCharacter, thatTree, david]):
#       BasicHandleCollisions(collision)
#

def BasicHandleCollisions(things):
    if not ThingGetMovable(things[0]):
        if not ThingGetMovable(things[1]):
            return
        newPos = VectorNegate(DirectionBetweenVectors(things[1][1], things[0][1]))
        things[1][1] = VectorAdd(things[1][1], newPos)
    else:
        newPos = VectorMulF(VectorNegate(DirectionBetweenVectors(things[0][1], things[1][1])), DistanceBetweenVectors(things[1][1], things[0][1]))
        things[0][1] = VectorAdd(things[0][1], newPos)

# HandlePhysics()
# Sets the position of each thing based on it's physics calculations.

# Usage:
#
#   ThingSetupPhysics(myCharacter)
#
#   while True:
#       HandlePhysics([myCharacter])
#

def HandlePhysics(thingList, floorHeight = 0):
    global physTime
    delta = time.time() - physTime
    physTime = time.time()
    for t in thingList:
        if ThingGetMovable(t) and ThingGetPhysics(t) != []:
            ThingAddVelocity(t, ThingGetAcceleration(t))
            # Drag
            ThingSetVelocity(t, VectorSub(ThingGetVelocity(t), [airDrag * sign(ThingGetVelocityX(t)), airDrag * sign(ThingGetVelocityY(t)), airDrag * sign(ThingGetVelocityZ(t))]))
            for axis in ThingGetVelocity(t):
                if abs(axis) <= 0.1:
                    axis = 0
            # Gravity
            ThingAddVelocity(t, VectorMulF(gravityDir, 0.05))
            ThingAddPos(t, VectorMulF(ThingGetVelocity(t), delta))
            if ThingGetPosY(t) >= floorHeight:
                ThingSetPosY(t, floorHeight)
                GroundBounce(t)

def PhysicsBounce(thing):
    d = VectorPureDirection(ThingGetVelocity(thing))
    ThingSetVelocity(thing, VectorMul(ThingGetVelocity(thing), VectorMulF(d, -ThingGetBounciness(thing))))

def GroundBounce(thing):
    ThingSetVelocityY(thing, ThingGetVelocityY(thing) * -ThingGetBounciness(thing))

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
            myforce = VectorMulF(VectorMulF(ThingGetVelocity(cols[0]), ThingGetMass(cols[0])), ThingGetFriction(cols[1]))
            if ThingGetPhysics(cols[1]) != []:
                thforce = VectorMulF(VectorMulF(ThingGetVelocity(cols[1]), ThingGetMass(cols[1])), ThingGetFriction(cols[0]))
                toforce = VectorAdd(myforce, thforce)
                ThingAddVelocity(cols[0], toforce)
                ThingAddVelocity(cols[1], VectorNegate(toforce))
            else:
                ThingAddVelocity(cols[0], toforce)
                PhysicsBounce(cols[0])
        else:
            # Assuming that if we ended up here, this one has to have physics.
            force = VectorMulF(VectorMulF(DirectionBetweenVectors(ThingGetPos(cols[1]), ThingGetPos(cols[0])), ThingGetMass(cols[1])), ThingGetFriction(cols[0]))
            ThingAddVelocity(cols[1], force)
            PhysicsBounce(cols[0])

def sign(f):
    return 1 if f >= 0 else -1

#==========================================================================
#  
# Rastering
#
#==========================================================================

# Raster functions return new triangles. Will not overwrite the old triangles.

# High-Level Raster Functions

# Raster()
# The engine takes care of all the lists.

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

def Raster(sortKey=triSortAverage, sortReverse=True):
    return RasterThings(things, sortKey, sortReverse)

# RasterThings()
# Supply your own list of things to draw.

# Usage:
#
# for tri in z3dpy.RasterThings([myCharacter]):
#
#   z3dpy.PgDrawTriFL(tri, surface, pygame)
#    
def RasterThings(thingList, sortKey=triSortAverage, sortReverse=True):
    try:
        test = intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCamera(yourCamera) before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in thingList:
            if t[5]:
                for m in t[0]:
                    viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m))
            else:
                for m in t[0]:
                    viewed += RasterPt1Static(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), MeshGetId(m), MeshGetColour(m))
        viewed.sort(key=sortKey, reverse=sortReverse)
        return RasterPt2(viewed)
    

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
        print("Internal Camera is not set. Use z3dpy.SetInternalCamera(yourCamera) before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for m in meshList:
            viewed += RasterPt1(MeshGetTris(m), MeshGetPos(m), MeshGetRot(m), MeshGetId(m), MeshGetColour(m))
        viewed.sort(key=sortKey, reverse=sortReverse)
        return RasterPt2(viewed)


# Draws things, as well as hitboxes, and any lights/rays you give it. 
# Triangles from debug objects will have an id of -1
def DebugRaster(sortKey=triSortAverage, sortReverse=True):
    try:
        test = intMatV[0][0]
    except:
        print("Internal Camera is not set. Use z3dpy.SetInternalCamera(yourCamera) before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in things:
            for m in t[0]:
                viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m))

            if t[4] != []:
                viewed += RasterPt1(MeshGetTris(ThingGetHitboxMesh(t)), ThingGetPos(t), [0, 0, 0], -1, [255, 0, 0])

        for l in lights:
            viewed += RasterPt1Static(MeshGetTris(lightMesh), LightGetPos(l), -1, [255, 255, 255])

        for r in rays:
            viewed += RasterPt1Static([Tri(RayGetStart(r), VectorAdd(RayGetStart(r), [0, 0.001, 0]), RayGetEnd(r))], [0, 0, 0], -1, [255, 0, 0])

        viewed.sort(key = sortKey, reverse=sortReverse)
        finished += RasterPt2(viewed)
        return finished

def RasterPt1(tris, pos, rot, id, colour):
    translated = []
    prepared = []
    for tri in TransformTris(tris, rot):
        if VectorDoP(GetNormal(tri), VectorMul(iC[8], [-1, 1, 1])) > -0.4:
            prepared.append(tri)
    for t in ViewTris(TranslateTris(prepared, pos)):
        for r in TriClipAgainstZ(t):
            r.append(colour)
            r.append(id)
            translated.append(r)
    return translated


def RasterPt1Static(tris, pos, id, colour):
    prepared = []
    translated = []
    for tri in tris:
        if VectorDoP(TriGetNormal(tri), VectorMul(iC[8], [-1, 1, 1])) > -0.4:
            prepared.append(tri)
    for t in ViewTris(TranslateTris(prepared, pos)):
        for r in TriClipAgainstZ(t):
            r.append(colour)
            r.append(id)
            translated.append(r)
    return translated

def RasterPt2(tris):
    output = []
    for i in ProjectTris(tris):
        for s in TriClipAgainstScreenEdges(i):
            s.append(i[6])
            s.append(i[7])
            output.append(s)
    return output

# Low-Level Raster Functions
# Rastering is based on Javidx9's C++ series
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

def TransformTris(tris, rot):
    transformed = []
    mX = MatrixMakeRotX(rot[0])
    mY = MatrixMakeRotZ(rot[2])
    mZ = MatrixMakeRotY(rot[1])
    mW = MatrixMatrixMul(mX, mY)
    mW = MatrixMatrixMul(mW, mZ)
    for t in tris:
        nt = TriMatrixMul(t, mW)
        nt[3] = GetNormal(nt)
        transformed.append(nt)
    return transformed

def TransformTri(tri, rot):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotY(rot[1]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotZ(rot[2]))
    nt = TriMatrixMul(tri, mW)
    nt[3] = GetNormal(nt)
    return nt
        
def TranslateTris(tris, pos):
    translated = []
    for tri in tris:
        ntri = TriAdd(tri, pos)
        ntri[4] = VectorAdd(TriAverage(ntri), pos)
        translated.append(ntri)
    return translated

def TranslateTri(tri, pos):
    newTri = TriAdd(tri, pos)
    TriSetWPos(newTri, TriAverage(newTri))
    return newTri

def ViewTris(tris):
    output = []
    for tri in tris:
        nTri = TriMatrixMul(tri, intMatV)
        output.append(nTri)
    output = tuple(output)
    return output

def ViewTri(tri):
    return TriMatrixMul(tri, intMatV)
                    
def ProjectTris(tris):
    projected = []
    for tri in tris:
        nt = TriMul(TriAdd(HowProjectTri(tri), [1, 1, 0]), [iC[5], iC[4], 1])
        nt.append(tri[6])
        nt.append(tri[7])
        projected.append(nt)
    return projected


#==========================================================================
#  
# Drawing/Shaders
#
#==========================================================================

# Drawing Functions
# Handy shortcuts for drawing to a PyGame or Tkinter screen.

# Usage:
#
# for tri in RasterThings(things):
#
#   PyGame:
#
#   PgDrawTriRGB(tri, [255, 213, 0], screen, pygame)
#   or
#   PgDrawTriRGBF(tri, [1, 0.75, 0], screen, pygame)
#   or
#   PgDrawTriS(tri, 0.8, screen, pygame)
#
# RGBF can be used to colour a triangle with it's normal value
#   PgDrawTriRGBF(tri, TriangleGetNormal(tri), screen, pygame)
#
#   Tkinter:
#
#   TkDrawTriRGB(tri, [255, 213, 0], canvas)
#   or
#   TkDrawTriRGBF(tri, [1, 0.75, 0], canvas)
#   or
#   TkDrawTriS(tri, 0.8, canvas)
#

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
    pygame.draw.polygon(surface, VectorMulF(TriGetColour(tri), FlatLighting(tri)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriFLB(tri, surface, pygame):
    pygame.draw.polygon(surface, VectorMulF(TriGetColour(tri), FlatLightingBaked(tri)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Deprecated
def PgDrawTriangleRGB(tri, colour, surface, pygame):
    PgDrawTriRGB(tri, colour, surface, pygame)
def PgDrawTriangleRGBF(tri, colour, surface, pygame):
    PgDrawTriRGBF(tri, colour, surface, pygame)
def PgDrawTriangleF(tri, f, surface, pygame):
    PgDrawTriF(tri, f, surface, pygame)
def PgDrawTriangleOutl(tri, colour, surface, pygame):
    PgDrawTriOutl(tri, colour, surface, pygame)
def PgDrawTriangleS(tri, f, surface, pygame):
    PgDrawTriS(tri, f, surface, pygame)


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
    fillCol = RGBToHex(VectorMulF(TriGetColour(tri), FlatLighting(tri)))
    TkDraw(tri, fillCol, canvas)

def TkDrawTriFLB(tri, canvas):
    fillCol = RGBToHex(VectorMulF(TriGetColour(tri), FlatLightingBaked(tri)))
    TkDraw(tri, fillCol, canvas)

# Deprecated
def TkDrawTriangleRGB(tri, colour, canvas):
    TkDrawTriRGB(tri, colour, canvas)
def TkDrawTriangleRGBF(tri, colour, canvas):
    TkDrawTriRGBF(tri, colour, canvas)
def TkDrawTriangleF(tri, f, canvas):
    TkDrawTriF(tri, f, canvas)
def TkDrawTriangleOutl(tri, colour, canvas):
    TkDrawTriOutl(tri, colour, canvas)
def TkDrawTriangleS(tri, f, canvas):
    TkDrawTriS(tri, f, canvas)

# FlatLighting()
# Returns a float indicating how much light the triangle recieves.

# Usage:
#
# for tri in RasterThings(things):
#
#   PgDrawTriangleS(tri, FlatLighting(tri), screen, pygame)
#
#   TkDrawTriangleS(tri, FlatLighting(tri), canvas)
#

# Flat lighting shader, meant to be put into DrawTriangleRGB's colour
# Takes the direction towards the light and compares that to a corrected normal.
def FlatLighting(tri):
    return CheapLightingCalc(tri)

# CheapLightingCalc takes the direction towards the light source, no shadow checks or anything.
# optionally, draws a ray between the triangle and light, for debugging purposes.
def CheapLightingCalc(tri):
    shading = 0.0
    intensity = 0.0
    nNormal = VectorMul(TriGetNormal(tri), [-1, 1, 1])
    pos = TriGetWPos(tri)
    if len(lights) != 0:
        for l in lights:
            dist = DistanceBetweenVectors(pos, LightGetPos(l))
            if dist <= LightGetRadius(l):
                lightDir = DirectionBetweenVectors(LightGetPos(l), pos)
                shading += VectorDoP(lightDir, nNormal)
                shading = max(shading, 0)
                intensity += 1 - ((dist / LightGetRadius(l)) ** 2)
        return shading * intensity * LightGetStrength(l)
    return 0

# ExpensiveLightingCalc uses the direction towards the light source, and draws a ray between the triangle and light, testing for ray collisions.
def ExpensiveLightingCalc(tri, things):
    global rays
    shading = 0.0
    intensity = 0.0
    pos = TriGetWPos(tri)
    for l in lights:
        dist = DistanceBetweenVectors(pos, LightGetPos(l))
        if dist <= LightGetRadius(l):
            testRay = Ray(pos, LightGetPos(l))
            cntnue = True
            if len(rays) > 100:
                rays.pop()
            rays.append(testRay)
            for th in things:
                if RayIntersectThingComplex(testRay, th):
                    cntnue = False
            if cntnue:
                lightDir = DirectionBetweenVectors(LightGetPos(l), pos)
                shading += (VectorDoP(lightDir, VectorMul(TriGetNormal(tri), [-1, 1, -1])) + 1) * 0.5
                intensity += 1 - ((dist / LightGetRadius(l)) ** 2)
    return shading * intensity * LightGetStrength(l)

# BakeLighting() and FlatLightingBaked()

# BakeLighting() saves the FlatLighting() calculation to the triangle's shade value, for cheaply referencing later.
# FlatLightingBaked() retrives a triangle's shade value.

# Usage:
#
# BakeLighting(things)
#
# for tri in RasterThings(things):
#
#   PgDrawTriangleS(tri, FlatLightingBaked(tri), screen, pygame)
#
#   TkDrawTriangleS(tri, FlatLightingBaked(tri), canvas)
#

def FlatLightingBaked(tri):
    return TriGetShade(tri)

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shader variable
def BakeLighting(things):
    global rays
    print("Baking Lighting...")
    for th in things:
        for m in th[0]:
            for t in m[0]:
                calc = CheapLightingCalc(TranslateTri(TransformTri(t, VectorAdd(MeshGetRot(m), ThingGetRot(th))), VectorAdd(MeshGetPos(m), ThingGetPos(th))))
                TriSetShade(t, calc)
    rays = []
    print("Lighting Baked!")

def FillSort(n):
    return int(n[0])

# My own filling triangle routines so I can move beyond single-colour flat shading and single-triangle depth sorting.

# TriangleToLines()
# Returns a tuple of lines to draw on the screen, given a triangle.

# Usage:
#
# for tri in RasterThings(things):
#   for line in TriangleToLines(tri):
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
                output.append((lStart, lEnd))

        output += FillTriangleLinePt2(list, slope)
    return tuple(output)

# Part Two: From P2 to P3

def FillTriangleLinePt2(list, fSlope):
    output = []
    # If this side is flat, no need.
    if list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        diff4 = list[1][0] - list[0][0]
        slope2 = (list[2][1] - list[1][1]) / diff2
        for x in range(0, int(diff2) + 1, sign(diff2)):
            lStart = (x + list[1][0], (slope2 * x) + list[1][1])
            lEnd = (x + list[1][0], (fSlope * (x + diff4)) + list[0][1])
            output.append((lStart, lEnd))
    return output

# TriangleToPixels()
# Returns a tuple of pixels to draw on the screen, given a triangle.
# Calculates Texture coordinates (or at least it's supposed to, working on it).

# Usage:
#
# for tri in RasterThings(things):
#   for pixel in TriangleToPixels(tri):
#       x = pixel[0]
#       y = pixel[1]
#       uv = pixel[2]
#       u = uv[0]
#       v = uv[1]
#

def UVCalc(uv1, uv2, uv3, stage):
    if stage == 0:
        # Meant to be multiplied by 0-1 for interpolation
        # From P1 to P2
        uvD1 = uv2[0] - uv1[0]
        uvD2 = uv2[1] - uv1[1]
    else:
        # From P2 to P3
        uvD1 = uv3[0] - uv2[0]
        uvD2 = uv3[1] - uv2[1]
    return [uvD1, uvD2]
        

# Lots of comments because something is broken, and
# so far I haven't found the issue, maybe there's someone who can.
def TriToPixels(tri):
    output = []
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    diffX = list[2][0] - list[0][0]

    if diffX != 0:
        # x * slope takes a screen X and turns it into a screen Y, along the P1-P3 line
        slope = (list[2][1] - list[0][1]) / diffX

        diff = list[1][0] - list[0][0]

        uv1 = list[0][4]
        uv2 = list[1][4]
        uv3 = list[2][4]

        uv = UVCalc(uv1, uv2, uv3, 0)

        # From P1 to P3
        uvD3 = uv3[1] - uv1[1]
        uvD4 = uv3[0] - uv1[0]

        # If this side's flat, no need.
        if diff != 0:

            diffY = list[1][1] - list[0][1]
            # x * diff3 takes a screen x and results in a screen y, on the P1-P2 line
            diff3 = diffY / diff

            for x in range(int(diff) + 1):

                range1 = int(diff3 * x + list[0][1])
                range2 = int(slope * x + list[0][1])

                # Converting screen x to 0-1
                # Normalized between P1 and P2
                nX = (x / (int(diff) + 1))
                # Normalized between P1 and P3
                nX2 = (x / diffX)

                # Figure out the UV for the vertical line we are about to draw.
                UVndX = nX2 * uvD4 + uv1[0]
                UVndY = nX2 * uvD3 + uv1[1]
                UVstY = nX * uv[1] + uv1[1]
                UVstX = nX * uv[0] + uv1[0]
                uvDy = UVndY - UVstY
                uvDx = UVndX - UVstX

                sgn = 1 if range1 < range2 else -1
                for y in range(range1, range2, sgn):

                    # Convering screen y to 0-1
                    nY = (y - range1) / (range2 - range1)

                    # Figure out the UV for the current pixel along the line.
                    uvY = nY * uvDy + UVstY
                        
                    uvX = nY * uvDx + UVstX
                        
                    # Pixel:
                    # [0] is the screen x, [1] is the screen y, [2] is the UV
                    output.append((x + int(list[0][0]), y, [uvX, uvY]))

        output += FillTrianglePixelPt2(list, slope, diff, uvD3, uvD4, diffX)
    return tuple(output)

def FillTrianglePixelPt2(list, fSlope, diff, diffUV3, diffUV4, diffX):
    output = []
    if list[2][0] != list[1][0]:
        diff2 = int(list[2][0] - list[1][0])
        if diff2 != 0:
            slope2 = (list[2][1] - list[1][1]) / diff2
            uv1 = list[0][4]
            uv2 = list[1][4]
            uv3 = list[2][4]

            uv = UVCalc(uv1, uv2, uv3, 1)

            for x in range(diff2 + 1):
                ranges = [int((slope2 * x) + list[1][1]), int((fSlope * (x + diff)) + list[0][1])]
                # Repeat pretty much the same steps except for this side now.
                nX = x / diff2
                nX2 = (x + (list[1][0] - list[0][0])) / diffX
                UVstX = nX * uv[0] + list[1][4][1]
                UVstY = nX * uv[1] + list[1][4][0]
                UVndX = nX2 * diffUV4 + list[1][4][0]
                UVndY = nX2 * diffUV3 + list[1][4][1]
                UVd1 = UVndX - UVstX
                UVd2 = UVndY - UVstY
                sgn = 1 if ranges[0] < ranges[1] else -1
                for y in range(ranges[0], ranges[1], sgn):
                    nY = ((y - ranges[0]) / (ranges[1] - ranges[0]))
                    uvX = nY * UVd1 + UVstX
                    uvY = nY * UVd2 + UVstY
                    output.append((int(x + list[1][0]), y, [uvX, uvY]))
    return output



# PgPixelShader()
# Calculates texturing (or at least it's supposed to, working on it), converts the triangle to pixels, then draws them to the screen via a PyGame PixelArray.

# Being a software renderer written in Python, looping through each pixel of the triangle is not feasible.
# It's only for PyGame because it's already bad enough with the extra speed that pygame has (even before adding any UV calc).

# There may be a way to get acceptable performance by compiling it.

# Usage:
#
# screenArray = pygame.PixelArray(screen)
#
# for tri in RasterThings(things):
#   PgPixelShader(tri, screenArray)
#
txtr = TestTexture()

def PgPixelShader(tri, pixelArray, surface, pygame):
    for pixel in TriToPixels(tri, surface, pygame):
        if pixel[0] > 0:
            if pixel[1] > 0:
                if pixelArray[pixel[0], pixel[1]] == 0:
                    rU = int(pixel[2][0] * len(txtr))
                    rV = int(pixel[2][1] * len(txtr[0]))
                    u = abs(rU) % len(txtr)
                    v = abs(rV) % len(txtr[0])
                    colour = txtr[int(u)][int(v)]

                    pixelArray[rU, rV] = (255, 255, 255)
                    pixelArray[pixel[0], pixel[1]] = colour

#==========================================================================
#  
# Calculating How Projection
#
#==========================================================================


def FindHowVars(fov):
    global howX
    global howY
    found = CalculateCam(fov)
    howX = found[0]
    howY = found[1]

def SetHowVars(x, y):
    global howX
    global howY
    howX = x
    howY = y

def ComplexX(x, fov):
    f = 1 / math.tan(fov * 0.5)
    return (16/9) * f * x

def ComplexY(x, fov):
    f = 1 / math.tan(fov * 0.5)
    return f * x

def ComplexZ(z, fc, nc):
    q = fc / (fc - nc)
    return (q * z) - (q * nc)

def SimpleFormula(x, m, b):
    return m * x + b

def CamX(m, b, fov):
    score = 0
    for x in range(1920):
        rY = ComplexX(x, fov)
        aY = SimpleFormula(x, m, b)
        score += abs(rY - aY)
    return score

def CamY(m, b, fov):
    score = 0
    for x in range(1920):
        rY = ComplexY(x, fov)
        aY = SimpleFormula(x, m, b)
        score += abs(rY - aY)
    return score

calc = True

# Calculating Camera Variables
# Starts at 1, then randomly guesses to find a better and better solution.

# What it's really doing is taking the full projection formula, and graphing it,
# then trying to replicate that graph as closely as possible with a simple mx + b

def CalculateCam(foV):
    print("Calculating Camera..")
    finished = [0, 0, 0]
    fov = foV * 0.0174533
    for z in range(0, 2):
        currentScore = 9999999
        bestY = 1
        bestB = 0
        noImp = 0
        srchRad = 12
        aiY = 1
        aiB = 0
        calc = True
        while calc:
            match z:
                case 0:
                    Score = CamX(aiY, aiB, fov,)
                case 1:
                    Score = CamY(aiY, aiB, fov)
            if Score < currentScore:
                bestY = aiY
                bestB = aiB
                currentScore = Score
            else:
                noImp += 1
                aiY = bestY
                aiB = bestB
            if noImp > 50:
                srchRad /= 2
                noImp = 0
            if srchRad < 0.00000000000000001:
                match z:
                    case 0:
                        finished[0] = bestY
                        print("Found X...")
                    case 1:
                        finished[1] = bestY
                        print("Found Y...")
                        print("Done!")
                        print("X: " + str(finished[0]) + ", Y: " + str(finished[1]))
                        print("Use SetHowVars() to skip the calculations")
                        return finished
                calc = False
            
            if rand.random() > 0.5:
                aiY = bestY + ((rand.random() - 0.5) * srchRad)
            else:
                aiB = bestY + ((rand.random() - 0.5) * srchRad)