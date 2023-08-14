import z3dpy as zp
import pygame

# Variables
speed = 11
zp.screenSize = (1280, 720)
zp.gravity = [0, 4, 0]
zp.worldColour = (0.3, 0.3, 0.3)
delta = 0

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


# Setting FOV
# FindHowVars(fov, *aspectRatio)
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

print("")
print("Controls:")
print("WASD to move character")
print("Space to jump")
print("Up and Down arrow to move platform")

# Cam(vPos)
myCamera = zp.Cam([0, 0, -2])

# LoadMesh(filename, *vPos, *vScale)
smallCube = zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [2.0, 0.5, 2.0])
cubeMesh = zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [0.5, 0.5, 0.5])
planeMesh = zp.LoadMesh("z3dpy/mesh/plane.obj", VScale=[5, 5, 5])
treeMeshes = zp.LoadMesh("z3dpy/mesh/thattree.obj")

zp.MeshSetColour(planeMesh, [0, 100, 0])
zp.MeshSetColour(smallCube, [255, 0, 0])

# Thing(meshList, vPos)
char = zp.Thing([cubeMesh], [0, 1, 3])

# Giving the character a hitbox and physics body
# ThingSetupHitbox(thing, *type, *id, *radius, *height)
zp.ThingSetupHitbox(char, 2, 0, 0.5, 0.5)
# Type determines the shape of the hitbox: 0 is sphere, 2 is cube
# Only things with the same id will collide
# Radius and height determine the size of hitbox
zp.ThingSetupPhysics(char)

bar = zp.Thing([smallCube], [0.5, 0, 3])
zp.ThingSetupHitbox(bar, 2, 0, 2, 0.5)


plane = zp.Thing([planeMesh], [0, 2, 0])

thatTree = zp.Thing(treeMeshes, [0, 0, 8])

zp.AddThings([char, bar, thatTree])

zp.AddThing(plane, 1)

zp.AddDupe(thatTree, [6, 0, 10], [0, 45, 0])

zp.AddDupe(thatTree, [-6, 0, 12], [0, 45, 0])


# Light_Sun(vAngle, FStrength, unused, *vColour)
myLight = zp.Light_Sun((-60, 0, 0), 1, 0)
zp.lights.append(myLight)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    delta = zp.GetDelta()

    # Input
    keys = pygame.key.get_pressed()

    trueSpeed = speed * delta

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(char, trueSpeed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(char, -trueSpeed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(char, -trueSpeed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(char, trueSpeed)

    if keys[pygame.K_UP]:
        zp.ThingAddPos(bar, [0, -8 * delta, 0])
    if keys[pygame.K_DOWN]:
        zp.ThingAddPos(bar, [0, 8 * delta, 0])
        
    if keys[pygame.K_SPACE] and zp.ThingGetVelocityY(char) >= -0.3:
        zp.ThingSetVelocity(char, [0, -13, 0])

    zp.HandlePhysicsFloor([char], 2)

    zp.PhysicsCollisions([char, bar])

    camLoc = zp.VectorSub(zp.ThingGetPos(char), [0, 2, 5])
    
    # Camera will ease towards the desired location
    zp.CamChase(myCamera, camLoc, 5)
    
    zp.CamSetTargetLoc(myCamera, zp.ThingGetPos(char))
    zp.SetInternalCam(myCamera) 

    screen.fill("black")

    for tri in zp.Raster():
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [255, 0, 0], screen, pygame)
        else:
            zp.PgDrawTriFL(tri, screen, pygame)
        
    pygame.display.flip()