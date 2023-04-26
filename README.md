# Zack's Python Rasterizer Library

I'm working on a 3D engine for Python. <br>
Wiki can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here</a>

# Installation Guide

First, install NumPy.

Then, copy the prez.py file into your script's directory and import it with
```python
from prez import *
```

Now you have all the functions and classes required to start

# Example Program
We'll import the engine and draw the results with PyGame.

```python
from prez import *
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

myMeshList = []

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMeshList.append(LoadMesh("example.obj", 0, 0, 2))

# Create our camera (x, y, z, width, height, fov, nearClip, farClip)
myCamera = Camera(0, 0, 0, 1280, 720, 90, 0.1, 1500)

# Raster Loop
done = False

while not done:
    # PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            
    clock.tick(30)
    screen.fill("black")
    
    # Pass our list of meshes and camera info to the rasterizer, it'll return a sorted list of triangles to draw on our screen
    for tri in RasterTriangles(myMeshList, myCamera):
        
        # Setting our light direction to the +Z axis
        triColour = (max(tri.normal.z, 0) * 255, max(tri.normal.z, 0) * 255, max(tri.normal.z, 0) * 255)
        
        # Draw the triangle to the screen
        pygame.draw.polygon(screen, triColour, [(tri.p1.x, tri.p1.y), (tri.p2.x, tri.p2.y), (tri.p3.x, tri.p3.y)])

    # Update display
    pygame.display.flip()
```
