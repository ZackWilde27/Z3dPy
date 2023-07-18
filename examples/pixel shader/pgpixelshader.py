import z3dpy as zp
import pygame
import time

# Variables
currentTime = time.time()
cooldown = 0
nrm = True
turnSpeed = 4

# Initialize PyGame
pygame.init()
screen = zp.PgScreen(640, 480, "black", pygame)
clock = pygame.time.Clock()

# Setting z3dpy screenSize
zp.screenSize = (640, 480)

# Pixel shader needs a pixel array
screenArray = pygame.PixelArray(screen)

# PS1 Resolution screen
fScreen = pygame.Surface((320, 240))
fScreenArray = pygame.PixelArray(fScreen)

# Setting FOV
# aspectRatio is height over width, so 4:3 becomes 3/4
#zp.FindHowVars(75, 3/4)
zp.SetHowVars(0.9774183786133211, 1.303224644941822)

print("")
print("Controls:")
print("WASD to move plane around")
print("Left and Right arrows to rotate the plane")
print("F to switch between full and ps1 resolution.")

# Cam(x, y, z)
ps1Camera = zp.Cam(0, 0, -4)
nrmCamera = zp.Cam(0, 0, -4)

# LoadMesh(filename, *x, *y, *z, *sclX, *sclY, *sclZ)
# Thing(meshList, x, y, z)
plane = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], 0, 0, 3)
zp.ThingSetRot(plane, [90, 0, 0])
zp.AddThing(plane)


myTexture = zp.PgLoadTexture("z3dpy/textures/test.png", pygame)

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
        zp.screenSize = (640, 480) if nrm else (320, 240)
        cooldown = 10

    cooldown -= 1
        
        
    if nrm:
        zp.SetInternalCam(nrmCamera)
        
        screen.fill("black")
        
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, screenArray, myTexture)
        
    else:
        zp.SetInternalCam(ps1Camera)
        
        fScreen.fill("black")
       
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, fScreenArray, myTexture)

        pygame.transform.scale_by(fScreen, 2, screen)
        
        
    pygame.display.flip()

    # FPS Calc
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
