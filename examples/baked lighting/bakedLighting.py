import pygame
import z3dpy as zp
import time
import random as rand

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myList = []

currentTime = time.time()

static = False

slowDown = 0

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)s
zack = zp.Thing([zp.NewSusanne()], 0, 0, 3)

zp.MeshSetColour(zack, [255, 215, 150])

zp.lights.append(zp.Light_Point(2, 0, 1, 1, 1500))

zp.CameraSetTargetFP(myCamera)

zp.SetInternalCamera(myCamera)

zp.BakeLighting([zack])

print("")
print("L to switch between static and dynamic lighting")

stuckInLoop = True

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True
    
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_l]:
        if slowDown < 0:
            slowDown = 10
            static = not static
    slowDown -= 1

    for tri in zp.RasterThings([zack]):
        if static:
            zp.PgDrawTriFLB(tri, screen, pygame)
        else:
            zp.PgDrawTriFL(tri, screen, pygame)

    pygame.display.flip()

    zp.ThingAddRot(zack, [3, 2, 4])

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
