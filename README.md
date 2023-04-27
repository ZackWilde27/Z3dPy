# Zack's 3D Library for Python
or Z3DPy for short

I'm working on a 3D engine for Python. <br>
Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here</a>

Very early in development, this engine will update with features as time goes on.

# Installation Guide

First, you'll need NumPy, my library requires it.

Then, copy the z3dpy.py file into your script's directory and import it with
```python
import z3dpy
```

Now you have all the functions and classes required to start

# Example Program
We'll import the engine and draw the results with PyGame.

```python
import z3dpy
import pygame

myMeshList = []

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMeshList.append(z3dpy.LoadMesh("example.obj", 0, 0, 2))

# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = z3dpy.Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)

# Just some PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

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
        z3dpy.DrawTriangleRGB(tri, screen, tri.normal, pygame)

    # Update display
    pygame.display.flip()
    
    # Rotate mesh for maximum screensaver effect
    myMeshList[0].roll += 0.1
    myMeshList[0].pitch += 0.14
    myMeshList[0].yaw += 0.07
```
