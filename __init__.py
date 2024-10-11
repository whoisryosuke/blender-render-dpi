bl_info = {
    "name": "Render DPI",
    "description": "Helps you convert inches and DPI dimensions to Blender's pixel size.",
    "author": "whoisryosuke",
    "version": (0, 0, 2),
    "blender": (2, 80, 0), # not sure if this is right
    "location": "Properties > Output",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/whoisryosuke/blender-render-dpi",
    "tracker_url": "",
    "category": "Development"
}


from PIL import Image
import bpy
import os
from datetime import datetime
from bpy.app.handlers import persistent
from bpy.props import (IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       )
from bpy.types import (
                       PropertyGroup,
                       )
from bpy.path import basename

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
        description = "DPI (dots per inch) or resolution of image",
        default = 300,
        min = 1,
        max = 1000
        )
    should_auto_save: BoolProperty(
        name = "Auto Save",
        description = "Auto saves image after every render with correct dimensions and DPI.",
        default = False,
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
        row.prop(dpi_props, "should_auto_save")

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

@persistent
def auto_save_render(scene):
    print("auto saving...")
    dpi_props = scene.dpi_props
    width = dpi_props.width
    height = dpi_props.height
    dpi = dpi_props.dpi
    should_auto_save = dpi_props.should_auto_save

    if not should_auto_save or not bpy.data.filepath:
        return

    render = scene.render
    extension = render.image_settings.file_format

    # Generate a file path
    # We pick the same folder as current Blender file and save inside a `/renders` folder
    # And we use the Blender filename as the basis for the image name
    blender_filepath = bpy.data.filepath
    blender_file_dir = os.path.dirname(blender_filepath)
    image_dir = os.path.join(blender_file_dir, "renders")
    image_base_name = basename(bpy.data.filepath).rpartition('.')[0]
    
    # We generate the current date to make a unique identifier for file
    now = datetime.now() # current date and time
    date_time = now.strftime("%m-%d-%Y-%H-%M-%S")

    # We also append the file info for quick ref
    image_size_info = str(round(width)) + "x" + str(round(height)) + "in-" + str(dpi) + "dpi"

    # Merge them all together
    image_name = image_base_name + "_" + image_size_info + "_" + date_time + "." + extension
    image_final_path = os.path.join(image_dir, image_name)

    print("blender_filepath", blender_filepath)
    print("blender_file_dir", blender_file_dir)
    print("image path", image_final_path)

    # Save image
    image = bpy.data.images['Render Result']
    try:
        image.save_render(image_final_path, scene=None)
    except:
        print("Couldn't save")

    # Resave image as proper DPI
    with Image.open(image_final_path) as img:
        img.save(image_final_path, dpi=(dpi,dpi))



# Load/unload addon into Blender
classes = (
    GI_SceneProperties,
    DPI_SETTINGS_sync_size,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dpi_props = PointerProperty(type=GI_SceneProperties)
    bpy.types.RENDER_PT_format.append(draw_func)
    bpy.app.handlers.render_post.append(auto_save_render)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.RENDER_PT_format.remove(draw_func)
    bpy.app.handlers.render_post.remove(auto_save_render)


if __name__ == "__main__":
    register()
