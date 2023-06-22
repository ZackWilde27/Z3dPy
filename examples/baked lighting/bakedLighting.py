import pygame
import z3dpy as zp
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

currentTime = time.time()

static = False

coolDown = 0

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Cam(0, 0, 0, 1280, 720)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)s
sus = zp.Thing([zp.NewSusanne()], 0, 0, 3)

zp.lights.append(zp.Light_Point(2, 0, 1, 1, 1500))

zp.CamSetTargetFP(myCamera)

zp.SetInternalCam(myCamera)

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
