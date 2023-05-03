import z3dpy
import pygame
import random as rand
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myList = []

birdVelocity = 0

# Use the LoadMesh function to load an OBJ file
bird = z3dpy.Thing([z3dpy.LoadMesh("bird.obj", 0, 0, 0)], 0, 0, 5)
myList.append(bird)

plane = z3dpy.Thing([z3dpy.LoadMesh("plane.obj", 0, 0, 0)], 0, 5, 0)

myList.append(plane)
myList.append(plane)
myList.append(plane)


# Pipe Pair

def SpawnPipePair(z):
    myList.pop()
    myList.pop()
    myList.append(z3dpy.Thing([z3dpy.LoadMesh("pipe.obj", 0, 0, 0)], 10, z, 5))
    myList.append(z3dpy.Thing([z3dpy.LoadMesh("pipe.obj", 0, 0, 0)], 10, z - 10, 5))
    myList[3].rot.z = 180

SpawnPipePair(-1)



# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, -3, 1280, 720, 90, 0.1, 1500)


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
    if myCamera.y > bird.pos.y:
        myCamera.y -= 0.25
    else:
        myCamera.y = bird.pos.y
    myCamera.x = bird.pos.x

    # Gravity
    if birdVelocity < 1:
        birdVelocity += 0.04

    # Tilting Bird
    bird.rot.z = birdVelocity * 50

    # Moving Pipe Pairs
    myList[2].pos.x -= 0.2
    myList[3].pos.x -=  0.2
    if myList[2].pos.x <= -8:
        SpawnPipePair(rand.random() * 3 + 1)
    
    if bird.pos.y < myList[1].pos.y - 1 or birdVelocity < 0:
        bird.pos.y += birdVelocity
    else:
        bird.pos.y = plane.pos.y - 1


    for tri in z3dpy.RasterThings(myList, myCamera):

        z3dpy.DrawTriangleS(tri, screen, max((-tri.normal.z + -tri.normal.y) / 2, 0), pygame)

    # Update display
    pygame.display.flip()

    
