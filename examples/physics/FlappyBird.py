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
birdBody.SetColour([255, 214, 91])
birdBeak.SetColour([255, 52, 38])

birdBody.material = zp.MATERIAL_DYNAMIC
birdBeak.material = zp.MATERIAL_DYNAMIC

birdBody.id = 1
birdBeak.id = 1

# Group two meshes with different colours into one Thing
bird = zp.Thing([birdBody, birdBeak], [0, 0, 5])

bird.physics = zp.PhysicsBody()
# Hitbox(type, id, radius, height)
bird.hitbox = zp.Hitbox(zp.HITBOX_BOX, 0, 1, 1)


# The Ground

planeMesh = zp.LoadMesh("mesh/plane.obj")

planeMesh.SetColour([119, 255, 102])

planeMesh.material = zp.MATERIAL_STATIC

plane = zp.Thing([planeMesh], [0, 5, 0])


# The Pipes

pipeMesh = zp.LoadMesh("mesh/pipe.obj")

# Setting the colour to green
pipeMesh.SetColour([0, 255, 0])

pipeMesh.material = zp.MATERIAL_STATIC

pipe = zp.Thing([pipeMesh], [10, 0, 5])

pipe2 = zp.Thing([pipeMesh], [10, -9, 5])

pipe2.rotation = [0, 0, 180]

pipe.hitbox = zp.Hitbox(zp.HITBOX_BOX, 0, 1, 2)
pipe2.hitbox = zp.Hitbox(zp.HITBOX_BOX, 0, 1, 2)

# Pipe Pair Functions
def SpawnPipePair(h):
    pipe.position[0] = 10
    pipe.position[1] = h
    pipe2.position[0] = 10
    pipe2.position[1] = h - 11

SpawnPipePair(-1)

def Reset():
    bird.position = [0, 0, 5]
    SpawnPipePair(-1)


# Adding everything to internal lists
zp.AddThings([bird, pipe, pipe2])
# Optional layer argument, which is normally 2 / the third layer
zp.AddThing(plane, 1)

# Sun light
# Light(type, vRot, FStrength, unused, *vColour)
theSun = zp.Light(zp.LIGHT_SUN, (-45, 15, 0), 0.8, 0, (244, 255, 193))

# Append all lights to global list
zp.lights.append(theSun)

# BakeLighting(things, *bExpensive, *lights, *shadowcasters)
zp.BakeLighting([plane, pipe, pipe2])

myCamera.position = [bird.position[0], bird.position[1], -3]

# Raster Loop
while True:
    delta = zp.GetDelta()
    
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Reset on collision
    if zp.GatherCollisions([bird, pipe, pipe2]):
        Reset()

    # Input
    keys = pygame.key.get_pressed()

    # Jump, but only when going down.
    if keys[pygame.K_e] and bird.physics.velocity[1] >= 0:
        bird.physics.velocity[1] = -20.0

    # HandlePhysicsFloor(things, *height)
    zp.HandlePhysicsFloor([bird], 5.0)

    # Bird Rotation
    rotation = bird.physics.velocity[1] * 2
    rotation = min(rotation, 40)
    if bird.position[1] == 5:
        bird.rotation = [0, 0, 0]
    else:
        bird.rotation = [0, 0, rotation]

    # Moving Pipe Pairs
    distance = 5 * delta
    pipe.position[0] -= distance
    pipe2.position[0] -= distance
    if pipe.position[0] <= -8:
        SpawnPipePair(rand.random() * 6 + 1)

    # Smoothly following the bird
    # Chase(targetLocation, speed)
    myCamera.Chase([bird.position[0], bird.position[1], -3], 5)

    # Setting the target forward
    myCamera.SetTargetDir([0, 0, 1])

    # Calculate the new view matrix
    zp.SetInternalCam(myCamera)

    # Clear Screen
    screen.fill("#88E5FF")

    # Render 3D
    for tri in zp.Render():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(tri, False))

    # Update display
    pygame.display.flip()

    # FPS calculation
    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(1 // (time.time() - currentTime)) + " FPS")
    currentTime = time.time()
    
