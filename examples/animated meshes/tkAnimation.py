import z3dpy as zp
import tkinter as tk
import time

tK = tk.Tk()
# 21:9 for the cinematic feel
canvas = zp.TkScreen(1680, 720, "black", tk)
canvas.pack()

currentTime = time.time()

maxDelta = 1/33

# Setting up FOV and aspect ratio
#zp.FindHowVars(65, 9/21)
zp.SetHowVars(0.6727218910344901, 1.5696847612112212)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(-10, -2, 3)

zp.CamSetTargetDir(myCamera, [1, 0, 0])

zp.SetInternalCam(myCamera)

# z3dpy.LoadAnimMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
anim = zp.LoadAnimMesh("mesh/anim/anim.obj")
anim2 = zp.LoadAnimMesh("mesh/char2/char2.obj")


zp.MeshSetColour(anim, [0, 255, 0])
zp.MeshSetColour(anim2, [255, 0, 0])


char1 = zp.Thing([anim], 0, 0, 3)
char2 = zp.Thing([anim2], 0, 0, 3)

plane = zp.Thing([zp.LoadMesh("z3dpy/mesh/plane.obj")], 0, 0, 3)

zp.AddThing(char1, 3)
zp.AddThing(char2)
zp.AddThing(plane)

while True:
    # Manual frame limiting
    if time.time() - currentTime >= maxDelta:
        canvas.delete("all")
        
        for tri in zp.Raster():
            nrm = zp.TriGetNormal(tri)
            shade = (-nrm[0] + nrm[1]) * 0.5
            zp.TkDrawTriS(tri, shade, canvas)

        tK.update()
        currentTime = time.time()

        # Play animation
        zp.ThingIncFrames(char1)
        zp.ThingIncFrames(char2)
