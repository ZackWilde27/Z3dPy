# Legend:
# - Parameters marked with a * are optional
# - Most parameters have a letter denoting type - capitals mean normalized.

try:
    import tkinter as tk
except:
    import Tkinter as tk
import z3dpy as zp

#Initialize Tkinter
tK = tk.Tk()
canvas = tk.Canvas(width=1280, height=720, background="black")
canvas.pack()

# Set the render size to match the output screen
zp.screenSize = (1280, 720)

# Create a camera to render from
# Cam(vPos)
myCamera = zp.Cam([0, 0, 0])

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    # Clear the screen
    canvas.delete("all")
    
    # Render 3D
    for tri in zp.RasterThings([myThing]):
        normal = zp.TriGetNormal(tri)
        zp.TkDrawTriF(tri, -normal[2], canvas)
        
    # Update the screen
    tK.update()
    
    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 2, 2])
