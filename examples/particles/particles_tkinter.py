try:
    import tkinter as tk
except:
    import Tkinter as tk
import z3dpy as zp
import random as rand

tK = tk.Tk()
screen = tk.Canvas(width=1280, height=720, background="#5B8EAF")
screen.pack()

# Setting render size (should match the output screen)
zp.screenSize = (1280, 720)

# Setting FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# z3dpy.Cam(vPos)
myCamera = zp.Cam([0, 0, -15])
zp.SetInternalCam(myCamera)

# Mesh to serve as the template
myMesh = zp.LoadMesh("z3dpy/mesh/dot.obj")

# Emitter(vPos, mshTemplate, iMax, vVelocity, fLifetime, vGravity)
myEmitter = zp.Emitter([0, 0, 0], myMesh, 100, [0, 15, 0], 1.0, [4, 1, 0])

# Add to global list
zp.emitters.append(myEmitter)


# The Ground
plane = zp.LoadMesh("z3dpy/mesh/plane.obj", [0, 0, 0], [5, 5, 5])
ground = zp.Thing([plane], [0, 2, 15])
zp.AddThing(ground)

while True:

    zp.GetDelta

    ranx = (rand.random() - 0.5) * 25
    rany = (rand.random() - 0.5) * 25

    # Making snow spawn at random locations by moving the emitter
    zp.EmitterSetPos(myEmitter, [ranx, -5, rany])

    zp.HandleEmitters()

    screen.delete("all")

    for tri in zp.Raster():
        zp.TkDrawTriF(tri, 1, screen)
        
    tK.update()
