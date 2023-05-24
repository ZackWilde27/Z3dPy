import z3dpy as zp
import pygame
import time
import math

print("")
print("Controls:")
print("Arrow Keys to move mesh around")
print("WASD to move camera")

# PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Used for FPS
curr = time.time()

# Create the Camera
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# Setting the constants for an FOV of 75
#zp.FindHowVars(75)
zp.SetHowVars(2.3168437616632214, 1.303224615935562)

# Susanne Mesh
sus = zp.Thing([zp.NewSusanne()], 0, 0, 4)

# Create a PointLight and append it to the z3dpy.lights list
myLight = zp.Light_Point(0, 0, 2, 1, 25)

zp.lights.append(myLight)

# Raster Loop
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
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
        zp.ThingAddPosZ(sus, -0.1)
    if keys[pygame.K_DOWN]:
        zp.ThingAddPosZ(sus, 0.1)
    if keys[pygame.K_LEFT]:
        zp.ThingAddPosX(sus, -0.1)
    if keys[pygame.K_RIGHT]:
        zp.ThingAddPosX(sus, 0.1)
        
    # The camera always looks forward
    zp.CameraSetTargetVector(myCamera, [0, 0, 1])

    # Each time the camera moves, the view matrix has to be recalculated
    zp.SetInternalCamera(myCamera)

    # Using DebugRasterThings() to draw the light as well
    for tri in zp.DebugRasterThings([sus]):
        
        # Debug things will have an ID of -1
        if zp.TriangleGetId(tri) == -1:
            zp.PgDrawTriangleOutl(tri, [1, 0, 0], screen, pygame)
        else:
            # Plug FlatLighting into DrawTriangleS
            zp.PgDrawTriangleS(tri, zp.FlatLighting(tri), screen, pygame)
            
    pygame.display.flip()

    zp.ThingAddRot(sus, [4, 3, 2])

    # FPS calculation
    pygame.display.set_caption(str(int(1 / (time.time() - curr))) + " FPS")
    curr = time.time()

    
