import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myCamera = zp.Camera(0, 0, 0, 1280, 720)

zp.CameraSetFOV(myCamera, 75)

myList = []

zack = zp.Thing([zp.LoadMesh("engine/mesh/zack.obj", 0, 0, 0)], 0, 0, 4)

counter = 0

myLight = zp.PointLight(0, 0, 0, 1, 1500)


zp.Lights.append(zp.PointLight(0, 0, 0, 1, 1500))

stuckInLoop = True
myList.append(zack)

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True 
            
    clock.tick(60)
    
    screen.fill("black")

    for tri in zp.RasterThings(myList, myCamera):
            # Draw the projected triangle to the screen, with it's normal value as it's colour
            # Normal Y and Z are flipped
            zp.DrawTriangleRGBF(tri, screen, zp.VectorMul(zp.TriangleGetNormal(tri), [1, -1, -1]), pygame)


    pygame.display.flip()

    zp.ThingAddRot(zack, 4, 3, 2)
