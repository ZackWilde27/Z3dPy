import pygame
import z3dpy as zp
import time
import random as rand

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myList = []

currentTime = time.time()

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

zp.CameraSetFOV(myCamera, 75)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
zack = zp.Thing([zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 0)], 0, 0, 3)



stuckInLoop = True

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True
            
    clock.tick(60)
    
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.CameraSetPos(myCamera, zp.VectorAdd(zp.CameraGetPos(myCamera), zp.CameraGetTargetVector(myCamera)))
    if keys[pygame.K_s]:
        zp.CameraSetPos(myCamera, zp.VectorSub(zp.CameraGetPos(myCamera), zp.CameraGetTargetVector(myCamera)))
    if keys[pygame.K_a]:
        zp.CameraSetPos(myCamera, zp.VectorAdd(zp.CameraGetPos(myCamera), zp.CameraGetRightVector(myCamera)))
    if keys[pygame.K_d]:
        zp.CameraSetPos(myCamera, zp.VectorSub(zp.CameraGetPos(myCamera), zp.CameraGetRightVector(myCamera)))

    zp.CameraSetTargetFP(myCamera, 0, 0)

    zp.SetInternalCamera(myCamera)

    for tri in zp.RasterThings([zack]):
        normal = zp.TriangleGetNormal(tri)
        zp.PgDrawTriangleF(tri, (normal[2] + normal[1]) / 2, screen, pygame)

    pygame.display.flip()

    zp.ThingAddRot(zack, [2, 1, 3])

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
