# Z3dPy v0.0.7
Zack's Python 3D Engine

![engine](https://user-images.githubusercontent.com/115175938/235578934-23defc68-c021-4b05-b169-272e9ac8d3c9.gif)

Written entirely in Python, no OpenGL or anything

Renders 950 on-screen triangles at 30 fps *(on a 3rd gen Ryzen 7)*

**This engine is still in development, so certain aspects are unfinished**

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

FAQ can be found at the bottom

# Installation Guide

Download the z3dpy.py file and engine folder, and put them in the same folder as your script, then import it with
```python
import z3dpy as z
```

There are two versions of Z3dPy. The function version is used by default, which is 2x faster than object-oriented. If you want to sacrifice some speed for ease of programming, you can instead import the OOP version.

```python
import z3dpyOOP as z
```

<br>

My library does not come with a display, you'll need some other library, like Tkinter or PyGame. In my experience PyGame is faster, so I built my library around it, but it's certainly possible to use other things.

# Example Program

Basically the 'Hello World' of Z3dPy. I'll be showing you the function version. The OOP version can be found in the wiki.

I'll be using PyGame for my display to draw on.
```python
import z3dpy as z
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
myCamera = z.Camera(0, 0, 0, 1280, 720)

```

By default, cameras are set with an FOV of 90, and the target is pointed along the z axis. These can be changed with functions, like CameraSetFOV(), and CameraSetTarget()

<br>

For games, it's recommended to create your objects as Things, since they can hold multiple meshes among other benefits, but for this example we're only using one mesh

Load a mesh with LoadMesh()

```python

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
# z of 5 to put it in front of the camera, which we will put at 0, 0, 0
myMesh = z.LoadMesh("engine/mesh/susanne.obj", 0, 0, 5)

```



Even though we only have one mesh, it's recommended to use RasterMeshList() or RasterThings() anyways, because it does things like setting the internal camera, and sorting the triangles automatically.

Pass the RasterMeshList() function your mesh to draw and camera to view from, and it'll return a list of triangles to draw on the screen.

```python

for tri in z.RasterMeshList([myMesh], myCamera):

    # This will colour the triangle with it's normal value.
    # RGBF will take a normalized vector convert it to colour
    z.DrawTriangleRGBF(tri, screen, z.TriangleGetNormal(tri), pygame)
    
# Update Display afterwards
pygame.display.flip()
```

I made convenient drawing functions for PyGame, but if you are using something else, ignore the z and just use the x and y points.

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
    for tri in z.RasterMeshList([myMesh], myCamera):
        z.DrawTriangleRGBF(tri, screen, z.TriangleGetNormal(tri), pygame)

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
