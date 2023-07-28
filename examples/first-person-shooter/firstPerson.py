import pygame
import z3dpy as zp

print("")
print("Controls:")
print("WASD to move")
print("Mouse to aim")

# Pygame stuff
pygame.init()
screen = zp.PgScreen(1280, 720, "#317FC4", pygame)
clock = pygame.time.Clock()

# Our camera to view from
FPCamera = zp.Cam(0, -10, 0)

# Changing FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.733063872892536, 1.303224560042964)

# Importing gun as two pieces to colour separately
gunMetal = zp.LoadMesh("mesh/gunMetal.obj")
gunWood = zp.LoadMesh("mesh/gunWood.obj")

zp.MeshSetColour(gunMetal, [128, 144, 171])
zp.MeshSetColour(gunWood, [214, 138, 102])

# Combine them into one Thing
Gun = zp.Thing([gunMetal, gunWood], 0, 0, 0)

world = zp.Thing([zp.LoadMesh("mesh/world4.obj", [0, 0, 0])], 0, 0, 0)

hideout = zp.Thing([zp.LoadMesh("mesh/world4_2.obj", [0, 0, 0])], 0, 0, 0)

world2 = zp.Thing([zp.LoadMesh("mesh/tourus.obj", [0, 0, 0])], -40, 0, -25)

name = zp.Thing([zp.LoadMesh("z3dpy/mesh/z3dpy.obj", [30, -5, -15], [5, 5, 5])], 0, 0, 0)

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
        zp.CamAddPos(FPCamera, zp.VectorRotateY([0, 0, 1], zp.CamGetYaw(FPCamera)))
    if keys[pygame.K_s]:
        zp.CamSubPos(FPCamera, zp.VectorRotateY([0, 0, 1], zp.CamGetYaw(FPCamera)))

    if keys[pygame.K_a]:
        zp.CamAddPos(FPCamera, zp.CamGetRightVector(FPCamera))
    if keys[pygame.K_d]:
        zp.CamSubPos(FPCamera, zp.CamGetRightVector(FPCamera))

    if mouseTrue:
        check = pygame.mouse.get_rel()
        zp.CamSetYaw(FPCamera, zp.CamGetYaw(FPCamera) + -check[0] * 0.5)
        newPitch = zp.CamGetPitch(FPCamera) + -check[1] * 0.5
        newPitch = min(newPitch, 90)
        zp.CamSetPitch(FPCamera, max(newPitch, -90))
        newDrag = int(weaponDrag + check[0] * 0.2)
        newDrag = max(newDrag, -wpnDrgMax)
        weaponDrag = min(newDrag, wpnDrgMax)
        
        pygame.mouse.set_pos([640, 360])

    # Gravity
    if zp.CamGetPos(FPCamera)[1] < -5:
        zp.CamAddPos(FPCamera, [0, 0.1, 0])
    else:
        zp.CamSetPosY(FPCamera, -5)

    # Weapon Drag
    if weaponDrag != 0:
        weaponDrag -= zp.sign(weaponDrag)
    
    zp.CamSetTargetFP(FPCamera)

    # Update Gun to camera
    zp.ThingSetPos(Gun, zp.CamGetPos(FPCamera))

    zp.ThingSetRoll(Gun, zp.CamGetYaw(FPCamera) - 90 + weaponDrag)

    # Setting Internal Camera
    zp.SetInternalCam(FPCamera)

    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.PgDrawTriS(tri, (normal[1] + normal[2]) / 2, screen, pygame)
        
    pygame.display.flip()

    # Rotate Torus
    zp.ThingAddRot(world2, [0, 3, 0])

    zp.ThingAddRot(name, [5, 0, 0])
    
    
