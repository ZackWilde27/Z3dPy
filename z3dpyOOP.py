# Zack's 3D Engine
# or ZedPy for short
# Object-Oriented Edition

# 0.1.4 Changes
#
# - Added thing.movable. When a thing is static, it won't calculate rotation, so that should speed things up.
#
# - Quite a few drawing optimizations, much faster culling. Internal Camera has pretty much been eliminated, except for the View Matrix which should be calculated before everything.
#
# - Added Camera.SetTargetDirection() and Camera.GetTargetDirection(), which will account for camera position to return direction.
#
# - Added a basic physics engine with delta calculations. Create a physics body for a Thing with myThing.physics = z3dpy.PhysicsBody(), then use z3dpy.HandlePhysics() in your game loop.
#
# - Added VectorNegate()
#

import math
import time

print("Z3dPy v0.1.4")

# The OOP version gets less support, because it's slower, but it's a lot easier to read, and a lot of the classes line up with the function version.
        

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



# Some stuff I need to declare before the Thing class

# Hitbox Object:
#
# Stores all the needed info regarding collisions, the type of hitbox, it's scale, and collision id.
# Only hitboxes with the same collision id will collide.
#
class Hitbox:
    def __init__(self, type, id, radius, height):
        self.SetCollisionParams(type, id, radius, height)

    def SetCollisionParams(self, type, id, radius, height):
        self.bbR = radius
        self.bbH = height
        self.collisionType = type
        self.collisionId = id
        match type:
            case 0:
                self.hitbox = LoadMeshScl("engine/mesh/sphere.obj", 0, 0, 0, self.bbR, self.bbR, self.bbR)
            case 1:
                self.hitbox = LoadMeshScl("engine/mesh/cylinder.obj", 0, 0, 0, self.bbR, self.bbH, self.bbR)
            case 2:
                self.hitbox = LoadMeshScl("engine/mesh/cube.obj", 0, 0, 0, self.bbR, self.bbH, self.bbR)

# PhysicsBody Object:
#
# Stores a bunch of variables for physics calculations.
#
class PhysicsBody:
    def __init__(self, mass, friction):
        self.velocity = Vector(0, 0, 0)
        self.acceleration = Vector(0, 0, 0)
        self.mass = mass
        self.friction = friction


# Thing Object:
#
# The Thing is what you would typically refer to as an in-game object, it has a collection of meshes, a hitbox, and physics information.
#
class Thing:
    def __init__(self, meshList, x, y, z):
        self.meshes = meshList
        self.pos = Vector(x, y, z)
        self.rot = Vector(0, 0, 0)
        self.id = 0
        self.hitbox = Hitbox(2, 0, 1, 1)
        self.physics = []
        self.movable = True

    

# Cameras:
#
# In order to render the triangles, we need information about the camera, like it's position, and fov.
# Camera rotation is determined by it's target and up vector. By default, the up vector is +Y direction and target is simply the Z direction.
# For the uninitiated, "direction" in this case simply refers to a vector between -1 and 1, like +Z direction is 0, 0, 1, and -Z direction is 0, 0, -1
#
# For a third person camera, set the target to a location
# For a first person camera, set the target to a direction + the camera's location
#

class Camera:
    def __init__(self, x, y, z, sW, sH):
        self.pos = Vector(x, y, z)
        self.rot = Vector(x, y, z)
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

    def SetFOV(self, fov):
        self.fov = fov * 0.0174533
        self.theta = fov / 2
        self.tan = (1 / math.tan(fov/2))

    def SetTargetLocation(self, v):
        self.target = v

    def SetTargetVector(self, v):
        self.target = VectorAdd(self.pos, VectorNormalize(v))

    def GetTargetVector(self):
        return VectorNormalize(VectorSub(self.pos, self.target))
    
    def GetRightVector(self):
        return VectorCrP(self.GetTargetVector(), self.up)

class Light:
    def __init__(self, x, y, z, colour, strength, radius):
        self.pos = Vector(x, y, z)
        self.col = colour
        self.str = strength
        self.rad = radius


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

# You can reference these at any time to get a global axis.
globalX = Vector(1, 0, 0)
globalY = Vector(0, 1, 0)
globalZ = Vector(0, 0, 1)

#projectionMatrix = np.matrix([[CamAspR * CamTan, 0, 0, 0], [0, CamTan, 0, 0], [0, 0, CamFC / (CamFC - CamNC), 1], [0, 0, (-CamFC * CamNC) / (CamFC - CamNC), 0]])

#matRotZ = np.matrix([[1, 0, 0, 0], [0, math.cos((time.time() - track) / 2), math.sin((time.time() - track) / 2), 0], [0, -math.sin((time.time() - track) / 2), math.cos((time.time() - track) / 2), 0], [0, 0, 1, 0]])

lights = []

gravityDir = Vector(0, 9.8, 0)

physTime = time.time()


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

def VectorNegate(v):
    return VectorMulF(v, -1)

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
    
def TriangleClipAgainstZ(tri, camera):
    return TriangleClipAgainstPlane(Vector(0, 0, camera.nc), Vector(0, 0, 1), tri)

def TriangleClipAgainstScreenEdges(tri, camera):
    output = []
    for p in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(0, 1, 0), tri):
        for s in TriangleClipAgainstPlane(Vector(0, camera.scrH - 1, 0), Vector(0, -1, 0), p):
            for z in TriangleClipAgainstPlane(Vector(0, 0, 0), Vector(1, 0, 0), s):
                for y in TriangleClipAgainstPlane(Vector(camera.scrW - 1, 0, 0), Vector(-1, 0, 0), z):
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
def PgDrawTriangleRGB(tri, colour, surface, pyg):
    pyg.draw.polygon(surface, (max(colour.x, 0), max(colour.y, 0), max(colour.z, 0)), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def PgDrawTriangleRGBF(tri, colour, surface, pyg):
    pyg.draw.polygon(surface, (max(colour.x, 0) * 255, max(colour.y, 0) * 255, max(colour.z, 0) * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def PgDrawTriangleOutl(tri, colour, surface, pyg):
    pyg.draw.lines(surface, (max(colour.x, 0) * 255, max(colour.y, 0) * 255, max(colour.z, 0) * 255), True, [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def PgDrawTriangleF(tri, f, surface, pyg):
    f = max(f, 0) * 255
    pyg.draw.polygon(surface, (f, f, f), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def PgDrawTriangleS(tri, f, surface, pyg):
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
    return (n.p1.z + n.p2.z + n.p3.z) / 3

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


def PointAtMatrix(cam):
    temp = MatrixStuff(cam.pos, cam.target, cam.up)
    return [[temp.p3.x, temp.p3.y, temp.p3.z, 0], [temp.p2.x, temp.p2.y, temp.p2.z, 0], [temp.p1.x, temp.p1.y, temp.p1.z, 0], [cam.pos.x, cam.pos.y, cam.pos.z, 1]]

def LookAtMatrix(cam):
    temp = MatrixStuff(cam.pos, cam.target, cam.up)
    return [[temp.p3.x, temp.p2.x, temp.p1.x, 0], [temp.p3.y, temp.p2.y, temp.p1.y, 0], [temp.p3.z, temp.p2.z, temp.p1.z, 0], [-(VectorDoP(cam.pos, temp.p3)), -(VectorDoP(cam.pos, temp.p2)), -(VectorDoP(cam.pos, temp.p1)), 1]]


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

#================
#  
# Collisions and Physics
#
#================

def GatherCollisions(thingList):
    results = []
    for me in range(0, len(thingList)):
        for ms in range(0, len(thingList)):
            # Staggering like this so they are done in order of speed
            if me != ms:
                if thingList[ms].hitbox.collisionId == thingList[me].hitbox.collisionId:
                    if [thingList[ms], thingList[me]] not in results:
                        match thingList[me].hitbox.collisionType:
                            case 0:
                                # Sphere
                                # Each object has a collision radius around it's origin, and if any object enters that radius, it's a hit.
                                
                                # Not colliding against self, and testing if they should collide
                                distance = DistanceBetweenVectors(thingList[me].pos, thingList[ms].pos)
                                if distance - thingList[me].hitbox.bbR < thingList[ms].hitbox.bbR:
                                    results.append([thingList[me], thingList[ms]])

                            case 1:
                                # Cylinder
                                # The distance is measured with no vertical in mind, and a check to make sure it's within height
                                distance = DistanceBetweenVectors(Vector(thingList[me].pos.x, 0, thingList[me].pos.z), Vector(thingList[ms].pos.x, 0, thingList[ms].pos.z))
                                if distance - thingList[me].hitbox.bbR < thingList[ms].hitbox.bbR and int(thingList[me].pos.y) in range(thingList[ms].pos.y - 5, thingList[ms].pos.y + 5):
                                    results.append([thingList[me], thingList[ms]])

                            case 2:
                                # Cube
                                # The position of the first mesh simply has to be in range of the other mesh's position.
                                myPos = thingList[me].pos
                                thPos = thingList[ms].pos
                                radius = thingList[ms].hitbox.bbR
                                height = thingList[ms].hitbox.bbH
                                if myPos.x > thPos.x - radius and myPos.x < thPos.x + radius:
                                    if myPos.y > thPos.y - height and myPos.y < thPos.y + height:
                                        if myPos.z > thPos.z - radius and myPos.z < thPos.z + radius:
                                            results.append([thingList[me], thingList[ms]])
    return results

def BasicHandleCollisions(pair):
    if not pair[0].movable:
        if not pair[1].movable:
            return
        pair[1].pos = VectorAdd(pair[1].pos, VectorNegate(DirectionBetweenVectors(pair[1].pos, pair[0].pos)))
    else:
        pair[0].pos = VectorAdd(pair[0].pos, VectorMulF(VectorNegate(DirectionBetweenVectors(pair[0].pos, pair[1].pos)), DistanceBetweenVectors(pair[1].pos, pair[0].pos)))

def HandlePhysics(thingList, floorHeight):
    global physTime
    delta = time.time() - physTime
    physTime = time.time()
    for t in thingList:
        if t.movable and t.physics != []:

            t.physics.velocity = VectorAdd(t.physics.velocity, t.physics.acceleration)

            # Drag
            t.physics.velocity = VectorSub(t.physics.velocity, Vector(t.physics.friction * sign(t.physics.velocity.x), t.physics.friction * sign(t.physics.velocity.x), t.physics.friction * sign(t.physics.velocity.z)))

            # Gravity

            t.physics.velocity = VectorAdd(t.physics.velocity, VectorMulF(gravityDir, 0.1))

            t.pos = VectorAdd(t.pos, VectorMulF(t.physics.velocity, delta))
            t.pos.y = min(t.pos.y, floorHeight)
    

def PhysicsCollisions(thingList):
    for cols in GatherCollisions(thingList):
        if cols[0].physics != []:
            force = VectorMulF(DirectionBetweenVectors(cols[0].pos, cols[1].pos), cols[0].physics.mass)
            if cols[1].physics != []:
                toforce = VectorAdd(force, VectorMulF(cols[1].physics.velocity), cols[1].physics.mass)
                cols[0].physics.velocity = VectorAdd(cols[0].physics.velocity, VectorNegate(toforce))
                cols[1].physics.velocity = VectorAdd(cols[1].physics.velocity, toforce)
            else:
                cols[0].physics.velocity = VectorAdd(cols[0].physics.velocity, VectorNegate(force))
        else:
            if cols[1].physics != []:
                force = VectorMulF(DirectionBetweenVectors(cols[1].pos, cols[0].pos), cols[1].physics.mass)
                cols[1].physics.velocity = VectorAdd(cols[1].physics.velocity, VectorNegate(force))


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
        for m in t.meshes:
            viewed += RasterPt1(m.tris, VectorAdd(m.pos, t.pos), VectorAdd(m.rot, t.rot), t.id, m.colour, camera)
    viewed.sort(reverse = True, key = triSort)
    finished = RasterPt2(viewed, camera)
    return finished

def RasterMeshList(meshList, camera):
    SetInternalCamera(camera)
    finished = []
    viewed = []
    for m in meshList:
        viewed += RasterPt1(m.tris, m.pos, m.rot, m.id, m.colour, camera)
    viewed.sort(reverse = True, key = triSort)
    return finished

def RasterPt1(tris, pos, rot, id, colour, camera):
    translated = []
    for c in ViewTriangles(TranslateTriangles(TransformTriangles(tris, rot), pos)):
        if VectorDoP(c.normal, Vector(0, 0, 1)) < 0.1:
            for r in TriangleClipAgainstZ(c, camera):
                r.colour = colour
                r.id = id
                translated.append(r)
    return translated

def RasterPt2(tris, camera):
    output = []
    for i in ProjectTriangles(tris, camera):
        for s in TriangleClipAgainstScreenEdges(i, camera):
            output.append(s)
    return output

intVecU = Vector(0, 1, 0)

def SetInternalCamera(camera):
    global intMatV
    intMatV = LookAtMatrix(camera)
    

def TransformTriangles(tris, rot):
    transformed = []
    matRotY = MatrixMakeRotY(rot.y)
    matRotX = MatrixMakeRotX(rot.x)
    matRotZ = MatrixMakeRotZ(rot.z)

    for t in tris:
        nt = TriMatrixMul(t, matRotY)
        nt = TriMatrixMul(nt, matRotX)
        nt = TriMatrixMul(nt, matRotZ)
        nt.normal = GetNormal(nt)
        transformed.append(nt)
        
    return transformed
        
def TranslateTriangles(tris, pos):
    translated = []
    for tri in tris:
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
        newTris.append(newTri)
    return newTris
                    
def ProjectTriangles(tris, camera):
    projected = []
    for tri in tris:
        newTri = TriangleAdd(ProjectTriangle(tri, camera.a, camera.tan, camera.fc, camera.nc), Vector(1, 1, 0))

        newTri = TriangleMul(newTri, Vector(camera.scrWh, camera.scrHh, 1))

        newTri.normal = tri.normal
        newTri.wpos = tri.wpos
        
        projected.append(newTri)
                        
    return projected


#================
#  
# Shaders
#
#================
       
def FlatLighting(tri):
    finalColour = Vector(0, 0, 0)
    for l in lights:
        finalColour = VectorAdd(finalColour, VectorMulF(VectorMulF(tri.colour, VectorDoP(VectorMul(tri.normal, Vector(-1, -1, -1)), DirectionBetweenVectors(l.pos, tri.wpos))), 1 - min(max(DistanceBetweenVectors(tri.wpos, l.pos) / l.rad, 0), 1)))
    return finalColour
