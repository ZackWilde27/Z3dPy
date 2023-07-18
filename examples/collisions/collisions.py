import z3dpy as zp
import pygame

# Variables
isCube = True
speed = 0.25
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

# z3dpy.Camera(x, y, z)
myCamera = zp.Cam(0, -2, -4)

# z3dpy.LoadMesh(filename, x, y, z)
smallCube = zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, 0.1, 0.1, 0.1)

# z3dpy.Thing(meshList, x, y, z)
char = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, 0.5, 0.5, 0.5)], 0, 1, 3)
zp.ThingSetupHitbox(char, 2, 0, 0.5, 0.5)
zp.ThingSetupPhysics(char)

bar = zp.Thing([smallCube], 0.5, 0, 3)
zp.ThingSetupHitbox(bar, 2, 0, 2, 0.5)

plane = zp.Thing([zp.LoadMesh("z3dpy/mesh/plane.obj")], 0, 2, 0)

zp.AddThings([char, bar, plane])

myLight = zp.Light_Sun((0, 1, 1), 1, 0)
zp.lights.append(myLight)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    delta = zp.GetDelta()

    # Input
    keys = pygame.key.get_pressed()

    speed = 11 * delta

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(char, speed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(char, -speed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(char, -speed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(char, speed)

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

    for tri in zp.DebugRaster():
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        else:
            zp.PgDrawTriFL(tri, screen, pygame)
        
    pygame.display.flip()
