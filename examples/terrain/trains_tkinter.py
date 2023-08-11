import z3dpy as zp
try:
    import tkinter as tk
except:
    import Tkinter as tk
import keyboard

# Initialize Tkinter
tK = tk.Tk()
screen = tk.Canvas(width=1280, height=720, background="black")
screen.pack()

# Set the render size, should match the output screen
zp.screenSize = (1280, 720)

# Setting FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

# Cam([x, y, z])
myCamera = zp.Cam([0, 0, -4])

# LoadMesh(filename, *vPos, *VScale)
# Thing(meshList, [x, y, z])
cube = zp.Thing([zp.LoadMesh("z3dpy/mesh/cube.obj")], [0, 0, 3])

zp.ThingSetupPhysics(cube)
zp.ThingSetupHitbox(cube, 2, 0, 1, 1)

zp.AddThing(cube)

# Creating a 15x15 train
myTrain = zp.Train(15, 15)

# Setting height at certain points
myTrain[10][7] = -15

myTrain[3][10] = 15

# Baking to create smooth hills
# BakeTrain(train, *passes, *strength, *amplitude)
zp.BakeTrain(myTrain, 5, 1.7, 1.0)

print("")
print("Controls:")
print("WASD to move around")

while True:

    screen.delete("all")

    # Input

    if keyboard.is_pressed("w"):
        zp.ThingAddPos(cube, [0, 0, 0.25])
    if keyboard.is_pressed("s"):
        zp.ThingAddPos(cube, [0, 0, -0.25])
    if keyboard.is_pressed("a"):
        zp.ThingAddPos(cube, [-0.25, 0, 0])
    if keyboard.is_pressed("d"):
        zp.ThingAddPos(cube, [0.25, 0, 0])

    # HandlePhysicsTrain(thingList, train)
    zp.HandlePhysicsTrain([cube], myTrain)

    # "Chase" the player rather than directly setting location
    zp.CamChase(myCamera, zp.VectorSub(zp.ThingGetPos(cube), [0, 2, 7]), 5)

    zp.CamSetTargetLoc(myCamera, zp.ThingGetPos(cube))

    zp.SetInternalCam(myCamera)

    for tri in zp.DebugRaster(myTrain):
        if zp.TriGetId(tri) == -1:
            zp.TkDrawTriOutl(tri, [255, 0, 0], screen)
        else:
            nrm = zp.TriGetNormal(tri)
            col = (-nrm[2] + -nrm[1]) * 0.5
            zp.TkDrawTriS(tri, col, screen)

    tK.update()
