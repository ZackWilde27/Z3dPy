#-zw

import pygame
import z3dpy as zp
import time

# Pygame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Our camera to view from
FPCamera = zp.Camera(0, -10, 0, 1280, 720)

# Setting up How-Does-That-Even-Work Projection
zp.SetHowVars(2.118671766119488, 1.191752868442212)

myList = []


Gun = zp.Thing([zp.LoadMesh("mesh/gunMetal.obj", 0, 0, 0), zp.LoadMesh("mesh/gunWood.obj", 0, 0, 0)], 0, 0, 0)
zp.MeshSetColour(Gun[0][0], [128, 144, 171])
zp.MeshSetColour(Gun[0][1], [214, 138, 102])
Gun[0][0][4] = 5

world = zp.Thing([zp.LoadMesh("mesh/world4.obj", 0, 0, 0)], 0, 0, 0)

hideout = zp.Thing([zp.LoadMesh("mesh/world4_2.obj", 0, 0, 0)], 0, 0, 0)

world2 = zp.Thing([zp.LoadMesh("mesh/tourus.obj", 0, 0, 0)], -40, 0, -25)

arrow = zp.Thing([zp.LoadMesh("engine/mesh/zack.obj", 0, 0, 0)], 0, 0, 0)

#
# Physics Objects
#

physics1 = zp.Thing([zp.LoadMesh("engine/mesh/cube.obj", 0, 0, 0)], 28, 0, -15)

physics2 = zp.Thing([zp.LoadMesh("engine/mesh/cube.obj", 0, 0, 0)], 32, 0, -10)

physics3 = zp.Thing([zp.LoadMesh("engine/mesh/cube.obj", 0, 0, 0)], 28, 0, -15)

physics4 = zp.Thing([zp.LoadMesh("engine/mesh/cube.obj", 0, 0, 0)], 32, 0, -10)



physics1[6] = zp.PhysicsBody()

physics2[6] = zp.PhysicsBody()

physics3[6] = zp.PhysicsBody()

physics4[6] = zp.PhysicsBody()



physics1[4] = zp.Hitbox(2, 0, 1, 1)

physics2[4] = zp.Hitbox(2, 0, 1, 1)

physics3[4] = zp.Hitbox(2, 0, 1, 1)

physics4[4] = zp.Hitbox(2, 0, 1, 1)

zp.ThingSetFriction(physics1, 0.1)
zp.ThingSetFriction(physics2, 0.1)
zp.ThingSetFriction(physics3, 0.1)
zp.ThingSetFriction(physics4, 0.1)

zp.ThingSetMass(physics1, 3)
zp.ThingSetMass(physics2, 3)

zp.ThingSetMass(physics3, 10)
zp.ThingSetMass(physics4, 10)

def ResetPhysicsDemo():
    zp.ThingSetPos(physics1, [29.5, 0, -15])
    zp.ThingSetPos(physics2, [30.5, 0, -10])
    zp.ThingSetVelocity(physics1, [0, 0, 5])
    zp.ThingSetVelocity(physics2, [0, 0, -5])

    zp.ThingSetPos(physics3, [29.5, 0, -35])
    zp.ThingSetPos(physics4, [30.5, 0, -30])
    zp.ThingSetVelocity(physics3, [0, 0, 5])
    zp.ThingSetVelocity(physics4, [0, 0, -5])

ResetPhysicsDemo()

zp.gravityDir = [0, 15, 0]


myList.append(Gun)

myList.append(physics1)

myList.append(physics2)

myList.append(physics3)

myList.append(physics4)

myList.append(world2)

myList.append(hideout)

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
        zp.CameraSetPitch(FPCamera, max(min(zp.CameraGetPitch(FPCamera) + -check[1] * 0.5, 160), -160))
        weaponDrag = min(max(int(weaponDrag + check[0] * 0.2), -wpnDrgMax), wpnDrgMax)
        
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

    # Handle Physics
    zp.HandlePhysics(myList, 0)

    zp.PhysicsCollisions(myList)

    # Setting Internal Camera
    zp.SetInternalCamera(FPCamera)
    

    for tri in zp.RasterThings([world]):
        normal = zp.TriangleGetNormal(tri)
        
        zp.PgDrawTriangleS(tri, (normal[1] + normal[2]) / 2, screen, pygame)

    for tri in zp.DebugRasterThings(myList):
        match zp.TriangleGetId(tri):
            case -1:
                zp.PgDrawTriangleOutl(tri, [1, 0, 0], screen, pygame)
            case _:
                normal = zp.TriangleGetNormal(tri)
                zp.PgDrawTriangleS(tri, (normal[1] + normal[2]) / 2, screen, pygame)
        
    pygame.display.flip()

    # Rotate Torus
    zp.ThingAddRot(world2, [0, 3, 0])
    
    