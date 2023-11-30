import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1680, 720))
clock = pygame.time.Clock()

zp.screenSize = (1680, 720)

# Setting up FOV and 21:9 aspect ratio
#zp.FindHowVars(65, 9/21)
zp.SetHowVars(0.6727219660070214, 1.5696847505584837)

# Cam(vPos)
myCamera = zp.Cam([-10, -2, 3])

# Setting Camera Target Direction
myCamera.SetTargetDir([1, 0, 0])

zp.SetInternalCam(myCamera)

# LoadAniMesh(filename, *vPos, *VScale)
anim = zp.LoadAniMesh("mesh/anim/anim.aobj")
anim2 = zp.LoadAniMesh("mesh/char2/char2.aobj")

def MyShader(tri):
    nrm = zp.TriGetNormal(tri)
    shade = (-nrm[0] + -nrm[1]) * 0.5
    shade = max(shade, 0)
    return zp.VectorMulF(zp.TriGetColour(tri), shade)

# Shaders can run on 3 different stages:
# - local: Before transformations
# - world: After transformations
# - view: After the view stage
myMaterial = zp.Material(view = MyShader)

anim.material = myMaterial
anim2.material = myMaterial


# mesh.SetColour(vColour)
anim.SetColour([0, 255, 0])
anim2.SetColour([255, 0, 0])

# Thing(meshList, vPos)
char1 = zp.Thing([anim], [0, 0, 3])
char2 = zp.Thing([anim2], [0, 0, 3])

plane = zp.Thing([zp.LoadMesh("z3dpy/mesh/plane.obj")], [0, 0, 3])

# Adding to the internal list to be drawn with Raster(), and putting char1 on it's own layer
zp.AddThing(char1, 3)
zp.AddThings([char2, plane])

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    clock.tick(30)
    screen.fill("black")
    
    for tri in zp.Raster():
        nrm = zp.TriGetNormal(tri)
        zp.PgDrawTriRGB(tri, zp.TriGetColour(tri), screen, pygame)

    # Play animation
    anim.frame += 1
    anim2.frame += 1
    
    pygame.display.flip()
