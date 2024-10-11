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
def convert_inch_to_cm(inches: float) -> float:
    return inches * 2.54

# DPI calculation is cm = widthPixels * (2.54 / dpi)
# But this requires knowing size in pixels, so we solve for left side in this function
def convert_dpi_to_px(centimeters: float, dpi: int) -> float:
    return centimeters / (2.54 / dpi)

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------


# UI properties
class GI_SceneProperties(PropertyGroup):
    width: FloatProperty(
        name = "Width (in)",
        description = "Width in inches",
        default = 8.5,
        min = 0.01,
        max = 1000.0
        )
    height: FloatProperty(
        name = "Height (in)",
        description = "Height in inches",
        default = 11.0,
        min = 0.01,
        max = 1000.0
        )
    dpi: IntProperty(
        name = "DPI",
        description = "Height in inches",
        default = 300,
        min = 1,
        max = 1000
        )

# UI Panel
def draw_func(self, context):
        # self.bl_label = "My Override"
        layout = self.layout

        scene = context.scene
        dpi_props = scene.dpi_props

        layout.label(text="DPI Settings")
        row = layout.column()
        row.prop(dpi_props, "width")
        row.prop(dpi_props, "height")
        row.prop(dpi_props, "dpi")

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
        dpi = dpi_props.dpi
        width_px = convert_dpi_to_px(width_cm, dpi)
        height_px = convert_dpi_to_px(height_cm, dpi)

        bpy.context.scene.render.resolution_x = round(width_px);
        bpy.context.scene.render.resolution_y = round(height_px);
        return {"FINISHED"}

# Load/unload addon into Blender
classes = (
    GI_SceneProperties,
    # GI_DPIPanel,
    DPI_SETTINGS_sync_size,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dpi_props = PointerProperty(type=GI_SceneProperties)
    bpy.types.RENDER_PT_format.append(draw_func)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.RENDER_PT_format.remove(draw_func)


if __name__ == "__main__":
    register()
