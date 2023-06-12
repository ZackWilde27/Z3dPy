import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# z3dpy.LoadMesh(filename)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

# z3dpy.Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCamera(myCamera)

# Raster Loop
while True:
    
    # More PyGame stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    screen.fill("black")

    # Render 3D
    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriF(tri, normal[2], screen, pygame)

    # Update the screen afterwards
    pygame.display.flip()

    # z3dpy.ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 1, 3])
