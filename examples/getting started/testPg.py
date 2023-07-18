import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))

zp.screenSize = (1280, 720)

# Cam(x, y, z)
myCamera = zp.Cam(0, 0, 0)

# LoadMesh(filename, *x, *y, *z, *sclX, *sclY, *sclZ)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

# Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:
    
    # More PyGame stuff to prevent freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Clear the screen
    screen.fill("black")

    # Render 3D
    for tri in zp.RasterThings([myThing]):
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriF(tri, normal[2], screen, pygame)

    # Update the screen
    pygame.display.flip()

    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 2, 2])
