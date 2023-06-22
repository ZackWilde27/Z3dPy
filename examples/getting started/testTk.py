import z3dpy as zp
try:
    import tkinter as tk
except:
    import Tkinter as tk

#Initialize Tkinter
tK = tk.Tk()
canvas = tk.Canvas(width=1280, height=720, background="black")
canvas.pack()

# Cam(x, y, z, scrW, scrH)
myCamera = zp.Cam(0, 0, 0, 1280, 720)

# LoadMesh(filename)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

# Thing(meshList, x, y, z)
myThing = zp.Thing([myMesh], 0, 0, 3)

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

# Raster Loop
while True:

    # Clear the screen
    canvas.delete("all")
    
    # Render 3D
    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.TkDrawTriF(tri, normal[2], canvas)
        
    # Update the screen
    tK.update()
    
    
    # ThingAddRot(thing, vector)
    zp.ThingAddRot(myThing, [2, 1, 3])

