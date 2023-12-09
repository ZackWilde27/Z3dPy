# Legend:
# - Parameters marked with a * are optional
# - Most parameters have a letter denoting type - capitals mean normalized.

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Triangle
from kivy.uix.label import Label
from kivy.clock import Clock
import z3dpy as zp

zp.Fast()

# Initialize Kivy
Window.size=(1280, 720)
class MyWidget(kivy.uix.widget.Widget):
    loop_thread = None

    # Is this the best way to do it? I'm relatively new to Kivy
    def callback_to_loop(self, dt):
        delta = zp.GetDelta()
        self.canvas.clear()
        with self.canvas:
            for tri in zp.RenderThings([myThing]):
                col = zp.VectorMulF(zp.TriGetColour(tri), 0.0039)
                Color(col[0], col[1], col[2], 1, mode='rgba')
                Triangle(points=(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]))
                myThing.rotation = zp.VectorAdd(myThing.rotation, [0.1, 0.1, 0.1])

    def __init__(self, **kwargs):
        super(MyWidget, self).__init__(**kwargs)
        self.loop_thread = Clock.schedule_interval(self.callback_to_loop, 0)
    
    
            
        

class MainApp(App):
    def build(self):
        return MyWidget()

# Just like Pyglet, the screen needs to be flipped for Kivy
zp.FindHowVars(-90, -(9/16))

# Create a camera to render from, and give it the dimensions of the previously set up screen
# Cam(vPos, screenWidth, screenHeight)
myCamera = zp.Cam([0, 0, 0], 1280, 720)

# Load a mesh to draw
# LoadMesh(filename, *vPos, *VScale)
myMesh = zp.LoadMesh("z3dpy/mesh/z3dpy.obj")

myMesh.material = zp.MATERIAL_SIMPLE

# Multiple meshes can be grouped into a thing
# Thing(meshes, vPos)
myThing = zp.Thing([myMesh], [0, 0, 3])

# Since the camera isn't going to move, we only need to set it once.
zp.SetInternalCam(myCamera)

if __name__ == '__main__':
    MainApp().run()
