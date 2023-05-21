# -zw

# Z3dPy v0.1.7
# *Nightly build, Wiki/examples are based on the release build.

# Change Notes:
#
# - Added Baked Lighting. Call BakeLighting(), then replace FlatLighting() with FlatLightingBaked()
#
# - Renamed FillTriangleLine() and FillTrianglePixel() to TriangleToLines() and TriangleToPixels()
#
# - Added object functions for lights and rays
#
# - Removed trys and excepts on vector functions since they aren't needed anymore.
#
# - Optimized rastering
#

import math
import time
import zpFormulaFinder

print("Z3dPy v0.1.7")


#==========================================================================
#  
# Variables
#
#==========================================================================


# You can reference these at any time to get a global axis.
globalX = (1, 0, 0)
globalY = (0, 1, 0)
globalZ = (0, 0, 1)

# Light list for FlatLighting(), and DebugRasterThings()
lights = []

gravityDir = [0, 9.8, 0]

drag = 0.1

physTime = time.time()

# Ray list for drawing with DebugRasterThings()
rays = []

stCPos = [0, 0, 0]
stCRot = [0, 0, 0]


#==========================================================================
#
# Objects
#
#==========================================================================


# Vector:
# [0] - [2] are the x y and z

def Vector(x, y, z):
    return [x, y, z]

def Vector2(u, v):
    return [u, v]

def Vector4(x, y, z, w):
    return [x, y, z, w]

# Triangles:
#[0] - [2] are the 3 points, [3] is the normal, [4] is shade, [5] is colour, [6] is world position,
# and [7] is Id

def Triangle(vector1, vector2, vector3):
    return [vector1, vector2, vector3, GetNormal([vector1, vector2, vector3]), 0, (255, 255, 255), TriangleAverage([vector1, vector2, vector3]), 0]

# Meshes:
# [0] is the tuple of triangles, [1] is the position, [2] is the rotation, [3] is the colour, and [4] is the id

def Mesh(tris, x, y, z):
    return [tris, [x, y, z], [0, 0, 0], [255, 255, 255], 0]

# Some stuff I need to declare before the Thing class

# Hitbox Object:
#
# Stores all the needed info regarding collisions, the type of hitbox, it's scale, and collision id.
# Only hitboxes with the same collision id will collide.
#
# [0] is type, [1] is id, [2] is radius, [3] is height, [4] is hitbox mesh for drawing.
#
# Enable collisions with myThing[4] = z3dpy.Hitbox()

def Hitbox(type, id, radius, height):
    return [type, id, radius, height, LoadMeshScl("engine/mesh/cube.obj", 0, 0, 0, radius, height, radius)]

# Physics Body:
#
# Enable physics with myThing[6] = z3dpy.PhysicsBody()
#
# [0] is velocity, [1] is acceleration, [2] is mass, [3] is friction, [4] is bounciness, [5] is drag

def PhysicsBody():
    return [[0, 0, 0], [0, 0, 0], 0.2, 0.2, 0.1, 2]

# Things:
#
# The Thing is what you would typically refer to as an object, it has a collection of meshes, and collision data.
#
#
# [0] is the list of meshes, [1] is position, [2] is rotation, [3] is object id, [4] is hitbox, [5] is IsMovable, and [6] is physics body, and [7] is visibility
#
# Hitbox and Physics body are empty till you assign them.

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], 0, [], True, [], True]

# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
#
# For a third person camera, use CameraSetTargetLocation()
# For a first person camera, use CameraSetTargetVector()
#

# [0] is position, [1] is rotation, [2] is fov, [3] is screenHeight, [4] is screenWidth, [5] is near clip, [6] is far clip
# [7] is target location, and [8] is up vector

def Camera(x, y, z, scrW, scrH):
    return [[x, y, z], [0, 0, 0], 90, scrH, scrW, 0.1, 1500, [0, 0, 1], [0, 1, 0]]

# Internal Camera
#
# the internal camera used for rendering. 
# Set the internal camera to one of your cameras when you want to render from it.
#
# [0] is location, [1] is rotation, [2] is fov, [3] is screen height, [4] is screen width, [5] is screen width / 2, [6] is screen height / 2
# [7] is near clip, [8] is far clip, [9] is target vector, [10] is up vector, [11] is fov / 2, [12] is tan, [13] is aspect ratio
#

iC = [[0, 0, 0], [0, 0, 0], 90, 720, 1280, 360, 640, 0.1, 1500, [0, 0, 1], [0, 1, 0], 45, (1 / math.tan(45)), 1280 / 720]

def SetInternalCamera(camera):
    global intMatV
    global iC
    iC = [CameraGetPos(camera), CameraGetRot(camera), CameraGetFOV(camera), CameraGetScH(camera), CameraGetScW(camera), CameraGetScH(camera) * 0.5, CameraGetScW(camera) * 0.5, CameraGetNCl(camera), CameraGetFCl(camera), CameraGetTargetVector(camera), CameraGetUpVector(camera), CameraGetFOV(camera) * 0.5, 1 / math.tan(CameraGetFOV(camera) * 0.5), CameraGetScH(camera) / CameraGetScW(camera)]
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intMatV = LookAtMatrix(camera)

# Point Lights:
#
# Point lights will light up triangles that are inside the radius and facing towards it's location
#
# Used for the FlatLighting() shader, which outputs a colour to be plugged into DrawTriangleRGB()
#

# [0] is position, [1] is strength, [2] is radius

def Light_Point(x, y, z, strength, radius):
    return [[x, y, z], strength, radius]



def Light_Sun(direction, strength):
    return [direction, strength, 1]

# Rays:
#
# Used for drawing rays to the screen.
#
# [0] is ray start location, [1] is ray end location, [2] is if it's drawn as red.

def Ray(raySt, rayNd):
    return [raySt, rayNd, True]



#==========================================================================
#
# Object Functions
#
# Everything is a list, so these functions are human-friendly ways to set and retrieve variables
#
#==========================================================================


# TRIANGLES


# GetNormal() will calculate a new normal, TriangleGetNormal() will return the stored one.
def TriangleGetNormal(tri):
    return tri[3]

# Normals are automatically calculated during the raster process, and by default will be the world space normal.
def TriangleSetNormal(tri, vector):
    tri[3] = vector


def TriangleGetColour(tri):
    return tri[5]

# Colour is automatically calculated during the raster process, and by default will be the colour of the associated mesh.
def TriangleSetColour(tri, vector):
    tri[5] = vector


def TriangleGetWPos(tri):
    return tri[6]

def TriangleSetWPos(tri, vector):
    tri[6] = vector

def TriangleGetId(tri):
    return tri[7]

# Id is automatically calculated during the raster process, and by default will be the id of the associated mesh.
def TriangleSetId(tri, id):
    tri[7] = id


# MESHES


def MeshSetTris(mesh, tris):
    mesh[0] = tris

def MeshGetTris(mesh):
    return mesh[0]

def MeshSetPos(mesh, vector):
    for tri in mesh[0]:
        tri = TriangleAdd(tri, vector)

def MeshGetPos(mesh):
    return mesh[1]

def MeshSetRot(mesh, vector):
    mesh[2] = vector

def MeshAddRot(mesh, vector):
    mesh[2] = [mesh[2][0] + vector[0], mesh[2][1] + vector[1], mesh[2][2] + vector[2]]

def MeshSubRot(mesh, vector):
    mesh[2] = [mesh[2][0] - vector[0], mesh[2][1] - vector[1], mesh[2][2] - vector[2]]

def MeshMulRot(mesh, vector):
    mesh[2] = [mesh[2][0] * vector[0], mesh[2][1] * vector[1], mesh[2][2] * vector[2]]

def MeshDivRot(mesh, vector):
    mesh[2] = [mesh[2][0] / vector[0], mesh[2][1] / vector[1], mesh[2][2] / vector[2]]

def MeshGetRot(mesh):
    return mesh[2]

def MeshSetColour(mesh, vector):
    mesh[3] = vector

def MeshGetColour(mesh):
    return mesh[3]

def MeshSetId(mesh, id):
    mesh[4] = id

def MeshGetId(mesh):
    return mesh[4]


# THINGS


def ThingSetPos(thing, vector):
    thing[1] = vector

def ThingAddPos(thing, vector):
    thing[1] = VectorAdd(thing[1], vector)

def ThingSubPos(thing, vector):
    thing[1] = VectorSub(thing[1], vector)

def ThingSetPosX(thing, x):
    thing[1] = [x, thing[1][1], thing[1][2]]

def ThingSetPosY(thing, y):
    thing[1] = [thing[1][0], y, thing[1][2]]

def ThingSetPosZ(thing, z):
    thing[1] = [thing[1][0], thing[1][1], z]

def ThingGetPos(thing):
    return thing[1]

def ThingGetPosX(thing):
    return thing[1][0]

def ThingGetPosY(thing):
    return thing[1][1]

def ThingGetPosZ(thing):
    return thing[1][2]

def ThingSetRot(thing, vector):
    thing[2] = vector

def ThingAddRot(thing, vector):
    thing[2] = VectorAdd(thing[2], vector)

def ThingSubRot(thing, vector):
    thing[2] = VectorSub(thing[2], vector)

def ThingMulRot(thing, vector):
    thing[2] = VectorMul(thing[2], vector)

def ThingDivRot(thing, vector):
    thing[2] = VectorDiv(thing[2], vector)

def ThingSetPitch(thing, deg):
    thing[2][0] = deg

def ThingSetRoll(thing, deg):
    thing[2][1] = deg

def ThingSetYaw(thing, deg):
    thing[2][2] = deg

def ThingGetRot(thing):
    return thing[2]

def ThingGetPitch(thing):
    return thing[2][0]

def ThingGetRoll(thing):
    return thing[2][2]

def ThingGetYaw(thing):
    return thing[2][1]

# Object Id is meant for the draw loop, so you can check a triangle's id to see what mesh it came from.

def ThingSetId(thing, id):
    thing[3] = id

def ThingGetId(thing):
    return thing[3]

# ThingSetCollision() will set the collision data and update the hitbox mesh.
# Type: 0 = Sphere, 1 = Cylinder, 2 = Cube
# Radius: radius of the sphere/cylinder, or length of the cube
# Height: height of the cylinder/cube.
# Id: Objects with the same ID will check for collisions. Everything is 0 by default, so if unsure, use that.

def ThingSetCollision(thing, type, id, radius, height):
        thing[4][2] = radius
        thing[4][3] = height
        thing[4][0] = type
        thing[4][1] = id
        match type:
            case 0:
                thing[4][4] = LoadMeshScl("engine/mesh/sphere.obj", 0, 0, 0, radius, radius, radius)
            case 1:
                thing[4][4] = LoadMeshScl("engine/mesh/cylinder.obj", 0, 0, 0, radius, height, radius)
            case 2:
                thing[4][4] = LoadMeshScl("engine/mesh/cube.obj", 0, 0, 0, radius, height, radius)

def ThingGetHitboxMesh(thing):
    if thing[4] != []:
        return thing[4][4]
    return []

def ThingGetHitboxHeight(thing):
    if thing[4] != []:
        return thing[4][3]
    return []

def ThingGetHitboxRadius(thing):
    if thing[4] != []:
        return thing[4][2]
    return []

def ThingGetHitboxId(thing):
    if thing[4] != []:
        return thing[4][1]
    return []

def ThingGetHitboxType(thing):
    if thing[4] != []:
        return thing[4][0]
    return []

def ThingSetMovable(thing, isMovable):
    thing[5] = isMovable

def ThingGetMovable(thing):
    return thing[5]

def ThingGetPhysics(thing):
    return thing[6]

def ThingSetVelocity(thing, vector):
    thing[6][0] = vector

def ThingSetVelocityX(thing, x):
    thing[6][0] = [x, thing[6][0][1], thing[6][0][2]]

def ThingSetVelocityY(thing, y):
    thing[6][0] = [thing[6][0][0], y, thing[6][0][2]]

def ThingSetVelocityZ(thing, z):
    thing[6][0] = [thing[6][0][0], thing[6][0][1], z]

def ThingGetVelocity(thing):
    return thing[6][0]

def ThingGetVelocityX(thing):
    return thing[6][0][0]

def ThingGetVelocityY(thing):
    return thing[6][0][1]

def ThingGetVelocityZ(thing):
    return thing[6][0][2]

def ThingAddVelocity(thing, vector):
    thing[6][0] = VectorAdd(thing[6][0], vector)

def ThingSubVelocity(thing, vector):
    thing[6][0] = VectorSub(thing[6][0], vector)

def ThingSetAcceleration(thing, vector):
    thing[6][1] = vector

def ThingGetAcceleration(thing):
    return thing[6][1]

def ThingSetMass(thing, mass):
    thing[6][2] = mass

def ThingGetMass(thing):
    return thing[6][2]

def ThingSetFriction(thing, frc):
    thing[6][3] = frc

def ThingGetFriction(thing):
    return thing[6][3]

def ThingSetBounciness(thing, bnc):
    thing[6][4] = bnc

def ThingGetBounciness(thing):
    return thing[6][4]


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

def CameraSetFOV(cam, deg):
    cam[2] = deg * 0.0174533

def CameraGetFOV(cam):
    return cam[2]

def CameraSetScH(cam, h):
    cam[3] = h

def CameraGetScH(cam):
    return cam[3]

def CameraSetScW(cam, w):
    cam[4] = w

def CameraGetScW(cam):
    return cam[4]

def CameraSetNCl(cam, nc):
    cam[5] = nc

def CameraGetNCl(cam):
    return cam[5]

def CameraSetFCl(cam, fc):
    cam[6] = fc

def CameraGetFCl(cam):
    return cam[6]

# Deprecated
def CameraSetTarget(cam, x, y, z):
    CameraSetTargetVector(cam, [x, y, z])
def CameraSetTargetV(cam, v):
    CameraSetTargetVector(cam, v)

# Backwards Compatibility / Direction is easier to understand
def CameraSetTargetDirection(cam, v):
    CameraSetTargetVector(cam, v)
def CameraGetTargetDirection(cam):
    return CameraGetTargetVector(cam)

def CameraSetTargetLocation(cam, v):
    cam[7] = v

def CameraSetTargetVector(cam, v):
    cam[7] = VectorAdd(cam[0], VectorNormalize(v))

# Set Target First Person: Takes care of rotating vectors, so you just supply a pitch and yaw.
def CameraSetTargetFP(cam):
    dir = VectorRotateX([0, 0, 1], CameraGetPitch(cam))
    dir = VectorRotateY(dir, CameraGetYaw(cam))
    CameraSetTargetVector(cam, dir)

def CameraGetTargetLocation(cam):
    return cam[7]

def CameraGetTargetVector(cam):
    return VectorNormalize(VectorSub(cam[7], cam[0]))

def CameraSetUpVector(cam, vector):
    cam[8] = vector

def CameraGetUpVector(cam):
    return cam[8]

def CameraGetRightVector(cam):
    return VectorCrP(CameraGetTargetVector(cam), cam[8])


# LIGHTS


def LightGetPos(light):
    return light[0]

def LightSetPos(light, vector):
    light[0] = vector

def LightGetStrength(light):
    return light[1]

def LightSetStrength(light, str):
    light[1] = str

def LightGetRadius(light):
    return light[2]

def LightSetRadius(light, radius):
    light[2] = radius


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

def RayGetIsRed(ray):
    return ray[2]

def RaySetIsRed(ray, bool):
    ray[2] = bool


#==========================================================================
#  
# Misc Functions
#
#==========================================================================


# WhatIs() will take a list and figure out what "object" it is.
# meant to be used with print() for debugging.
# If it's not a list, it'll return the built-in type()
def WhatIs(any):
    try:
        test = len(any)
    except:
        return str(type(any))
    else:
        match len(any):
            case 3:
                try:
                    test = any[0] + 1
                    return "Vector3"
                except:
                    try:
                        test = any[0][0] + 1
                        # S for shortened triangle, it only includes the points, and no other information.
                        return "STriangle"
                    except:
                        return "Unknown"
            case 4:
                return "Vector4"
            case 5:
                try:
                    test = any[0] + 1
                    return "Hitbox"
                except:
                    try:
                        test = any[2][0] + 1
                        return "Mesh"
                    except:
                        return "VectorUV"
            case 6:
                return "PhysicsBody"
            case 7:
                return "Thing"
            case 8:
                return "Triangle"
            case 14:
                return "Camera"

# WhatIsInt() is the same as WhatIs(), except instead of a string response it's a number
def WhatIsInt(any):
    match len(any):
        case 3:
            try:
                test = any[0] + 1
                # Vector3
                return 0
            except:
                try:
                    test = any[0][0] + 1
                    # STriangle
                    return 1
                except:
                    # Unknown
                    return -1
        case 4:
            # Vector4
            return 2
        case 5:
            try:
                test = any[0] + 1
                # Hitbox
                return 3
            except:
                try:
                    test = any[2][0] + 1
                    # Mesh
                    return 4
                except:
                    # VectorUV
                    return 5
        case 14:
            # Camera
            return 9
        case _:
            return len(any)

def Projection(vector, a, f, fc, nc):
    # At the start I went the full formula route instead of matrix form, and
    # I kept it because it works.
    q = fc / (fc - nc)
    if vector[2] != 0:
        return [(a * f * vector[0]) / vector[2], (f * vector[1]) / vector[2], (q * vector[2]) - (q * nc)]
    else:
        return vector

# Wrote a script to brute-force finding a single multiplier that could do most of the projection.
# I call it: How-Does-That-Even-Work Projection

# I've already calculated the constants for an FOV of 90: 
# To recalculate, use FindHowVars(). Although it's VERY slow, so do this once at the start.
howX = 1.0975459978374298
howY = 0.6173470654658898

def HowProjection(vector):
    # Assumes 16/9 aspect ratio, because of this 3.
    return [(vector[0] * howX) / (vector[2] * 3), (vector[1] * howY) / vector[2], vector[2]]

def FindHowVars(fov):
    global howX
    global howY
    found = zpFormulaFinder.CalculateCam(fov)
    howX = found[0]
    howY = found[1]

def SetHowVars(x, y):
    global howX
    global howY
    howX = x
    howY = y

def ProjectTriangle(t, a, f, fc, nc):
    if t != None:
        basic = [Projection(t[0], a, f, fc, nc), Projection(t[1], a, f, fc, nc), Projection(t[2], a, f, fc, nc)]
        try:
            return [basic[0], basic[1], basic[2], t[3], t[4], t[5], t[6], t[7]]
        except:
            return basic
        
def HowProjectTriangle(t):
    if t != None:
        basic = [HowProjection(t[0]), HowProjection(t[1]), HowProjection(t[2])]
        try:
            return [basic[0], basic[1], basic[2], t[3], t[4], t[5], t[6], t[7]]
        except:
            return basic


#==========================================================================
#  
# Vector Functions
#
#==========================================================================


def VectorAdd(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]  

def VectorSub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def VectorMul(v1, v2):
    return [v1[0] * v2[0], v1[1] * v2[1], v1[2] * v2[2]]

def VectorMulF(v, f):
    return [v[0] * f, v[1] * f, v[2] * f]

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
    
# Vector Cross Product gives you the direction of the 3rd dimension, given 2 Vectors. If you give it an X and a Y direction, it will give you the Z direction.
def VectorCrP(v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

def VectorDiv(v1, v2):
    return [v1[0] / v2[0], v1[1] / v2[1], v1[2] / v2[2]]

def VectorDivF(v, f):
    return [v[0] / f, v[1] / f, v[2] / f]

def VectorGetLength(v):
    return math.sqrt((v[0] * v[0]) + (v[1] * v[1]) + (v[2] * v[2]))

def VectorNormalize(v):
    l = abs(VectorGetLength(v))
    if l != 0:
        return [v[0] / l, v[1] / l, v[2] / l]
    return v

# Vector Dot Product compares 2 directions. 1 is apposing, -1 is facing the same direction. (or the other way around, not too sure)
# Useful for lighting calculations.
def VectorDoP(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def VectorEqual(v1, v2):
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def DistanceBetweenVectors(v1, v2):
    return math.sqrt(((v2[0] - v1[0]) ** 2) + ((v2[1] - v1[1]) ** 2) + ((v2[2] - v1[2]) ** 2))

def VectorNegate(v):
    return [v[0] * -1, v[1] * -1, v[2] * -1]

def VectorABS(v):
    return [abs(v[0]), abs(v[1]), abs(v[2])]

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))

def VectorRotateX(vec, deg):
    return MatrixMul(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return MatrixMul(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return MatrixMul(vec, MatrixMakeRotZ(deg))

def TriangleGetVectorNormals(tri):
    try:
        return VectorDivF(VectorAdd(VectorAdd(tri[0][3], tri[1][3]), tri[2][3]), 3)
    except:
        print("TriangleGetVectorNormals(): Triangle has no vector normals")
        return []


#==========================================================================
#  
# Triangle Functions
#
#==========================================================================


def TriangleAdd(t, v):
    basic = [VectorAdd(t[0], v), VectorAdd(t[1], v), VectorAdd(t[2], v)]
    return [basic[0], basic[1], basic[2], t[3], t[4], t[5], t[6], t[7]]

def TriangleSub(t, v):
    return [VectorSub(t[0], v), VectorSub(t[1], v), VectorSub(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriangleMul(t, v):
    return [VectorMul(t[0], v), VectorMul(t[1], v), VectorMul(t[2], v), t[3], t[4], t[5], t[6], t[7]]

def TriangleMulF(t, f):
    return [VectorMulF(t[0], f), VectorMulF(t[1], f), VectorMulF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

def TriangleDivF(t, f):
    return [VectorDivF(t[0], f), VectorDivF(t[1], f), VectorDivF(t[2], f), t[3], t[4], t[5], t[6], t[7]]

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

def TriangleClipAgainstPlane(pPos, pNrm, tri):
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
        outT = [insideP[0], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[1]), VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        return [outT]

    if len(insideP) == 2 and len(outsideP) == 1:
        outT1 = [insideP[0],insideP[1], VectorIntersectPlane(pPos, pNrm, insideP[1], outsideP[0]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        outT2 = [insideP[0], outT1[2], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri[3], tri[4], tri[5], tri[6], tri[7]]
        return [outT1, outT2]

def GetNormal(tri):
    triLine1 = VectorSub(tri[1], tri[0])
    triLine2 = VectorSub(tri[2], tri[0])
    normal = VectorCrP(triLine1, triLine2)
    return VectorNormalize(VectorMul(normal, [1, -1, -1]))

def TriangleAverage(tri):
    return Vector((tri[0][0] + tri[1][0] + tri[2][0]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3)

# Sort Triangles based on their distance from the camera
def triSortAverage(n):
    return (n[0][2] + n[1][2] + n[2][2]) / 3

def triSortFurthest(n):
    return max(n[0][2], n[1][2], n[2][2])

def TriangleClipAgainstZ(tri):
    return TriangleClipAgainstPlane([0, 0, iC[7]], [0, 0, 1], tri)

def TriangleClipAgainstScreenEdges(tri):
    output = []
    for t in TriangleClipAgainstPlane([0, 0, 0], [0, 1, 0], tri):
        for r in TriangleClipAgainstPlane([0, iC[3] - 1, 0], [0, -1, 0], t):
            for i in TriangleClipAgainstPlane([0, 0, 0], [1, 0, 0], r):
                for s in TriangleClipAgainstPlane([iC[4] - 1, 0, 0], [-1, 0, 0], i):
                    output.append(s)
    return tuple(output)


#==========================================================================
#  
# Mesh Functions
#
#==========================================================================


# Load OBJ File
def LoadMeshScl(filename, x, y, z, sclX, sclY, sclZ):
    try:
        file = open(filename)
    except:
        if filename == "engine/mesh/error.obj":
            raise Exception("Can't load placeholder mesh. (Is the engine folder missing?)")
        else:
            return LoadMeshScl("engine/mesh/error.obj", x, y, z, sclX, sclY, sclZ)
    verts = []
    currentLine = ""
    scaped = True
    output = []

    while scaped:
        currentLine = file.readline()
        if currentLine == "":
            scaped = False
            break
        if currentLine[0] == 'v':
                currentLine = currentLine[2:].split(" ")
                verts.append([float(currentLine[0]) * sclX, float(currentLine[1]) * sclY, float(currentLine[2]) * sclZ, [0, 0, 0], 0, 0])
            
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            qTri = [verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1]]
            normal = GetNormal(qTri)
            verts[int(currentLine[0]) - 1][3] = VectorAdd(verts[int(currentLine[0]) - 1][3], normal)
            verts[int(currentLine[1])- 1][3] = VectorAdd(verts[int(currentLine[1])- 1][3], normal)
            verts[int(currentLine[2]) - 1][3] = VectorAdd(verts[int(currentLine[2]) - 1][3], normal)
            output.append(Triangle(verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1]))
        
    file.close()
    return Mesh(tuple(output), x, y, z)

def LoadMesh(filename, x, y, z):
    return LoadMeshScl(filename, x, y, z, 1, 1, 1)

lightMesh = LoadMesh("engine/mesh/light.obj", 0, 0, 0)


#==========================================================================
#  
# Matrix Functions
#
#==========================================================================


def TriMatrixMul(t, m):
    try:
        return [MatrixMul(t[0], m), MatrixMul(t[1], m), MatrixMul(t[2], m), t[3], t[4], t[5], t[6], t[7]]
    except:
        return [MatrixMul(t[0], m), MatrixMul(t[1], m), MatrixMul(t[2], m)]

def MatrixMul(v, m):
    try:
        return [v[0] * m[0][0] + v[1] * m[1][0] + v[2] * m[2][0] + m[3][0], v[0] * m[0][1] + v[1] * m[1][1] + v[2] * m[2][1] + m[3][1], v[0] * m[0][2] + v[1] * m[1][2] + v[2] * m[2][2] + m[3][2], v[0] * m[0][3] + v[1] * m[1][3] + v[2] * m[2][3] + m[3][3], v[3], v[4], v[5]]
    except:
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
    rad = (deg * 0.0174533) * 0.5
    return [[1, 0, 0, 0], [0, math.cos(rad), math.sin(rad), 0], [0, -math.sin(rad), math.cos(rad), 0], [0, 0, 0, 1]]

def MatrixMakeRotY(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), 0, math.sin(rad), 0], [0, 1, 0, 0], [-math.sin(rad), 0, math.cos(rad), 0], [0, 0, 0, 1]]

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), math.sin(rad), 0, 0], [-math.sin(rad), math.cos(rad), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    return ((temp[2][0], temp[2][1], temp[2][2], 0), (temp[1][0], temp[1][1], temp[1][2], 0), (temp[0][0], temp[0][1], temp[0][2], 0), (pos[0], pos[1], pos[2], 1))

def LookAtMatrix(camera):
    temp = MatrixStuff(CameraGetPos(camera), CameraGetTargetLocation(camera), CameraGetUpVector(camera))
    return ((temp[2][0], temp[1][0], temp[0][0], 0), (temp[2][1], temp[1][1], temp[0][1], 0), (temp[2][2], temp[1][2], temp[0][2], 0), (-VectorDoP(camera[0], temp[2]), -VectorDoP(camera[0], temp[1]), -VectorDoP(camera[0], temp[0]), 1))

def MatrixMakeProjection():
    return [[iC[13] * iC[12], 0, 0, 0], [0, iC[12], 0, 0], [0, 0, iC[8] / (iC[8] - iC[7]), 1], [0, 0, (-iC[8] * iC[7]) / (iC[8] - iC[7]), 0]]


#==========================================================================
#  
# Ray Functions
#
#==========================================================================


def RayIntersectTriangle(raySt, rayDr, tri):
    # Using the Moller Trumbore algorithm
    # Not very tested as I now need a way of drawing rays
    e1 = VectorSub(tri[1], tri[0])
    e2 = VectorSub(tri[2], tri[0])
    o = VectorSub(raySt, tri[0])
    h = VectorCrP(o, rayDr)
    
    d = -VectorDoP(rayDr, TriangleGetNormal(tri))
    f = 1 / d

    ds = VectorDoP(o, TriangleGetNormal(tri)) * f
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
        rays.append()
        return Hit
        
    else:
        return [False]

def RayIntersectMesh(rayStart, rayDr, mesh):
    for t in mesh[0]:
        hit = RayIntersectTriangle(rayStart, rayDr, t)
        if hit[0]:
            return hit
    return [False]

# Does a ray intersection test with the hitbox
def RayIntersectThingSimple(rayStart, rayEnd, thing):
    rayDr = VectorNormalize(VectorSub(rayEnd, rayStart))
    for t in thing[4][0]:
        hit = RayIntersectMesh(rayStart, rayDr, t)
        if hit[0]:
            return hit
    return [False]

# Does a ray intersection test with each triangle
def RayIntersectThingComplex(rayStart, rayEnd, thing):
    rayDr = VectorNormalize(VectorSub(rayEnd, rayStart))
    for m in thing[0]:
        for t in TranslateTriangles(TransformTriangles(m[0], VectorAdd(m[1], thing[1])), VectorAdd(m[2], thing[2])):
            inrts = RayIntersectTriangle(rayStart, rayDr, t)
            if inrts[0]:
                return inrts
    return [False]


#==========================================================================
#  
# Collisions and Physics
#
#==========================================================================


# CollisionLoop() will return a list of lists, containing the two things that are colliding.
# Makes sure that there are no repeats in the list.

def GatherCollisions(thingList):
    results = []
    for me in range(0, len(thingList)):
        if thingList[me][4] != []:
            for ms in range(0, len(thingList)):

                # In order of speed
                if ms != me:
                    if ThingGetHitboxId(thingList[ms]) == ThingGetHitboxId(thingList[me]):
                        if thingList[ms][4] != []:
                            if [thingList[ms], thingList[me]] not in results:

                                myPos = ThingGetPos(thingList[me])
                                thPos = ThingGetPos(thingList[ms])
                                match ThingGetHitboxType(thingList[me]):
                                    case 0:
                                        # Sphere
                                        # Each object has a collision radius around it's origin, and if any object enters that radius, it's a hit.
                                        distance = DistanceBetweenVectors(myPos, thPos)
                                        if distance < ThingGetHitboxRadius(thingList[ms]):
                                            results.append([thingList[me], thingList[ms]])

                                    case 1:
                                        # Cylinder
                                        # The distance is measured with no vertical in mind, and a check to make sure it's within height
                                        if abs(thPos[2] - myPos[2]) <= ThingGetHitboxHeight(thingList[ms]):
                                            distance = DistanceBetweenVectors(Vector(myPos[0], 0, myPos[2]), Vector(thPos[0], 0, thPos[2]))
                                            if distance < ThingGetHitboxRadius(thingList[ms]):
                                                results.append([thingList[me], thingList[ms]])
                                    case 2:
                                        # Cube
                                        # Just a bunch of range checks
                                        thR = ThingGetHitboxRadius(thingList[ms])
                                        thH = ThingGetHitboxHeight(thingList[ms])
                                        myR = ThingGetHitboxRadius(thingList[me])
                                        myH = ThingGetHitboxHeight(thingList[me])
                                        if myPos[0] + thR > thPos[0] - thR and myPos[0] - thR < thPos[0] + thR:
                                            if myPos[1] + thH > thPos[1] - thH and myPos[1] - thH < thPos[1] + thH:
                                                if myPos[2] + thR > thPos[2] - thR and myPos[2] - thR < thPos[2] + thR:
                                                    results.append([thingList[me], thingList[ms]])
    return results

def BasicHandleCollisions(things):
    if not ThingGetMovable(things[0]):
        if not ThingGetMovable(things[1]):
            return
        newPos = VectorNegate(DirectionBetweenVectors(things[1][1], things[0][1]))
        things[1][1] = VectorAdd(things[1][1], newPos)
    else:
        newPos = VectorMulF(VectorNegate(DirectionBetweenVectors(things[0][1], things[1][1])), DistanceBetweenVectors(things[1][1], things[0][1]))
        things[0][1] = VectorAdd(things[0][1], newPos)

def HandlePhysics(thingList, floorHeight):
    global physTime
    delta = time.time() - physTime
    physTime = time.time()
    for t in thingList:
        if ThingGetMovable(t) and ThingGetPhysics(t) != []:

            ThingAddVelocity(t, ThingGetAcceleration(t))

            # Drag
            ThingSetVelocity(t, VectorSub(ThingGetVelocity(t), [ThingGetFriction(t) * sign(ThingGetVelocityX(t)), ThingGetFriction(t) * sign(ThingGetVelocityY(t)), ThingGetFriction(t) * sign(ThingGetVelocityZ(t))]))

            # Gravity

            ThingAddVelocity(t, VectorMulF(gravityDir, 0.05))

            ThingSetPos(t, VectorAdd(t[1], VectorMulF(ThingGetVelocity(t), delta)))
            ThingSetPosY(t, min(ThingGetPosY(t), floorHeight))

def PhysicsCollisions(thingList):
    for cols in GatherCollisions(thingList):
        if ThingGetPhysics(cols[0]) != []:
            force = VectorMulF(DirectionBetweenVectors(ThingGetPos(cols[0]), ThingGetPos(cols[1])), ThingGetMass(cols[0]))
            if ThingGetPhysics(cols[1]) != []:
                toforce = VectorAdd(force, VectorMulF(ThingGetVelocity(cols[1]), ThingGetMass(cols[1])))
                ThingAddVelocity(cols[0], toforce)
                ThingAddVelocity(cols[1], toforce)
            else:
                ThingAddVelocity(cols[0], force)
        else:
            if ThingGetPhysics(cols[1]) != []:
                force = VectorMulF(DirectionBetweenVectors(ThingGetPos(cols[1]), ThingGetPos(cols[0])), ThingGetMass(cols[1]))
                ThingAddVelocity(cols[1], toforce)

def sign(f):
    return 1 if f > 0 else -1


#==========================================================================
#  
# Rastering
#
#==========================================================================


# Raster functions return new triangles. Will not overwrite the old triangles.

# High-Level Raster Functions

def RasterThings(thingList):
    try:
        test = intMatV[0][0]
    except:
        print("ViewTriangles(): Internal Camera is not set. Use z3dpy.SetInternalCamera() before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in thingList:
            for m in t[0]:
                viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m))
        viewed.sort(key=triSortAverage, reverse=True)
        finished = RasterPt2(viewed)
        return tuple(finished)

def RasterThingsStatic(thingList):
    try:
        test = intMatV[0][0]
    except:
        print("ViewTriangles(): Internal Camera is not set. Use z3dpy.SetInternalCamera() before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in thingList:
            for m in t[0]:
                viewed += RasterPt1Static(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), MeshGetId(m), MeshGetColour(m))
        viewed.sort(key=triSortAverage, reverse=True)
        finished = RasterPt2(viewed)
        return finished

def DebugRasterThings(thingList):
    try:
        test = intMatV[0][0]
    except:
        print("ViewTriangles(): Internal Camera is not set. Use z3dpy.SetInternalCamera() before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for t in thingList:
            for m in t[0]:
                viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m))

            if t[4] != []:
                viewed += RasterPt1(MeshGetTris(ThingGetHitboxMesh(t)), ThingGetPos(t), [0, 0, 0], -1, [255, 0, 0])

            for l in lights:
                viewed += RasterPt1(lightMesh[0], l[0], [0, 0, 0], -1, [255, 255, 255])

            for r in rays:
                # [0] is ray start, [1] is ray direction
                viewed += RasterPt1Static([Triangle(r[0], VectorAdd(r[0], VectorMulF(r[1], 10)), VectorSub(r[0], [0, 0.1, 0]))], [0, 0, 0], -1, [255, 0, 0])

        viewed.sort(key = triSortAverage, reverse=True)
        finished = RasterPt2(viewed)
        return finished

def RasterMeshList(meshList):
    try:
        test = intMatV[0][0]
    except:
        print("ViewTriangles(): Internal Camera is not set. Use z3dpy.SetInternalCamera() before rastering.")
        return []
    else:
        finished = []
        viewed = []
        for m in meshList:
            viewed += RasterPt1(MeshGetTris(m), MeshGetPos(m), MeshGetRot(m), MeshGetId(m), MeshGetColour(m))
        viewed.sort(key=triSortAverage, reverse=True)
        finished = RasterPt2(viewed)
        return finished

internalTris = []

# Raster a single triangle, in hopes I can figure out multi-processing at some point.
# appends each new triangle to an internal triangle list.
def RasterTriangle(tri, pos, rot, id, colour):
    newTri = TriangleAdd(TransformTriangle(tri, rot), pos)
    if VectorDoP(GetNormal(newTri), iC[9]) > -0.4:
        newTri = ViewTriangle(newTri)
        internalTris.append(newTri)

def RasterPt1(tris, pos, rot, id, colour):
    translated = []
    prepared = []
    for tri in TransformTriangles(tris, rot):
        if VectorDoP(GetNormal(tri), VectorMul(iC[9], [-1, 1, 1])) > -0.4:
            prepared.append(tri)

    for t in ViewTriangles(TranslateTriangles(prepared, pos)):
        for r in TriangleClipAgainstZ(t):
            TriangleSetColour(r, colour)
            TriangleSetId(r, id)
            translated.append(r)
    return translated


def RasterPt1Static(tris, pos, id, colour):
    translated = []
    prepared = []
    for tri in tris:
        if VectorDoP(TriangleGetNormal(tri), iC[9]) > -0.4:
            prepared.append(tri)

    for t in ViewTriangles(TranslateTriangles(prepared, pos)):
        for r in TriangleClipAgainstZ(t):
            TriangleSetColour(r, colour)
            TriangleSetId(r, id)
            translated.append(r)
    return translated

def RasterPt2(tris):
    output = []
    for i in ProjectTriangles(tris):
        for s in TriangleClipAgainstScreenEdges(i):
            output.append(s)
    return output

# Low-Level Raster Functions
# Credit to Javidx9

def TransformTriangles(tris, rot):
    transformed = []
    mX = MatrixMakeRotX(rot[0])
    mY = MatrixMakeRotY(rot[1])
    mZ = MatrixMakeRotZ(rot[2])
    mW = MatrixMatrixMul(mX, mY)
    mW = MatrixMatrixMul(mW, mZ)
    for t in tris:
        nt = TriMatrixMul(t, mW)
        nt[3] = GetNormal(nt)
        transformed.append(nt)
    return tuple(transformed)

def TransformTriangle(tri, rot):
    mW = MatrixMatrixMul(MatrixMakeRotX(rot[0]), MatrixMakeRotY(rot[1]))
    mW = MatrixMatrixMul(mW, MatrixMakeRotZ(rot[2]))
    nt = TriMatrixMul(tri, mW)
    nt[3] = GetNormal(nt)
    return nt
        
def TranslateTriangles(tris, pos):
    translated = []
    for tri in tris:
        ntri = TriangleAdd(tri, pos)
        ntri[6] = TriangleAverage(ntri)
        translated.append(ntri)
    return tuple(translated)

def TranslateTriangle(tri, pos):
    newTri = TriangleAdd(tri, pos)
    newTri[6] = TriangleAverage(newTri)
    return newTri

def ViewTriangles(tris):
    output = []
    for tri in tris:
        output.append(TriMatrixMul(tri, intMatV))
    return tuple(output)

def ViewTriangle(tri):
    return TriMatrixMul(tri, intMatV)
                    
def ProjectTriangles(tris):
    projected = []
    for tri in tris:
        projected.append(TriangleMul(TriangleAdd(HowProjectTriangle(tri), [1, 1, 0]), [iC[6], iC[5], 1]))
    return tuple(projected)


#==========================================================================
#  
# Drawing/Shaders
#
#==========================================================================


# Pygame
# Pygame is the fastest at drawing, but installed separately.

def PgDrawTriangleRGB(tri, colour, surface, pyg):
    colour = VectorMaxF(colour, 0)
    pyg.draw.polygon(surface, tuple(colour), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleRGBF(tri, colour, surface, pyg):
    colour = VectorMaxF(colour, 0)
    pyg.draw.polygon(surface, tuple(VectorMulF(colour, 255)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleF(tri, f, surface, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleOutl(tri, colour, surface, pyg):
    colour = VectorMaxF(colour, 0)
    pyg.draw.lines(surface, tuple(VectorMulF(colour, 255)), True, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleS(tri, f, surface, pyg):
    f = max(f, 0)
    pyg.draw.polygon(surface, tuple(VectorMulF(tri[5], f)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Tkinter
# Slower, but almost always pre-installed

def TkDrawTriangleFill(tri, fillCol, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=fillCol)

def TkDrawTriangleF(tri, f, canvas):
    f = str(math.floor(max(f, 0) * 100))
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill="gray" + f)

def TkDrawTriangleOutl(tri, fillCol, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], outline=fillCol)

def TkDrawTriangleS(tri, fillCol, canvas):
    canvas.create_polygon([(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])], fill=fillCol)

# Flat lighting shader, meant to be put into DrawTriangleRGB's colour
# Takes the direction towards the light and compares that to a corrected normal.
def FlatLighting(tri):
    return LightingCalc(tri)

def LightingCalc(tri):
    shading = 0.0
    intensity = 0.0
    for l in lights:
        lightDir = DirectionBetweenVectors(l[0], TriangleGetWPos(tri))
        shading += (VectorDoP(lightDir, VectorMul(TriangleGetNormal(tri), [-1, 1, -1])) + 1) * 0.5
        intensity += min(DistanceBetweenVectors(TriangleGetWPos(tri), l[0]), l[2]) / l[2]
    return shading * ((1 - intensity)  ** 2)

def FlatLightingBaked(tri):
    return tri[4]

# Baked Lighting:
# Do the FlatLighting(), and bake it to the triangle's shader variable
def BakeLighting(things):
    print("Baking Lighting...")
    for th in things:
        for m in th[0]:
            for t in m[0]:
                calc = LightingCalc(TranslateTriangle(TransformTriangle(t, VectorAdd(MeshGetRot(m), ThingGetRot(th))), VectorAdd(MeshGetPos(m), ThingGetPos(th))))
                t[4] = calc
    print("Lighting Baked!")

def FillSort(n):
    return int(n[0])

# My own filling triangle routines so I can move beyond single-colour flat shading and single-triangle depth sorting.

# FillTriangleLine()
# Returns a tuple of lines to draw to the screen, given a triangle

# Part One: From P1 to P2

def TriangleToLines(tri):
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

# Usage:
#
# for tri in RasterThings(things):
#   for pixel in TriangleToPixels(tri):
#       x = pixel[0]
#       y = pixel[1]
#       pygame.draw.line(screen, (255, 255, 255), x, y, x + 1, y)
#

def TriangleToPixels(tri):
    output = []
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    if list[2][0] != list[0][0]:

        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])
        diff = int(list[1][0] - list[0][0])
        if diff != 0:

            diff3 = (list[1][1] - list[0][1]) / diff
            for x in range(diff + 1):
                range1 = int((diff3 * x) + list[0][1])
                range2 = int((slope * x) + list[0][1])
                daList = [range1, range2]
                daList.sort()
                for y in range(daList[0], daList[1]):

                    output.append((int(x + list[0][0]), y))

        output += FillTrianglePixelPt2(list, slope, diff)
    return tuple(output)

def FillTrianglePixelPt2(list, fSlope, diff):
    output = []
    if list[2][0] != list[1][0]:
        diff2 = int(list[2][0] - list[1][0])
        if diff2 != 0:
            slope2 = (list[2][1] - list[1][1]) / diff2
            for x in range(diff2):
                ranges = [int((slope2 * x) + list[1][1]), int((fSlope * (x + diff)) + list[0][1])]
                ranges.sort()
                for y in range(ranges[0], ranges[1]):
                    output.append((int(x + list[1][0]), y))
    return output


def PgPixelShader(tri, bufferArray, screenArray, pygame):
    z = int((tri[0][2] + tri[1][2] + tri[2][2]) / 3)
    shade = LightingCalc(tri) * 255
    for pixel in TriangleToPixels(tri):
        x = pixel[0]
        y = pixel[1]
        if bufferArray[x, y] > z or bufferArray[x, y] == 0:
            screenArray[x, y] = (shade, shade, shade)
            bufferArray[x, y] = z