import z3dpy as zp
import time
import math

# Setup the Tk Screen
zp.SetupScreen(1280, 720)

# Used for FPS calculation later
currentTime = time.time()

# z3dpy.Camera(x, y, z, scrW, scrH)
myCamera = zp.Camera(0, 0, 0, 1280, 720)

zp.CameraSetFOV(myCamera, 75)

# Set the view camera
# the camera doesn't move, no need to do this per frame
zp.SetInternalCamera(myCamera)

# z3dpy.LoadMesh(filename, x, y, z)
mesh = zp.LoadMesh("engine/mesh/zack.obj", 0, 0, 0)

# z3dpy.Thing(meshList, x, y, z)
logo = zp.Thing([mesh], 0, 0, 3.5)

# Raster Loop

while True:

    # Render 3D
    for tri in zp.RasterThings([logo]):
        normal = zp.TriangleGetNormal(tri)
        zp.DrawTriangleF(tri, normal[2])
        
    # Update the screen afterwards
    zp.UpdateScreen()
    
    # z3dpy.ThingAddRot(thing, vector)
    zp.ThingAddRot(logo, [2, 1, 3])
    
    # FPS Calculation
    zp.tK.title(str(math.floor(1 / max(time.time() - currentTime, 0.01))) + " FPS")
    currentTime = time.time()

    

