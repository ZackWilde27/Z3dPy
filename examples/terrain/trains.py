import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, -4, 1280, 720)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
cube = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0)], 0, 0, 3)

zp.ThingSetupPhysics(cube)

zp.AddThing(cube)



# Creating a 15x15 train
myTrain = zp.Train(15, 15)

# Setting height at certain points
myTrain[10][7] = -15

myTrain[3][10] = 15

# Baking to create smooth hills
zp.BakeTrain(myTrain, 2, 1.7)



while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    #clock.tick(60)
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        zp.ThingAddPos(cube, [0, 0, 0.25])
    if keys[pygame.K_DOWN]:
        zp.ThingAddPos(cube, [0, 0, -0.25])
    if keys[pygame.K_LEFT]:
        zp.ThingAddPos(cube, [-0.25, 0, 0])
    if keys[pygame.K_RIGHT]:
        zp.ThingAddPos(cube, [0.25, 0, 0])

    zp.CameraSetPos(myCamera, zp.VectorSub(zp.ThingGetPos(cube), [0, 2, 5]))

    zp.CameraSetTargetLocation(myCamera, zp.ThingGetPos(cube))

    zp.SetInternalCamera(myCamera)

    # Make sure to use HandlePhysicsTrain()
    zp.HandlePhysicsTrain([cube], myTrain)

    # DebugRaster can draw Trains.
    for tri in zp.DebugRaster(myTrain):
            nrm = zp.TriGetNormal(tri)
            col = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriS(tri, col, screen, pygame)

    pygame.display.flip()
