bl_info = {
    "name": "Render DPI",
    "description": "Helps you convert inches and DPI dimensions to Blender's pixel size. This doesn't change image metadata (yet).",
    "author": "whoisryosuke",
    "version": (0, 0, 1),
    "blender": (2, 80, 0), # not sure if this is right
    "location": "Properties > Output",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/whoisryosuke/blender-render-dpi",
    "tracker_url": "",
    "category": "Development"
}


import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (
                       PropertyGroup,
                       )

# ------------------------------------------------------------------------
#    Utility Functions
# ------------------------------------------------------------------------

# 1 inch = 2.54 cm
def convert_inch_to_cm(inches):
    return round(inches * 2.54, 1)

# DPI calculation is cm = widthPixels * (2.54 / dpi)
# But this requires knowing size in pixels, so we solve for left side in this function
def convert_dpi_to_px(centimeters, dpi):
    return centimeters / (2.54 / dpi)

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------


# UI properties
class GI_SceneProperties(PropertyGroup):
    width: FloatProperty(
        name = "Width",
        description = "Width in inches",
        default = 1.0,
        min = 0.01,
        max = 1000.0
        )
    height: FloatProperty(
        name = "Height",
        description = "Height in inches",
        default = 1.0,
        min = 0.01,
        max = 1000.0
        )
    dpi: IntProperty(
        name = "DPI",
        description = "Height in inches",
        default = 72,
        min = 1,
        max = 1000
        )

# UI Panel
class GI_DPIPanel(bpy.types.Panel):
    """Creates a Panel in the render output window"""
    bl_category = "DPI Panel"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        dpi_props = scene.dpi_props

        layout.label(text="DPI Settings")
        row = layout.row()
        row.prop(dpi_props, "width")
        row.prop(dpi_props, "height")
        row = layout.row()
        row.prop(dpi_props, "dpi")

        row = layout.row()
        row.operator("dpi_settings.sync_size")

class DPI_SETTINGS_sync_size(bpy.types.Operator):
    bl_idname = "dpi_settings.sync_size"
    bl_label = "Sync Size with Pixels"
    bl_description = "Converts your image size to pixels and updates the Blender Render Output settings"
    bl_options = {"UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene
        dpi_props = scene.dpi_props

        # Convert Inches to Centimeters (necessary to DPI formula)
        width_cm = convert_inch_to_cm(dpi_props.width)
        height_cm = convert_inch_to_cm(dpi_props.height)

        # Get DPI value for each side
        width_px = convert_dpi_to_px(width_cm)
        height_px = convert_dpi_to_px(height_cm)


        bpy.context.scene.render.resolution_x = width_px;
        bpy.context.scene.render.resolution_y = height_px;
        return {"FINISHED"}

# Load/unload addon into Blender
classes = (
    GI_SceneProperties,
    GI_DPIPanel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dpi_props = PointerProperty(type=GI_SceneProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
