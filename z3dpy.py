# Zack's 3D Engine
# or ZedPy for short

# 0.0.6 Changes
#
# - New Function version. Everything is a list now, which is faster than object-oriented programming, but more difficult to work with.
# To help with this, I've added functions that start with the object name, like MeshGetPos() and ThingSetPosY() as shortcuts.
#

import math

print("Z3dPy v0.0.6")

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


def TriangleGetNormal(tri):
    # My engine has flipped normals, so flipping it back
    return VectorMulF(tri[3], -1)

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
# [6] is hitbox height, [7] is collision id and [8] is collision type.

def Thing(meshList, x, y, z):
    return [meshList, [x, y, z], [0, 0, 0], 0, LoadMesh("engine/mesh/cube.obj", x, y, z), 1, 1, 0, 2]



# SetCollisionParams(type, radius, height, id) will set the collision data and update the hitbox, for drawing to the screen.
# Type: 0 = Sphere, 1 = Cylinder, 2 = Cube
# Radius: radius of the hitbox
# Height: height of the cylinder, if it's a cylinder.
# Id: Objects with the same ID will check for collisions. Everything is 0 by default, so if unsure, use that.

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
            thing[4] = LoadMeshScl("engine/mesh/cube.obj", thing[1][0], thing[1][1], thing[1][2], radius, radius, radius)



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



# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
# For the uninitiated, "direction" in this case simply refers to a vector between -1 and 1, like +Z direction is 0, 0, 1, and -Z direction is 0, 0, -1
#
# For a third person camera, set the target to a location
# For a first person camera, set the target to a direction + the camera's location
#

# [0] is position, [1] is rotation, [2] is fov, [3] is screenHeight, [4] is screenWidth, [5] and [6] are half.
# [7] is near clip, [8] is far clip, [9] is target, [10] is forward, [11] is up, [12] is theta, [13] is tan,
# and [14] is a

def Camera(x, y, z, scrW, scrH):
    return [[x, y, z], [0, 0, 0], 90, scrH, scrW, scrH / 2, scrW / 2, 0.1, 1500, [0, 0, 1], [0, 0, 1], [0, 1, 0], 45, (1 / math.tan(45)), scrH / scrW]


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

def CameraGetForward(cam):
    return cam[10]

def CameraSetTarget(cam, x, y, z):
    cam[9] = [x, y, z]

def CameraSetTargetV(cam, v):
    cam[9] = v

def CameraGetTarget(cam):
    return cam[9]

def CameraSetUp(cam, x, y, z):
    cam[11] = [x, y, z]

def CameraSetUpV(cam, v):
    cam[11] = v

def CameraGetUp(cam):
    return cam[11]

# Unfinished, but right now it's much easier to make a third person game, so I'm planning
# a first person camera object that makes it easier.

class FirstPersonCamera:
    def __init__(self, x, y, z, sW, sH, fov, near, far):
        self.cam = Camera(x, y, z, sW, sH, fov, near, far)


# Textures are a matrix, so you can specify an X and Y number with myTexture[x][y]
# Unfinished
def Texture(w, h):
    pixels = []
    for x in range (0, w):
        pixels.append([])
        for y in range(0, h):
            pixels[x].append(Vector(255, 255, 255))
    return pixels


#================       
#  
# Variables
#
#================

globalX = [1, 0, 0]
globalY = [0, 1, 0]
globalZ = [0, 0, 1]

#ProjectionMatrix = np.matrix([[CamAspR * CamTan, 0, 0, 0], [0, CamTan, 0, 0], [0, 0, CamFC / (CamFC - CamNC), 1], [0, 0, (-CamFC * CamNC) / (CamFC - CamNC), 0]])

#matRotZ = np.matrix([[1, 0, 0, 0], [0, math.cos((time.time() - track) / 2), math.sin((time.time() - track) / 2), 0], [0, -math.sin((time.time() - track) / 2), math.cos((time.time() - track) / 2), 0], [0, 0, 1, 0]])

showCollisions = True

debugThings = []
        

# Functions
# There's a lot of them.

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
    #a = CamAspR
    #f = 1 / math.tan(CamTheta)
    q = fc / (fc - nc)
    if vector[2] != 0:
        return [(a * f * vector[0]) / vector[2], (f * vector[1]) / vector[2], (q * vector[2]) - (q * nc)]
    else:
        return vector

def ProjectTriangle(t, a, f, fc, nc):
    return [Projection(t[0], a, f, fc, nc), Projection(t[1], a, f, fc, nc), Projection(t[2], a, f, fc, nc), t[3], t[4], t[5], t[6], t[7]]


# Vector Functions

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

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))


# Triangle Functions

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

def TriangleCullTestZ(t):
    return t[0][2] > 0.1 and t[0][2] > 0.1 and t[0][2] > 0.1

def TriangleCullTestXY(t):
    return t[0][0] > -5 and t[1][0] > -5 and t[2][0] > -5 and t[0][1] > -5 and t[1][1] > -5 and t[2][1] > -5

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

# Returns the direction a triangle is facing
def GetNormal(tri):
    triLine1 = VectorSub(tri[1], tri[0])
    triLine2 = VectorSub(tri[2], tri[0])
    normal = VectorCrP(triLine1, triLine2)
    # Y and Z are flipped
    return VectorNormalize(normal)


# Shortcuts for drawing to a PyGame screen.
def DrawTriangleRGB(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour[0], 0), max(colour[1], 0), max(colour[2], 0)), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleF(tri, surface, f, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

def DrawTriangleS(tri, surface, f, pyg):
    f = max(f, 0)
    pyg.draw.polygon(surface, (tri[5][0] * f, tri[5][1] * f, tri[5][2] * f), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Averages all points together to get the center point.
def TriangleAverage(tri):
    return [(tri[0][0] + tri[1][0] + tri[2][0]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3]


# Sort Triangles based on their distance from the camera
def triSort(n):
    return (intCam[8] + intCam[7]) - ((n[0][2] + n[1][2] + n[2][2]) / 3)

def VectorRotateX(vec, deg):
    return MatrixMul(vec, MatrixMakeRotX(deg))

def VectorRotateY(vec, deg):
    return MatrixMul(vec, MatrixMakeRotY(deg))

def VectorRotateZ(vec, deg):
    return MatrixMul(vec, MatrixMakeRotZ(deg))

def MeshRotateX(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotX(deg))

def MeshRotateY(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotY(deg))

def MeshRotateZ(msh, deg):
    for tri in msh.tris:
        tri = TriMatrixMul(tri, MatrixMakeRotZ(deg))


# Matrix Functions

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
    # Now for the matrix
    return [[temp[2][0], temp[2][1], temp[2][2], 0], [temp[1][0], temp[1][1], temp[1][2], 0], [temp[0][0], temp[0][1], temp[0][2], 0], [cam[0][0], cam[0][1], cam[0][2], 1]]

def LookAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    # Now for the matrix
    return [[temp[2][0], temp[1][0], temp[0][0], 0], [temp[2][1], temp[1][1], temp[0][1], 0], [temp[2][2], temp[1][2], temp[0][2], 0], [-(VectorDoP(intCam[0], temp[2])), -(VectorDoP(intCam[0], temp[1])), -(VectorDoP(intCam[0], temp[0])), 1]]


def MatrixMakeRotX(deg):
    rad = deg * 0.0174533
    return [[1, 0, 0, 0], [0, math.cos(rad / 2), math.sin(rad / 2), 0], [0, -math.sin(rad / 2), math.cos(rad / 2), 0], [0, 0, 0, 1]]

def MatrixMakeRotY(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), 0, math.sin(rad), 0], [0, 1, 0, 0], [-math.sin(rad), 0, math.cos(rad), 0], [0, 0, 0, 1]]

def MatrixMakeRotZ(deg):
    rad = deg * 0.0174533
    return [[math.cos(rad), math.sin(rad), 0, 0], [-math.sin(rad), math.cos(rad), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

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
                currentLine = currentLine[3:]
                currentLine = currentLine.split(" ")
                verts[vtCount].u = currentLine[0]
                verts[vtCount].v = currentLine[1]
                vtCount += 1
            else:
                currentLine = currentLine[2:]
                currentLine = currentLine.split(" ")
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

intCam = Camera(0, 0, 0, 256, 240)

def CollisionLoop(meshList):
    results = []
    for me in range(0, len(meshList)):
        match meshList[me].collisionType:
            case 0:
                # Sphere
                # Each object has a collision radius around it's origin, and if any object enters that radius, it's a hit.
                for ms in range(0, len(meshList)):
                    # Not colliding against self, and testing if they should collide
                    if ms != me and meshList[ms].collisionId == meshList[me].collisionId:
                        distance = DistanceBetweenVectors(meshList[me].pos, meshList[ms].pos)
                        if distance - meshList[me].bbR < meshList[ms].bbR:
                            results.append([meshList[me], meshList[ms]])

            case 1:
                # Cylinder
                # The distance is measured with no vertical in mind, and a check to make sure it's within height
                for ms in range(0, len(meshList)):
                    if ms != me and meshList[ms].collisionId == meshList[me].collisionId:
                        distance = DistanceBetweenVectors(Vector(meshList[me].pos.x, 0, meshList[me].pos.z), Vector(meshList[ms].pos.x, 0, meshList[ms].pos.z))
                        if distance - meshList[me].bbR < meshList[ms].bbR and int(meshList[me].pos.y) in range(meshList[ms].pos.y - 5, meshList[ms].pos.y + 5):
                            results.append([meshList[me], meshList[ms]])

            case 2:
                # Cube
                # The position of the first mesh simply has to be in range of the other mesh's position.
                for ms in range(0, len(meshList)):
                    if ms != me and meshList[ms].collisionId == meshList[me].collisionId:
                        if int(meshList[me].pos.y) in range(meshList[ms].pos.y - 5, meshList[ms].pos.y + 5) or int(meshList[me].pos.x) in range(meshList[ms].pos.x - 5, meshList[ms].pos.x + 5) or int(meshList[me].pos.z) in range(meshList[ms].pos.z - 5, meshList[ms].pos.z + 5):
                            results.append([meshList[me], meshList[ms]])

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



# Rastering

def RasterThings(thingList, camera):
    SetInternalCamera(camera)
    projected = []
    for t in thingList:
        for msh in t[0]:
            translated = []
            for c in ViewTriangles(TranslateTriangles(TransformTriangles(msh[0], VectorAdd(msh[2], t[2])), VectorAdd(msh[1], t[1]))):
                if VectorDoP(c[3], camera[10]) < 0.1:
                    for r in TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], c):
                        translated.append(r)
            
            for i in ProjectTriangles(translated):
                for p in TriangleClipAgainstPlane([0, 0, 0], [0, 1, 0], i):
                    for s in TriangleClipAgainstPlane([0, intCam[3] - 1, 0], [0, -1, 0], p):
                        for z in TriangleClipAgainstPlane([0, 0, 0], [1, 0, 0], s):
                            for y in TriangleClipAgainstPlane([intCam[4] - 1, 0, 0], [-1, 0, 0], z):
                                y[5] = msh[3]
                                y[7] = msh[4]
                                projected.append(y)

    projected.sort(key = triSort)
    return projected

def RasterMeshList(meshList, camera):
    SetInternalCamera(camera)
    finished = []
    for m in meshList:
        finished += RasterMesh(m, camera)
    finished.sort(key = triSort)
    return finished

def RasterTriangles(meshList, camera):
    return RasterMeshList(meshList, camera)

def RasterMesh(msh, camera):
    projected = []
    translated = []
    for c in ViewTriangles(TranslateTriangles(TransformTriangles(msh[0], msh[2]), msh[1])):
        if VectorDoP(c[3], intCam[10]) > -0.1:
            for r in TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], c):
                translated.append(r)

        
    for i in ProjectTriangles(translated):
        for p in TriangleClipAgainstPlane([0, 0, 0], [0, 1, 0], i):
            for s in TriangleClipAgainstPlane([0, intCam[3] - 1, 0], [0, -1, 0], p):
                for z in TriangleClipAgainstPlane([0, 0, 0], [1, 0, 0], s):
                    for y in TriangleClipAgainstPlane([intCam[4] - 1, 0, 0], [-1, 0, 0], z):
                        y[5] = msh[3]
                        y[7] = msh[4]
                        projected.append(y)
    return projected

# [0] is position, [1] is rotation, [2] is fov, [3] is screenHeight, [4] is screenWidth, [5] and [6] are half.
# [7] is near clip, [8] is far clip, [9] is target, [10] is forward, [11] is up, [12] is theta, [13] is tan,
# and [14] is a

def RasterThing(thing, camera):
    projected = []

    for msh in thing[0]:
        translated = []
        for c in ViewTriangles(TranslateTriangles(TransformTriangles(msh[0], VectorAdd(msh[2], thing[2])), VectorAdd(msh[1], thing[1]))):
            if VectorDoP(c[3], camera[10]) < 0.1:
                for r in TriangleClipAgainstPlane([0, 0, camera[7]], [0, 0, 1], c):
                    translated.append(r)

        for i in ProjectTriangles(translated):
            for p in TriangleClipAgainstPlane([0, 0, 0], [0, 1, 0], i):
                for s in TriangleClipAgainstPlane([0, intCam[3] - 1, 0], [0, -1, 0], p):
                    for z in TriangleClipAgainstPlane([0, 0, 0], [1, 0, 0], s):
                        for y in TriangleClipAgainstPlane([intCam[4] - 1, 0, 0], [-1, 0, 0], z):
                            y[5] = msh[3]
                            y[7] = msh[4]
                            projected.append(y)
    return projected

intVecU = [0, 1, 0]

def SetInternalCamera(camera):
    global intCam
    global intMatT
    global intMatV
    global intVecT
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intCam = camera
    intMatT = GetTranslationMatrix(camera[0][0], camera[0][1], camera[0][2])
    camera[10] = VectorRotateY(camera[9], camera[1][1])
    intCam[10] = camera[10]
    intVecT = VectorAdd(camera[0], camera[10])
    intMatV = LookAtMatrix(camera[0], intVecT, intVecU)




def TransformTriangles(tris, rot):
    transformed = []
    # Matrix Stuff
    matRotY = MatrixMakeRotY(rot[1])
    matRotX = MatrixMakeRotX(rot[0])
    matRotZ = MatrixMakeRotZ(rot[2])

    matWorld = MatrixMatrixMul(matRotZ, matRotY)
    matWorld = MatrixMatrixMul(matWorld, matRotX)
    for t in tris:
        # Moving Triangle based on Object Rotation (It's also supposed to take camera position into account but apparently not)
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
        tri[6] = TriangleAverage(tri)
        tri = TriangleAdd(tri, pos)
        
        translated.append(tri)
    
    return translated

def ViewTriangles(tris):
    newTris = []
    for tries in tris:
        newTri = TriMatrixMul(tries, intMatV)
        newTri[3] = tries[3]
        newTri[6] = tries[6]
        # Converting World Space to View Space
        newTris.append(newTri)
    return newTris
                    
def ProjectTriangles(tris):
    projected = []
    for tri in tris:
        # Projecting 3D into 2D
        newTri = TriangleAdd(ProjectTriangle(tri, intCam[14], intCam[13], intCam[8], intCam[7]), [1, 1, 0])

        newTri[0][0] *= intCam[6]
        newTri[0][1] *= intCam[5]
        newTri[1][0] *= intCam[6]
        newTri[1][1] *= intCam[5]
        newTri[2][0] *= intCam[6]
        newTri[2][1] *= intCam[5]

        # Z should be flipped towards the camera
        newTri[3] = tri[3]
        newTri[6] = tri[6]
        
        projected.append(newTri)
                        
    return projected
