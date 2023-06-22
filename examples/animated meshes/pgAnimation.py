import z3dpy as zp
import pygame

pygame.init()
screen = pygame.display.set_mode((1680, 720))
clock = pygame.time.Clock()

# Setting up FOV
zp.FindHowVars(65, 9/21)

#zp.SetHowVars(0.733063825608609, 1.3032244924564758)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(-10, -2, 3, 1680, 720)

zp.CamSetTargetDir(myCamera, [1, 0, 0])

zp.SetInternalCam(myCamera)

# z3dpy.LoadAnimMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
anim = zp.LoadAnimMesh("mesh/anim/anim.obj")
anim2 = zp.LoadAnimMesh("mesh/char2/char2.obj")


zp.MeshSetColour(anim, [0, 255, 0])
zp.MeshSetColour(anim2, [255, 0, 0])


char1 = zp.Thing([anim], 0, 0, 3)
char2 = zp.Thing([anim2], 0, 0, 3)

plane = zp.Thing([zp.LoadMesh("z3dpy/mesh/plane.obj")], 0, 0, 3)

zp.AddThing(char1, 3)
zp.AddThing(char2)
zp.AddThing(plane)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    clock.tick(30)
    screen.fill("black")
    
    
    for tri in zp.Raster():
        nrm = zp.TriGetNormal(tri)
        shade = (-nrm[0] + nrm[1]) * 0.5
        zp.PgDrawTriS(tri, shade, screen, pygame)

    # Play animation
    zp.ThingIncFrames(char1)
    zp.ThingIncFrames(char2)
    
    pygame.display.flip()
