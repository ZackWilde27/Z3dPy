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

# Create a camera to render from, and give it the dimensions of the output screen
# Cam(vPos, *screenWidth, *screenHeight)
myCamera = zp.Cam([0, 0, 0], 1280, 720)

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

myMesh.shader = zp.SHADER_SIMPLE

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

# Since the camera isn't going to move, this only needs to be done once
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    # Clear the screen
    canvas.delete("all")
    
    # Render 3D
    for tri in zp.RasterThings([myThing]):
        canvas.create_polygon(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], fill=zp.RGBToHex(zp.TriGetColour(tri)))
        
    # Update the screen
    tK.update()
    
    myThing.rotation = zp.VectorAdd(myThing.rotation, [2, 2, 2])
