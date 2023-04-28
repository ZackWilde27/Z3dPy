import z3dpy
import pygame
import random as rand

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myMeshList = []

birdVelocity = 0

# Use the LoadMesh function to load an OBJ file
myMeshList.append(z3dpy.LoadMesh("bird.obj", 0, 0, 5))
myMeshList.append(z3dpy.LoadMesh("plane.obj", 0, 5, 0))
myMeshList.append(z3dpy.LoadMesh("plane.obj", 0, 5, 0))
myMeshList.append(z3dpy.LoadMesh("plane.obj", 0, 5, 0))
# Pipe Pair

def SpawnPipePair(z):
    myMeshList.pop()
    myMeshList.pop()
    myMeshList.append(z3dpy.LoadMesh("pipe.obj", 10, z, 5))
    myMeshList.append(z3dpy.LoadMesh("pipe.obj", 10, z - 10, 5))
    myMeshList[3].rot.z = 180 * 0.0174533

SpawnPipePair(-1)



# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)

# Raster Loops
done = False

while not done:
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
    clock.tick(30)
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_e]:
        birdVelocity = -0.5

    # Locking Camera to Bird kinda
    if myCamera.y > myMeshList[0].pos.y:
        myCamera.y -= 0.25
    else:
        myCamera.y = myMeshList[0].pos.y
    myCamera.x = myMeshList[0].pos.x

    # Gravity
    if birdVelocity < 1:
        birdVelocity += 0.04

    # Tilting Bird
    myMeshList[0].rot.z = min(max(birdVelocity, -1), 1)

    # Moving Pipe Pairs
    myMeshList[2].pos.x -= 0.2
    myMeshList[3].pos.x -=  0.2
    if myMeshList[2].pos.x <= -8:
        SpawnPipePair(rand.random() * 3 + 1)
    
    if myMeshList[0].pos.y < myMeshList[1].pos.y - 1 or birdVelocity < 0:
        myMeshList[0].pos.y += birdVelocity
    else:
        myMeshList[0].pos.y = myMeshList[1].pos.y - 1
    
    for tris in z3dpy.RasterTriangles(myMeshList, myCamera):
        z3dpy.DrawTriangleF(tris, screen, max((tris.normal.z + -tris.normal.y )/ 2, 0), pygame)

    # Update display
    pygame.display.flip()

    
