# Z3dPy
![enginef](https://github.com/ZackWilde27/Z3dPy/assets/115175938/072e0f64-a536-4ae9-bc7e-60f542c3f950)

Z3dPy is my open-source 3D engine written in Python, packaged into a module.

It does all the math for 3D rendering without any dependencies, and includes some basic features to get you started, like lighting, collisions, physics, and rays.

You'll need a module to drive the screen and handle controls, I recommend PyGame as it's quite fast.

Documentation can be found <a href="https://github.com/ZackWilde27/Z3dPy/wiki">here.</a>

<br>

# Installation Guide

Download the zip folder, extract it somewhere, and create a new script in the same directory. Import it with:
```python
import z3dpy as zp
```

Builds that end in an odd number are nightly builds, which may be unstable / lacking documentation (outside of the script itself)

<br>

# Getting Started

![example](https://github.com/ZackWilde27/Z3dPy/assets/115175938/49541f9d-d88c-491c-934f-5e22b65402b2)

(Don't mind the dithering, just a low quality GIF)

I'll use PyGame to drive the screen.</a>

```python
import pygame
import z3dpy as zp

# PyGame stuff
pygame.init()
pygame.display.set_mode((1280, 720))
```

<br>

First, create a camera to view from, and set the screenSize to match the previously set up window.

```python
# Vectors are lists or tuples, [x, y, z]
myCamera = zp.Cam([0, 0, 0])

zp.screenSize = (1280, 720)
```

<br>

Now load a mesh to draw, I'll use the built-in suzanne monkey.

For games it's handy to combine meshes into Things, but this example doesn't need those.

```python
# Use the LoadMesh function to load an OBJ file (filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj", [0, 0, 2])
# Z is forward in this case, so it's placed in front of the camera
```
*Parameters marked with a * are optional*

<br>

Rendering 3D is done in 3 stages:
- Set the internal camera
- Rastering
- Draw the triangles (the method will depend on the module handling the screen)

```python
# Set Internal Camera
zp.SetInternalCam(myCamera)

# Rastering
for tri in zp.RasterMeshList([myMesh]):

    # Draw the triangles
    colour = zp.VectorMulF(zp.TriGetNormal(tri), -255)
    pygame.draw.polygon(screen, colour, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Also update the display afterwards
pygame.display.flip()
```

<br>

If your display method doesn't have a native triangle drawing function, triangles can be converted into either lines or pixels (although the performance cost of looping through each line or pixel can be drastic, especially with the latter).
```python
for tri in zp.RasterMeshList([myMesh]):
    # Draw the triangles
    colour = zp.VectorMulF(zp.TriGetNormal(tri), -255)
    for pixel in zp.TriToPixels(tri):
        x = pixel[0]
        y = pixel[1]
        # Drawing a 1 pixel line, although using a pixel array would be faster
        pygame.draw.line(screen, colour, (x, y), (x + 1, y))
```

or

```python
for tri in zp.RasterMeshList([myMesh]):
    # Draw the triangles
    colour = zp.VectorMulF(zp.TriGetNormal(tri), -255)
    for line in zp.TriToLines(tri):
        sx = line[0][0]
        sy = line[0][1]
        ex = line[1][0]
        ey = line[1][1]
        pygame.draw.line(screen, colour, (sx, sy), (ex, ey))
```

<br>

Lastly, chuck it in a loop.

```python
# This only needs to be done per frame if the camera's going to move.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    # Clear screen
    screen.fill("black")

    # Render 3D
    for tri in zp.RasterMeshList([myMesh]):
        colour = zp.VectorMulF(zp.TriGetNormal(tri), -255)
        pygame.draw.polygon(screen, colour, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

    # Update screen
    pygame.display.flip()
    
    # Rotate mesh
    # MeshAddRot(mesh, vector)
    zp.MeshAddRot(myMesh, [1, 2, 3])
```

Final Script:

```python
import z3dpy as zp
import pygame

# PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Create a camera
# Cam(vPosition)
myCamera = zp.Cam([0, 0, 0])
zp.screenSize = (1280, 720)

# Use the LoadMesh function to load an OBJ file (filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj", [0, 0, 2])

zp.SetInternalCam(myCamera)

# Raster Loop

while True:
    # more PyGame Stuff
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill("black")
    
    for tri in zp.RasterMeshList([myMesh]):
        colour = zp.VectorMulF(zp.TriGetNormal(tri), -255)
        pygame.draw.polygon(screen, colour, [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

    pygame.display.flip()
    
    zp.MeshAddRot(myMesh, [1, 2, 3])
```

Everything is coloured with it's normal direction, so X is red, Y is green, Z is blue.

<br>

# Exporting Mesh

Export your mesh as an OBJ file.
- UV coordinates are used in the pixel shaders.
- LoadMesh() will triangulate all n-gons
- If materials are exported, LoadMesh() will automatically separate it into a list of meshes, and colour them based on the mtl file.
<br>
Up axis is -Y, and Forward axis is Z.

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)

<br>
