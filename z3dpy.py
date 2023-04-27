# Python Raster Engine by Zack
# or prez for short

import math
import numpy as np
import time
import random as rand

# Object Objects

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

class Mesh:
    def __init__(self, triangles, x, y, z):
        self.tris = triangles
        self.pos = Vector(x, y, z)
        self.rot = Vector(0, 0, 0)

class Camera:
    def __init__(self, x, y, z, sW, sH, fov, near, far):
        self.loc = Vector(x, y, z)
        self.fov = fov
        self.scrH = sH
        self.scrW = sW
        self.nc = near
        self.fc = far
        self.theta = fov / 2
        self.tan = (1 / math.tan(self.theta))
        self.a = self.scrH / self.scrW

        
# Variables

# Dimension associated with basic flat shading. 0 is X, 1 is Y, 2 is Z
colorDir = 2

# Didn't end up using these but they're good to know
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
    return Vector(v.x / l, v.y / l, v.z / l)

def VectorAdd(v1, v2):
    return Vector(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def VectorSub(v1, v2):
    return Vector(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def VectorMul(v1, v2):
    return Vector(v1.x * v2.x, v1.y * v2.y, v1.z * v2.z)

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


# Triangle Functions

def TriangleAdd(t, v):
    return Triangle(VectorAdd(t.p1, v), VectorAdd(t.p2, v), VectorAdd(t.p3, v))

def TriangleCullTest(t):
    threshold = 0.5
    return t.p1.z > threshold and t.p1.z > threshold and t.p1.z > threshold

def GetNormal(tri):
    triLine1 = VectorSub(tri.p2, tri.p1)
    triLine2 = VectorSub(tri.p3, tri.p1)
    normal = VectorCrP(triLine1, triLine2)
    # Y and Z are flipped
    return VectorNormalize(normal)

def DrawTriangleRGB(tri, surface, colour, pyg):
    pyg.draw.polygon(surface, (max(colour.x, 0) * 255, max(colour.y, 0) * 255, max(colour.z, 0) * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleF(tri, surface, f, pyg):
    pyg.draw.polygon(surface, (f * 255, f * 255, f * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

# Sort Triangles based on their distance from the camera
def triSort(n):
    return intCam.fc - abs(((n.p1.z + n.p2.z + n.p3.z) / 3) - intCam.loc.z)


# Matrix Functions

def GetTranslationMatrix(x, y, z):
    return np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [x, y, z, 1]])

def MatrixMul(vector, matrix):
    output = np.matmul(np.array([[vector.x, vector.y, vector.z, 1]]), matrix)
    return Vector(output[0,0], output[0,1], output[0,2])

def TriMatrixMul(t, m):
    return Triangle(MatrixMul(t.p1, m), MatrixMul(t.p2, m), MatrixMul(t.p3, m))

# After having some issues I thought numpy was the problem, so I made my own Matrix Multiply function
def MatrixMult(v, m):
    return Vector4(v.x * m[0,0] + v.y * m[1,0] + v.z * m[2,0] + m[3,0], v.x * m[0,1] + v.y * m[1,1] + v.z * m[2,1] + m[3,1], v.x * m[0,2] + v.y * m[1,2] + v.z * m[2,2] + m[3,2], v.x * m[0,3] + v.y * m[1,3] + v.z * m[2,3] + m[3,3])

# Stuff for the PointAt and LookAt Matrix
def MatrixStuff(pos, target, up):
    newForward = VectorSub(target, pos);
    newForward = VectorNormalize(newForward)

    a = VectorMul(newForward, VectorDoP(up, newForward))
    newUp = VectorSub(up, a)
    newUp = VectorNormalize(newUp)

    newRight = VectorCrP(newUp, newForward)

    return Triangle(newForward, newUp, newRight)

def PointAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    # Now for the matrix
    return np.matrix([[temp.p3.x, temp.p3.y, temp.p3.z, 0], [temp.p2.x, temp.p2.y, temp.p2.z, 0], [temp.p1.x, temp.p1.y, temp.p1.z, 0], [CamX, CamY, CamZ, 1]])

# LookAtMatrix is not finished, still needs the last row
def LookAtMatrix(pos, target, up):
    temp = MatrixStuff(pos, target, up)
    # Now for the matrix
    return np.matrix([[temp.p3.x, temp.p2.x, temp.p1.x, 0], [temp.p3.y, temp.p2.y, temp.p1.y, 0], [temp.p3.z, temp.p2.z, temp.p1.z, 0], []])

def MatrixMakeRotX(Ang):
    return np.matrix([[1, 0, 0, 0], [0, math.cos(Ang / 2), math.sin(Ang / 2), 0], [0, -math.sin(Ang / 2), math.cos(Ang / 2), 0], [0, 0, 1, 0]])



# Load OBJ File
def LoadMesh(filename, x, y, z):
    file = open(filename)
    verts = []
    triangles = []
    currentLine = ""
    scaped = True
    while scaped:
        currentLine = file.readline()
        if currentLine == "":
            scaped = False
            break
        if currentLine[0] == 'v':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            verts.append(Vector(float(currentLine[0]), float(currentLine[1]), float(currentLine[2])))
        if currentLine[0] == 'f':
            currentLine = currentLine[2:]
            currentLine = currentLine.split(" ")
            triangles.append(Triangle(verts[int(currentLine[0]) - 1], verts[int(currentLine[1])- 1], verts[int(currentLine[2]) - 1]))
        
    file.close()
    return Mesh(triangles, x, y, z)

intCam = Camera(0, 0, 0, 256, 240, 90, 0.1, 1500)

# Rastering

def RasterTriangles(meshList, camera):
    intCam = camera
    # Clear Lists
    TrisToDraw = []

    # This one we only need to calculate once per frame
    matTrans = GetTranslationMatrix(camera.loc.x, camera.loc.y, camera.loc.z)
    
    # Gather Triangles
    for meshes in meshList:
        
        matRotX = MatrixMakeRotX(meshes.rot.x)
        matRotZ = np.matrix([[math.cos(meshes.rot.z), math.sin(meshes.rot.z), 0, 0], [-math.sin(meshes.rot.z), math.cos(meshes.rot.z), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        
        matWorld = np.matmul(matRotZ, matRotX)
        matWorld = np.matmul(matWorld, matTrans)
        
        for t in meshes.tris:
            
                triTransformed = Triangle(Vector(t.p1.x, t.p1.y, t.p1.z), Vector(t.p2.x, t.p2.y, t.p2.z), Vector(t.p3.x, t.p3.y, t.p3.z))
                
                # Moving Triangle based on Object Rotation (It's also supposed to take camera position into account but apparently not)
                triTransformed = TriMatrixMul(t, matWorld)

                # Moving Triangle Again Depending on Object Position
                triTranslated = TriangleAdd(triTransformed, meshes.pos)

                # Moving Triangle Again Again Based on Camera Position, because the first line didn't do that
                triTranslated = TriMatrixMul(triTranslated, matTrans)
                
                # Calculating Normal Vector
                triTranslated.normal = GetNormal(triTranslated)
                
                # Culling triangles we can't see and ones that go behind the camera especially
                if VectorDoP(triTranslated.normal, Vector(0,0,1)) <= 0.3 and TriangleCullTest(triTranslated):
                    
                    # Projecting 3D into 2D
                    triProjected = ProjectTriangle(triTranslated, camera.a, camera.tan, camera.fc, camera.nc)

                    # Scale into view
                    triProjected.p1.x += 1
                    triProjected.p1.y += 1
                    triProjected.p2.x += 1
                    triProjected.p2.y += 1
                    triProjected.p3.x += 1
                    triProjected.p3.y += 1

                    triProjected.p1.x *= 0.5 * camera.scrW
                    triProjected.p1.y *= 0.5 * camera.scrH
                    triProjected.p2.x *= 0.5 * camera.scrW
                    triProjected.p2.y *= 0.5 * camera.scrH
                    triProjected.p3.x *= 0.5 * camera.scrW
                    triProjected.p3.y *= 0.5 * camera.scrH
                    
                    # Normal X and Z are flipped for some reason
                    triProjected.normal = VectorMul(triTranslated.normal, Vector(-1, 1, -1))
                        
                    TrisToDraw.append(triProjected)

    #Sorting Triangles
    TrisToDraw.sort(key = triSort)
    return TrisToDraw
        
