import z3dpy as zp
import pygame

pygame.init()
screen = zp.PgScreen(1280, 720, "black", pygame)
clock = pygame.time.Clock()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

print("")
print("Controls:")
print("WASD to move character")
print("Space to jump")
print("Up and Down arrow to move platform")

# z3dpy.Camera(x, y, z)
myCamera = zp.Cam(0, -2, -4)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
char = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, 0.5, 0.5, 0.5)], 0, 1, 3)

bar = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", 0, 0, 0, 0.1, 0.1, 0.1)], 0.5, 0, 3)

plane = zp.Thing([zp.LoadMesh("z3dpy/mesh/plane.obj")], 0, 2, 0)

zp.ThingSetupHitbox(char, 2, 0, 0.5, 0.5)

zp.ThingSetupHitbox(bar, 2, 0, 2, 0.5)

zp.ThingSetupPhysics(char)

zp.AddThing(char)

zp.AddThing(bar)

zp.AddThing(plane)

zp.gravity = [0, 4, 0]

speed = 0.25

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(30)

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.ThingAddPosZ(char, speed)
    if keys[pygame.K_s]:
        zp.ThingAddPosZ(char, -speed)
    if keys[pygame.K_a]:
        zp.ThingAddPosX(char, -speed)
    if keys[pygame.K_d]:
        zp.ThingAddPosX(char, speed)

    if keys[pygame.K_UP]:
        zp.ThingAddPos(bar, [0, -0.25, 0])
    if keys[pygame.K_DOWN]:
        zp.ThingAddPos(bar, [0, 0.25, 0])
        
    if keys[pygame.K_SPACE]:
        zp.ThingSetVelocity(char, [0, -2, 0])

    zp.HandlePhysicsFloor([char], 2)

    zp.PhysicsCollisions([char, bar])

    camLoc = zp.VectorSub(zp.ThingGetPos(char), [0, 2, 5])
    
    # Camera will ease towards the desired location
    zp.CamChase(myCamera, camLoc)

    zp.CamSetTargetLoc(myCamera, zp.ThingGetPos(char))

    zp.SetInternalCam(myCamera) 

    screen.fill("black")

    for tri in zp.DebugRaster():
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        else:
            nrm = zp.TriGetNormal(tri)
            col = (nrm[2] + nrm[1]) * 0.5
            zp.PgDrawTriF(tri, col, screen, pygame)
        
    pygame.display.flip()
