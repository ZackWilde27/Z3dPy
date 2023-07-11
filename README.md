# Z3dPy
![enginef](https://github.com/ZackWilde27/Z3dPy/assets/115175938/072e0f64-a536-4ae9-bc7e-60f542c3f950)

Z3dPy is my open-source 3D software renderer written entirely in Python. (Now with an extension to speed up rendering.)

Still in active development

You'll need something to draw on. I recommend PyGame for it's speed, but Tkinter also has built-in support.

Handles all the math for drawing, as well as lighting, rays/collisions, and basic physics.

Documentation can be found <a href="https://github.com/ZackWilde27/pythonRasterizer/wiki">here.</a>

<br>

# Installation Guide

First you'll need a display, like pygame, or tkinter or something.

Download the release build and extract the zip folder to the same folder as your script, then import it with:
```python
import z3dpy as zp
```

Builds that end in an odd number are nightly builds, which may be unstable / lacking documentation (outside of the script itself)

<br>

# Getting Started

![example](https://github.com/ZackWilde27/Z3dPy/assets/115175938/49541f9d-d88c-491c-934f-5e22b65402b2)

We'll import the engine and use PyGame for the screen. Tkinter version can be found <a href="https://github.com/ZackWilde27/Z3dPy/wiki/Tkinter">here</a>

```python
import z3dpy as zp
import pygame

# PyGame stuff
pygame.init()
pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
```

In 0.2.6+, the screen size is now global instead of inside cameras.
```python
zp.screenSize = (1280, 720)
```

Next create a camera object. Placing it at 0, 0, 0 will make placing the mesh easier.

```python
# Create our camera (x, y, z)
myCamera = zp.Cam(0, 0, 0)
```

Now load a mesh to draw, I'll use the built-in susanne.

For games it's handy to combine meshes into Things, but this example doesn't need those.

```python
# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj", 0, 0, 2)
# Z is forward in this case, so it's placed in front of the camera
```

Rendering 3D is done in 3 stages:
- Set the internal camera
- Rastering
- Draw the triangles

The drawing stage has <a href="https://github.com/ZackWilde27/Z3dPy/wiki/Drawing-Triangles">several different functions</a> depending on the desired shading.

```python
# Set Internal Camera
zp.SetInternalCam(myCamera)

# Rastering
for tri in zp.RasterMeshList([myMesh]):

    # Draw the triangles
    # Colouring the triangles with their normal value.
    zp.PgDrawTriRGBF(tri, zp.TriGetNormal(tri), screen, pygame)

# Also update the display afterwards
pygame.display.flip()
```

Lastly, chuck it in a loop.

```python
# This only needs to be done per frame if the camera's going to move.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    screen.fill("black")
    
    for tri in zp.RasterMeshList([myMesh]):

        zp.PgDrawTriRGBF(tri, zp.TriGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    # Rotate mesh
    # MeshAddRot(mesh, vector)
    zp.MeshAddRot(myMesh, [1, 4, 3])
```

Final Script:

```python
import z3dpy as zp
import pygame

# PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

zp.screenSize = (1280, 720)

# Create our camera (x, y, z)
myCamera = zp.Cam(0, 0, 0)

# Use the LoadMesh function to load an OBJ file (filename, x, y, z)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj", 0, 0, 2)

zp.SetInternalCam(myCamera)

# Raster Loop

while True:
    # more PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    # Make sure FPS stays the same across various machines.
    clock.tick(30)
    screen.fill("black")
    
    for tri in zp.RasterMeshList([myMesh]):

        zp.PgDrawTriRGBF(tri, zp.TriGetNormal(tri), screen, pygame)

    pygame.display.flip()
    
    zp.MeshAddRot(myMesh, [1, 4, 3])
```

Everything is coloured with it's normal direction, so X is red, Y is green, Z is blue.

<br>

# Exporting Mesh

Export your mesh as an OBJ file.
- UV coordinates are supported and used in the pixel shaders.
- N-gons are triangulated automatically.
- If materials are exported, LoadMesh() will automatically separate it into a list of meshes.
<br>
Up axis is -Y, and Forward axis is Z.

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)
