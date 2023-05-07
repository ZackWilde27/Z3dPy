# Z3dPy v0.1.0
Zack's Python 3D Engine

![engine](https://user-images.githubusercontent.com/115175938/235578934-23defc68-c021-4b05-b169-272e9ac8d3c9.gif)

Z3dPy is a personal project I'm working on, a 3D engine written entirely in Python. While it doesn't handle the display or inputs, it does pretty much everything else. It's meant to be used with PyGame to make for a speedy 3D engine, but it can also be used independently as quite the starting point for your own 3D engine.

Renders 950 on-screen triangles at 30 fps *(tested on my ryzen 7)*

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

FAQ can be found at the bottom

# Installation Guide

Download the latest release and extract the zip folder to the same folder as your script, then import it with:
```python
import z3dpy as zp
```
There are two versions of Z3dPy. The function version is used by default, which is 2x faster than object-oriented. If you don't mind sacrificing some speed for ease of programming, you can instead import the OOP version.

```python
import z3dpyOOP as zp
```

Lastly, you'll need a display to draw on, I recommend PyGame, but you could use Tkinter or something.

# Example Program

Basically the 'Hello World' of Z3dPy. I'll be showing you the function version. The OOP version can be found in the wiki.

I'll be using PyGame for my display to draw on.
```python
import z3dpy as zp
import pygame

# Just some PyGame stuff
pygame.init()
# We'll need to use the width and height for our camera later
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

First, create a camera with it's location, screen width, and screen height. Make sure it matches the output display.

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

Pass the RasterMeshList() function your mesh to draw and camera to view from, and it'll return a list of triangles to draw on the screen.

```python
for tri in zp.RasterMeshList([myMesh], myCamera):

    # RGBF will take a normalized vector convert it to colour
    zp.DrawTriangleRGBF(tri, screen, zp.TriangleGetNormal(tri), pygame)
    
pygame.display.flip()
```

I made convenient drawing functions for PyGame, but if you are using something else, check the <a href="https://github.com/ZackWilde27/Z3dPy/wiki/Drawing-Triangles">Drawing Triangles</a> page

<br>

Now all that's left is to chuck it in a loop.

```python
# Raster Loop
done = False

while not done:
    # more PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True    
    clock.tick(30)
    screen.fill("black")
    
    
    # Render 3D
    for tri in zp.RasterMeshList([myMesh], myCamera):
        zp.DrawTriangleRGBF(tri, screen, zp.TriangleGetNormal(tri), pygame)

    pygame.display.flip()
    
    # Rotate mesh
    zp.MeshAddRot(myMesh, 2, 5, 1)
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
