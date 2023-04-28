# Zack's 3D Python Library v0.0.2
or ZedPy for short

My hope is that 3D games in Python will be as easy as 2D games

Written entirely in Python. Renders 900 triangles at 30 FPS, 720p on my 3rd Gen Ryzen 7

No OpenGL, mostly because I don't understand graphics code

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here</a>

# Installation Guide

First, you'll need NumPy, my library requires it.

Then, download the repo as a zip file, extract it to the same folder as your script, and import it with
```python
import z3dpy
```

You only really need the z3dpy.py file, but the engine folder has some built-in meshes to use

# Example Program
To display the finished results we need a screen. In my experience, PyGame is faster than Tkinter, so I'll use that.

```python
import z3dpy
import pygame

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

In order to render objects to the screen, we need both a list of meshes to draw, and the camera that we are viewing from.
<br>
Load a mesh with z3dpy.LoadMesh() and then append it to a list.

```python
myMeshList = []

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = z3dpy.LoadMesh("engine/mesh/susanne.obj", 0, 0, 5)

myMeshList.append(myMesh)

# Create our camera object (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)
# The Components you'd probably be interested in modifying later: x, y, z, roll, pitch, yaw

```

To draw the meshes to the screen, rasterize them with RasterizeTriangles()

```python
# Pass our list of meshes and camera object to the rasterizer, it'll return a sorted list of triangles to draw on our screen
for tri in z3dpy.RasterTriangles(myMeshList, myCamera):
        
    # My library has handy functions for PyGame
    # This will colour the triangle with it's normal value.
    z3dpy.DrawTriangleRGB(tri, screen, tri.normal, pygame)
        
    # If you wanted flat shading instead of normal colouring
    #z3dpy.DrawTriangleF(tri, screen, tri.normal.z, pygame)
    
# Update Display afterwards
pygame.display.flip()
```

Now all that's left is to chuck it in a loop

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
    
    # For this example, it's easier to raster all triangles at once. for a more custom pipeline, see the wiki
    
    # Render 3D
    for tri in z3dpy.RasterTriangles(myMeshList, myCamera):
        z3dpy.DrawTriangleRGB(tri, screen, tri.normal, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    myMeshList[0].rot.x += 2
    myMeshList[0].rot.y += 5
    myMeshList[0].rot.z += 1
```


# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
Up axis is -Y, and Forward axis is -Z. In this case I wanted the mesh to face the camera

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)
