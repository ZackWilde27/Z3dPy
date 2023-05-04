# Zack's 3D Engine
# or ZedPy for short
# Object-Oriented Edition

# 0.0.7 Changes
#
# - Z3dPy has been split off into the OOP version, and regular Function version
#
# - Added a toggle between FirstPerson and ThirdPerson when setting the camera
#
# - Added DrawTriangleRGBF() because I now realize the problem with giving a normalized vector when it expects 0-255
#
# - Removed Camera's forward vector, it was basically a bodge in order to get first person working, but I would instead use RotateVectorY() or something to get a new target vector.
#

import math

print("Z3dPy v0.0.7")

#================
#
# Object Objects
#
#================

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
        self.wpos = TriangleAverage(self)
        self.id = 0



class Mesh:
    def __init__(self, triangles, x, y, z):
        self.tris = triangles
        self.pos = Vector(x, y, z)
        self.rot = Vector(0, 0, 0)
        self.colour = Vector(255, 255, 255)
        self.id = 0

    def SetColour(self, r, g, b):
        self.colour = Vector(r, g, b)
    
    def SetId(self, id):
        self.id = id


# Thing Object:
#
# The Thing is what you would typically refer to as an object, it has a collection of meshes, and collision data.
#
# SetCollisionParams(id, radius, height) will set the collision data and update the hitbox, for drawing to the screen.
# Id: 0 = Sphere, 1 = Cylinder, 2 = Cube
# Radius: radius of the hitbox
# Height: height of the cylinder, if it's a cylinder.

class Thing:
    def __init__(self, meshList, x, y, z):
        self.meshes = meshList
        self.pos = Vector(x, y, z)
        self.rot = Vector(0, 0, 0)
        self.id = 0
        self.hitbox = LoadMesh("engine/mesh/cube.obj", x, y, z)
        # Collision Data
        self.bbR = 1
        self.bbH = 1
        self.collisionId = 0
        self.collisionType = 2

    def SetCollisionParams(self, id, radius, height):
        self.bbR = radius
        self.bbH = height
        self.collisionId = id
        match id:
            case 0:
                self.hitbox = LoadMeshScl("engine/mesh/sphere.obj", self.x, self.y, self.z, self.bbR, self.bbR, self.bbR)
            case 1:
                self.hitbox = LoadMeshScl("engine/mesh/cylinder.obj", self.x, self.y, self.z, self.bbR, self.bbH, self.bbR)
            case 2:
                self.hitbox = LoadMeshScl("engine/mesh/cube.obj", self.x, self.y, self.z, self.bbR, self.bbR, self.bbR)

# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
# For the uninitiated, "direction" in this case simply refers to a vector between -1 and 1, like +Z direction is 0, 0, 1, and -Z direction is 0, 0, -1
#
# For a third person camera, set the target to a location
# For a first person camera, set the target to a direction + the camera's location
#
# GetVector() will simply return the x, y, and z as a vector
# SetVector() sets the x, y, and z to the vector given. It's a shortcut instead of setting them individually.

class Camera:
    def __init__(self, x, y, z, sW, sH):
        self.x = x
        self.y = y
        self.z = z
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.fov = 90
        self.scrH = sH
        self.scrW = sW
        self.scrHh = sH / 2
        self.scrWh = sW / 2
        self.nc = 0.1
        self.fc = 1500
        self.target = Vector(0, 0, 1)
        self.up = Vector(0, 1, 0)
        self.theta = 90 / 2
        self.tan = (1 / math.tan(self.theta))
        self.a = self.scrH / self.scrW

    def GetPos(self):
        return Vector(self.x, self.y, self.z)
    
    def SetPos(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def SetPosV(self, vector):
        self.x = vector.x
        self.y = vector.y
        self.z = vector.z

#

class Light:
    def __init__(self, x, y, z, colour, strength, radius):
        self.pos = Vector(x, y, z)
        self.col = colour
        self.str = strength
        self.rad = radius
        debugThings.append(Thing([LoadMesh("engine/mesh/light.obj", 0, 0, 0)], x, y, z))

# Unfinished, but right now it's much easier to make a third person game, so I'm planning
# a first person camera object that makes it easier.

class FirstPersonCamera:
    def __init__(self, x, y, z, sW, sH, fov, near, far):
        self.cam = Camera(x, y, z, sW, sH, fov, near, far)


# Textures are a matrix, so you can specify an X and Y number with myTexture[x][y]
# There's no built-in support yet.
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

globalX = Vector(1, 0, 0)
globalY = Vector(0, 1, 0)
globalZ = Vector(0, 0, 1)

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

def VectorEqual(v1, v2):
    return v1.x == v2.x and v1.y == v2.y and v1.z == v2.z

def DistanceBetweenVectors(v1, v2):
    return math.sqrt(((v2.x - v1.x) ** 2) + ((v2.y - v1.y) ** 2) + ((v2.z - v1.z) ** 2))

# Returns the direction from the first vector towards the second
def DirectionBetweenVectors(v1, v2):
    return VectorNormalize(VectorSub(v2, v1))


#================
#  
# Triangle Functions
#
#================

def TriangleAdd(t, v):
    return CreateTriangleComplex(VectorAdd(t.p1, v), VectorAdd(t.p2, v), VectorAdd(t.p3, v), t.normal, t.lighting, t.colour, t.wpos, t.id)

def TriangleSub(t, v):
    return CreateTriangleComplex(VectorSub(t.p1, v), VectorSub(t.p2, v), VectorSub(t.p3, v), t.normal, t.lighting, t.colour, t.wpos, t.id)

def TriangleMul(t, v):
    return CreateTriangleComplex(VectorMul(t.p1, v), VectorMul(t.p2, v), VectorMul(t.p3, v), t.normal, t.lighting, t.colour, t.wpos, t.id)

def TriangleMulF(t, f):
    return CreateTriangleComplex(VectorMulF(t.p1, f), VectorMulF(t.p2, f), VectorMulF(t.p3, f), t.normal, t.lighting, t.colour, t.wpos, t.id)

def TriangleDivF(t, f):
    return CreateTriangleComplex(VectorDivF(t.p1, f), VectorDivF(t.p2, f), VectorDivF(t.p3, f), t.normal, t.lighting, t.colour, t.wpos, t.id)

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
        outT = CreateTriangleComplex(insideP[0], VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[1]), VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri.normal, tri.lighting, tri.colour, tri.wpos, tri.id)
        return [outT]
    

    if len(insideP) == 2 and len(outsideP) == 1:
        outT1 = CreateTriangleComplex(insideP[0],insideP[1], VectorIntersectPlane(pPos, pNrm, insideP[1], outsideP[0]), tri.normal, tri.lighting, tri.colour, tri.wpos, tri.id)
        outT2 = CreateTriangleComplex(insideP[0], outT1.p3, VectorIntersectPlane(pPos, pNrm, insideP[0], outsideP[0]), tri.normal, tri.lighting, tri.colour, tri.wpos, tri.id)
        return [outT1, outT2]
    
def TriangleClipAgainstZ(tri):
    return TriangleClipAgainstPlane(Vector(0, 0, intCam.nc), Vector(0, 0, 1), tri)

def TriangleClipAgainstScreenEdges(tri):
    output = []
    for p in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(0, 1, 0), tri):
        for s in TriangleClipAgainstPlane(Vector(0, intCam.scrH - 1, 0), Vector(0, -1, 0), p):
            for z in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(1, 0, 0), s):
                for y in TriangleClipAgainstPlane(Vector(intCam.scrW - 1, 0, 0), Vector(-1, 0, 0), z):
                    output.append(y)
    return output
    
# Creates a triangle, but you can set every variable on creation.
def CreateTriangleComplex(p1, p2, p3, nrm, light, c, wpos, id):
    newTri = Triangle(p1, p2, p3)
    newTri.normal = nrm
    newTri.lighting = light
    newTri.colour = c
    newTri.wpos = wpos
    newTri.id = id
    return newTri

# Returns the direction a triangle is facing
def GetNormal(tri):
    triLine1 = VectorSub(tri.p2, tri.p1)
    triLine2 = VectorSub(tri.p3, tri.p1)
    normal = VectorCrP(triLine1, triLine2)
    # Y and Z are flipped
    return VectorNormalize(normal)


# Shortcuts for drawing to a PyGame screen.
def DrawTriangleRGB(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour.x, 0), max(colour.y, 0), max(colour.z, 0)), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleF(tri, surface, f, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleS(tri, surface, f, pyg):
    f = max(f, 0)
    pyg.draw.polygon(surface, (tri.colour.x * f, tri.colour.y * f, tri.colour.z * f), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

# Averages all points together to get the center point.
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
    return (intCam.fc + intCam.nc) - ((n.p1.z + n.p2.z + n.p3.z) / 3)

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


#================
#  
# Matrix Functions
#
#================

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
                verts.append(Vector(float(currentLine[0]) * sclX, float(currentLine[1]) * sclY, float(currentLine[2]) * sclZ))
            
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            newTriangle = Triangle(verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1])
            triangles.append(newTriangle)
        
    file.close()
    return Mesh(triangles, x, y, z)

def LoadMesh(filename, x, y, z):
    return LoadMeshScl(filename, x, y, z, 1, 1, 1)

intCam = Camera(0, 0, 0, 256, 240, 90, 0.1, 1500)

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


#================
#  
# Rendering
#
#================

def RasterThings(thingList, camera):
    SetInternalCamera(camera)
    finished = []
    for t in thingList:
        finished += RasterThing(t, camera)
    finished.sort(key = triSort)
    return finished

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
    for c in ViewTriangles(TranslateTriangles(TransformTriangles(msh.tris, msh.rot), msh.pos)):
        if VectorDoP(c.normal, camera.forward) < 0.1:
            for r in TriangleClipAgainstPlane(Vector(0, 0, camera.nc), Vector(0, 0, 1), c):
                translated.append(r)
        
    for i in ProjectTriangles(translated):
        for p in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(0, 1, 0), i):
            for s in TriangleClipAgainstPlane(Vector(0, intCam.scrH - 1, 0), Vector(0, -1, 0), p):
                for z in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(1, 0, 0), s):
                    for y in TriangleClipAgainstPlane(Vector(intCam.scrW - 1, 0, 0), Vector(-1, 0, 0), z):
                        y.colour = msh.colour
                        y.id = msh.id
                        projected.append(y)
    return projected

def RasterThing(thing, camera):
    projected = []

    for msh in thing.meshes:
        translated = []
        for c in ViewTriangles(TranslateTriangles(TransformTriangles(msh.tris, VectorAdd(msh.rot, thing.rot)), VectorAdd(msh.pos, thing.pos))):
            if VectorDoP(c.normal, camera.forward) < 0.1:
                for r in TriangleClipAgainstPlane(Vector(0, 0, camera.nc), Vector(0, 0, 1), c):
                    translated.append(r)

        for i in ProjectTriangles(translated):
            for p in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(0, 1, 0), i):
                for s in TriangleClipAgainstPlane(Vector(0, intCam.scrH - 1, 0), Vector(0, -1, 0), p):
                    for z in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(1, 0, 0), s):
                        for y in TriangleClipAgainstPlane(Vector(intCam.scrW - 1, 0, 0), Vector(-1, 0, 0), z):
                            y.colour = msh.colour
                            y.id = msh.id
                            projected.append(y)
    return projected

intVecU = Vector(0, 1, 0)

def SetInternalCamera(camera, isFP):
    global intCam
    global intMatT
    global intMatV
    global intVecT
    # doing all these calculations once so we can hold on to them for the rest of calculations
    intCam = camera
    intMatT = GetTranslationMatrix(camera.x, camera.y, camera.z)
    intVecT = camera.forward
    intMatV = LookAtMatrix(camera.GetVector(), intVecT, intVecU)
    
    

def TransformTriangles(tris, rot):
    transformed = []
    # Matrix Stuff
    matRotY = MatrixMakeRotY(rot.y)
    matRotX = MatrixMakeRotX(rot.x)
    matRotZ = MatrixMakeRotZ(rot.z)

    matWorld = MatrixMatrixMul(matRotZ, matRotY)
    matWorld = MatrixMatrixMul(matWorld, matRotX)
    for t in tris:
        # Moving Triangle based on Object Rotation (It's also supposed to take camera position into account but apparently not)
        nt = TriMatrixMul(t, matRotY)
        nt = TriMatrixMul(nt, matRotX)
        nt = TriMatrixMul(nt, matRotZ)
        nt.normal = GetNormal(nt)
        transformed.append(nt)
        
    return transformed
        
def TranslateTriangles(tris, pos):
    translated = []
    for tri in tris:
        # Moving triangle based on object position
        tri = TriangleAdd(tri, pos)
        tri.wpos = TriangleAverage(tri)
        
        translated.append(tri)
    
    return translated

def ViewTriangles(tris):
    newTris = []
    for tries in tris:
        newTri = TriMatrixMul(tries, intMatV)
        newTri.normal = tries.normal
        newTri.wpos = tries.wpos
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
        newTri.wpos = tri.wpos
        #newTri.normal.z *= -1
        
        projected.append(newTri)
                        
    return projected


#================
#  
# Shaders
#
#================
       
def FlatLighting(tri, lightList):
    finalColour = Vector(0, 0, 0)
    for l in lightList:
        finalColour = VectorAdd(finalColour, VectorMulF(VectorMulF(tri.colour, VectorDoP(VectorMul(tri.normal, Vector(-1, -1, -1)), DirectionBetweenVectors(l.pos, tri.wpos))), 1 - min(max(DistanceBetweenVectors(tri.wpos, l.pos) / l.rad, 0), 1)))
    return finalColour
