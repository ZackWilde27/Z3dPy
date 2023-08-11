import z3dpy as zp
import pygame

print("")
print("Controls:")
print("W and S to move ray-shooter up and down")
print("A and D to rotate ray-shooter")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Set the render size
zp.screenSize = (1280, 720)

# Cam(vPos)
myCamera = zp.Cam([0, 0, -4])

# Setting FOV
# zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)


# z3dpy.LoadMesh(filename, *vPos, *VScale)
# z3dpy.Thing(meshList, vPos)
player = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0])], [-5, 0, 3])

zp.ThingSetupPhysics(player)

cube = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0])], [0, 0, 6])

zp.AddThing(player)

zp.AddThing(cube)

zp.CamSetPos(myCamera, zp.VectorSub(zp.ThingGetPos(player), [0, 8, 0]))

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.ThingAddPos(player, [0, 0, -0.25])
    if keys[pygame.K_s]:
        zp.ThingAddPos(player, [0, 0, 0.25])

    if keys[pygame.K_d]:
        zp.ThingAddRot(player, [0, -1, 0])
    if keys[pygame.K_a]:
        zp.ThingAddRot(player, [0, 1, 0])
        

    rayStart = zp.ThingGetPos(player)

    rayDir = zp.RotTo(zp.ThingGetRot(player), [1, 0, 0])
    
    rayEnd = zp.VectorAdd(rayStart, zp.VectorMulF(rayDir, 5))
    
    theRay = zp.Ray(rayStart, rayEnd)

    hit = zp.RayIntersectThingComplex(theRay, cube)

    if(hit[0]):
        pygame.display.set_caption("Yep")
    else:
        pygame.display.set_caption("Nope")

    # Append to the global list for drawing.
    zp.rays.append(theRay)

    # New CamChase() will make the camera "chase" a location rather than being set.
    zp.CamChase(myCamera, zp.VectorSub(zp.ThingGetPos(player), [0, 8, 0]), 1)
    
    zp.CamSetTargetDir(myCamera, [0, 1, 0])
    zp.CamSetUpVector(myCamera, [0, 0, 1])

    zp.SetInternalCam(myCamera)

    zp.dots = []

    screen.fill("black")
        
    # Render 3D
    for tri in zp.DebugRaster():
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [255, 0, 0], screen, pygame)
        else:
            nrm = zp.TriGetNormal(tri)
            col = (nrm[2] + -nrm[1]) * 0.5
            zp.PgDrawTriS(tri, col, screen, pygame)

    zp.rays = []

    pygame.display.flip()
