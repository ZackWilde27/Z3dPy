import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
# PgScreen(height, width, bgCol, pygame)
screen = zp.PgScreen(1280, 720, "black", pygame)

# Cam(x, y, z)
myCamera = zp.Cam(0, 0, 0)

# LoadMesh(filename)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

# Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Adding to render queue
zp.AddThing(myThing)

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
    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriF(tri, normal[2], screen, pygame)

    # Update the screen
    pygame.display.flip()

    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [1, 2, 3])
