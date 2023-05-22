# Z3dPy
Zack's 3D Module for Python


![enginef](https://github.com/ZackWilde27/Z3dPy/assets/115175938/072e0f64-a536-4ae9-bc7e-60f542c3f950)

Z3dPy is a personal project I'm working on, a 3D module written entirely in Python, focused on ease of use.

Built for pygame to make games with, but tkinter works just fine.

Renders nearly 1000 on-screen triangles at 30 fps *(tested on my ryzen 7)*

Handles Rasterization, Physics/Collisions, and Lighting. Still in active development, so improvements/features are on the way

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

# Installation Guide

First you'll need a display, like pygame, or tkinter or something.

Download the latest release and extract the zip folder to the same folder as your script, then import it with:
```python
import z3dpy as zp
```

# Getting Started

![example](https://github.com/ZackWilde27/Z3dPy/assets/115175938/49541f9d-d88c-491c-934f-5e22b65402b2)

We'll import the engine and use pygame for our screen.

```python
import z3dpy as zp
import pygame

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

Next we create our camera object. width and height should match the output screen

```python
# Create our camera (x, y, z, width, height)
myCamera = zp.Camera(0, 0, 0, 1280, 720)
```

Now we load our mesh, I'll use the built-in susanne.

For games it's handy to combine meshes into Things, but this example doesn't need those.

```python
# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 2)
# Z is forward in this case, so it's placed in front of the camera
```

Rendering 3D in Z3dPy takes 3 steps:
- Set the internal camera
- Raster the meshes
- Draw the triangles

The drawing stage has several different functions depending on the desired shading.

```python
# Set Internal Camera
zp.SetInternalCamera(myCamera)

# Raster the meshes
for tri in zp.RasterMeshList([myMesh]):

    # Draw the triangles
    zp.PgDrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)

# Also update the display afterwards
pygame.display.flip()
```

We got one frame, next is to chuck it in a loop.

```python
# This only needs to be done per frame if the camera's going to move.
zp.SetInternalCamera(myCamera)

# Raster Loop
while True:

    screen.fill("black")
    
    for tri in zp.RasterMeshList([myMesh], myCamera):

        zp.PgDrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    # MeshAddRot(mesh, vector)
    zp.MeshAddRot(myMesh, [1, 4, 3])
```

Final Script:

```python
import z3dpy as zp
import pygame

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Create our camera (x, y, z, width, height)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 2)

zp.SetInternalCamera(myCamera)

# Raster Loop
done = False

while not done:
    # more PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True    
    clock.tick(30)
    screen.fill("black")
    
    for tri in zp.RasterMeshList([myMesh]):

        zp.PgDrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    zp.MeshAddRot(myMesh, [1, 4, 3])
```
<br>
Everything is coloured with it's normal direction, so X is red, Y is green, Z is blue.

<br> 
To do flat shading, call DrawTriangleF() and put in one of the normal axis

# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
Up axis is -Y, and Forward axis is Z.

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)

# FAQ

I don't get asked questions, but I've compiled a list of mistakes that I've made before

### TypeError: can only concatenate list (not "int") to list

When drawing a thing with one mesh, this usually means forgetting to put the meshes in a list: z3dpy.Thing([myMesh], x, y, z)

### There aren't any errors, but it's a black screen

If you are drawing the screen using DrawTriangleRGB, keep in mind that it's expecting 0-255, so a normalized vector (0-1) will remain black. Use DrawTriangleRGBF() instead, or use a VectorMulF() and multiply it by 255
