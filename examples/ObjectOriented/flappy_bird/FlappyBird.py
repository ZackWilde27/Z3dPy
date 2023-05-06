import z3dpy as z
import pygame
import random as rand
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myList = []

# Use the LoadMesh function to load an OBJ file
birdBody = z.LoadMesh("mesh/bird.obj", 0, 0, 0)
birdBeak = z.LoadMesh("mesh/beak.obj", 0, 0, 0)

z.MeshSetColour(birdBody, 255, 214, 91)
z.MeshSetColour(birdBeak, 255, 52, 38)

# We can group two meshes with different colours into one Thing
bird = z.Thing([birdBody, birdBeak], 0, 0, 5)
myList.append(bird)

planeMesh = z.LoadMesh("mesh/plane.obj", 0, 0, 0)

z.MeshSetColour(planeMesh, 119, 255, 102)

plane = z.Thing([planeMesh], 0, 5, 0)
myList.append(plane)

# This one is going to be replaced by the pipes
myList.append(z.Thing([planeMesh], 0, 5, 0))

pipeMesh = z.LoadMesh("mesh/pipe.obj", 0, 0, 0)
# Offset the second pipe upwards
otherPipeMesh = z.LoadMesh("mesh/pipe.obj", 0, -11, 0)
z.MeshSetRot(otherPipeMesh, 0, 0, 180)
# Setting the colour to green
z.MeshSetColour(pipeMesh, 0, 255, 0)
z.MeshSetColour(otherPipeMesh, 0, 255, 0)

# Pipe Pair
def SpawnPipePair(h):
    myList.pop()
    myList.append(z.Thing([pipeMesh, otherPipeMesh], 10, h, 5))

SpawnPipePair(-1)


# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z.Camera(0, 0, -3, 1280, 720)

birdVelocity = 0


# Raster Loops
done = False

while not done:
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
    clock.tick(30)
    screen.fill("#88E5FF")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_e]:
        birdVelocity = -0.5

    # Locking Camera to Bird kinda
    if z.CameraGetPos(myCamera)[1] > z.ThingGetPos(bird)[1]:
        z.CameraSubPos(myCamera, 0, 0.25, 0)
    else:
        z.CameraSetPosY(myCamera, z.ThingGetPosY(bird))
    z.CameraSetPosX(myCamera, z.ThingGetPosX(bird))

    z.CameraSetTargetV(myCamera, z.VectorAdd(z.CameraGetPos(myCamera), [0, 0, 1]))

    # Gravity
    if birdVelocity < 1:
        birdVelocity += 0.04

    # Tilting Bird
    z.ThingSetRot(bird, 0, 0, birdVelocity * 50)

    # Moving Pipe Pairs
    z.ThingSubPos(myList[2], 0.2, 0, 0)
    if z.ThingGetPosX(myList[2]) <= -8:
        SpawnPipePair(rand.random() * 3 + 1)
    
    # Moving the bird by it's velocity, if we're not on the ground
    if z.ThingGetPos(bird)[1] < z.ThingGetPos(plane)[1] - 1 or birdVelocity < 0:
        z.ThingAddPos(bird, 0, birdVelocity, 0)
    else:
        z.ThingSetPosY(bird, z.ThingGetPosY(plane) - 1)


    for tri in z.RasterThings(myList, myCamera):
        normal = z.TriangleGetNormal(tri)
        z.DrawTriangleS(tri, screen, max((-normal[2] + -normal[1]) / 2, 0), pygame)

    # Update display
    pygame.display.flip()

    
