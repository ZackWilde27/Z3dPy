try:
    import tkinter as tk
except:
    import Tkinter as tk
import z3dpy as zp
import random as rand

# Initialize Tkinter

tK = tk.Tk()
screen = tk.Canvas(width=1280, height=720, background="black")
screen.pack()

zp.screenSize = (1280, 720)

# Cam(vPos)
myCamera = zp.Cam([7.5, 7.5, -10])

zp.CamSetTargetDir(myCamera, [0, 0, 1])

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/cube.obj")

# Thing(meshList, vPos)
myThing = zp.Thing([myMesh], [0, 0, 0])

# Adding to render queue
zp.AddThing(myThing)

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

amount = 0

mx = 150

# Raster Loop
while True:

    # Clear the screen
    screen.delete("all")

    # Render 3D
    for tri in zp.Raster():
        normal = zp.TriGetNormal(tri)
        zp.TkDrawTriF(tri, -normal[2], screen)

    # Update the screen
    tK.update()

    if amount < mx:

        # Add another dupe, with a random location and rotation
        zp.AddDupe(myThing, [rand.random() * 15, rand.random() * 15, rand.random() * 15], [rand.random() * 270, rand.random() * 270, rand.random() * 270])
        # It's going to end up drawing more triangles, but it only needs to reference the one mesh.

        amount += 1

        
    
