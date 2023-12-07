# Legend:
# - Parameters marked with a * are optional
# - Most parameters have a letter denoting type - capitals mean normalized.

import z3dpy as zp

buffer = ""
buffer = [[" " for u in range(64)] for b in range(32)]

# Set the render size to match the output screen
zp.screenSize = (64, 24)

#zp.FindHowVars(90, (24/64))
zp.SetHowVars(0.374999782861215, 0.9999994949884249)

# Create a camera to render from
# Cam(vPos)
myCamera = zp.Cam([0, 0, 0])

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/cube.obj")

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

values = " -#@"

def myDraw(x, y):
    # The current triangle in the for loop below can be accessed from here
    if (val := values[int((zp.TriGetColour(tri)[2] / 255) * 3)]):
        buffer[y][x] = val

# Raster Loop
while True:

    # Clear Screen
    buffer = [[" " for u in range(64)] for b in range(24)]

    # Render 3D
    for tri in zp.RasterThings([myThing]):
        zp.TriToPixels(tri, myDraw)

    # Update the screen
    for y in range(24):
        print(''.join(buffer[y]))

    myThing.rotation = zp.VectorAdd(myThing.rotation, [2, 2, 2])
