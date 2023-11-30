import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

# Setting FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# Cam([x, y, z])
myCamera = zp.Cam([0, 0, -4])

# LoadMesh(filename, *vPos, *vScale)
# Thing(meshList, vPos)
cube = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj")], [0, 0, 3])

cube.meshes[0].material = zp.MATERIAL_DYNAMIC

cube.physics = zp.PhysicsBody()
cube.hitbox = zp.Hitbox(2, 0, 1, 1)

zp.AddThing(cube)

# Creating a 15x15 train
myTrain = zp.Train(16, 16)

# Setting height at certain points
myTrain[10][7] = -15

myTrain[3][10] = 15

# Baking to create smooth hills
# BakeTrain(train, *passes, *strength, *amplitude)
zp.BakeTrain(myTrain, 5, 1.7, 1.0)

zp.trainMesh.SetColour((50, 255, 50))

myLight = zp.Light(zp.LIGHT_SUN, [-45, 0, 0], 1.0, 5.0, (255, 255, 255))

zp.lights.append(myLight)
zp.trainMesh.material = zp.MATERIAL_DYNAMIC

print("")
print("Controls:")
print("WASD to move around")

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    screen.fill("black")

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        cube.position[2] += 0.25
    if keys[pygame.K_s]:
        cube.position[2] -= 0.25
    if keys[pygame.K_a]:
        cube.position[0] -= 0.25
    if keys[pygame.K_d]:
        cube.position[0] += 0.25

    # HandlePhysicsTrain(thingList, train)
    zp.HandlePhysicsTrain([cube], myTrain)

    # "Chase" the player rather than directly setting location
    myCamera.Chase(zp.VectorSub(cube.position, [0, 2, 7]), 5)

    myCamera.target = cube.position

    zp.SetInternalCam(myCamera)

    for tri in zp.Render():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(tri, False))

    #for tri in zp.DebugRender(myTrain):
        #zp.PgDrawTriOutl(tri, [255, 0, 0], screen, pygame)

    pygame.display.flip()
