import z3dpy as zp
import pygame
import time

pygame.init()
# ps1 resolution to go along with the texture mapping
fScreen = pygame.Surface((320, 240))
screen = zp.PgScreen(640, 480, "black", pygame)
clock = pygame.time.Clock()
fScreenArray = pygame.PixelArray(fScreen)
screenArray = pygame.PixelArray(screen)

currentTime = time.time()

#zp.FindHowVars(75, 3/4)
zp.SetHowVars(0.9774183786133211, 1.303224644941822)

print("")
print("Controls:")
print("WASD to move plane around")
print("Left and Right arrows to rotate the plane")
print("F to switch between full and ps1 resolution.")

# z3dpy.Camera(x, y, z, scrW, scrH)
ps1Camera = zp.Cam(0, 0, -4)

nrmCamera = zp.Cam(0, 0, -4)

nrm = True

turnSpeed = 4

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
plane = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], 0, 0, 3)

zp.ThingSetRot(plane, [90, 0, 0])

zp.AddThing(plane)


myText = zp.PgLoadTexture("z3dpy/textures/test.png", pygame)

cooldown = 0

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LSHIFT]:
        speed = 0.05
    else:
        speed = 0.25

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(plane, speed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(plane, -speed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(plane, -speed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(plane, speed)

    if keys[pygame.K_LEFT]:
        zp.ThingAddRot(plane, [0, -turnSpeed, 0])
    if keys[pygame.K_RIGHT]:
        zp.ThingAddRot(plane, [0, turnSpeed, 0])

    if keys[pygame.K_f] and cooldown < 0:
        nrm = not nrm
        if nrm:
            zp.screenSize = (640, 480)
        else:
            zp.screenSize = (320, 240)
        cooldown = 4

    cooldown -= 1
        
        
    if nrm:
        screen.fill("black")
        zp.SetInternalCam(nrmCamera)
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, screenArray, myText)
        
    else:
        fScreen.fill("black")
        zp.SetInternalCam(ps1Camera)
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, fScreenArray, myText)

        pygame.transform.scale_by(fScreen, 2, screen)
        
        
    pygame.display.flip()

    # FPS Calc
    # Setting the title is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
