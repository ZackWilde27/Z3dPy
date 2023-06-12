#-zw

import pygame
import z3dpy as zp
import time

print("")
print("Controls:")
print("WASD to move")
print("Mouse to aim")

# Pygame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Our camera to view from
FPCamera = zp.Camera(0, -10, 0, 1280, 720)

# Setting up How-Does-That-Even-Work Projection
#zp.FindHowVars(75)
zp.SetHowVars(0.733063872892536, 1.303224560042964)

gunMetal = zp.LoadMesh("mesh/gunMetal.obj", 0, 0, 0)
gunWood = zp.LoadMesh("mesh/gunWood.obj", 0, 0, 0)

zp.MeshSetColour(gunMetal, [128, 144, 171])
zp.MeshSetColour(gunWood, [214, 138, 102])

Gun = zp.Thing([gunMetal, gunWood], 0, 0, 0)

world = zp.Thing([zp.LoadMesh("mesh/world4.obj", 0, 0, 0)], 0, 0, 0)

hideout = zp.Thing([zp.LoadMesh("mesh/world4_2.obj", 0, 0, 0)], 0, 0, 0)

world2 = zp.Thing([zp.LoadMesh("mesh/tourus.obj", 0, 0, 0)], -40, 0, -25)

name = zp.Thing([zp.LoadMesh("z3dpy/mesh/z3dpy.obj", 30, -5, -15, 5, 5, 5)], 0, 0, 0)

zp.ThingSetRot(name, [0, -90, 0])

zp.gravityDir = [0, 15, 0]

zp.AddThings([Gun, hideout, name, world2])
zp.AddThing(world, 1)

stuckInLoop = True
gunPos = [0, 0, 0]

weaponDrag = 0
wpnDrgMax = 8

mouseTrue = True


while stuckInLoop:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            stuckInLoop = True
            
        if event.type == pygame.ACTIVEEVENT:
            pygame.mouse.set_pos([640, 360])
            mouseTrue = not mouseTrue
            pygame.mouse.set_visible(not mouseTrue)
            
    clock.tick(30)
    # Filling with a sky colour
    screen.fill("#317FC4")
    
    #
    # Input
    #
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.CameraAddPos(FPCamera, zp.VectorRotateY([0, 0, 1], zp.CameraGetYaw(FPCamera)))
    if keys[pygame.K_s]:
        zp.CameraSubPos(FPCamera, zp.VectorRotateY([0, 0, 1], zp.CameraGetYaw(FPCamera)))

    if keys[pygame.K_a]:
        zp.CameraAddPos(FPCamera, zp.CameraGetRightVector(FPCamera))
    if keys[pygame.K_d]:
        zp.CameraSubPos(FPCamera, zp.CameraGetRightVector(FPCamera))

    if keys[pygame.K_r]:
        ResetPhysicsDemo()

    if mouseTrue:
        check = pygame.mouse.get_rel()
        zp.CameraSetYaw(FPCamera, zp.CameraGetYaw(FPCamera) + -check[0] * 0.5)
        newPitch = zp.CameraGetPitch(FPCamera) + -check[1] * 0.5
        newPitch = min(newPitch, 90)
        zp.CameraSetPitch(FPCamera, max(newPitch, -90))
        newDrag = int(weaponDrag + check[0] * 0.2)
        newDrag = max(newDrag, -wpnDrgMax)
        weaponDrag = min(newDrag, wpnDrgMax)
        
        pygame.mouse.set_pos([640, 360])

    # Gravity
    if zp.CameraGetPos(FPCamera)[1] < -5:
        zp.CameraAddPos(FPCamera, [0, 0.1, 0])
    else:
        zp.CameraSetPosY(FPCamera, -5)

    # Weapon Drag
    if weaponDrag != 0:
        if weaponDrag < 0:
            weaponDrag += 1
        else:
            weaponDrag -= 1
    
    zp.CameraSetTargetFP(FPCamera)

    # Update Gun to camera
    zp.ThingSetPos(Gun, zp.CameraGetPos(FPCamera))

    zp.ThingSetRoll(Gun, zp.CameraGetYaw(FPCamera) - 90 + weaponDrag)

    # Setting Internal Camera
    zp.SetInternalCamera(FPCamera)

    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriS(tri, (normal[1] + normal[2]) / 2, screen, pygame)
        
    pygame.display.flip()

    # Rotate Torus
    zp.ThingAddRot(world2, [0, 3, 0])

    zp.ThingAddRot(name, [5, 0, 0])
    
    
