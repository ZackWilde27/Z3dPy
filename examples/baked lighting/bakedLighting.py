import pygame
import z3dpy as zp
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

currentTime = time.time()
static = False
coolDown = 0

# Camera(x, y, z, scrW, scrH)
myCamera = zp.Cam(0, 0, -5)

zp.CamSetTargetDir(myCamera, [0, 0, 1])
zp.SetInternalCam(myCamera)

# LoadMesh(filename, x, y, z)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")
# Thing(meshList, x, y, z)
sus = zp.Thing([myMesh], 0, 0, 0)

# Light_Point(x, y, z, FStrength, fRadius, vColour)
redLight = zp.Light_Point(2.25, 0, 2, 0.8, 3.0, (255, 0, 0))

blueLight = zp.Light_Point(-2.25, 0, -2, 0.8, 3.0, (0, 0, 255))

# Append to global list
zp.lights.append(redLight)
zp.lights.append(blueLight)

# BakeLighting(thingList, bExpensive)
zp.BakeLighting([sus])

print("")
print("L to switch between static and dynamic lighting")

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_l]:
        if coolDown < 0:
            coolDown = 10
            static = not static
    coolDown -= 1

    if static:
        for tri in zp.RasterThings([sus]):
            zp.PgDrawTriFLB(tri, screen, pygame)

    else:
        for tri in zp.RasterThings([sus]):
            zp.PgDrawTriFL(tri, screen, pygame)

    pygame.display.flip()

    zp.ThingAddRot(sus, [1, 2, 3])

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
