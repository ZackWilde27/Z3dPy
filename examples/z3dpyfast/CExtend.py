import z3dpy as zp
import pygame
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

print("")
print("Controls: ")
print("T to switch between Python and C++ Rastering")
print("")

currentTime = time.time()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

zp.CamSetTargetDir(myCamera, [0, 0, 1])
    
zp.SetInternalCam(myCamera)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
sus = zp.Thing([zp.LoadMesh("z3dpy/mesh/susanne.obj", 0, 0, 0)], 0, 0, 3)

zp.CAddThing(sus)

isC = False

cooldown = 0

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill("black")

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_t] and cooldown < 0:
        isC = not isC
        if isC:
            print("C++")
        else:
            print("Python")
        cooldown = 15

    cooldown -= 1

    if keys[pygame.K_UP]:
        zp.LightAddPos(myLight, [0, 0, 1])
    if keys[pygame.K_DOWN]:
        zp.LightAddPos(myLight, [0, 0, -1])
    if keys[pygame.K_LEFT]:
        zp.LightAddPos(myLight, [-1, 0, 0])
    if keys[pygame.K_RIGHT]:
        zp.LightAddPos(myLight, [1, 0, 0])

    if isC:
        
        for tri in zp.CRaster():
            nrm = zp.TriGetNormal(tri)
            shade = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriF(tri, shade, screen, pygame)
        
    else:
        for tri in zp.Raster():
            
            nrm = zp.TriGetNormal(tri)
            shade = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriF(tri, shade, screen, pygame)
        
    

    pygame.display.flip()

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(int(1 / (time.time() - currentTime))) + " FPS")
    currentTime = time.time()
