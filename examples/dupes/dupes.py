import pygame
import z3dpy as zp
import random as rand

# Initialize PyGame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

# Cam(vPos)
myCamera = zp.Cam([7.5, 7.5, -10])

myCamera.SetTargetDir([0, 0, 1])

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

myMesh.shader = zp.SHADER_SIMPLE

# Thing(meshList, vPos)
myThing = zp.Thing([myMesh], [0, 0, 0])

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

amount = 0

mx = 25

# Raster Loop
while True:
    
    # More PyGame stuff to prevent freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Clear the screen
    screen.fill("black")

    # Render 3D
    for tri in zp.Render():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(tri, False))

    # Update the screen
    pygame.display.flip()

    if amount >= mx:
        zp.layers = ([], [], [myThing], [])
        amount = 0
    else:

        # Add another dupe, with a random location and rotation
        zp.AddDupe(myThing, [rand.random() * 15, rand.random() * 15, rand.random() * 15], [rand.random() * 270, rand.random() * 270, rand.random() * 270])
        # It's going to end up drawing more triangles anyway, so it's not much of a performance fix, but it only needs to reference the one mesh.

        amount += 1

        
    
