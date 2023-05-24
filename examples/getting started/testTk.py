import z3dpy as zp
try:
    import tkinter as tk
except:
    import Tkinter as tk

#Initialize Tkinter
tK = tk.Tk()
canvas = tk.Canvas(width=1280, height=720, background="black")
canvas.pack()

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

# z3dpy.LoadMesh(filename, x, y, z)
try:
    susanne = zp.LoadMesh("z3dpy/mesh/susanne.obj", 0, 0, 0)
except:
    # Installed globally, retrieve the built-in mesh from the module
    susanne = zp.NewSusanne()

# z3dpy.Thing(meshList, x, y, z)
thing = zp.Thing([susanne], 0, 0, 3)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCamera(myCamera)

# Raster Loop
while True:
    
    # Render 3D
    for tri in zp.RasterThings([thing]):
        zp.TkDrawTriangleF(tri, zp.TriangleGetNormal(tri)[2], canvas)
        
    # Update the screen afterwards
    tK.update()
    canvas.delete("all")
    
    # z3dpy.ThingAddRot(thing, vector)
    zp.ThingAddRot(thing, [2, 1, 3])

