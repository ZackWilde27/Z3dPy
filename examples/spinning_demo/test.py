import z3dpy
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90 * 0.0174533, 0.5, 1200)

myMeshList = []

myMesh = z3dpy.LoadMesh("susanne.obj", 0, 0, 3)
stuckInLoop = True

while stuckInLoop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stuckInLoop = True 
            
    clock.tick(60)
    screen.fill("black")
    z3dpy.SetInternalCamera(myCamera)
    tris = z3dpy.RasterMesh(myMesh, myCamera)
    tris.sort(key = z3dpy.triSort)
    for tri in tris:
                
            # Draw the projected triangle to the screen, using the Z as our light direction
            pygame.draw.polygon(screen, (max(tri.normal.x, 0) * 255, max(-tri.normal.y, 0) * 255, max(-tri.normal.z, 0) * 255), [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

    pygame.display.flip()

    myMesh.rot.x += 5
    myMesh.rot.z += 8
