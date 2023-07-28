import z3dpy as zp
try:
    import tkinter as tk
except:
    import Tkinter as tk

#Initialize Tkinter
tK = tk.Tk()
canvas = tk.Canvas(width=1280, height=720, background="black")
canvas.pack()

zp.screenSize = (1280, 720)

# Cam(x, y, z)
myCamera = zp.Cam(0, 0, 0)

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

# Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    # Clear the screen
    canvas.delete("all")
    
    # Render 3D
    for tri in zp.RasterThings([myThing]):
        normal = zp.TriGetNormal(tri)
        zp.TkDrawTriF(tri, normal[2], canvas)
        
    # Update the screen
    tK.update()
    
    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 2, 2])
