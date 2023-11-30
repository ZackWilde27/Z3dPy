import pygame
import z3dpy as zp

pygame.init()
screen = pygame.display.set_mode((1280, 720))

zp.screenSize = (1280, 720)

myCam = zp.Cam([0, 0, 0])
zp.SetInternalCam(myCam)

myMesh = zp.LoadMesh("z3dpy/mesh/cube.obj", VScale=[0.5, 0.5, 0.15])

myMesh.material = zp.MATERIAL_DYNAMIC

# Emitter(vPos, templateMesh, max, vVelocity, lifetime, vGravity, randomness)
emit = zp.Emitter([0, 0, 5], myMesh, 50, [0, 5, 0], 1.0, (0, -4.5, 0), 7.0)
zp.emitters.append(emit)

zp.lights.append(zp.Light(zp.LIGHT_POINT, [0, 4, 3], 0.8, 10, [255, 106, 0]))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    zp.HandleEmitters([emit])

    screen.fill("black")

    for tri in zp.Raster():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(tri, False))

    pygame.display.flip()
