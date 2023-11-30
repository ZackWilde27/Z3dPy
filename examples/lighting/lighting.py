import pygame
import z3dpy as zp
import time

#zp.Fast()

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
array = pygame.PixelArray(screen)

zp.screenSize = (1280, 720)

currentTime = time.time()
static = False
coolDown = 0

# Camera(vPos)
myCamera = zp.Cam([0, 0, -3])

myCamera.SetTargetDir([0, 0, 1])
zp.SetInternalCam(myCamera)

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj")

myMesh.colour = (255, 255, 255)

myMesh.shader = zp.SHADER_DYNAMIC

# Thing(meshes, vPos)
sus = zp.Thing([myMesh], [0, 0, 0])

zp.AddThing(sus)

# Light(type, position, strength, radius, *colour)
redLight = zp.Light(zp.LIGHT_POINT, [2.25, 0, 2], 0.8, 4.0, (255, 0, 0))

blueLight = zp.Light(zp.LIGHT_POINT, [-2.25, 0, -2], 0.8, 4.0, (100, 100, 255))

# Append to global list
zp.lights.append(redLight)
zp.lights.append(blueLight)

zp.worldColour = (0.02, 0.00, 0.02)

# BakeLighting(thingList, bExpensive)
zp.BakeLighting([sus])

def LineDraw(x, y):
    col = zp.TriGetColour(tri)
    array[x, y] = (col[0], col[1], col[2])

fps = 30

print("")
print("L to switch between static and dynamic lighting")
print("F to enable z3dpyfast")

drawDebug = False

while True:

    delta = zp.GetDelta()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_l]:
        if coolDown < 0:
            coolDown = 10
            static = not static
            myMesh.shader = zp.SHADER_STATIC if static else zp.SHADER_DYNAMIC

    if keys[pygame.K_f]:
        if coolDown < 0:
            coolDown = 10
            zp.fast()

    if keys[pygame.K_d]:
        if coolDown < 0:
            coolDown = 10
            drawDebug = not drawDebug
    coolDown -= 1

    screen.fill("black")
    
    for tri in zp.Render():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])


    if drawDebug:
        for tri in zp.DebugRender():
            pygame.draw.polygon(screen, zp.TriGetColour(tri), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])
    pygame.display.flip()

    sus.rotation[0] += 2
    sus.rotation[1] = sus.rotation[0]
    sus.rotation[2] = sus.rotation[0]

    fps = int(1 / (time.time() - currentTime))

    # Setting the caption is much faster than printing
    pygame.display.set_caption(str(fps) + " FPS")
    currentTime = time.time()
