import z3dpy as zp
import pygame
import random as rand
import time

print("")
print("Controls:")
print("E to jump")

delta = 0
currentTime = time.time()

# Changing Gravity
zp.gravity = [0, 10, 0]

zp.worldColour = (0.15, 0.15, 0.2)

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Set the internal screen size
zp.screenSize = (1280, 720)

# Create a camera (vPos)
myCamera = zp.Cam([0, 0, 0])


# The Bird

# Use the LoadMesh function to load an OBJ file
birdBody = zp.LoadMesh("mesh/bird.obj", [0, 0, 0], [0.75, 0.75, 0.75])
birdBeak = zp.LoadMesh("mesh/beak.obj", [0, 0, 0], [0.75, 0.75, 0.75])

# Setting Bird Colour
zp.MeshSetColour(birdBody, [255, 214, 91])
zp.MeshSetColour(birdBeak, [255, 52, 38])

zp.MeshSetId(birdBody, 1)
zp.MeshSetId(birdBeak, 1)

# Group two meshes with different colours into one Thing
bird = zp.Thing([birdBody, birdBeak], [0, 0, 5])

zp.ThingSetupPhysics(bird)
# Hitbox(thing, type, id, radius, height)
zp.ThingSetupHitbox(bird, 2, 0, 1, 1)


# The Ground

planeMesh = zp.LoadMesh("mesh/plane.obj")

zp.MeshSetColour(planeMesh, [119, 255, 102])

plane = zp.Thing([planeMesh], [0, 5, 0])


# The Pipes

pipeMesh = zp.LoadMesh("mesh/pipe.obj")

# Setting the colour to green
zp.MeshSetColour(pipeMesh, [0, 255, 0])

pipe = zp.Thing([pipeMesh], [10, 0, 5])

pipe2 = zp.Thing([pipeMesh], [10, -9, 5])

zp.ThingSetRot(pipe2, [0, 0, 180])

zp.ThingSetupHitbox(pipe, 2, 0, 1, 2)
zp.ThingSetupHitbox(pipe2, 2, 0, 1, 2)

# Pipe Pair Functions
def SpawnPipePair(h):
    zp.ThingSetPosX(pipe, 10)
    zp.ThingSetPosY(pipe, h)
    zp.ThingSetPosX(pipe2, 10)
    zp.ThingSetPosY(pipe2, h - 9)

SpawnPipePair(-1)

def Reset():
    zp.ThingSetPos(bird, [0, 0, 5])
    SpawnPipePair(-1)


# Adding everything to internal lists
zp.AddThings([bird, pipe, pipe2])
# Optional layer argument, which is normally 2 / the third layer
zp.AddThing(plane, 1)

# Sun light
# Light_Sun(vRot, FStrength, unused, *vColour)
theSun = zp.Light_Sun((-45, 15, 0), 0.8, 0, (244, 255, 193))

# Append all lights to global list
zp.lights.append(theSun)

# BakeLighting(things, *bExpensive, *lights, *shadowcasters)
zp.BakeLighting()

zp.CamSetPos(myCamera, [zp.ThingGetPosX(bird), zp.ThingGetPosY(bird), -3])

# Raster Loop
while True:
    delta = zp.GetDelta()
    
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Reset on collision
    if len(zp.GatherCollisions([bird, pipe, pipe2])):
        Reset()

    # Input
    keys = pygame.key.get_pressed()

    # Jump, but only when going down.
    if keys[pygame.K_e] and zp.ThingGetVelocityY(bird) >= 0:
        zp.ThingSetVelocityY(bird, -20.0)

    # HandlePhysicsFloor(things, *height)
    zp.HandlePhysicsFloor([bird], 5.0)

    # Bird Rotation
    rotation = zp.ThingGetVelocityY(bird) * 2
    rotation = min(rotation, 40)
    if zp.ThingGetPosY(bird) == 5:
        zp.ThingSetRot(bird, [0, 0, 0])
    else:
        zp.ThingSetRot(bird, [0, 0, rotation])

    # Moving Pipe Pairs
    zp.ThingSubPos(pipe, [5 * delta, 0, 0])
    zp.ThingSubPos(pipe2, [5 * delta, 0, 0])
    if zp.ThingGetPosX(pipe) <= -8:
        SpawnPipePair(rand.random() * 6 + 1)

    # Smoothly following the bird
    # CamChase(camera, targetLocation, speed)
    zp.CamChase(myCamera, [zp.ThingGetPosX(bird), zp.ThingGetPosY(bird), -3], 10)

    # Setting the target forward
    zp.CamSetTargetDir(myCamera, [0, 0, 1])

    # Calculate the new view matrix
    zp.SetInternalCam(myCamera)

    # Clear Screen
    screen.fill("#88E5FF")

    # Render 3D
    for tri in zp.Raster():
        if zp.TriGetId(tri) == 0:
            zp.PgDrawTriFLB(tri, screen, pygame)
        else:
            zp.PgDrawTriFL(tri, screen, pygame)

    # Update display
    pygame.display.flip()

    # FPS calculation
    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(1 // (time.time() - currentTime)) + " FPS")
    currentTime = time.time()
    
