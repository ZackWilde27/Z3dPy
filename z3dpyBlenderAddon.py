bl_info = {
    "name": "Z3dPy Blender Addon",
    "blender": (2, 80, 0),
    "category": "Editor"
}

import bpy

z3dpy_scriptName = "z3dpyScript"

def RadsToAngle(rads):
    return rads * 57.2958

def ConvertLoc(loc):
    return "[" + str(round(loc[0], 3)) + ", " + str(round(-loc[2], 3)) + ", " + str(round(loc[1], 3)) + "]"

def ListConvertLoc(loc):
    return (round(loc[0], 3), round(-loc[2], 3), round(loc[1], 3))

def ListConvertRot(rot):
    return (round(RadsToAngle(rot[0]) - 90, 3), round(RadsToAngle(rot[2]), 3), round(RadsToAngle(rot[1]), 3))

def ConvertCol(col):
    return "[" + str(round(col.r * 255)) + ", " + str(round(col.g * 255)) + ", " + str(round(col.b * 255)) + "]"

class Z3dPyDocs(bpy.types.Operator):
    """Z3dPy map editor documentation"""
    bl_idname = "z3dpy.docs"
    bl_label = "Documentation"

    def execute(self, context):
        bpy.ops.wm.url_open(url="https://github.com/ZackWilde27/Z3dPy/wiki/Z3dPy-Map-Editor#Using")
        return { 'FINISHED' }

class Z3dPyExportMeshes(bpy.types.Operator):
    """For all meshes, reset the transform, export as OBJ, then move it back."""
    bl_idname = "z3dpy.export"
    bl_label = "Export Meshes"

    def execute(self, context):
        for object in bpy.data.objects:
            if object.type == 'MESH':
                if object.parent != None:
                    tLoc = (object.parent.location.x, object.parent.location.y, object.parent.location.z)
                    tRot = (object.parent.rotation_euler.x, object.parent.rotation_euler.y, object.parent.rotation_euler.z)
                    object.parent.location = (0, 0, 0)
                    object.parent.rotation_euler = (0, 0, 0)

                mLoc = (object.location.x, object.location.y, object.location.z)
                mRot = (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z)
                object.location = (0, 0, 0)
                object.rotation_euler = (0, 0, 0)
                object.select_set(True)
                try:
                    bpy.ops.export_scene.obj(filepath=bpy.path.abspath("//mesh/" + object.name + ".obj"), use_selection=True, group_by_material=True, axis_forward='Z', axis_up='-Y')
                except:
                    bpy.ops.file.directory_new(bpy.path.abspath("//mesh"), True)
                    bpy.ops.export_scene.obj(filepath=bpy.path.abspath("//mesh/" + object.name + ".obj"), use_selection=True, group_by_material=True, axis_forward='Z', axis_up='-Y')
                    
                object.location = mLoc
                object.rotation_euler = mRot
                if object.parent != None:
                    object.parent.location = tLoc
                    object.parent.rotation_euler = tRot

                object.select_set(False)
                
        return { 'FINISHED' }

class Z3dPyRefresh(bpy.types.Operator):
    """Write changes to script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "z3dpy.refresh_script"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Refresh Script"         # Display name in the interface.

    def execute(self, context):
        
        if z3dpy_scriptName not in bpy.data.texts:
            bpy.data.texts.new(z3dpy_scriptName)
        
        bpy.data.texts[z3dpy_scriptName].clear()
        
        bpy.data.texts[z3dpy_scriptName].write("import z3dpy as zp\n")    
        
        fov = round(RadsToAngle(bpy.data.cameras[0].angle))
        resX = bpy.data.scenes["Scene"].render.resolution_x
        resY = bpy.data.scenes["Scene"].render.resolution_y
        
        if fov != 90 or resY/resX != 9/16:
            bpy.data.texts[z3dpy_scriptName].write("zp.FindHowVars(" + str(fov) +", " + str(bpy.data.scenes["Scene"].render.resolution_y) + "/" + str(bpy.data.scenes["Scene"].render.resolution_x) + "))\n")
            

        cameras = ""
        mbuffer = []
        meshes = ""
        tbuffer = []
        things = ""
        lights = ""
        realname = ""
        for object in bpy.data.objects:
            match object.type:
                case 'CAMERA':
                    cameras += object.name + " = zp.Cam(" + ConvertLoc(object.location) + ")\n"
                case 'MESH':
                    mbuffer.append(object.name)
                    meshes += object.name + " = zp.LoadMesh(\"filename.obj\""
                    if object.location.x + object.location.y + object.location.z != 0:
                        meshes += " [" + str(object.location.x) + ", " + str(object.location.z) + ", " + str(object.location.y) + "]"
                    meshes += ")\n"
                case 'EMPTY':
                    if object.name != "z3dpy_axis":
                        tbuffer.append(object.name)
                case 'LIGHT':
                    if object.data.type == 'SUN':
                        lights += object.name + " = zp.Light_Sun(" + str(ListConvertRot(object.rotation_euler)) + ", " + str(object.data.energy / 300) + ", 0, " + ConvertCol(object.data.color) + ")\n"
                    else:
                        radius = object.data.cutoff_distance if object.data.use_custom_distance else (object.data.energy / 2.5)
                        lights += object.name + " = zp.Light_Point(" + ConvertLoc(object.location) + ", " + str(round(object.data.energy / 300, 3)) + ", " +  str(round(radius, 3)) + ", " + ConvertCol(object.data.color) + ")\n"
                        
        for thing in tbuffer:
            things += thing + " = zp.Thing(["
            for msh in mbuffer:
                if bpy.data.objects[msh].parent != None and bpy.data.objects[msh].parent.name == thing:
                    things += msh + ", "
            things = things[:-2]
            things += "], " + ConvertLoc(bpy.data.objects[thing].location) + ")\n"
            
        
                
        bpy.data.texts[z3dpy_scriptName].write("# Cameras\n" + cameras + "# Meshes\n" + meshes + "# Things\n" + things + "zp.AddThings(" + str(tbuffer).replace("'", "") + ")\n# Lights\n" + lights)
        bpy.data.texts[z3dpy_scriptName].write("\nwhile True:\n\tfor tri in zp.Raster():\n\t")
    
                

        return {'FINISHED'}

class CustomMenu(bpy.types.Menu):
    bl_label = "Z3dPy"
    bl_idname = "TOPBAR_MT_z3dpy"

    def draw(self, context):
        layout = self.layout
        layout.operator("z3dpy.refresh_script")
        layout.operator("z3dpy.export")
        layout.operator("z3dpy.docs")


def draw_item(self, context):
    layout = self.layout
    layout.menu(CustomMenu.bl_idname)
  
def register():
    bpy.utils.register_class(Z3dPyRefresh)
    bpy.utils.register_class(Z3dPyDocs)
    bpy.utils.register_class(Z3dPyExportMeshes)
    bpy.utils.register_class(CustomMenu)
        
    
    bpy.types.TOPBAR_HT_upper_bar.prepend(draw_item)
    
def unregister():
    bpy.utils.unregister_class(Z3dPyRefresh)
    bpy.utils.unregister_class(Z3dPyDocs)
    bpy.utils.unregister_class(Z3dPyExportMeshes)
    bpy.utils.unregister_class(CustomMenu)
    
    
if __name__ == "__main__":
    register()
