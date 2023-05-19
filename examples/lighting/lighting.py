import z3dpy as zp
import pygame
import time
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

curr = time.time()

myCamera = zp.Camera(15, -2, -3, 1280, 720)

# Find the constants for an FOV of 75
zp.SetHowVars(2.3168437616632214, 1.303224615935562)

print("")
print("Controls:")
print("Arrow Keys to move light around")
print("WASD to move camera")

sus = zp.Thing([zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 0)], 13, -2, 4)

# Create a PointLight and append it to the z3dpy.lights list.
myLight = zp.PointLight(13, -2, 0, 1, 10)

zp.lights.append(myLight)


# Raster Loop
stuckInLoop = True

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True 
            
    clock.tick(60)
    
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.CameraAddPos(myCamera, zp.VectorMulF(zp.CameraGetTargetVector(myCamera), 0.1))
        zp.SetInternalCamera(myCamera)
    if keys[pygame.K_s]:
        zp.CameraSubPos(myCamera, zp.VectorMulF(zp.CameraGetTargetVector(myCamera), 0.1))
        zp.SetInternalCamera(myCamera)
    if keys[pygame.K_a]:
       zp.CameraAddPos(myCamera, zp.VectorMulF(zp.CameraGetRightVector(myCamera), 0.1))
       zp.SetInternalCamera(myCamera)
    if keys[pygame.K_d]:
        zp.CameraSubPos(myCamera, zp.VectorMulF(zp.CameraGetRightVector(myCamera), 0.1))
        

    if keys[pygame.K_UP]:
        myLight[0][2] += 0.1
    if keys[pygame.K_DOWN]:
        myLight[0][2] -= 0.1
    if keys[pygame.K_LEFT]:
        myLight[0][0] -= 0.1
    if keys[pygame.K_RIGHT]:
        myLight[0][0] += 0.1

    zp.CameraSetTargetVector(myCamera, [0, 0, 1])

    zp.SetInternalCamera(myCamera)
        
    for tri in zp.DebugRasterThings([sus]):
        if zp.TriangleGetId(tri) == -1:
            zp.PgDrawTriangleOutl(tri, [1, 0, 0], screen, pygame)
        else:
            # Plug FlatLighting into DrawTriangleRGB's colour
            zp.PgDrawTriangleRGB(tri, zp.FlatLighting(tri), screen, pygame)
            
    pygame.display.flip()
    

    zp.ThingAddRot(sus, [4, 3, 2])

    pygame.display.set_caption(str(int(1 / (time.time() - curr))) + " FPS")
    curr = time.time()

    
