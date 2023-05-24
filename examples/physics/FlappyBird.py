import z3dpy as zp
import pygame
import random as rand
import time

print("")
print("Controls:")
print("E to jump")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Use the LoadMesh function to load an OBJ file
birdBody = zp.LoadMesh("mesh/bird.obj", 0, 0, 0)
birdBeak = zp.LoadMesh("mesh/beak.obj", 0, 0, 0)

# Setting Bird Colour
zp.MeshSetColour(birdBody, [255, 214, 91])
zp.MeshSetColour(birdBeak, [255, 52, 38])

# Increasing Gravity
zp.gravityDir = [0, 15, 0]

# We can group two meshes with different colours into one Thing
bird = zp.Thing([birdBody, birdBeak], 0, 0, 5)

# Setting up Physics Body
bird[6] = zp.PhysicsBody()

planeMesh = zp.LoadMesh("mesh/plane.obj", 0, 0, 0)

zp.MeshSetColour(planeMesh, [119, 255, 102])

plane = zp.Thing([planeMesh], 0, 5, 0)

pipeMesh = zp.LoadMesh("mesh/pipe.obj", 0, 0, 0)


# Offset the second pipe upwards
otherPipeMesh = zp.LoadMesh("mesh/pipe.obj", 0, -11, 0)
zp.MeshSetRot(otherPipeMesh, [0, 0, 180])

# Setting the colour to green
zp.MeshSetColour(pipeMesh, [0, 255, 0])
zp.MeshSetColour(otherPipeMesh, [0, 255, 0])

pipe = zp.Thing([pipeMesh, otherPipeMesh], 10, 0, 5)

# Setting up hitbox
pipe[4] = zp.Hitbox(2, 0, 1, 1)
zp.ThingSetCollision(pipe, 2, 1, 15, 0)


# Pipe Pair
def SpawnPipePair(h):
    zp.ThingSetPosX(pipe, 10)
    zp.ThingSetPosY(pipe, h)

SpawnPipePair(-1)

def Reset():
    zp.ThingSetPos(bird, [0, 0, 5])
    zp.ThingSetVelocity(bird, [0, 0, 0])
    SpawnPipePair(-1)


# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = zp.Camera(0, 0, -3, 1280, 720)

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
        zp.ThingSetVelocityY(bird, -12)

    # The physics system causes the bird to slowly inch towards the camera
    # Pushing it back as a band-aid fix till I figure out the cause
    zp.ThingSetVelocityZ(bird, 0.2)

    # Z3dPy Physics System
    zp.HandlePhysics([bird], 5)

    for cols in zp.GatherCollisions([bird, pipe]):
        Reset()
        

    # Locking Camera to Bird kinda
    if zp.CameraGetPos(myCamera)[1] > zp.ThingGetPos(bird)[1]:
        zp.CameraSubPos(myCamera, [0, 0.25, 0])
    else:
        zp.CameraSetPosY(myCamera, zp.ThingGetPosY(bird))
    zp.CameraSetPosX(myCamera, zp.ThingGetPosX(bird))

    zp.CameraSetTargetVector(myCamera, [0, 0, 1])

    zp.SetInternalCamera(myCamera)

    # Tilting Bird
    rotation = min(zp.ThingGetVelocityY(bird) * 2, 40)
    if zp.ThingGetPosY(bird) == 5:
        zp.ThingSetRot(bird, [0, 0, 0])
    else:
        zp.ThingSetRot(bird, [0, 0, rotation])

    # Moving Pipe Pairs
    zp.ThingSubPos(pipe, [0.2, 0, 0])
    if zp.ThingGetPosX(pipe) <= -8:
        SpawnPipePair(rand.random() * 3 + 1)

    for tri in zp.RasterThings([plane]):
        normal = zp.TriangleGetNormal(tri)
        zp.PgDrawTriangleS(tri, (normal[2] + normal[1]) / 2, screen, pygame)

    for tri in zp.RasterThings([bird, pipe]):
        normal = zp.TriangleGetNormal(tri)
        zp.PgDrawTriangleS(tri, (normal[2] + normal[1]) / 2, screen, pygame)

    # Update display
    pygame.display.flip()

    
