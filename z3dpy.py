# Zack's 3D Python Engine
# or ZedPy for short

import math
import time
import random as rand

print("Z3dPy v0.0.4")

# Object Objects

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.u = 0
        self.v = 0

class Vector4:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

class Triangle:
    def __init__(self, loc1, loc2, loc3):
        self.p1 = loc1
        self.p2 = loc2
        self.p3 = loc3
        self.normal = GetNormal(self)
        self.lighting = 0
        self.colour = Vector(255, 255, 255)
        self.worldP1 = loc1
        self.worldP2 = loc2
        self.worldP3 = loc3
        self.pos = TriangleAverage(self)
        self.id = 0



class Mesh:
    def __init__(self, triangles, x, y, z):
        self.tris = triangles
        self.pos = Vector(x, y, z)
        self.rot = Vector(0, 0, 0)
        self.colour = Vector(255, 255, 255)
        self.id = 0
        self.bbH = 1
        self.bbW = 1

    def SetColour(self, c):
        self.colour = c
    
    def SetId(self, id):
        self.id = id

class Camera:
    def __init__(self, x, y, z, sW, sH, fov, near, far):
        self.x = x
        self.y = y
        self.z = z
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.fov = fov
        self.scrH = sH
        self.scrW = sW
        self.scrHh = sH / 2
        self.scrWh = sW / 2
        self.nc = near
        self.fc = far
        self.target = Vector(0, 0, 1)
        self.forward = Vector(0, 0, 1)
        self.up = Vector(0, 1, 0)
        self.theta = fov / 2
        self.tan = (1 / math.tan(self.theta))
        self.a = self.scrH / self.scrW

    def GetVector(self):
        return Vector(self.x, self.y, self.z)

    def SetVector(self, vector):
        self.x = vector.x
        self.y = vector.y
        self.z = vector.z

class FirstPersonCamera:
    def __init__(self, x, y, z, sW, sH, fov, near, far):
        self.cam = Camera(x, y, z, sW, sH, fov, near, far)
        

class basicVectors:
    def __init__(self):
        self.gx = Vector(1, 0, 0)
        self.gy = Vector(0, 1, 0)
        self.gz = Vector(0, 0, 1)


# Textures are a matrix, so you can specify an X and Y number with myTexture[x][y]
def Texture(w, h):
    pixels = []
    for x in range (0, w):
        pixels.append([])
        for y in range(0, h):
            pixels[x].append(Vector(255, 255, 255))
    return pixels

        
# Variables

track = time.time()

# Dimension associated with basic flat shading. 0 is X, 1 is Y, 2 is Z
colorDir = 2

quickVectors = basicVectors()


#ProjectionMatrix = np.matrix([[CamAspR * CamTan, 0, 0, 0], [0, CamTan, 0, 0], [0, 0, CamFC / (CamFC - CamNC), 1], [0, 0, (-CamFC * CamNC) / (CamFC - CamNC), 0]])

#matRotZ = np.matrix([[1, 0, 0, 0], [0, math.cos((time.time() - track) / 2), math.sin((time.time() - track) / 2), 0], [0, -math.sin((time.time() - track) / 2), math.cos((time.time() - track) / 2), 0], [0, 0, 1, 0]])

# Lists
TrisToDraw = []
TrisToRef = []
Objs = []
usedColours = []
        

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
    if vector.z != 0:
        return Vector((a * f * vector.x) / vector.z, (f * vector.y) / vector.z, (q * vector.z) - (q * nc))
    else:
        return Vector(0, 0, 0)

def ProjectTriangle(t, a, f, fc, nc):
    return Triangle(Projection(t.p1, a, f, fc, nc), Projection(t.p2, a, f, fc, nc), Projection(t.p3, a, f, fc, nc))

def DistanceToPoints(x, y, x2, y2):
    return math.sqrt(((x - x2) * (x - x2)) + ((y - y2) * (y - y2)))


# Vector Functions

def VectorNormalize(v):
    l = VectorGetLength(v)
    if l != 0:
        return Vector(v.x / l, v.y / l, v.z / l)
    return v

def VectorAdd(v1, v2):
    return Vector(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def VectorSub(v1, v2):
    return Vector(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def VectorMul(v1, v2):
    return Vector(v1.x * v2.x, v1.y * v2.y, v1.z * v2.z)

def VectorMulF(v1, f):
    return Vector(v1.x * f, v1.y * f, v1.z * f)

def VectorCrP(v1, v2):
    return Vector(v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x)

def VectorDivF(v, f):
    return Vector(v.x / f, v.y / f, v.z / f)

def VectorGetLength(v):
    return math.sqrt((v.x * v.x) + (v.y * v.y) + (v.z * v.z))

def VectorDoP(v1, v2):
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)

def VectorToList(v):
    return [v.x, v.y, v.z]

def DistanceBetweenVectors(v1, v2):
    return math.sqrt(((v2.x - v1.x) ** 2) + ((v2.y - v1.y) ** 2) + ((v2.z - v1.z) ** 2))

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))


# Triangle Functions

def TriangleAdd(t, v):
    return CreateTriangleComplex(VectorAdd(t.p1, v), VectorAdd(t.p2, v), VectorAdd(t.p3, v), t.normal, t.lighting, t.colour, t.worldP1, t.worldP2, t.worldP3, t.id)

def TriangleSub(t, v):
    return CreateTriangleComplex(VectorSub(t.p1, v), VectorSub(t.p2, v), VectorSub(t.p3, v), t.normal, t.lighting, t.colour, t.worldP1, t.worldP2, t.worldP3, t.id)

def TriangleMul(t, v):
    return CreateTriangleComplex(VectorMul(t.p1, v), VectorMul(t.p2, v), VectorMul(t.p3, v), t.normal, t.lighting, t.colour, t.worldP1, t.worldP2, t.worldP3, t.id)

def TriangleMulF(t, f):
    return CreateTriangleComplex(VectorMulF(t.p1, f), VectorMulF(t.p2, f), VectorMulF(t.p3, f), t.normal, t.lighting, t.colour, t.worldP1, t.worldP2, t.worldP3, t.id)

def TriangleDivF(t, f):
    return CreateTriangleComplex(VectorDivF(t.p1, f), VectorDivF(t.p2, f), VectorDivF(t.p3, f), t.normal, t.lighting, t.colour, t.worldP1, t.worldP2, t.worldP3, t.id)

def TriangleCullTestZ(t):
    return t.p1.z > 0.1 and t.p2.z > 0.1 and t.p3.z > 0.1

def TriangleCullTestXY(t):
    return t.p1.x > -5 and t.p2.x > -5 and t.p3.x > -5 and t.p1.y > -5 and t.p2.y > -5 and t.p3.y > -5

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
    d1 = ShortestPointToPlane(tri.p1, pNrm, pPos)
    d2 = ShortestPointToPlane(tri.p2, pNrm, pPos)
    d3 = ShortestPointToPlane(tri.p3, pNrm, pPos)
    if d1 >= 0:
        insideP.append(tri.p1)
    else:
        outsideP.append(tri.p1)
    if d2 >= 0:
        insideP.append(tri.p2)
    else:
        outsideP.append(tri.p2)
    if d3 >= 0:
        insideP.append(tri.p3)
    else:
        outsideP.append(tri.p3)

    if len(insideP) == 0:
        return []
    
    if len(insideP) == 3:
        return [tri]
    
    if len(insideP) == 1 and len(outsideP) == 2:
        outT = Triangle(insideP[0], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[1]), VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]))
        outT.normal = tri.normal
        outT.pos = tri.pos
        return [outT]
    

    if len(insideP) == 2 and len(outsideP) == 1:
        outT1 = Triangle(insideP[0],insideP[1], VectorIntersectPlane(pPos, pNrm, insideP[1], outsideP[0]))
        outT2 = Triangle(insideP[0], outT1.p3, VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]))
        outT1.normal = tri.normal
        outT2.normal = tri.normal
        outT1.pos = tri.pos
        outT2.pos = tri.pos
        return [outT1, outT2]
    
def CreateTriangleComplex(p1, p2, p3, nrm, l, c, wp1, wp2, wp3, id):
    newTri = Triangle(p1, p2, p3)
    newTri.normal = nrm
    newTri.lighting = l
    newTri.colour = c
    newTri.worldP1 = wp1
    newTri.worldP2 = wp2
    newTri.worldP3 = wp3
    newTri.id = id
    return newTri

    
def GetNormal(tri):
    triLine1 = VectorSub(tri.p2, tri.p1)
    triLine2 = VectorSub(tri.p3, tri.p1)
    normal = VectorCrP(triLine1, triLine2)
    # Y and Z are flipped
    return VectorNormalize(normal)

def DrawTriangleRGB(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour.x, 0), max(colour.y, 0), max(colour.z, 0)), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleF(tri, surface, f, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleS(tri, surface, f, pyg):
    f = max(f, 0)
    pyg.draw.polygon(surface, (tri.colour.x * f, tri.colour.y * f, tri.colour.z * f), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def TriangleAverage(tri):
    return Vector((tri.p1.x + tri.p2.x + tri.p3.x) / 3, (tri.p1.y + tri.p2.y + tri.p3.y) / 3, (tri.p1.z + tri.p2.z + tri.p3.z) / 3)

def TriangleCopyUV(inTri, outTri):
    outTri.p1.u = inTri.p1.u
    outTri.p2.u = inTri.p2.u
    outTri.p3.u = inTri.p3.u
    outTri.p1.v = inTri.p1.v
    outTri.p2.v = inTri.p2.v
    outTri.p3.v = inTri.p3.v

# Sort Triangles based on their distance from the camera
def triSort(n):
    return abs(intCam.fc - (((n.p1.z + n.p2.z + n.p3.z) / 3) - intCam.z))

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
    return Triangle(MatrixMul(t.p1, m), MatrixMul(t.p2, m), MatrixMul(t.p3, m))

def MatrixMul(v, m):
    return Vector4(v.x * m[0][0] + v.y * m[1][0] + v.z * m[2][0] + m[3][0], v.x * m[0][1] + v.y * m[1][1] + v.z * m[2][1] + m[3][1], v.x * m[0][2] + v.y * m[1][2] + v.z * m[2][2] + m[3][2], v.x * m[0][3] + v.y * m[1][3] + v.z * m[2][3] + m[3][3])

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

    return Triangle(newForward, newUp, newRight)

def PointAtMatrix(pos, target, up, cam):
    temp = MatrixStuff(pos, target, up)
    # Now for the matrix
    return [[temp.p3.x, temp.p3.y, temp.p3.z, 0], [temp.p2.x, temp.p2.y, temp.p2.z, 0], [temp.p1.x, temp.p1.y, temp.p1.z, 0], [cam.x, cam.y, cam.z, 1]]

def LookAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    # Now for the matrix
    return [[temp.p3.x, temp.p2.x, temp.p1.x, 0], [temp.p3.y, temp.p2.y, temp.p1.y, 0], [temp.p3.z, temp.p2.z, temp.p1.z, 0], [-(VectorDoP(intCam.GetVector(), temp.p3)), -(VectorDoP(intCam.GetVector(), temp.p2)), -(VectorDoP(intCam.GetVector(), temp.p1)), 1]]


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
def LoadMesh(filename, x, y, z):
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
                verts.append(Vector(float(currentLine[0]), float(currentLine[1]), float(currentLine[2])))
            
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            newTriangle = Triangle(verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1])
            triangles.append(newTriangle)
        
    file.close()
    return Mesh(triangles, x, y, z)

intCam = Camera(0, 0, 0, 256, 240, 90, 0.1, 1500)

# Rastering

def RasterTriangles(meshList, camera):
    SetInternalCamera(camera)
    projected = []
    for m in meshList:
        translated = []
        viewed = []
        for c in ViewTriangles(TranslateTriangles(TransformTriangles(m, m.rot), m.pos)):
            if VectorDoP(c.normal, camera.forward) < 0.1:
                for r in TriangleClipAgainstPlane(Vector(0, 0, camera.nc), Vector(0, 0, 1), c):
                    translated.append(r)

        for i in ProjectTriangles(translated):
            for p in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(0, 1, 0), i):
                for s in TriangleClipAgainstPlane(Vector(0, intCam.scrH - 1, 0), Vector(0, -1, 0), p):
                    for z in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(1, 0, 0), s):
                        for y in TriangleClipAgainstPlane(Vector(intCam.scrW - 1, 0, 0), Vector(-1, 0, 0), z):
                            y.colour = m.colour
                            y.id = m.id
                            projected.append(y)

    projected.sort(key = triSort)
    return projected

intVecU = Vector(0, 1, 0)

def SetInternalCamera(camera):
    global intCam
    global intMatT
    global intMatV
    global intVecT
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intCam = camera
    intMatT = GetTranslationMatrix(camera.x, camera.y, camera.z)
    camera.forward = VectorRotateY(camera.target, camera.yaw)
    intVecT = VectorAdd(camera.GetVector(), camera.forward)
    intMatV = LookAtMatrix(camera.GetVector(), intVecT, intVecU)
    
    

def TransformTriangles(mesh, rot):
    transformed = []
    # Matrix Stuff
    matRotY = MatrixMakeRotY(rot.y)
    matRotX = MatrixMakeRotX(rot.x)
    matRotZ = MatrixMakeRotZ(rot.z)

    matWorld = MatrixMatrixMul(matRotZ, matRotY)
    matWorld = MatrixMatrixMul(matWorld, matRotX)
    #matWorld = np.matmul(matWorld, intMatT)
    for t in mesh.tris:
        # Moving Triangle based on Object Rotation (It's also supposed to take camera position into account but apparently not)
        nt = TriMatrixMul(t, matRotY)
        nt = TriMatrixMul(nt, matRotX)
        nt = TriMatrixMul(nt, matRotZ)
        nt.pos = t.pos
        nt.normal = GetNormal(nt)
        transformed.append(nt)
        
    return transformed
        
def TranslateTriangles(tris, pos):
    translated = []
    for tri in tris:
        # Moving triangle based on object position
        tri.worldP1 = tri.p1
        tri.worldP2 = tri.p2
        tri.worldP3 = tri.p3
        tri = TriangleAdd(tri, pos)
        tri.pos = tri.pos
        tri.normal = tri.normal
        
        translated.append(tri)
    
    return translated

def ViewTriangles(tris):
    newTris = []
    for tries in tris:
        newTri = TriMatrixMul(tries, intMatV)
        newTri.normal = tries.normal
        newTri.worldP1 = tries.worldP1
        newTri.worldP2 = tries.worldP2
        newTri.worldP3 = tries.worldP3
        newTri.pos = tries.pos
        # Converting World Space to View Space
        newTris.append(newTri)
    return newTris
                    
def ProjectTriangles(tris):
    projected = []
    for tri in tris:
        # Projecting 3D into 2D
        newTri = TriangleAdd(ProjectTriangle(tri, intCam.a, intCam.tan, intCam.fc, intCam.nc), Vector(1, 1, 0))

        newTri.p1.x *= intCam.scrWh
        newTri.p1.y *= intCam.scrHh
        newTri.p2.x *= intCam.scrWh
        newTri.p2.y *= intCam.scrHh
        newTri.p3.x *= intCam.scrWh
        newTri.p3.y *= intCam.scrHh

        # Z should be flipped towards the camera
        newTri.normal = tri.normal
        newTri.worldP1 = tri.worldP1
        newTri.worldP2 = tri.worldP2
        newTri.worldP3 = tri.worldP3
        newTri.pos = tri.pos
        #newTri.normal.z *= -1
        
        projected.append(newTri)
                        
    return projected

def CollisionCheck(msh1, msh2):
    return False
