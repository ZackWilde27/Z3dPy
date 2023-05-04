import z3dpy
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myCamera = z3dpy.Camera(0, 0, 0, 1280, 720)

myList = []

myThing = z3dpy.Thing([z3dpy.LoadMesh("susanne.obj", 0, 0, 0)], 0, 0, 3)
stuckInLoop = True
myList.append(myThing)

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True 
            
    clock.tick(30)
    screen.fill("black")
    for tri in z3dpy.RasterThings(myList, myCamera):
            # Draw the projected triangle to the screen, with it's normal value as it's colour
            # Normal Y and Z are flipped
           z3dpy.DrawTriangleRGBF(tri, screen, z3dpy.VectorMul(z3dpy.TriangleGetNormal(tri), [1, -1, -1]), pygame)

    pygame.display.flip()

    myThing[2][0] += 5
    myThing[2][2] += 8
