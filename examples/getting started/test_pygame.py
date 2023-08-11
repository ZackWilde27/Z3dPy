# Legend:
# - Parameters marked with a * are optional
# - Most parameters have a letter denoting type - capitals mean normalized.

import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Set the render size to match the output screen
zp.screenSize = (1280, 720)

# Create a camera to render from
# Cam(vPos)
myCamera = zp.Cam([0, 0, 0])

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

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
        zp.PgDrawTriF(tri, -normal[2], screen, pygame)

    # Update the screen
    pygame.display.flip()

    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 2, 2])
