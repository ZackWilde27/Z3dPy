import pygame
import z3dpy as zp
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

currentTime = time.time()
static = False
coolDown = 0

# Camera(x, y, z)
myCamera = zp.Cam(0, 0, -3)

zp.CamSetTargetDir(myCamera, [0, 0, 1])
zp.SetInternalCam(myCamera)

# LoadMesh(filename, x, y, z)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

zp.MeshSetColour(myMesh, (255, 255, 255))
# Thing(meshList, x, y, z)
sus = zp.Thing([myMesh], 0, 0, 0)

zp.AddThing(sus)

# Light_Point(x, y, z, FStrength, fRadius, vColour)
redLight = zp.Light_Point([2.25, 0, 2], 0.8, 4.0, (255, 0, 0))
blueLight = zp.Light_Point([-2.25, 0, -2], 0.8, 4.0, (100, 100, 255))

# Append to global list
zp.lights.append(redLight)
zp.lights.append(blueLight)

zp.worldColour = (0.02, 0.00, 0.02)

# BakeLighting(thingList, bExpensive)
zp.BakeLighting()

held = False
fps = 30

print("")
print("L to switch between static and dynamic lighting")

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    # Making sure that it only flips once when you press it.
    if keys[pygame.K_l]:
        if not held:
            held = True
            static = not static
    else:
        held = False
    coolDown -= 1

    if static:
        for tri in zp.Raster():
            zp.PgDrawTriFLB(tri, screen, pygame)

    else:
        for tri in zp.Raster():
            zp.PgDrawTriFL(tri, screen, pygame)

    pygame.display.flip()

    zp.ThingAddRot(sus, (2, 2, 2))

    fps = int(1 / (time.time() - currentTime))

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(fps) + " FPS")
    currentTime = time.time()
