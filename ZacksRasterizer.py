# Zack's Python Rasterizer

import math
import numpy as np
import time
import pygame
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

# Variables

# Screen Variables
scrW = 256
scrH = 240

ResolutionScale = 2

scrW *= ResolutionScale
scrH *= ResolutionScale

track = time.time()

pygame.init()
screen = pygame.display.set_mode((scrW, scrH))

clock = pygame.time.Clock()



# Camera Controls   
Yaw = 0
Roll = 0
Pitch = 15
CamLoc = Vector(0, 0, 0)

# Other Camera Variables
CamFOV = 80
# Near Clip
CamNC = 0.2
# Far Clip
CamFC = 1000

CamTheta = CamFOV / 2
CamTan = (1 / math.tan(CamTheta))
CamAspR = scrH/scrW

# Dimension associated with basic flat shading. 0 is X, 1 is Y, 2 is Z
colorDir = 2


ProjectionMatrix = np.matrix([[CamAspR * CamTan, 0, 0, 0], [0, CamTan, 0, 0], [0, 0, CamFC / (CamFC - CamNC), 1], [0, 0, (-CamFC * CamNC) / (CamFC - CamNC), 0]])

matRotZ = np.matrix([[1, 0, 0, 0], [0, math.cos((time.time() - track) / 2), math.sin((time.time() - track) / 2), 0], [0, -math.sin((time.time() - track) / 2), math.cos((time.time() - track) / 2), 0], [0, 0, 1, 0]])

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

def Projection(vector):
    a = CamAspR
    f = 1 / math.tan(CamTheta)
    q = CamFC / (CamFC - CamNC)
    if vector.z != 0:
        return Vector((a * f * vector.x) / vector.z, (f * vector.y) / vector.z, (q * vector.z) - (q * CamNC))
    else:
        return Vector(0, 0, 0)

def ProjectTriangle(t):
    return Triangle(Projection(t.p1), Projection(t.p2), Projection(t.p3))

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

def DrawTriangleRGB(tri, surface, colour):
    pygame.draw.polygon(surface, (max(colour.x, 0) * 255, max(colour.y, 0) * 255, max(colour.z, 0) * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

def DrawTriangleF(tri, surface, f):
    pygame.draw.polygon(surface, (f * 255, f * 255, f * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

# Sort Triangles based on their distance from the camera
def triSort(n):
    return CamFC - abs(((n.p1.z + n.p2.z + n.p3.z) / 3) - CamLoc.z)


# Matrix Functions

def GetTranslationMatrix():
    return np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [CamLoc.x, CamLoc.y, CamLoc.z, 1]])

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

# Start

print("")
print("Enter the name of the object to display (n for default susanne): ")
print("If your file was example.obj, type example")
print("*Note the obj has to be in the same directory as this script")

customMesh = input("File Name: ")

Objs.append(LoadMesh(customMesh + '.obj', 0, 0, 4))

print("")
shade = input("Shade with lighting or normals?[l/n]: ")
print("Done, if the model exists, it should appear on the pygame screen")
print("")
print("WASD to move around, Q and E to change elevation")



# Raster Loop

thereYet = False

while not thereYet:
    
    # For some reason I need this or else it'll crash
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            thereYet = True
            
    # Tick at 30 FPS
    clock.tick(30)
    
    # Reset Screen
    screen.fill("black")

    # Clear Lists
    TrisToDraw = []
    TrisToRef = []
    usedColours = []
    
    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        CamLoc.z -= 1
    if keys[pygame.K_s]:
        CamLoc.z += 1
    if keys[pygame.K_a]:
        CamLoc.x -= 1
    if keys[pygame.K_d]:
        CamLoc.x += 1
    if keys[pygame.K_q]:
        CamLoc.y += 1
    if keys[pygame.K_e]:
        CamLoc.y -= 1

    # This one we only need to calculate once per frame
    matTrans = GetTranslationMatrix()
    
    # Gather Triangles
    for gh in Objs:
        
        matRotX = MatrixMakeRotX(gh.rot.x)
        matRotZ = np.matrix([[math.cos(gh.rot.z), math.sin(gh.rot.z), 0, 0], [-math.sin(gh.rot.z), math.cos(gh.rot.z), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        
        matWorld = np.matmul(matRotZ, matRotX)
        matWorld = np.matmul(matWorld, matTrans)
        
        for t in gh.tris:
            
                triTransformed = Triangle(Vector(t.p1.x, t.p1.y, t.p1.z), Vector(t.p2.x, t.p2.y, t.p2.z), Vector(t.p3.x, t.p3.y, t.p3.z))
                
                # Moving Triangle based on Object Rotation (It's also supposed to take camera position into account but apparently not)
                triTransformed = TriMatrixMul(t, matWorld)

                # Moving Triangle Again Depending on Object Position
                triTranslated = TriangleAdd(triTransformed, gh.pos)

                # Moving Triangle Again Again Based on Camera Position, because the first line didn't do that
                triTranslated = TriMatrixMul(triTranslated, matTrans)
                
                # Calculating Normal Vector
                triTranslated.normal = GetNormal(triTranslated)
                
                # Culling triangles we can't see and ones that go behind the camera especially
                if VectorDoP(triTranslated.normal, Vector(0,0,1)) <= 0.3 and TriangleCullTest(triTranslated):
                    
                    # Projecting 3D into 2D
                    triProjected = ProjectTriangle(triTranslated)

                    # Scale into view
                    triProjected.p1.x += 1
                    triProjected.p1.y += 1
                    triProjected.p2.x += 1
                    triProjected.p2.y += 1
                    triProjected.p3.x += 1
                    triProjected.p3.y += 1

                    triProjected.p1.x *= 0.5 * scrW
                    triProjected.p1.y *= 0.5 * scrH
                    triProjected.p2.x *= 0.5 * scrW
                    triProjected.p2.y *= 0.5 * scrH
                    triProjected.p3.x *= 0.5 * scrW
                    triProjected.p3.y *= 0.5 * scrH
                    
                    # Normal X and Z are flipped for some reason
                    triProjected.normal = VectorMul(triTranslated.normal, Vector(-1, 1, -1))
                        
                    TrisToDraw.append(triProjected)

    #Sorting Triangles
    TrisToDraw.sort(key = triSort)
    
    # Drawing Triangles to Buffers
    for fd in TrisToDraw:
        
        if shade == "n":
            
            DrawTriangleRGB(fd, screen, fd.normal)
            
        else:
            
            currentColour = max(VectorToList(fd.normal)[colorDir], 0.05)
            DrawTriangleF(fd, screen, currentColour)

                        
    # Update Visualization Afterwards
    pygame.display.flip()
    
    # Rotating Object
    Objs[0].rot.x += 0.1
    Objs[0].rot.z += 0.13

pygame.quit()
        
