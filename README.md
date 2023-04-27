# Zack's 3D Python Library
or ZedPy for short

I'm working on a 3D engine for Python. <br>
Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here</a>

# Installation Guide

First, you'll need NumPy, my library requires it.

Next, you'll need some way to display the graphics, I recommend PyGame.

Then, copy the z3dpy.py file into your script's directory and import it with
```python
import z3dpy
```

# Exporting Mesh

Export your mesh as an OBJ file, with no extra information. Make sure to triangulate.
<br>
The forward axis is +Z, and up axis is -Y

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)


# Example Program
We'll import the engine and use PyGame for our screen.

```python
import z3dpy
import pygame

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

Next we create our camera object. width and height should match the output screen

```python
# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)
```

Now we need to define a list of meshes to draw, we could do this manually but there's a function to load a mesh from a file
```python
myMeshList = []

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = z3dpy.LoadMesh("example.obj", 0, 0, 2)
myMeshList.append(myMesh)
```

Now all that's left is defining our draw loop

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
    
    # Pass our list of meshes and camera info to the rasterizer, it'll return a sorted list of triangles to draw on our screen
    for tri in z3dpy.RasterTriangles(myMeshList, myCamera):
        
        # My library has handy functions for PyGame
        # This will colour the triangle with it's normal value.
        z3dpy.DrawTriangleRGB(tri, screen, tri.normal, pygame)
        
        # If you wanted flat shading instead of normal colouring
        #z3dpy.DrawTriangleF(tri, screen, tri.normal.z, pygame)

    # Update display
    pygame.display.flip()
    
    # Rotate mesh for maximum screensaver effect
    myMeshList[0].roll += 0.1
    myMeshList[0].pitch += 0.14
    myMeshList[0].yaw += 0.07
```
