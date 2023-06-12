import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
screenArray = pygame.PixelArray(screen)

zp.SetHowVars(0.733063825608609, 1.3032244924564758)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, -4, 1280, 720)

zp.SetInternalCamera(myCamera)

# z3dpy.LoadAnimMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
anim = zp.Thing([zp.LoadAnimMesh("mesh/explode/explode.obj", 0, 0, 0)], 0, 0, 3)

zp.AddThing(anim)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    clock.tick(30)
    screen.fill("black")
    
    
    for tri in zp.Raster():
        nrm = zp.TriGetNormal(tri)
        shade = (nrm[2] + nrm[1]) * 0.5
        zp.PgDrawTriF(tri, shade, screen, pygame)

    # Increment the frame counter each frame
    zp.ThingIncFrames(anim)
    
    pygame.display.flip()
