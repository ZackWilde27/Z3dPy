# Z3dPy v0.0.6
Zack's Python 3D Engine

![engine](https://user-images.githubusercontent.com/115175938/235578934-23defc68-c021-4b05-b169-272e9ac8d3c9.gif)

Written entirely in Python, no graphics libraries. 

Renders 1400 triangles at 30 fps *(on a 3rd gen Ryzen 7)*

This engine is still very early on, I'm planning many more updates with features.

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

# Installation Guide

Download the z3dpy.py file and engine folder, and put them in the same folder as your script, then import it with
```python
import z3dpy as z
```

There are two versions of Z3dpy. The function version is used by default, which is faster. If you want to sacrifice some speed for ease of programming, you can instead import the object-oriented version.

```python
import z3dpyOOP as z
```

My library does not come with a display, you'll need some other library, like Tkinter or PyGame. In my experience PyGame is faster.

# Example Program

Basically the 'Hello World' of z3dpy. I'll be showing you the function version. The OOP version can be found in the wiki.

I'll be using PyGame for my display to draw on.
```python
import z3dpy as z
import pygame

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

In order to render objects to the screen, we need both a list of objects to draw, and the camera that we are viewing from.

For games, it's recommended to create your objects as Things, since they can hold multiple meshes among other benefits, but for this example we're only using one mesh

Load a mesh with LoadMesh()

```python

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = z.LoadMesh("engine/mesh/susanne.obj", 0, 0, 5)

```

Next, create a camera with it's location, screen width, and screen height. Make sure it matches the output display

```python

# Create our camera object (x, y, z, width, height)
myCamera = z.Camera(0, 0, 0, 1280, 720)

```

For individual objects, we'll need to set the internal camera before we render, this is done automatically with RasterThings() or RasterMeshList()

Pass the RasterMesh() function your mesh to draw and camera to view from, and it'll return a list of triangles to draw on the screen.

I made convenient drawing functions for PyGame, but if you are using something else, ignore the z and just use the x and y points.

```python
# This is done automatically for RasterThings() and RasterMeshList(), but not for individual items
z.SetInternalCamera(myCamera)

for tri in z.RasterMesh(myMesh, myCamera):
        
    # My library has handy functions for PyGame
    # This will colour the triangle with it's normal value.
    # We need to multiply the normal vector by 255 to get a colour value
    z.DrawTriangleRGBF(tri, screen, z.VectorMulF(z.TriangleGetNormal(tri), 255), pygame)
        
    # If you wanted flat shading instead of normal colouring
    # [0] is x, [1] is y, [2] is z
    #z.DrawTriangleF(tri, screen, z.TriangleGetNormal(tri)[2], pygame)
    
# Update Display afterwards
pygame.display.flip()
```

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
    
    z.SetInternalCamera(myCamera)
    
    # Render 3D
    for tri in z.RasterMesh(myMesh, myCamera):
        z.DrawTriangleRGB(tri, screen, z.VectorMulF(z.TriangleGetNormal(tri), 255), pygame)

    pygame.display.flip()
    
    # Rotate mesh
    z.MeshAddRot(myMesh, 2, 5, 1)
```
There's more ways to raster triangles depending on how custom of a pipeline you need, all of which can be found on the wiki

# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
Up axis is -Y, and Forward axis is -Z. In this case I wanted the mesh to face the camera

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)

# FAQ

I don't get asked questions, but I've compiled a list of mistakes that I've made before

### return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]] TypeError: can only concatenate list (not "int") to list


When drawing a thing with one mesh, this usually means forgetting to put the meshes in a list: z3dpy.Thing([myMesh], x, y, z)

### There aren't any errors, but it's a black screen

If you are drawing the screen using DrawTriangleRGB, keep in mind that it's expecting 0-255, so a normalized vector (0-1) will remain black. Use DrawTriangleRGBF() instead, or use a VectorMulF() and multiply it by 255
