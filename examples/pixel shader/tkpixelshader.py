import z3dpy as zp
import tkinter as tk

tK = tk.Tk()
canvas = tk.Canvas(width=320, height=240, background="black")
canvas.pack()

zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Cam(0, 0, -4, 320, 240)

# z3dpy.LoadMesh(filename, x, y, z)
# z3dpy.Thing(meshList, x, y, z)
zack = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], 0, 0, 3)

zp.ThingSetRot(zack, [90, 0, 0])

zp.AddThing(zack)

while True:

    zp.SetInternalCam(myCamera)

    for tri in zp.Raster():
        zp.TkPixelShader(tri, canvas)
        
    tK.update()
    canvas.delete("all")

    zp.ThingAddRot(zack, [0, 0, 5])
