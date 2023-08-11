import pygame
import z3dpy as zp
import time

print("")
print("L to switch between static and dynamic lighting")
print("WASD to move the model")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

currentTime = time.time()
static = False
coolDown = 0

# Cam(vPos)
myCamera = zp.Cam([0, 0, -3])

zp.CamSetTargetDir(myCamera, [0, 0, 1])
zp.SetInternalCam(myCamera)

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

zp.MeshSetColour(myMesh, (255, 255, 255))
# Thing(meshList, vPos)
susanne = zp.Thing([myMesh], [0, 0, 0])

# Add to global list
zp.AddThing(susanne)

# Light_Point(vPos, FStrength, fRadius, vColour)
redLight = zp.Light_Point([2.25, 0, 2], 0.8, 5.0, (255, 0, 0))
blueLight = zp.Light_Point([-2.25, 0, -2], 0.8, 5.0, (100, 100, 255))

# Append to global list
zp.lights.append(redLight)
zp.lights.append(blueLight)

# worldColour is the minimum amount of light
zp.worldColour = (0.02, 0.00, 0.02)

# BakeLighting(*things, *bExpensive)
# By default, everything in the internal layers
zp.BakeLighting()

held = False
fps = 30

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.ThingAddPos(susanne, [0, 0, 0.25])
    if keys[pygame.K_s]:
        zp.ThingAddPos(susanne, [0, 0, -0.25])
    if keys[pygame.K_a]:
        zp.ThingAddPos(susanne, [-0.25, 0, 0])
    if keys[pygame.K_d]:
        zp.ThingAddPos(susanne, [0.25, 0, 0])

    # Making sure that it only flips once per press.
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
        for tri in zp.DebugRaster():
            if zp.TriGetId(tri) == -1:
                zp.PgDrawTriOutl(tri, [255, 0, 0], screen, pygame)
            else:
                zp.PgDrawTriFL(tri, screen, pygame)

    pygame.display.flip()
    
    zp.ThingAddRot(susanne, (2, 2, 2))

    fps = 1 // (time.time() - currentTime)

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(fps) + " FPS")
    currentTime = time.time()
