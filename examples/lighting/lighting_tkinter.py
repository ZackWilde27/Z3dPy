try:
    import tkinter as tk
except:
    import Tkinter as tk

import keyboard
import z3dpy as zp
import time

print("")
print("L to switch between static and dynamic lighting")
print("WASD to move the model")

tK = tk.Tk()
screen = tk.Canvas(width=1280, height=720, background="black")
screen.pack()

zp.screenSize = (1280, 720)

currentTime = time.time()
static = False
coolDown = 0

# Camera(vPos)
myCamera = zp.Cam([0, 0, -3])

zp.CamSetTargetDir(myCamera, [0, 0, 1])
zp.SetInternalCam(myCamera)

# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/susanne.obj")

zp.MeshSetColour(myMesh, (255, 255, 255))
# Thing(meshList, vPos)
sus = zp.Thing([myMesh], [0, 0, 0])

zp.AddThing(sus)

# Light_Point(vPos, FStrength, fRadius, *vColour)
redLight = zp.Light_Point([2.25, 0, 2], 0.8, 5.0, (255, 0, 0))
blueLight = zp.Light_Point([-2.25, 0, -2], 0.8, 5.0, (100, 100, 255))

# Append to global list
zp.lights.append(redLight)
zp.lights.append(blueLight)

zp.worldColour = (0.02, 0.00, 0.02)

# BakeLighting(*things, *bExpensive)
zp.BakeLighting()

held = False
fps = 30



while True:

    screen.delete("all")

    # Input
    if keyboard.is_pressed("w"):
        zp.ThingAddPos(sus, [0, 0, 0.25])
    if keyboard.is_pressed("s"):
        zp.ThingAddPos(sus, [0, 0, -0.25])
    if keyboard.is_pressed("a"):
        zp.ThingAddPos(sus, [-0.25, 0, 0])
    if keyboard.is_pressed("d"):
        zp.ThingAddPos(sus, [0.25, 0, 0])

    # Making sure that it only flips once when you press it.
    if keyboard.is_pressed("l"):
        if not held:
            held = True
            static = not static
    else:
        held = False
    coolDown -= 1

    if static:
        for tri in zp.Raster():
            zp.TkDrawTriFLB(tri, screen)

    else:
        for tri in zp.DebugRaster():
            if zp.TriGetId(tri) == -1:
                zp.TkDrawTriOutl(tri, [255, 0, 0], screen)
            else:
                zp.TkDrawTriFL(tri, screen)

    tK.update()
    
    zp.ThingAddRot(sus, (2, 2, 2))

    fps = 1 // (time.time() - currentTime)

    # Setting the caption is much faster than printing
    tK.title(str(fps) + " FPS")
    currentTime = time.time()
