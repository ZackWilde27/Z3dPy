# Zack's 3D Engine
# or ZedPy for short
# Function/List Edition

# 0.1.2 Changes
#
# - Added IsMovable to things. When a thing is static, it won't calculate rotation, so that should speed things up if you don't need it
#
# - Quite a few drawing optimizations, much faster culling. Internal Camera has pretty much been eliminated, except for the View Matrix which should be calculated before everything.
#
# - Split CameraSetTarget() into CameraSetTargetWorld() and CameraSetTargetDirection(). World will point at a location, Direction will point in a direction relative to the camera.
# similarly, CameraGetTargetWorld() will get the un-altered target, CameraGetTargetDirection() will get the direction the camera is facing.
#

import math
import time

print("Z3dPy v0.1.2")

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
Lights = []

gravityDir = [0, 0.1, 0]


#================
#
# Object Functions
#
#================

# Vector:
# [0] - [2] are the x y and z, [3] is the w

def Vector(x, y, z):
    return [x, y, z]

def Vector4(x, y, z, w):
    return [x, y, z, w]

# Triangles:
#[0] - [2] are the 3 points, [3] is the normal, [4] is a user variable, [5] is colour, [6] is world position,
# and [7] is Id

def Triangle(v1, v2, v3):
    return [v1, v2, v3, GetNormal([v1, v2, v3]), 0, [255, 255, 255], TriangleAverage([v1, v2, v3]), 0]


# GetNormal() will calculate a new normal, TriangleGetNormal() will not.
def TriangleGetNormal(tri):
    return tri[3]

def TriangleGetColour(tri):
    return tri[5]

def TriangleGetWPos(tri):
    return tri[6]

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

def MeshSetPos(mesh, x, y, z):
    mesh[1] = [x, y, z]

def MeshSetPosV(mesh, v):
    mesh[1] = v

def MeshGetPos(mesh):
    return mesh[1]

def MeshSetRot(mesh, x, y, z):
    mesh[2] = [x, y, z]

def MeshAddRot(mesh, x, y, z):
    mesh[2] = [mesh[2][0] + x, mesh[2][1] + y, mesh[2][2] + z]

def MeshSubRot(mesh, x, y, z):
    mesh[2] = [(mesh[2][0] - x) % 360, (mesh[2][1] - y) % 360, (mesh[2][2] - z) % 360]

def MeshMulRot(mesh, x, y, z):
    mesh[2] = [(mesh[2][0] * x) % 360, (mesh[2][1] * y) % 360, (mesh[2][2] * z) % 360]

def MeshDivRot(mesh, x, y, z):
    mesh[2] = [(mesh[2][0] / x) % 360, (mesh[2][1] / y) % 360, (mesh[2][2] / z) % 360]

def MeshGetRot(mesh):
    return mesh[2]

def MeshSetColour(mesh, r, g, b):
    mesh[3] = [r, g, b]

def MeshGetColour(mesh):
    return mesh[3]

def MeshSetId(mesh, id):
    mesh[4] = id

def MeshGetId(mesh):
    return mesh[4]


# Things:
#
# The Thing is what you would typically refer to as an object, it has a collection of meshes, and collision data.
#
#
# [0] is the list of meshes, [1] is position, [2] is rotation, [3] is object id, [4] is hitbox mesh, [5] is hitbox radius,
# [6] is hitbox height, [7] is collision id [8] is collision type, and [9] is IsMovable, and [10] is velocity
#

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], 0, LoadMesh("engine/mesh/cube.obj", x, y, z), 1, 1, 0, 2, True, [0, 0, 0]]


# SetCollisionParams(type, radius, height, id) will set the collision data and update the hitbox, for drawing to the screen.
# Type: 0 = Sphere, 1 = Cylinder, 2 = Cube
# Radius: radius of the sphere/cylinder, or length of the cube
# Height: height of the cylinder/cube.
# Id: Objects with the same ID will check for collisions. Everything is 0 by default, so if unsure, use that.
# Hitbox Mesh: not used, it's meant for drawing to the screen when debugging.

def ThingSetCollisionParams(thing, type, radius, height, id):
    thing[8] = type
    thing[5] = radius
    thing[6] = height
    thing[7] = id
    match type:
        case 0:
            thing[4] = LoadMeshScl("engine/mesh/sphere.obj", thing[1][0], thing[1][1], thing[1][2], radius, radius, radius)
        case 1:
            thing[4] = LoadMeshScl("engine/mesh/cylinder.obj", thing[1][0], thing[1][1], thing[1][2], radius, height, radius)
        case 2:
            thing[4] = LoadMeshScl("engine/mesh/cube.obj", thing[1][0], thing[1][1], thing[1][2], radius, height, radius)



def ThingSetPos(thing, x, y, z):
    thing[1] = [x, y, z]

def ThingSetPosV(thing, v):
    thing[1] = v

def ThingAddPos(thing, x, y, z):
    thing[1] = [thing[1][0] + x, thing[1][1] + y, thing[1][2] + z]

def ThingSubPos(thing, x, y, z):
    thing[1] = [thing[1][0] - x, thing[1][1] - y, thing[1][2] - z]

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

def ThingSetRot(thing, x, y, z):
    thing[2] = [x, y, z]

def ThingSetRotV(thing, vector):
    thing[2] = vector

def ThingAddRot(thing, x, y, z):
    thing[2] = VectorAdd(thing[2], [x, y, z])

def ThingAddRotV(thing, vector):
    thing[2] = VectorAdd(thing[2], vector)

def ThingSubRot(thing, x, y, z):
    thing[2] = VectorSub(thing[2], [x, y, z])

def ThingMulRot(thing, x, y, z):
    thing[2] = VectorMul(thing[2], [x, y, z])

def ThingDivRot(thing, x, y, z):
    thing[2] = VectorDiv(thing[2], [x, y, z])

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

def ThingSetMovable(thing, isMovable):
    thing[9] = isMovable

def ThingGetMovable(thing):
    return thing[9]



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

def Camera(x, y, z, scrW, scrH):
    return [[x, y, z], [0, 0, 0], 90, scrH, scrW, scrH / 2, scrW / 2, 0.1, 1500, [0, 0, 1], [0, 1, 0], 45, (1 / math.tan(45)), scrH / scrW]

def CameraSetPos(cam, x, y, z):
    cam[0] = [x, y, z]

def CameraSetPosX(cam, x):
    cam[0] = [x, cam[0][1], cam[0][2]]

def CameraSetPosY(cam, y):
    cam[0] = [cam[0][0], y, cam[0][2]]

def CameraSetPosZ(cam, z):
    cam[0] = [cam[0][0], cam[0][1], z]

def CameraSetPosV(cam, v):
    cam[0] = v

def CameraAddPos(cam, x, y, z):
    cam[0] = [cam[0][0] + x, cam[0][1] + y, cam[0][2] + z]

def CameraAddPosV(cam, v):
    cam[0] = VectorAdd(cam[0], v)

def CameraSubPos(cam, x, y, z):
    cam[0] = [cam[0][0] - x, cam[0][1] - y, cam[0][2] - z]

def CameraSubPosV(cam, v):
    cam[0] = VectorSub(cam[0], v)

def CameraMulPos(cam, x, y, z):
    cam[0] = [cam[0][0] * x, cam[0][1] * y, cam[0][2] * z]

def CameraMulPosV(cam, v):
    cam[0] = VectorMul(cam[0], v)

def CameraDivPos(cam, x, y, z):
    cam[0] = [cam[0][0] / x, cam[0][1] / y, cam[0][2] / z]

def CameraDivPosF(cam, f):
    cam[0] = VectorDivF(cam[0], f)

def CameraModPos(cam, x, y, z):
    cam[0] = [cam[0][0] % x, cam[0][1] % y, cam[0][2] % z]

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

def CameraSetRot(cam, x, y, z):
    cam[1] = [x % 360, y % 360, z % 360]

def CameraSetRotV(cam, v):
    cam[1] = v

def CameraAddRot(cam, x, y, z):
    cam[1] = [(cam[1][0] + x) % 360, (cam[1][1] + y) % 360, (cam[1][2] + z) % 360]

def CameraAddRotV(cam, v):
    cam[1] = VectorAdd(cam[1], v)

def CameraSubRot(cam, x, y, z):
    cam[1] = [cam[1][0] - x, cam[1][1] - y, cam[1][2] - z]

def CameraSubRotV(cam, v):
    cam[1] = VectorSub(cam[1], v)

def CameraMulRot(cam, x, y, z):
    cam[1] = [cam[1][0] * x, cam[1][1] * y, cam[1][2] * z]

def CameraMulRotV(cam, v):
    cam[1] = VectorMul(cam[1], v)

def CameraDivRot(cam, x, y, z):
    cam[1] = [cam[1][0] / x, cam[1][1] / y, cam[1][2] / z]

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

def CameraSetScW(cam, w):
    cam[4] = w
    cam[6] = w / 2

def CameraGetScW(cam):
    return cam[4]

def CameraSetNCl(cam, nc):
    cam[7] = nc

def CameraGetNCl(cam):
    return cam[7]

def CameraSetFCl(cam, fc):
    cam[8] = fc

def CameraGetFCl(cam):
    return cam[8]

# Deprecated in favour of CameraSetTargetWorld()

def CameraSetTarget(cam, x, y, z):
    CameraSetTargetWorld(cam, x, y, z)

def CameraSetTargetV(cam, v):
    CameraSetTargetWorldV(cam, v)


def CameraSetTargetWorld(cam, x, y, z):
    cam[9] = [x, y, z]

def CameraSetTargetDirection(cam, x, y, z):
    cam[9] = VectorAdd(cam[0], VectorNormalize([x, y, z]))

def CameraSetTargetWorldV(cam, v):
    cam[9] = v

def CameraSetTargetDirectionV(cam, v):
    cam[9] = VectorAdd(cam[0], VectorNormalize(v))

def CameraGetTargetWorld(cam):
    return cam[9]

def CameraGetTargetDirection(cam):
    return VectorSub(cam[9], cam[0])

def CameraSetUp(cam, x, y, z):
    cam[10] = [x, y, z]

def CameraSetUpV(cam, v):
    cam[10] = v

def CameraGetUp(cam):
    return cam[10]


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
    
# but here's the matrix if you're curious
# (I haven't tested it in a while so for all I know, maybe it's wrong)
#ProjectionMatrix = [[CamA * CamTan, 0, 0, 0], [0, CamTan, 0, 0], [0, 0, CamFC / (CamFC - CamNC), 1], [0, 0, (-CamFC * CamNC) / (CamFC - CamNC), 0]]

def ProjectTriangle(t, a, f, fc, nc):
    return [Projection(t[0], a, f, fc, nc), Projection(t[1], a, f, fc, nc), Projection(t[2], a, f, fc, nc), t[3], t[4], t[5], t[6], t[7]]


#================
#  
# Vector Functions
#
#================

def VectorNormalize(v):
    l = VectorGetLength(v)
    if l != 0:
        return [v[0] / l, v[1] / l, v[2] / l]
    return v

def VectorAdd(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def VectorSub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def VectorMul(v1, v2):
    return [v1[0] * v2[0], v1[1] * v2[1], v1[2] * v2[2]]

def VectorMulF(v1, f):
    return [v1[0] * f, v1[1] * f, v1[2] * f]

def VectorCrP(v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

def VectorDiv(v1, v2):
    return [v1[0] / v2[0], v1[1] / v2[1], v1[2] / v2[2]]

def VectorDivF(v, f):
    return [v[0] / f, v[1] / f, v[2] / f]

def VectorGetLength(v):
    return math.sqrt((v[0] * v[0]) + (v[1] * v[1]) + (v[2] * v[2]))

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

#================       
#  
# OBJ Functions
#
#================

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
            if currentLine[1] == 't':
                currentLine = currentLine[3:].split(" ")
                verts[vtCount].u = currentLine[0]
                verts[vtCount].v = currentLine[1]
                vtCount += 1
            else:
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

#================       
#  
# Collision Loop
#
#================

# CollisionLoop() will return a list of lists, containing the two things that are colliding.

def CollisionLoop(thingList):
    results = []
    for me in range(0, len(thingList)):
        for ms in range(0, len(thingList)):
            if ms != me:
                if thingList[ms][7] == thingList[me][7]:
                    if [thingList[ms], thingList[me]] not in results:
                        myPos = thingList[me][1]
                        thPos = thingList[ms][1]
                        match thingList[me][8]:
                            case 0:
                                # Sphere
                                # Each object has a collision radius around it's origin, and if any object enters that radius, it's a hit.
                                distance = DistanceBetweenVectors(myPos, thPos)
                                if distance < thingList[ms][5]:
                                    results.append([thingList[me], thingList[ms]])

                            case 1:
                                # Cylinder
                                # The distance is measured with no vertical in mind, and a check to make sure it's within height
                                distance = DistanceBetweenVectors(Vector(myPos[0], 0, myPos[2]), Vector(thPos[0], 0, thPos[2]))
                                if distance < thingList[ms][5] and abs(thPos[2] - myPos[2]) <= thingList[ms][6]:
                                    results.append([thingList[me], thingList[ms]])
                            case 2:
                                # Cube

                                # In order to simplify, I'm subtracting the positions, adding the absolute axis together, to see if it's within range
                                distance = VectorSub(thPos, myPos)
                                distance = abs(distance[0]) + abs(distance[1]) + abs(distance[2])
                                if distance <= thingList[ms][5] * 3:
                                    results.append([thingList[me], thingList[ms]])

                            case 3:
                            # All Triangles
                            # Accurate but SLOW
                            # Unfinished
                                """
                                for ms in range(0, len(meshList)):
                                    if ms != me and meshList[ms].collisionId == meshList[me].collisionId:
                                        dir = DirectionBetweenVectors(meshList[me].pos, meshList[ms].pos)
                                        # Calculate the intersection of a ray with a triangle using the Thomas Moller alogrithm
                                        for tri in meshList[me].tris:
                                            for tri2 in meshList[ms].tris:
                                                n2 = GetNormal(tri2)
                                                d2 = -VectorDoP(n2, tri2.p1)
                                                n1 = GetNormal(tri)
                                                d1 = -VectorDoP(n1, tri.p1)

                                                dv1 = VectorDoP(n1, tri2.p1) + d1
                                                dv2 = VectorDoP(n1, tri2.p2) + d1
                                                dv3 = VectorDoP(n1, tri2.p3) + d1
                                                # Getting rid of irrelevant triangles
                                                if dv1 == 0 and dv2 == 0 and dv3 == 0:
                                                    break
                                                else:
                                                    if dv1 < 0 and dv2 < 0 and dv3 < 0 or dv1 > 0 and dv2 > 0 and dv3 > 0:
                                                        break
                                                
                                                dt1 = VectorDoP(n2, tri.p1) + d2
                                                dt2 = VectorDoP(n2, tri.p2) + d2
                                                dt3 = VectorDoP(n2, tri.p3) + d2
                                                # Same thing on the other side
                                                if dt1 == 0 and dt2 == 0 and dt3 == 0:
                                                    break
                                                else:
                                                    if dt1 < 0 and dt2 < 0 and dt3 < 0 or dt1 > 0 and dt2 > 0 and dt3 > 0:
                                                        break

                                                # Plane Intersection
                                                pi2 = VectorDoP(n2, tri2.p1) + d2
                                                pi1 = VectorDoP(n1, tri.p1) + d1
                                                if pi1 == 0 and pi2 == 0:
                                                    print("Triangle Hit")
                                """
    return results

def HandleCollisions(things):
    # [9] is Movable
    if not things[0][9]:
        if not things[1][9]:
            return
        things[1][1] = VectorAdd(things[1][1], VectorNegate(DirectionBetweenVectors(things[1][1], things[0][1])))
    else:
        things[0][1] = VectorAdd(things[0][1], VectorMulF(VectorNegate(DirectionBetweenVectors(things[0][1], things[1][1])), DistanceBetweenVectors(things[1][1], things[0][1])))

def HandlePhysics(thingList, floorHeight):
    for t in thingList:
        if t[9]:
            t[10] = VectorAdd(t[10], gravityDir)
            t[1] = VectorAdd(t[1], t[10])
            t[1][1] = min(t[1][1], floorHeight)
    CollisionLoop(thingList)



#================
#  
# Rendering
#
#================

def RasterThings(thingList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for t in thingList:
        for m in t[0]:
            if t[9]:
                viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]), m[4], m[3], camera)
            else:
                viewed += RasterPt1Static(m[0], m[1], m[4], m[3], camera)
    viewed.sort(key = triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def DebugRasterThings(thingList, camera):
    global lightMesh
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for t in thingList:
        for m in t[0]:
            if t[9]:
                viewed += RasterPt1(m[0], VectorAdd(m[1], t[1]), VectorAdd(m[2], t[2]), m[4], m[3], camera)
            else:
                viewed += RasterPt1Static(m[0], m[1], m[4], m[3], camera)

        viewed += RasterPt1(t[4][0], t[1], [0, 0, 0], -1, [255, 0, 0], camera)

        for l in Lights:
            viewed += RasterPt1(lightMesh[0], l[0], [0, 0, 0], -1, [255, 255, 255], camera)

    viewed.sort(key = triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def RasterMeshList(meshList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for m in meshList:
        viewed += RasterPt1(m[0], m[1], m[2], m[4], m[3], camera)
    viewed.sort(key=triSort, reverse=True)
    finished = RasterPt2(viewed, camera)
    return finished

def RasterPt1(tris, pos, rot, id, colour, camera):
    translated = []
    prepared = []
    for tri in TransformTriangles(tris, rot):
        if VectorDoP(tri[3], VectorSub(camera[9], camera[0])) < 0.4:
            prepared.append(tri)

    for c in ViewTriangles(TranslateTriangles(prepared, pos)):
        for r in TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], c):
            r[5] = colour
            r[7] = id
            translated.append(r)
    return translated

def RasterPt1Static(tris, pos, id, colour, camera):
    translated = []
    prepared = []
    for tri in tris:
        if VectorDoP(tri[3], camera[9]) < 0.4:
            prepared.append(tri)

    for c in ViewTriangles(TranslateTriangles(prepared, pos)):
        for r in TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], c):
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
        newTri = TriangleAdd(ProjectTriangle(tri, camera[13], camera[12], camera[8], camera[7]), [1, 1, 0])

        # Converting to Screen Space
        newTri = TriangleMul(newTri, [camera[6], camera[5], 1])
        
        projected.append(newTri)
                        
    return projected


#================
#  
# Drawing/Shaders
#
#================

# Shortcuts for drawing to a PyGame screen.

def DrawTriangleRGB(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleRGBF(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour[0], 0) * 255, max(colour[1], 0) * 255, max(colour[2], 0) * 255), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleF(tri, surface, f, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleOutl(tri, surface, colour, pyg):
    pyg.draw.lines(surface, (max(colour[0], 0) * 255, max(colour[1], 0) * 255, max(colour[2], 0) * 255), True, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleS(tri, surface, f, pyg):
    f = max(f, 0)
    pyg.draw.polygon(surface, (tri[5][0] * f, tri[5][1] * f, tri[5][2] * f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Flat lighting shader, meant to be put into DrawTriangleRGB's colour
# Takes the direction towards the light and compares that to a corrected normal. Or at least it should in theory. Still working on this one.
def FlatLighting(tri):
    finalColour = [0, 0, 0]
    for l in Lights:
        finalColour = VectorAdd(finalColour, VectorMulF(VectorMulF(tri[5], VectorDoP(VectorMul(tri[3], [1, 1, -1]), DirectionBetweenVectors(tri[6], l[0]))), 1 - min(DistanceBetweenVectors(tri[6], l[0]) / l[2], 1)))
    return finalColour


def FillSort(n):
    return int(n[0])

# My own filling triangle routine so I can move beyond flat shading.

# Part One: From P1 to P2

def FillTriangle(tri, colour, screen, pyg):
    list = [tri[0], tri[1], tri[2]]
    list.sort(key=FillSort)

    # Trying to do as many calculations before I start as I can
    diff = int(list[1][0] - list[0][0])
    if list[2][0] != list[0][0]:
        slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0])
    else:
        slope = (list[2][1] - list[0][1])

    if list[0][1] == list[1][1]:
        # Flat-Top Triangle
        for x in range(0, abs(diff)):
            lStart = (x + list[0][0], list[0][1])
            lEnd = (x + list[0][0], (slope * x) + list[0][1])
            pyg.draw.line(screen, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), lStart, lEnd)
        FillTrianglePt2(list, True, screen, colour, pyg, diff)
    else:
        if list[1][0] != list[0][0]:
            # More Complicated Triangle
            diff3 = (list[1][1] - list[0][1]) / (list[1][0] - list[0][0])
            for x in range(0, abs(diff)):
                lStart = (x + list[0][0], (diff3 * x) + list[0][1])
                lEnd = (x + list[0][0], (slope * x) + list[0][1])
                pyg.draw.line(screen, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), lStart, lEnd)
            FillTrianglePt2(list, False, screen, colour, pyg, slope)


# Part Two: From P2 to P3

def FillTrianglePt2(list, flat, screen, colour, pyg, fSlope):
    # If this side is flat, no need.
    if list[2][1] != list[1][1]:
        #slope = (list[2][1] - list[0][1]) / (list[2][0] - list[0][0]) if list[2][0] != list[0][0] else list[2][1] - list[0][1]
        slope = fSlope
        slope2 = (list[2][1] - list[1][1]) / (list[2][0] - list[1][0]) if list[2][0] != list[1][0] else list[2][1] - list[1][1]
        # this flat refers to p1 and p2
        if flat:
            for x in range(0, int(list[2][0] - list[1][0])):
                lStart = (x + list[1][0], (slope2 * x) + list[1][1])
                lEnd = (x + list[0][0], (slope * x) + list[0][1])
                pyg.draw.line(screen, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), lStart, lEnd)
            
        else:
            for x in range(0, int(list[2][0] - list[1][0])):

                lStart = (x + list[1][0], (slope2 * x) + list[1][1])
                lEnd = (x + list[1][0], (slope * x) + list[0][1])
                pyg.draw.line(screen, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), lStart, lEnd)
    else:
            return
    

lightMesh = LoadMesh("engine/mesh/light.obj", 0, 0, 0)
