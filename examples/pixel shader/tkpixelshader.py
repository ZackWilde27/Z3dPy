import z3dpy as zp
import tkinter as tk

res = input("Half resolution? (y/n): ")

tK = tk.Tk()

if res == "y":
    canvas = zp.TkScreen(320, 240, "black", tk)
else:
    canvas = zp.TkScreen(640, 480, "black", tk)

zp.FindHowVars(90, 3/4)

zp.SetHowVars(0.7499994966812669, 0.9999993845600877)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Cam(0, 0, -4)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
plane = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], 0, 0, 3)

zp.ThingSetRot(plane, [90, 0, 0])

zp.AddThing(plane)

while True:

    zp.SetInternalCam(myCamera)

    for tri in zp.Raster():
        zp.TkPixelShader(tri, canvas)
        
    tK.update()
    canvas.delete("all")

    zp.ThingAddRot(plane, [0, 0, 5])