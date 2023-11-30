# Legend:
# - Parameters marked with a * are optional
# - Most parameters have a letter denoting type - capitals mean normalized.

import pyglet
import z3dpy as zp

#zp.Fast()

# Initialize Pyglet
screen = pyglet.window.Window()
myBatch = pyglet.graphics.Batch()

# Negating FOV to fix the picture being upside down
zp.FindHowVars(-90, -(screen.height/screen.width))

# Create a camera to render from
# Cam(vPos)
myCamera = zp.Cam([0, 0, 0], screen.width, screen.height)

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

myMesh.shader = zp.SHADER_SIMPLE

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

# Raster Loop
@screen.event
def on_draw():

    # Render 3D
    triangles = [pyglet.shapes.Triangle(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], color=zp.VectorFloor(zp.TriGetColour(tri)), batch=myBatch) for tri in zp.RasterThings([myThing])]

    # Clear the screen
    screen.clear()
    
    # Update the screen
    myBatch.draw()
    # ThingAddRot(thing, vector)
    myThing.rotation = zp.VectorAdd(myThing.rotation, [2, 2, 2])

pyglet.app.run()
