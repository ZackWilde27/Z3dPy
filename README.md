# Zack's 3D Engine v0.0.6
or Z3dPy for short

![engine](https://user-images.githubusercontent.com/115175938/235578934-23defc68-c021-4b05-b169-272e9ac8d3c9.gif)

Written entirely in Python.

Renders 1400 triangles at 30 fps.

Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

# Installation Guide

Download the z3dpy.py file and engine folder, and put them in the same folder as your script, then import it with
```python
import z3dpy
```

My library does not come with a display, you'll need some other library, like Tkinter or PyGame. In my experience PyGame is faster.

# Example Program
Like I said in the installation guide, we'll need some kind of display to draw on, and I'll be using PyGame for this.

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
```

Next, create a camera with all the required info

```python

# Create our camera object (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)
# The Components you'd probably be interested in modifying later: x, y, z

```

Pass the RasterTriangles() function your list of meshes to draw and camera to view from, and it'll return a list of triangles to draw on the screen.

I made convenient drawing functions for PyGame, but if you are using something else, ignore the z and just use the x and y points.

```python
for tri in z3dpy.RasterTriangles(myMeshList, myCamera):
        
    # My library has handy functions for PyGame
    # This will colour the triangle with it's normal value.
    z3dpy.DrawTriangleRGB(tri, screen, z.TriangleGetNormal(tri), pygame)
        
    # If you wanted flat shading instead of normal colouring
    # [0] is x, [1] is y, [2] is z
    #z3dpy.DrawTriangleF(tri, screen, z.TriangleGetNormal(tri)[2], pygame)
    
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
    
    # For this example, it's easier to raster all triangles at once. for a more custom pipeline, see the wiki
    
    # Render 3D
    for tri in z3dpy.RasterTriangles(myMeshList, myCamera):
        z3dpy.DrawTriangleRGB(tri, screen, tri.normal, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    z.MeshAddRot(myMesh, [2, 5, 1])
```


# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
Up axis is -Y, and Forward axis is -Z. In this case I wanted the mesh to face the camera

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)
