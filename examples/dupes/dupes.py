import pygame
import z3dpy as zp
import random as rand

# Initialize PyGame

# PgInit(width, height, bgCol, pygame)
# PgInit replaces pygame.init(), sets the global screen size, and returns the screen,
# filled with bgCol
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

# Cam(x, y, z)
myCamera = zp.Cam(7.5, 7.5, -10)

zp.CamSetTargetDir(myCamera, [0, 0, 1])

# LoadMesh(filename)
myMesh = zp.LoadMesh("z3dpy/mesh/cube.obj")

# Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 0)

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

amount = 0

mx = 150

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

    if amount < mx:

        # Add another dupe, with a random location and rotation
        zp.AddDupe(myThing, [rand.random() * 15, rand.random() * 15, rand.random() * 15], [rand.random() * 270, rand.random() * 270, rand.random() * 270])
        # It's going to end up drawing more triangles, but it only needs to reference the one mesh.

        amount += 1

        
    
