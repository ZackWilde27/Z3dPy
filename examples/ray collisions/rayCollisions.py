import z3dpy as zp
import pygame
import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

currentTime = time.time()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, -4, 1280, 720)



# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
player = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0)], -5, 0, 3)

zp.ThingSetupPhysics(player)

cube = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0)], 0, 0, 6)

zp.AddThing(player)

zp.AddThing(cube)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    screen.fill("black")

    zp.CameraSetPos(myCamera, zp.VectorSub(zp.ThingGetPos(player), [0, 8, 0]))
    zp.CameraSetTargetVector(myCamera, [0, 1, 0])
    zp.CameraSetUpVector(myCamera, [0, 0, 1])

    zp.SetInternalCamera(myCamera)

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.ThingAddPos(player, [0, 0, -0.25])
    if keys[pygame.K_s]:
        zp.ThingAddPos(player, [0, 0, 0.25])
        

    rayStart = zp.ThingGetPos(player)
    
    rayEnd = zp.VectorAdd(zp.ThingGetPos(player), [15, 0, 0])
    
    theRay = zp.Ray(rayStart, rayEnd)

    zp.rays.append(theRay)

    hit = zp.RayIntersectThingComplex(theRay, cube)

    if(hit[0]):
        pygame.display.set_caption("Yep")
    else:
        pygame.display.set_caption("Nope")
        
    # Render 3D
    for tri in zp.DebugRaster():
            nrm = zp.TriGetNormal(tri)
            col = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriS(tri, col, screen, pygame)

    zp.rays = []

    pygame.display.flip()
