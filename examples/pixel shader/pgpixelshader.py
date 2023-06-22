import z3dpy as zp
import pygame
import time

pygame.init()
# ps1 resolution to go along with the texture mapping
fScreen = pygame.Surface((320, 240))
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
fScreenArray = pygame.PixelArray(fScreen)
screenArray = pygame.PixelArray(screen)

currentTime = time.time()

zp.FindHowVars(75, 3/4)

#zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

print("")
print("F to switch between normal and ps1 resolution")

# z3dpy.Camera(x, y, z, scrW, scrH)
ps1Camera = zp.Cam(0, 0, -4, 320, 240)

nrmCamera = zp.Cam(0, 0, -4, 640, 480)

nrm = True

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
zack = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], 0, 0, 3)

zp.ThingSetRot(zack, [90, 0, 0])

zp.AddThing(zack)

myText = zp.PgLoadTexture("z3dpy/textures/test.png", pygame)

cooldown = 0

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(30)
    fScreen.fill("black")
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LSHIFT]:
        speed = 0.05
    else:
        speed = 0.25

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(zack, speed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(zack, -speed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(zack, -speed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(zack, speed)

    if keys[pygame.K_UP]:
        zp.CamAddPos(myCamera, [0, 0, speed])
    if keys[pygame.K_DOWN]:
        zp.CamAddPos(myCamera, [0, 0, -speed])
    if keys[pygame.K_LEFT]:
        zp.CamAddPos(myCamera, [-speed, 0, 0])
    if keys[pygame.K_RIGHT]:
        zp.CamAddPos(myCamera, [speed, 0, 0])

    if keys[pygame.K_f] and cooldown < 0:
        nrm = not nrm
        cooldown = 2

    cooldown -= 1
        
        
    if nrm:
        zp.SetInternalCam(nrmCamera)
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, screenArray, myText)
        
    else:
        zp.SetInternalCam(ps1Camera)
        for tri in zp.Raster(zp.triSortAverage, False):
            zp.PgPixelShader(tri, fScreenArray, myText)

        pygame.transform.scale_by(fScreen, 2, screen)
        
        
    pygame.display.flip()

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
