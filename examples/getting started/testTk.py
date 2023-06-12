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
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj", 0, 0, 0)

# z3dpy.Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCamera(myCamera)

# Raster Loop
while True:
    
    # Render 3D
    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.TkDrawTriF(tri, normal[2], canvas)
        
    # Update the screen afterwards
    tK.update()
    canvas.delete("all")
    
    # z3dpy.ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 1, 3])

