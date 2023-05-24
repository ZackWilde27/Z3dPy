import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# z3dpy.LoadMesh(filename, x, y, z)
try:
    susanne = zp.LoadMesh("z3dpy/mesh/susanne.obj", 0, 0, 0)
except:
    # Installed globally, retrieve the built-in mesh from the module
    susanne = zp.NewSusanne()

# z3dpy.Thing(meshList, x, y, z)
thing = zp.Thing([susanne], 0, 0, 3)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCamera(myCamera)

# Raster Loop
while True:
    
    # More PyGame stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    clock.tick(60)
    screen.fill("black")

    # Render 3D
    for tri in zp.RasterThings([thing]):
        zp.PgDrawTriangleF(tri, zp.TriangleGetNormal(tri)[2], screen, pygame)

    # Update the screen afterwards
    pygame.display.flip()

    # z3dpy.ThingAddRot(thing, vector)
    zp.ThingAddRot(thing, [2, 1, 3])
