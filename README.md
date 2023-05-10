# Z3dPy v0.1.4
Zack's Python 3D Engine

![engine](https://user-images.githubusercontent.com/115175938/235578934-23defc68-c021-4b05-b169-272e9ac8d3c9.gif)

Z3dPy is a personal project I'm working on, a 3D engine written entirely in Python. While it doesn't handle the window itself or inputs, it does pretty much everything else. It's meant to be used with Pygame to make speedy 3D easy, but it can be used with any library that can draw to a screen.

Renders nearly 1000 on-screen triangles at 30 fps *(tested on my ryzen 7, in pygame)*

Z3dPy not only handles Rasterization, but also has a simple physics and collision system

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

FAQ can be found at the bottom

# Installation Guide

My library does not handle the window itself, so first you'll need something like Pygame. Although <a href="https://github.com/ZackWilde27/Z3dPy/wiki/Drawing-Triangles">it doesn't have to be Pygame</a>

Download the latest release and extract the zip folder to the same folder as your script, then import it with:
```python
import z3dpy as zp
```
There are two versions of Z3dPy. The function version is used by default, which is 2x faster than object-oriented. If you don't mind sacrificing some speed for ease of programming, you can instead import the OOP version.

```python
import z3dpyOOP as zp
```

# Example Program

Basically the 'Hello World' of Z3dPy. I'll be showing you the function version. The OOP version can be found in the wiki.

I'll be using Pygame for my display to draw on.
```python
import z3dpy as zp
import pygame

# Just some Pygame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

First, create a camera with it's location, screen width, and screen height. Make sure it matches the Pygame display.

```python

# Create our camera object (x, y, z, width, height)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

```

By default, cameras are set with an FOV of 90, and the target is pointed along the z axis. These can be changed with functions

<br>

For games, it's recommended to create your objects as Things, since they can hold multiple meshes among other benefits, but for this example we're only using one mesh

```python

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 5)

```

Drawing to the screen is as simple as 2 lines

```python
for tri in zp.RasterMeshList([myMesh], myCamera):

    # RGBF will take a normalized vector convert it to colour
    zp.DrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)
    
# Update window afterwards
pygame.display.flip()
```

Now all that's left is to chuck it in a loop.

```python
# Raster Loop
done = False

while not done:
    # more Pygame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True    
    clock.tick(30)
    screen.fill("black")
    
    
    # Render 3D
    for tri in zp.RasterMeshList([myMesh], myCamera):
        zp.DrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    zp.MeshAddRot(myMesh, [2, 5, 1])
```

Final script:

```python
import z3dpy as zp
import pygame

# Just some Pygame stuff
pygame.init()
# We'll need to use the width and height for our camera later
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Create our camera object (x, y, z, width, height)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("engine/mesh/susanne.obj", 0, 0, 5)

# Raster Loop
done = False

while not done:
    # more Pygame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True    
    clock.tick(30)
    screen.fill("black")
    
    
    # Render 3D
    for tri in zp.RasterMeshList([myMesh], myCamera):
        zp.DrawTriangleRGBF(tri, zp.TriangleGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    zp.MeshAddRot(myMesh, [2, 5, 1])
```

# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
Up axis is -Y, and Forward axis is -Z. In this case I wanted the mesh to face the camera

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)

# FAQ

I don't get asked questions, but I've compiled a list of mistakes that I've made before

### TypeError: can only concatenate list (not "int") to list

When drawing a thing with one mesh, this usually means forgetting to put the meshes in a list: z3dpy.Thing([myMesh], x, y, z)

### There aren't any errors, but it's a black screen

If you are drawing the screen using DrawTriangleRGB, keep in mind that it's expecting 0-255, so a normalized vector (0-1) will remain black. Use DrawTriangleRGBF() instead, or use a VectorMulF() and multiply it by 255
