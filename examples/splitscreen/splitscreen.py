import pygame
import z3dpy as zp

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))

zp.FindHowVars(90, 360/1280)

# Create a camera to render from
# Cam(position, *screenWidth, *screenHeight)
firstCamera = zp.Cam([0, 0, 0], 1280, 360)
secondCamera = zp.Cam([0, -3, 2])

# Vectors are a list or tuple [x, y, z]

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj", [0, 0, 3])

myMesh.material = zp.MATERIAL_SIMPLE

secondCamera.target = myMesh.position

# Shader has 5 built-in options:
# SHADER_UNLIT
# Colour is untouched

# SHADER_SIMPLE
# Simple normal-based shading.

# SHADER_DYNAMIC
# Dynamic Lighting, based on lights in the zp.lights list

# SHADER_STATIC
# Baked Lighting, requires a zp.BakeLighting() call.
myMesh.shader = zp.SHADER_SIMPLE


# Draw Loop
while True:
    
    # More PyGame stuff to prevent freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Clear the screen
    screen.fill("black")

    zp.SetInternalCam(firstCamera)

    # Render 3D
    for tri in zp.RenderMeshList([myMesh]):
        pygame.draw.polygon(screen, zp.TriGetColour(tri), ((tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])))

    zp.SetInternalCam(secondCamera)

    for tri in zp.RenderMeshList([myMesh]):
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(zp.TriAdd(tri, [0, 360, 0]), False))

    # Update the screen
    pygame.display.flip()

    # Rotate the Thing
    myMesh.rotation[0] += 2
    myMesh.rotation[1] += 2
    myMesh.rotation[2] += 2
