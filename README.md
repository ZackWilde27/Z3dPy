# Z3dPy
<br>

Z3dPy is my open-source 3D renderer written in Python, packaged into a module.

You'll need something to draw on, I recommend PyGame for it's speed.

- It's Fast (fast enough that the speed will depend on your drawing method)
- Easy to use
- 100% Python, but can be sped up even further with an extension
- Stores vertex animation efficiently with my Animated OBJ format.
- Built-in features for making games, with the expandability to do more.

<br>

https://github.com/ZackWilde27/Z3dPy/assets/115175938/401e94e4-83dc-46e9-baea-2bb687ff741b

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
import z3dpy as zp
import pygame

pygame.init()
pygame.display.set_mode((1280, 720))
```

<br>

First, create a camera to view from, and give it the dimensions of the previously set up window.

```python
myCamera = zp.Cam([0, 0, 0], 1280, 720)
# Vectors are lists or tuples, [x, y, z]
```

<br>

Now load a mesh to draw, I'll use the built-in suzanne monkey.

```python
# Use the LoadMesh function to load an OBJ, DAE, or X3D file (filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj", [0, 0, 2])
# Z is forward in this case, so it's placed in front of the camera
```
*Parameters marked with a * are optional*

<br>

Rendering can be broken down into 3 stages:
- Set the internal camera
- Rendering
- Drawing (the method will depend on the module handling the screen)

```python
# Set Internal Camera
zp.SetInternalCam(myCamera)

# Rastering
# For games I'd recommend combining meshes into Things, but for now just use RenderMeshList()
for tri in zp.RenderMeshList([myMesh]):
    pygame.draw.polygon(screen, zp.TriGetColour(tri), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

# Also update the display afterwards
pygame.display.flip()
```

<br>

If your display method doesn't have a native triangle drawing function, triangles can be converted into either lines or pixels (although the performance cost of looping through each line or pixel can be drastic, especially with the latter).
```python
def MyPixelDraw(x, y)
    # Draw code here
    # The current triangle from the for loop can be accessed from here
    colour = zp.TriGetColour(tri)

for tri in zp.RenderMeshList([myMesh]):
    # Draw the triangles
    zp.TriToPixels(tri, MyPixelDraw)
    
```

or

```python
def MyLineDraw(sx, sy, ex, ey):
   # Draw code here
   pygame.draw.line(screen, zp.TriGetColour(tri), (sx, sy), (ex, ey))

for tri in zp.RasterMeshList([myMesh]):
    # Draw the triangles
    zp.TriToLines(tri, MyLineDraw)
        
```

<br>

Right now, the mesh is using the default shader, SHADER_UNLIT, which will just pass the colour of the triangle through.

![image](https://github.com/ZackWilde27/Z3dPy/assets/115175938/f19598ed-ab67-4ace-af56-57a1dbca62ca)

To get something shaded, go back to where the mesh was defined and change it's shader to either a built-in option or your own shader function.
```python
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj", [0, 0, 2])
# Z is forward in this case, so it's placed in front of the camera

myMesh.shader = zp.SHADER_SIMPLE

# Shaders are just functions that take a tri and returns a colour for it
def MyShader(tri):
    return (255, 0, 0)
```

With SHADER_SIMPLE it should look like this

![image](https://github.com/ZackWilde27/Z3dPy/assets/115175938/6d4a4a74-45cd-49d8-ac40-b8f5206e99ee)

More on shaders can be found on the <a href="https://github.com/ZackWilde27/Z3dPy/wiki/Meshes-0.4">Meshes</a> page

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
    for tri in zp.RenderMeshList([myMesh]):
        pygame.draw.polygon(screen, zp.TriGetColour(tri), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

    # Update screen
    pygame.display.flip()
    
    # Rotate mesh
    myMesh.rotation = zp.VectorAdd(myMesh.rotation, [1, 2, 3])
```

Final Script:

```python
import z3dpy as zp
import pygame


pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Create a camera
# Cam(vPosition, *screenWidth, *screenHeight)
myCamera = zp.Cam([0, 0, 0], 1280, 720)

# Use the LoadMesh function to load an OBJ, DAE, or X3D file (filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/suzanne.obj", [0, 0, 2])

zp.SetInternalCam(myCamera)

# Render Loop

while True:
    # PyGame stuff to prevent freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill("black")
    
    for tri in zp.RenderMeshList([myMesh]):
        pygame.draw.polygon(screen, zp.TriGetColour(tri), [(tri[0][0], tri[0][1]), (tri[1][0], tri[1][1]), (tri[2][0], tri[2][1])])

    pygame.display.flip()
    
    myMesh.rotation = zp.VectorAdd(myMesh.rotation, [1, 2, 3])
```

Everything is coloured with it's normal direction, so X is red, Y is green, Z is blue.

<br>

# Exporting Mesh

Export your mesh as an OBJ, DAE, or X3D file.
- UV coordinates are supported, kinda.
- LoadMesh() will automatically triangulate n-gons.
- If materials are exported in an OBJ, LoadMesh() will automatically separate it into a list of meshes to be put in a Thing, and colour them based on the mtl file.
<br>
Up axis is -Y, and Forward axis is Z.

![image](https://user-images.githubusercontent.com/115175938/235002154-62bb03ad-13f3-4084-b410-aa0074553865.png)

<br>
