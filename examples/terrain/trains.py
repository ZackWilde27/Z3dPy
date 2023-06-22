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

zp.ThingSetupHitbox(cube, 2, 0, 1, 1)

zp.AddThing(cube)

# Creating a 15x15 train
myTrain = zp.Train(15, 15)

# Setting height at certain points
myTrain[10][7] = -15

myTrain[3][10] = 15

# Baking to create smooth hills
zp.BakeTrain(myTrain, 5, 1.7)

print("")
print("Controls:")
print("WASD to move around")

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    #clock.tick(60)
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.ThingAddPos(cube, [0, 0, 0.25])
    if keys[pygame.K_s]:
        zp.ThingAddPos(cube, [0, 0, -0.25])
    if keys[pygame.K_a]:
        zp.ThingAddPos(cube, [-0.25, 0, 0])
    if keys[pygame.K_d]:
        zp.ThingAddPos(cube, [0.25, 0, 0])

    # Make sure to use HandlePhysicsTrain()
    zp.HandlePhysicsTrain([cube], myTrain)

    zp.CamChase(myCamera, zp.VectorSub(zp.ThingGetPos(cube), [0, 2, 7]), 0.05)

    zp.CamSetTargetLocation(myCamera, zp.ThingGetPos(cube))

    zp.SetInternalCam(myCamera)

    # DebugRaster can draw Trains.
    for tri in zp.DebugRaster(myTrain):
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        else:
            nrm = zp.TriGetNormal(tri)
            col = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriS(tri, col, screen, pygame)

    pygame.display.flip()
