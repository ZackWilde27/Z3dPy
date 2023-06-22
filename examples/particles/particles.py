import z3dpy as zp
import pygame
import random as rand

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, -4, 1280, 720)

zp.gravity = [1, 4, 0]

myMesh = zp.LoadMesh("z3dpy/mesh/dot.obj", 0, 0, 0, 1, 1, 1)

# Emitter(vStartPos, mshTemplate, iMax, vStartVelocity, fLifetime, bActive)
myEmitter = zp.Emitter([0, 0, 0], myMesh, 25, [0, 15, 0], 25.0, True)

zp.emitters.append(myEmitter)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(30)
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LSHIFT]:
        speed = 0.05
    else:
        speed = 0.25

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(zack, speed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(zack, -speed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(zack, -speed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(zack, speed)

    zp.SetInternalCam(myCamera)

    ranx = (rand.random() - 0.5) * 25
    rany = (rand.random() - 0.5) * 25

    zp.EmitterSetPos(myEmitter, [ranx, -5, rany])

    zp.TickEmitters()

    for tri in zp.Raster():
        zp.PgDrawTriF(tri, 1, screen, pygame)
        
    pygame.display.flip()
