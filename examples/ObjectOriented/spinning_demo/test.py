import z3dpyOOP as z3dpy
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myCamera = z3dpy.Camera(0, 0, 0, 1280, 720)

myCamera.SetFOV(75)

myList = []

zack = z3dpy.Thing([z3dpy.LoadMesh("engine/mesh/zack.obj", 0, 0, 0)], 0, 0, 5)


stuckInLoop = True
myList.append(zack)

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True 
            
    clock.tick(30)
    
    screen.fill("black")

    for tri in z3dpy.RasterThings(myList, myCamera):
            # Draw the projected triangle to the screen, with it's normal value as it's colour
            # Normal Y and Z are flipped
           
            match tri.id:
                case 0:
                   z3dpy.DrawTriangleRGBF(tri, screen, z3dpy.VectorMul(tri.normal, z3dpy.Vector(1, -1, -1)), pygame)
                case 1:
                    normal = tri.normal
                    z3dpy.DrawTriangleF(tri, screen, (-normal.y + -normal.z) / 2, pygame)
                case 2:
                    z3dpy.DrawTriangleOutl(tri, screen, z3dpy.Vector(1, 1, 1), pygame)


    pygame.display.flip()

    zack.rot = z3dpy.VectorAdd(zack.rot, z3dpy.Vector(4, 3, 2))
