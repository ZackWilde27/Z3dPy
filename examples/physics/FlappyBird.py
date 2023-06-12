import z3dpy as zp
import pygame
import random as rand

print("")
print("Controls:")
print("E to jump")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Use the LoadMesh function to load an OBJ file
# LoadMesh has optional arguments for x, y, z, and sclx, scly, sclz.

birdBody = zp.LoadMesh("mesh/bird.obj", 0, 0, 0, 0.75, 0.75, 0.75)
birdBeak = zp.LoadMesh("mesh/beak.obj", 0, 0, 0, 0.75, 0.75, 0.75)

# Setting Bird Colour
zp.MeshSetColour(birdBody, [255, 214, 91])
zp.MeshSetColour(birdBeak, [255, 52, 38])

# Changing Gravity
zp.gravityDir = [0, 4, 0]

# Group two meshes with different colours into one Thing
bird = zp.Thing([birdBody, birdBeak], 0, 0, 5)

# Setting up Physics Body
zp.ThingSetupPhysics(bird)

planeMesh = zp.LoadMesh("mesh/plane.obj")

zp.MeshSetColour(planeMesh, [119, 255, 102])

plane = zp.Thing([planeMesh], 0, 5, 0)

pipeMesh = zp.LoadMesh("mesh/pipe.obj")


# Offset the second pipe upwards
otherPipeMesh = zp.LoadMesh("mesh/pipe.obj", 0, -11, 0)
zp.MeshSetRot(otherPipeMesh, [0, 0, 180])

# Setting the colour to green
zp.MeshSetColour(pipeMesh, [0, 255, 0])
zp.MeshSetColour(otherPipeMesh, [0, 255, 0])

pipe = zp.Thing([pipeMesh, otherPipeMesh], 10, 0, 5)


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


# Adding everything to internal lists

zp.AddThings([bird, pipe])
# Optional layer argument, which is normally 2 / the third layer
zp.AddThing(plane, 1)


# Raster Loop
while True:
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    clock.tick(30)
    screen.fill("#88E5FF")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_e] and (zp.ThingGetVelocityY(bird) >= 0 or zp.ThingGetPosY(bird) == 5):
        zp.ThingSetVelocityY(bird, -2.5)

    zp.ThingSetPosZ(bird, 5)

    # Z3dPy Physics System
    zp.HandlePhysicsFloor([bird], 5)

    # Smoothly following the bird
    comp = zp.ThingGetPosY(bird) - zp.CameraGetPos(myCamera)[1]
    if abs(comp) > 0.1:
        zp.CameraSubPos(myCamera, [0, -comp * 0.25, 0])
    else:
        zp.CameraSetPosY(myCamera, zp.ThingGetPosY(bird))
    zp.CameraSetPosX(myCamera, zp.ThingGetPosX(bird))

    zp.CameraSetTargetVector(myCamera, [0, 0, 1])

    zp.SetInternalCamera(myCamera)

    # Tilting Bird
    rotation = min(zp.ThingGetVelocityY(bird) * 15, 40)
    if zp.ThingGetPosY(bird) == 5:
        zp.ThingSetRot(bird, [0, 0, 0])
    else:
        zp.ThingSetRot(bird, [0, 0, rotation])

    # Moving Pipe Pairs
    zp.ThingSubPos(pipe, [0.2, 0, 0])
    if zp.ThingGetPosX(pipe) <= -8:
        SpawnPipePair(rand.random() * 6 + 1)

    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriS(tri, (normal[2] + normal[1]) / 2, screen, pygame)

    # Update display
    pygame.display.flip()

    
