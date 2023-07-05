import z3dpy as zp
import pygame
import random as rand

pygame.init()
screen = zp.PgScreen(1280, 720, "black", pygame)
clock = pygame.time.Clock()

# Setting FOV to 75
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Cam(x, y, z)
myCamera = zp.Cam(0, 0, -4)

zp.SetInternalCam(myCamera)

# Mesh to serve as the template
myMesh = zp.LoadMesh("z3dpy/mesh/dot.obj")

# Emitter(vPos, mshTemplate, iMax, vVelocity, fLifetime, vGravity)
myEmitter = zp.Emitter([0, 0, 0], myMesh, 25, [0, 15, 0], 25.0, [1, 4.0, 0])
# vVelocity is the particle's starting velocity

# Add to global list
zp.emitters.append(myEmitter)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(30)
    screen.fill("black")

    ranx = (rand.random() - 0.5) * 25
    rany = (rand.random() - 0.5) * 25

    zp.EmitterSetPos(myEmitter, [ranx, -5, rany])

    zp.TickEmitters()

    for tri in zp.Raster():
        zp.PgDrawTriF(tri, 1, screen, pygame)
        
    pygame.display.flip()
