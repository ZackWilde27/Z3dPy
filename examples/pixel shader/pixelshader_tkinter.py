import z3dpy as zp
import tkinter as tk
import time
import keyboard

currentTime = time.time()

res = "n"

tK = tk.Tk()

canvas = tk.Canvas(width=640, height=480, background="black")
zp.screenSize = (640, 480)
canvas.pack()

zp.FindHowVars(90, 3/4)

zp.SetHowVars(0.7499994966812669, 0.9999993845600877)

# z3dpy.Cam(vPos)
myCamera = zp.Cam([0, 0, -4])

# z3dpy.LoadMesh(filename, *vPos, *VScale)
# z3dpy.Thing(meshList, vPos)
plane = zp.Thing([zp.LoadMesh("mesh/uvpln.obj")], [0, 0, 3])

zp.ThingSetRot(plane, [90, 0, 0])

zp.AddThing(plane)

cooldown = 0
turnSpeed = 2

while True:

    # Input
    if keyboard.is_pressed("SHIFT"):
        speed = 0.05
    else:
        speed = 0.25

    if keyboard.is_pressed("w"):
        zp.ThingAddPosZ(plane, speed)
    if keyboard.is_pressed("s"):
        zp.ThingAddPosZ(plane, -speed)
    if keyboard.is_pressed("a"):
        zp.ThingAddPosX(plane, -speed)
    if keyboard.is_pressed("d"):
        zp.ThingAddPosX(plane, speed)

    if keyboard.is_pressed("LEFT"):
        zp.ThingAddRot(plane, [0, -turnSpeed, 0])
    if keyboard.is_pressed("RIGHT"):
        zp.ThingAddRot(plane, [0, turnSpeed, 0])

    zp.SetInternalCam(myCamera)

    canvas.delete("all")

    for tri in zp.Raster():
        zp.TkPixelShader(tri, canvas)
        
    tK.update()
    
    zp.ThingAddRot(plane, [0, 0, 5])

    # FPS Calc
    delta = time.time() - currentTime
    tK.title(str(int(1 / max(delta, 0.01))) + " FPS")
    currentTime = time.time()
