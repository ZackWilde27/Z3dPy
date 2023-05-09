# Zack's 3D Engine
# or ZedPy for short
# Function/List Edition

# 0.1.4 Changes
#
# - Added IsMovable to things. When a thing is static, it won't calculate rotation, so that should speed things up if you don't need it
#
# - Quite a few drawing optimizations, much faster culling. Internal Camera has pretty much been eliminated, except for the View Matrix which should be calculated before everything.
#
# - Split CameraGetTarget() into CameraGetTargetLocation() and CameraGetTargetVector(). Vector will return the normalized direction, Location will return the world location.
# similarly, CameraSetTargetLocation() will set the location, CameraSetTargetVector() will set the direction relative to the camera.
#
# - Added a basic physics engine with delta calculations. Create a physics body for a Thing with myThing[10] = z3dpy.PhysicsBody(), then use z3dpy.HandlePhysics() and z3dpy.PhysicsCollisions() in your game loop.
#
# - Added TriangleSetNormal(), TriangleSetColour(), and TriangleSetWPos(). These things are set automatically during the raster process, but it's nice to have.
#
# - Replaced regular object functions with their V counterpart, as splitting the axis up can be done by making a new vector, like z3dpy.CameraSetPos(myCamera, [x, y, z])
#
# - Added CameraGetRightVector()
#
# - DrawTriangle*() functions have been changed to PgDrawTriangle*(), because I've added TkDrawTriangle*() functions.
#

import math
import time

print("Z3dPy v0.1.4")

#================
#  
# Variables
#
#================

# You can reference these at any time to get a global axis.
globalX = [1, 0, 0]
globalY = [0, 1, 0]
globalZ = [0, 0, 1]

#matRotZ = np.matrix([[1, 0, 0, 0], [0, math.cos((time.time() - track) / 2), math.sin((time.time() - track) / 2), 0], [0, -math.sin((time.time() - track) / 2), math.cos((time.time() - track) / 2), 0], [0, 0, 1, 0]])

# This is for drawing hitboxes and stuff, to-be-finished
debugThings = []

# Light list for FlatShading()
lights = []

gravityDir = [0, 9.8, 0]

drag = 0.1

physTime = time.time()




#================
#
# Object Functions
#
#================

# Most if not all the placements for variables are the same, so the OOP version is basically the more read-able version.

# Vector:
# [0] - [2] are the x y and z, [3] is the w

def Vector(x, y, z):
    return [x, y, z]

def Vector4(x, y, z, w):
    return [x, y, z, w]

# Triangles:
#[0] - [2] are the 3 points, [3] is the normal, [4] is the shader, [5] is colour, [6] is world position,
# and [7] is Id

def Triangle(vector1, vector2, vector3):
    return [vector1, vector2, vector3, GetNormal([vector1, vector2, vector3]), 0, [255, 255, 255], TriangleAverage([vector1, vector2, vector3]), 0]


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

# Meshes:
# [0] is the list of triangles, [1] is the position, [2] is the rotation, [3] is the colour, and [4] is the id

def Mesh(tris, x, y, z):
    return [tris, [x, y, z], [0, 0, 0], [255, 255, 255], 0]


def MeshSetTris(mesh, tris):
    mesh[0] = tris

def MeshGetTris(mesh):
    return mesh[0]

def MeshSetPos(mesh, vector):
    mesh[1] = vector

def MeshGetPos(mesh):
    return mesh[1]

def MeshSetRot(mesh, vector):
    mesh[2] = vector

def MeshAddRot(mesh, vector):
    mesh[2] = [(mesh[2][0] + vector[0]) % 360, (mesh[2][1] + vector[1]) % 360, (mesh[2][2] + vector[2]) % 360]

def MeshSubRot(mesh, vector):
    mesh[2] = [(mesh[2][0] - vector[0]) % 360, (mesh[2][1] - vector[1]) % 360, (mesh[2][2] - vector[2]) % 360]

def MeshMulRot(mesh, vector):
    mesh[2] = [(mesh[2][0] * vector[0]) % 360, (mesh[2][1] * vector[1]) % 360, (mesh[2][2] * vector[2]) % 360]

def MeshDivRot(mesh, vector):
    mesh[2] = [(mesh[2][0] / vector[0]) % 360, (mesh[2][1] / vector[1]) % 360, (mesh[2][2] / vector[2]) % 360]

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
# [0] is the list of meshes, [1] is position, [2] is rotation, [3] is object id, [4] is hitbox, [5] is IsMovable, and [6] is physics body
#
# I'm no computer scientist, but I'm assuming that a bigger list is worse, so hitbox and physics body are empty until you need them.

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], 0, [], True, []]



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

def ThingSetRotV(thing, v):
    thing[2] = v

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
    return thing[4][4]

def ThingGetHitboxHeight(thing):
    return thing[4][3]

def ThingGetHitboxRadius(thing):
    return thing[4][2]

def ThingGetHitboxId(thing):
    return thing[4][1]

def ThingGetHitboxType(thing):
    return thing[4][0]

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


# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
#
# For a third person camera, set the target to a location
# For a first person camera, set the target to a direction + the camera's location
#

# [0] is position, [1] is rotation, [2] is fov, [3] is screenHeight, [4] is screenWidth, [5] and [6] are half.
# [7] is near clip, [8] is far clip, [9] is target, [10] is up, [11] is theta, [12] is tan,
# and [13] is a
#

def Camera(x, y, z, scrW, scrH):
    return [[x, y, z], [0, 0, 0], 90, scrH, scrW, scrH / 2, scrW / 2, 0.1, 1500, [0, 0, 1], [0, 1, 0], 45, (1 / math.tan(45)), scrH / scrW]

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
    cam[11] = cam[2] / 2
    cam[12] = 1 / (math.tan(cam[11]))

def CameraGetFOV(cam):
    return cam[2]

def CameraSetScH(cam, h):
    cam[3] = h
    cam[5] = h / 2

def CameraGetScH(cam):
    return cam[3]

def CameraGetScHh(cam):
    return cam[5]

def CameraSetScW(cam, w):
    cam[4] = w
    cam[6] = w / 2

def CameraGetScW(cam):
    return cam[4]

def CameraGetScWh(cam):
    return cam[6]

def CameraSetNCl(cam, nc):
    cam[7] = nc

def CameraGetNCl(cam):
    return cam[7]

def CameraSetFCl(cam, fc):
    cam[8] = fc

def CameraGetFCl(cam):
    return cam[8]

# Deprecated
def CameraSetTarget(cam, x, y, z):
    CameraSetTargetVector(cam, [x, y, z])
def CameraSetTargetV(cam, v):
    CameraSetTargetVector(cam, v)

def CameraSetTargetLocation(cam, v):
    cam[9] = v

def CameraSetTargetVector(cam, v):
    cam[9] = VectorAdd(cam[0], VectorNormalize(v))

def CameraGetTargetLocation(cam):
    return cam[9]

def CameraGetTargetVector(cam):
    return VectorNormalize(VectorSub(cam[9], cam[0]))

def CameraSetUpVector(cam, vector):
    cam[10] = vector

def CameraGetUpVector(cam):
    return cam[10]

def CameraGetRightVector(cam):
    return VectorCrP(CameraGetTargetVector(cam), cam[10])


# Point Lights:
#
# Point lights will light up triangles that are inside the radius and facing towards it's location
#
# Used for the FlatShading() shader, which outputs a colour to be plugged into DrawTriangleRGB()
#

# [0] is position, [1] is strength, [2] is radius

def PointLight(x, y, z, strength, radius):
    return [[x, y, z], strength, radius]


# Textures are a matrix, so you can specify an X and Y number with myTexture[x][y]
# Unfinished for now, so think of it like a coding challenge.
def Texture(w, h):
    pixels = []
    for x in range (0, w):
        pixels.append([])
        for y in range(0, h):
            pixels[x].append(Vector(255, 255, 255))
    return pixels
        

#================
#  
# Misc Functions
#
#================

# Debug code for creating a basic cube
def NewCube(scale, x, y, z):
    return Mesh([
    # North
    Triangle(Vector(0, 0, 0), Vector(0, scale, 0), Vector(scale, scale, 0)),
    Triangle(Vector(0, 0, 0), Vector(scale, scale, 0), Vector(scale, 0, 0)),
    # East
    Triangle(Vector(scale, 0, 0), Vector(scale, scale, 0), Vector(scale, scale, scale)),
    Triangle(Vector(scale, 0, 0), Vector(scale, scale, scale), Vector(scale, 0, scale)),
    # South
    Triangle(Vector(scale, 0, scale), Vector(scale, scale, scale), Vector(0, scale, scale)),
    Triangle(Vector(scale, 0, scale), Vector(0, scale, scale), Vector(0, 0, scale)),
    # West
    Triangle(Vector(0, 0, scale), Vector(0, scale, scale), Vector(0, scale, 0)),
    Triangle(Vector(0, 0, scale), Vector(0, scale, 0), Vector(0, 0, 0)),
    # Top
    Triangle(Vector(scale, scale, 0), Vector(0, scale, 0), Vector(0, scale, scale)),
    Triangle(Vector(scale, scale, 0), Vector(0, scale, scale), Vector(scale, scale, scale)),
    # Bottom
    Triangle(Vector(scale, 0, 0), Vector(0, 0, 0), Vector(0, 0, scale)),
    Triangle(Vector(scale, 0, 0), Vector(0, 0, scale), Vector(scale, 0, scale))
], x, y, z)

def Projection(vector, a, f, fc, nc):
    # At the start I went the full formula route instead of matrix form, and
    # I kept it because it works.
    q = fc / (fc - nc)
    if vector[2] != 0:
        return [(a * f * vector[0]) / vector[2], (f * vector[1]) / vector[2], (q * vector[2]) - (q * nc)]
    else:
        return vector
    

def ProjectTriangle(t, a, f, fc, nc):
    return [Projection(t[0], a, f, fc, nc), Projection(t[1], a, f, fc, nc), Projection(t[2], a, f, fc, nc), t[3], t[4], t[5], t[6], t[7]]


#================
#  
# Vector Functions
#
#================

def VectorAdd(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def VectorSub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def VectorMul(v1, v2):
    return [v1[0] * v2[0], v1[1] * v2[1], v1[2] * v2[2]]

def VectorMulF(v1, f):
    return [v1[0] * f, v1[1] * f, v1[2] * f]

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
    l = VectorGetLength(v)
    if l != 0:
        return [v[0] / l, v[1] / l, v[2] / l]
    return v

# Vector Dot Product compares how similar two *normalized* vectors are, 1 is facing towards eachother, -1 is facing away from eachother. Useful for lighting calculations.
def VectorDoP(v1, v2):
    return (v1[0] * v2[0]) + (v1[1] * v2[1]) + (v1[2] * v2[2])

def VectorEqual(v1, v2):
    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]

def DistanceBetweenVectors(v1, v2):
    return math.sqrt(((v2[0] - v1[0]) ** 2) + ((v2[1] - v1[1]) ** 2) + ((v2[2] - v1[2]) ** 2))

def VectorNegate(v):
    return [v[0] * -1, v[1] * -1, v[2] * -1]

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))

def VectorRotateX(vec, deg):
    return MatrixMul(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return MatrixMul(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return MatrixMul(vec, MatrixMakeRotZ(deg))


#================
#  
# Triangle Functions
#
#================

def TriangleAdd(t, v):
    return [VectorAdd(t[0], v), VectorAdd(t[1], v), VectorAdd(t[2], v), t[3], t[4], t[5], t[6], t[7]]

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
    return VectorNormalize(normal)


def TriangleAverage(tri):
    return [(tri[0][0] + tri[1][0] + tri[2][0]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3]


# Sort Triangles based on their distance from the camera
def triSort(n):
    return  ((n[0][2] + n[1][2] + n[2][2]) / 2)


def TriangleClipAgainstZ(tri, camera):
    return TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], tri)

def TriangleClipAgainstScreenEdges(tri, camera):
    output = []
    for t in TriangleClipAgainstPlane([0, 0, 0], [0, 1, 0], tri):
        for r in TriangleClipAgainstPlane([0, camera[3] - 1, 0], [0, -1, 0], t):
            for i in TriangleClipAgainstPlane([0, 0, 0], [1, 0, 0], r):
                for s in TriangleClipAgainstPlane([camera[4] - 1, 0, 0], [-1, 0, 0], i):
                    output.append(s)
    return output

#================
#  
# Mesh Functions
#
#================

def MeshRotateX(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotX(deg))

def MeshRotateY(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotY(deg))

def MeshRotateZ(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotZ(deg))

# Load OBJ File
def LoadMeshScl(filename, x, y, z, sclX, sclY, sclZ):
    file = open(filename)
    verts = []
    vtCount = 0
    triangles = []
    currentLine = ""
    scaped = True
    while scaped:
        currentLine = file.readline()
        if currentLine == "":
            scaped = False
            break
        if currentLine[0] == 'v':
                currentLine = currentLine[2:].split(" ")
                verts.append([float(currentLine[0]) * sclX, float(currentLine[1]) * sclY, float(currentLine[2]) * sclZ])
            
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            newTriangle = Triangle(verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1])
            triangles.append(newTriangle)
        
    file.close()
    return Mesh(triangles, x, y, z)

def LoadMesh(filename, x, y, z):
    return LoadMeshScl(filename, x, y, z, 1, 1, 1)

lightMesh = LoadMesh("engine/mesh/light.obj", 0, 0, 0)


#================
#  
# Matrix Functions
#
#================

def GetTranslationMatrix(x, y, z):
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [x, y, z, 1]]

def TriMatrixMul(t, m):
    return [MatrixMul(t[0], m), MatrixMul(t[1], m), MatrixMul(t[2], m), t[3], t[4], t[5], t[6], t[7]]

def MatrixMul(v, m):
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


def PointAtMatrix(pos, target, up, cam):
    temp = MatrixStuff(pos, target, up)
    return [[temp[2][0], temp[2][1], temp[2][2], 0], [temp[1][0], temp[1][1], temp[1][2], 0], [temp[0][0], temp[0][1], temp[0][2], 0], [cam[0][0], cam[0][1], cam[0][2], 1]]

def LookAtMatrix(camera):
    temp = MatrixStuff(camera[0], camera[9], camera[10])
    return [[temp[2][0], temp[1][0], temp[0][0], 0], [temp[2][1], temp[1][1], temp[0][1], 0], [temp[2][2], temp[1][2], temp[0][2], 0], [-(VectorDoP(camera[0], temp[2])), -(VectorDoP(camera[0], temp[1])), -(VectorDoP(camera[0], temp[0])), 1]]


def MatrixMakeRotX(deg):
    rad = deg * 0.0174533
    return [[1, 0, 0, 0], [0, math.cos(rad / 2), math.sin(rad / 2), 0], [0, -math.sin(rad / 2), math.cos(rad / 2), 0], [0, 0, 0, 1]]

def MatrixMakeRotY(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), 0, math.sin(rad), 0], [0, 1, 0, 0], [-math.sin(rad), 0, math.cos(rad), 0], [0, 0, 0, 1]]

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), math.sin(rad), 0, 0], [-math.sin(rad), math.cos(rad), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

# Ended up going the formula route, but here's the matrix anyways
def MatrixMakeProjection(camera):
    return [[camera[13] * camera[12], 0, 0, 0], [0, camera[12], 0, 0], [0, 0, camera[8] / (camera[8] - camera[7]), 1], [0, 0, (-camera[8] * camera[7]) / (camera[8] - camera[7]), 0]]

#================       
#  
# Collisions and Physics
#
#================

# CollisionLoop() will return a list of lists, containing the two things that are colliding.

def GatherCollisions(thingList):
    results = []
    for me in range(0, len(thingList)):
        if thingList[me][4] != []:
            for ms in range(0, len(thingList)):
                if ms != me:
                    if thingList[ms][4] != []:
                        if ThingGetHitboxId(thingList[ms]) == ThingGetHitboxId(thingList[me]):
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
                                        radius = ThingGetHitboxRadius(thingList[ms])
                                        height = ThingGetHitboxHeight(thingList[ms])
                                        if myPos[0] > thPos[0] - radius and myPos[0] < thPos[0] + radius:
                                            if myPos[1] > thPos[1] - height and myPos[1] < thPos[1] + height:
                                                if myPos[2] > thPos[2] - radius and myPos[2] < thPos[2] + radius:
                                                    results.append([thingList[me], thingList[ms]])
    return results

def BasicHandleCollisions(things):
    # [9] is Movable
    if not ThingGetMovable(things[0]):
        if not ThingGetMovable(things[1]):
            return
        things[1][1] = VectorAdd(things[1][1], VectorNegate(DirectionBetweenVectors(things[1][1], things[0][1])))
    else:
        things[0][1] = VectorAdd(things[0][1], VectorMulF(VectorNegate(DirectionBetweenVectors(things[0][1], things[1][1])), DistanceBetweenVectors(things[1][1], things[0][1])))

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
        if cols[0][10] != []:
            force = VectorMulF(DirectionBetweenVectors(ThingGetPos(cols[0]), ThingGetPos(cols[1])), ThingGetMass(cols[0]))
            if cols[1][10] != []:
                toforce = VectorAdd(force, VectorMulF(ThingGetVelocity(cols[1]), ThingGetMass(cols[1])))
                ThingAddVelocity(cols[0], VectorNegate(toforce))
                ThingAddVelocity(cols[1], toforce)
            else:
                ThingAddVelocity(cols[0], VectorNegate(force))
        else:
            if cols[1][10] != []:
                force = VectorMulF(DirectionBetweenVectors(ThingGetPos(cols[1]), ThingGetPos(cols[0])), ThingGetMass(cols[1]))
                ThingAddVelocity(cols[1], VectorNegate(force))

def sign(f):
    # I know, but it's fast
    return 1 if f > 0 else 0 if f == 0 else -1


#================
#  
# Rastering
#
#================

def RasterThings(thingList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for t in thingList:
        for m in t[0]:
            if ThingGetMovable(t):
                viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m), camera)
            else:
                viewed += RasterPt1Static(MeshGetTris(m), MeshGetPos(m), MeshGetId(m), MeshGetColour(m), camera)
    viewed.sort(key = triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def DebugRasterThings(thingList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for t in thingList:
        for m in t[0]:
            if ThingGetMovable(t):
                viewed += RasterPt1(MeshGetTris(m), VectorAdd(MeshGetPos(m), ThingGetPos(t)), VectorAdd(MeshGetRot(m), ThingGetRot(t)), MeshGetId(m), MeshGetColour(m), camera)
            else:
                viewed += RasterPt1Static(MeshGetTris(m), MeshGetPos(m), MeshGetId(m), MeshGetColour(m), camera)
        viewed += RasterPt1(ThingGetHitboxMesh(t), ThingGetPos(t), [0, 0, 0], -1, [255, 0, 0], camera)

        for l in lights:
            viewed += RasterPt1(lightMesh[0], l[0], [0, 0, 0], -1, [255, 255, 255], camera)

    viewed.sort(key = triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def RasterMeshList(meshList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for m in meshList:
        viewed += RasterPt1(MeshGetTris(m), MeshGetPos(m), MeshGetRot(m), MeshGetId(m), MeshGetColour(m), camera)
    viewed.sort(key=triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def RasterPt1(tris, pos, rot, id, colour, camera):
    translated = []
    prepared = []
    for tri in TranslateTriangles(TransformTriangles(tris, rot), pos):
        if VectorDoP(TriangleGetNormal(tri), CameraGetTargetVector(camera)) < 0.4:
            prepared.append(tri)

    for t in ViewTriangles(prepared):
        for r in TriangleClipAgainstZ(t, camera):
            TriangleSetColour(r, colour)
            r[7] = id
            translated.append(r)
    return translated

def RasterPt1Static(tris, pos, id, colour, camera):
    translated = []
    prepared = []
    for tri in tris:
        if VectorDoP(TriangleGetNormal(tri), CameraGetTargetVector(camera)) < 0.4:
            prepared.append(tri)

    for t in ViewTriangles(TranslateTriangles(prepared, pos)):
        for r in TriangleClipAgainstZ(t, camera):
            r[5] = colour
            r[7] = id
            translated.append(r)
    return translated

def RasterPt2(tris, camera):
    output = []
    for i in ProjectTriangles(tris, camera):
        for s in TriangleClipAgainstScreenEdges(i, camera):
            output.append(s)
    return output

def SetInternalCamera(camera):
    global intMatV
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intMatV = LookAtMatrix(camera)


def TransformTriangles(tris, rot):
    transformed = []
    # Matrix Stuff  
    matRotY = MatrixMakeRotY(rot[1])
    matRotX = MatrixMakeRotX(rot[0])
    matRotZ = MatrixMakeRotZ(rot[2])
    for t in tris:
        nt = TriMatrixMul(t, matRotY)
        nt = TriMatrixMul(nt, matRotX)
        nt = TriMatrixMul(nt, matRotZ)
        nt[3] = GetNormal(nt)
        transformed.append(nt)
        
    return transformed
        
def TranslateTriangles(tris, pos):
    translated = []
    for tri in tris:
        # Moving triangle based on object position
        tri = TriangleAdd(tri, pos)
        tri[6] = TriangleAverage(tri)
        translated.append(tri)
    
    return translated

def ViewTriangles(tris):
    newTris = []
    for tries in tris:
        # Converting World Space to View Space
        newTri = TriMatrixMul(tries, intMatV)
        newTris.append(newTri)
    return newTris
                    
def ProjectTriangles(tris, camera):
    projected = []
    for tri in tris:
        # Flattening View Space
        newTri = TriangleAdd(ProjectTriangle(tri, camera[13], camera[12], CameraGetFCl(camera), CameraGetNCl(camera)), [1, 1, 0])

        # Converting to Screen Space
        newTri = TriangleMul(newTri, [CameraGetScWh(camera), CameraGetScHh(camera), 1])
        
        projected.append(newTri)
                        
    return projected


#================
#  
# Drawing/Shaders
#
#================

# Shortcuts for drawing to a screen.

# Pygame
# Pygame is the fastest at drawing.

def PgDrawTriangleRGB(tri, colour, surface, pyg):
    pyg.draw.polygon(surface, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleRGBF(tri, colour, surface, pyg):
    pyg.draw.polygon(surface, (max(colour[0], 0) * 255, max(colour[1], 0) * 255, max(colour[2], 0) * 255), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleF(tri, f, surface, pyg):
    f = min(max(f, 0), 1) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleOutl(tri, colour, surface, pyg):
    pyg.draw.lines(surface, (max(colour[0], 0) * 255, max(colour[1], 0) * 255, max(colour[2], 0) * 255), True, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def PgDrawTriangleS(tri, f, surface, pyg):
    f = min(max(f, 0), 1)
    pyg.draw.polygon(surface, (tri[5][0] * f, tri[5][1] * f, tri[5][2] * f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Tkinter

def TkDrawTriangleFill(tri, fillCol, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill=fillCol)

def TkDrawTriangleF(tri, f, canvas):
    f = max(f, 0)
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], fill="gray" + str(int(f * 100)))

def TkDrawTriangleOutl(tri, fillCol, canvas):
    canvas.create_polygon([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]], outline=fillCol)

def TkDrawTriangleS(tri, fillCol, canvas):
    canvas.create_polygon([(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])], fill=fillCol)


# Flat lighting shader, meant to be put into DrawTriangleRGB's colour
# Takes the direction towards the light and compares that to a corrected normal. Or at least it should in theory. Still working on this one.
def FlatLighting(tri):
    finalColour = [0, 0, 0]
    for l in lights:
        finalColour = VectorAdd(finalColour, VectorMulF(VectorMulF(tri[5], VectorDoP(VectorMul(TriangleGetColour(tri), [1, -1, -1]), DirectionBetweenVectors(tri[6], l[0]))), 1 - min(DistanceBetweenVectors(tri[6], l[0]) / l[2], 1)))
    return finalColour

def FillSort(n):
    return int(n[0])

# My own filling triangle routine so I can move beyond single-colour flat shading.

# Part One: From P1 to P2

def FillTriangle(tri, screen, colour, pyg):
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    # Trying to do as many calculations before I start as I can
    diff = int(list[1][0] - list[0][0])
    diff2 = int(list[1][1] - list[0][1])
    if list[2][0] != list[0][0]:
        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])
        if list[1][0] != list[0][0]:
            diff3 = (list[1][1] - list[0][1]) / (list[1][0] - list[0][0])
            for x in range(0, diff):
                lStart = (x + list[0][0], (diff3 * x) + list[0][1])
                lEnd = (x + list[0][0], (slope * x) + list[0][1])
                pyg.draw.line(screen, (max(colour[0], 15), max(colour[1], 15), max(colour[2], 15)), lStart, lEnd)
        FillTrianglePt2(list, screen, colour, pyg, slope)


# Part Two: From P2 to P3

def FillTrianglePt2(list, screen, colour, pyg, fSlope):
    # If this side is flat, no need.
    if list[2][1] != list[1][1] and list[2][0] != list[1][0]:
        diff2 = list[2][0] - list[1][0]
        diff4 = list[1][0] - list[0][0]
        slope2 = (list[2][1] - list[1][1]) / diff2
        for x in range(0, int(diff2)):
            lStart = (x + list[1][0], (slope2 * x) + list[1][1])
            lEnd = (x + list[1][0], (fSlope * (x + diff4)) + list[0][1])
            pyg.draw.line(screen, (max(colour[0], 15), max(colour[1], 15), max(colour[2], 15)), lStart, lEnd)
    else:
            return