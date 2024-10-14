bl_info = {
    "name": "Render DPI Plus",
    "description": "Helps you convert inches, cm, mm, m and DPI dimensions to Blender's pixel size.",
    "author": "whoisryosuke, juliushilker",
    "version": (0, 0, 3),
    "blender": (4, 20, 0), # not sure if this is right
    "location": "Properties > Output",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/whoisryosuke/blender-render-dpi",
    "tracker_url": "",
    "category": "Development"
}


# ------------------------------------------------------------------------
#    ADDED by Julius Hilker
#    - Presets
#    - Bleed Margin
#    - Select Unit
# ------------------------------------------------------------------------


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
from bpy.types import Operator, Menu
from bl_operators.presets import AddPresetBase
import shutil

# ------------------------------------------------------------------------
#    Utility Functions
# ------------------------------------------------------------------------

# 1 inch = 2.54 cm

def dpi_preset_create_default_presets(basepath):
    
    builtin_presets = {
        "A0" : {"width":841,"height":1189},
        "A1" : {"width":420,"height":594},
        "A2" : {"width":420,"height":594},
        "A3" : {"width":297,"height":420},
        "A4" : {"width":210,"height":297},
        "A5" : {"width":148,"height":210},
        "A6" : {"width":105,"height":148},
        "A7" : {"width":74,"height":105},
        "A8" : {"width":52,"height":74}
        }
        
    resolutions = {"print":300,"screen":72}


    for _index in builtin_presets:
        name = _index
        filepath = basepath+"\\"+name+".py"
        current = builtin_presets[_index]
        string = "import bpy \n"
        string += "props = bpy.context.scene.dpi_props \n" 
        string += "\n"
        string += "props.unit = 'mm' \n"
        string += "props.width = "+str(current["width"])+" \n"
        string += "props.height = "+str(current["height"])+" \n"

        f = open(filepath, "w")
        f.write(string)
        f.close()
        print("Make built-In preset-"+name)


def dpi_preset_folder_setup():
    # #Make sure there is a directory for presets
    dpi_preset_subdir = "dpi_settings_presets"    
    dpi_preset_directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", dpi_preset_subdir)
    dpi_preset_paths = bpy.utils.preset_paths(dpi_preset_subdir)
    
    if dpi_preset_directory not in dpi_preset_paths:
        if not os.path.exists(dpi_preset_directory):
            print("HALLO")
            os.makedirs(dpi_preset_directory)            
            dpi_preset_create_default_presets(dpi_preset_directory)
    



def convert_inch_to_cm(value: float) -> float:
    return value * 2.54

    pass

def convert_mm_to_cm(value: float) -> float:
    return value * 0.1
    pass

def convert_m_to_cm(value: float) -> float:
    return value * 0.1
    pass

def calculate_dimensions(width: float,height: float):
    
    
    scene = bpy.context.scene
    dpi_props = scene.dpi_props
    unit = dpi_props.unit
    bleed_value = 0

    if dpi_props.bleed_linked:
        bleed_value_width = dpi_props.bleed_even * 2
        bleed_value_height = dpi_props.bleed_even * 2
        
    else:
        bleed_value_width = dpi_props.bleed_left + dpi_props.bleed_right
        bleed_value_height = dpi_props.bleed_top + dpi_props.bleed_bottom
 
    width += bleed_value_width
    height += bleed_value_height

    if unit == "mm":
        bleed_value_width = convert_mm_to_cm(bleed_value_width)
        bleed_value_height = convert_mm_to_cm(bleed_value_height)
        width = convert_mm_to_cm(width)
        height = convert_mm_to_cm(height)
    elif unit== "m":
        bleed_value_width = convert_m_to_cm(bleed_value_width)
        bleed_value_height = convert_m_to_cm(bleed_value_height)
        width = convert_m_to_cm(width)
        height = convert_m_to_cm(height)
    elif unit== "inch":
        bleed_value_width = convert_inch_to_cm(bleed_value_width)
        bleed_value_height = convert_inch_to_cm(bleed_value_height)
        width = convert_inch_to_cm(width)
        height = convert_inch_to_cm(height)

    if dpi_props.set_camera_borders and dpi_props.bleed_linked:
        bleed_percentage_width = bleed_value_width / width
        bleed_percentage_height = bleed_value_height / height
        scene.safe_areas.action.x = bleed_percentage_width
        scene.safe_areas.action.y = bleed_percentage_height



    return {"width":width,"height":height}

# DPI calculation is cm = widthPixels * (2.54 / dpi)
# But this requires knowing size in pixels, so we solve for left side in this function
def convert_dpi_to_px(centimeters: float, dpi: int) -> float:
    return centimeters / (2.54 / dpi)

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------


def set_bleed(self, val):
    scene = bpy.context.scene
    dpi_props = scene.dpi_props
    print("Set BLEEE")

    if val:
        dpi_props.bleed_top = dpi_props.bleed_even
        dpi_props.bleed_left = dpi_props.bleed_even
        dpi_props.bleed_bottom = dpi_props.bleed_even
        dpi_props.bleed_right = dpi_props.bleed_even


# UI properties
class GI_SceneProperties(PropertyGroup):

    unit: EnumProperty(
        name="Unit",
        description="Select the Unit",
        items=[
        ("mm","Millimeter",""),
        ("cm","Centimeter",""),
        ("m","Meter",""),
        ("inch","Inch",""),
        ]
    )

    width: FloatProperty(
        name = "Width",
        description = "Width in selected unit",
        default = 8.5,
        min = 0.01
        )
    height: FloatProperty(
        name = "Height",
        description = "Height in selected unit",
        default = 11.0,
        min = 0.01
        )

    set_camera_borders: BoolProperty(
        name = "Sync Camera Borders",
        description = "Set bleeding as camera border",
        default = True
        )
    use_bleed: BoolProperty(
        name = "Use bleed margin",
        description = "Use bleed margin",
        default = False
        )

    bleed_linked: BoolProperty(
        name = "Even",
        description = "Activate even bleeding",
        default = True,
        update = set_bleed
        )
    bleed_even: FloatProperty(
        name = "Even Bleed",
        description = "Add bleeding to all sides (In selected unit)",
        default = 3,
        min = 0
        )
    bleed_top: FloatProperty(
        name = "Top",
        description = "Add bleeding to the top (In selected unit)",
        default = 3,
        min = 0
        )
    bleed_bottom: FloatProperty(
        name = "Bottom",
        description = "Add bleeding to the bottom (In selected unit)",
        default = 3,
        min = 0
        )
    bleed_left: FloatProperty(
        name = "Left",
        description = "Add bleeding to the left (In selected unit)",
        default = 3,
        min = 0
        )
    bleed_right: FloatProperty(
        name = "Right",
        description = "Add bleeding to the right (In selected unit)",
        default = 3,
        min = 0
        )
    dpi: IntProperty(
        name = "DPI",
        description = "DPI (dots per inch) or resolution of image",
        default = 300,
        min = 1
        )
    should_auto_save: BoolProperty(
        name = "Auto Save",
        description = "Auto saves image after every render with correct dimensions and DPI.",
        default = False,
        )



#presets

class OBJECT_MT_dpi_settings_presets(Menu):
    bl_label = "Presets"
    preset_subdir = "dpi_settings_presets"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class AddPresetDpiSettings(AddPresetBase, Operator):
    '''Add a Object Display Preset'''
    bl_idname = "scene.dpi_preset_add"
    bl_label = "Add DPI Settings Preset"
    preset_menu = "OBJECT_MT_dpi_settings_presets"

    # variable used for all preset values
    preset_defines = [
        "props = bpy.context.scene.dpi_props"
    ]

    # properties to store in the preset
    preset_values = [
        "props.unit",
        "props.width",
        "props.height",
        "props.dpi"
    ]

    # where to store the preset
    preset_subdir = "dpi_settings_presets"


# UI Panel


class DpiSettingsPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_DpiSettingsPanel"
    bl_label = "DPI Setiings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_parent_id = "RENDER_PT_format"

    # def draw(self, context):
    #     self.layout.label(text="Hello World")


    def draw(self, context):
            # self.bl_label = "My Override"
            layout = self.layout

            scene = context.scene
            dpi_props = scene.dpi_props
            unit = scene.unit_settings
            
            row = layout.row()
            row.operator("dpi_settings.sync_size",icon="CHECKMARK")
            row = layout.row()
            preset_row = row.row(align=True)
            
            preset_row.menu(OBJECT_MT_dpi_settings_presets.__name__, text=OBJECT_MT_dpi_settings_presets.bl_label)
            
            preset_row.operator(AddPresetDpiSettings.bl_idname, text="", icon='ADD')
            preset_row.operator(AddPresetDpiSettings.bl_idname, text="", icon='REMOVE').remove_active = True
            
            
            row = layout.row()
            #row.prop(unit, "system")
            #row.prop(unit, "length_unit", text="Unit")
            row.prop(dpi_props, "unit")
            row = layout.row(align=False)

            row2 = layout.column()
            x = row2.row(align=True)
            x.prop(dpi_props, "width")
            x2 = x.row(align=True)
            x2.alignment = "RIGHT"
            x2.label(text=dpi_props.unit)
            

            x = row2.row(align=True)
            x.prop(dpi_props, "height")
            x2 = x.row(align=True)
            x2.alignment = "RIGHT"
            x2.label(text=dpi_props.unit)


            
          #  row.operator(DpiSettingSwitchDimensions.bl_idname, text="",icon='FILE_REFRESH')
            
            row = layout.column()

            row.prop(dpi_props, "dpi")
            
            row.prop(dpi_props, "should_auto_save")

            


class DpiSettingsBleedPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_DpiSettingsBleedPanel"
    bl_label = "Bleed Margin"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_parent_id = "SCENE_PT_DpiSettingsPanel"

    def draw_header(self,context):

        scene = context.scene
        dpi_props = scene.dpi_props

        # Example property to display a checkbox, can be anything
        self.layout.prop(dpi_props, "use_bleed", text="")

    def draw(self, context):
            # self.bl_label = "My Override"
            layout = self.layout

            scene = context.scene
            dpi_props = scene.dpi_props

            row = layout.row()

            if not dpi_props.use_bleed:
                layout.enabled = False

           # row.prop(dpi_props, "bleed_linked")

           # bleed_col = row.column()
           # bleed_col.prop(dpi_props, "bleed_even",text="")


           # line = row.row(align=True)

            checkbox = row.row(align=True)            
            checkbox.alignment = "LEFT"
            checkbox.prop(dpi_props, "bleed_linked")

            prop = row.row(align=True)            
            prop.alignment = "EXPAND"
            prop.prop(dpi_props, "bleed_even")

            label = row.row(align=True)            
            label.alignment = "RIGHT"
            label.label(text=dpi_props.unit)



            # line.prop(dpi_props, "bleed_top")
            # label = line.row(align=True)
            # label.alignment = "RIGHT"
            # label.label(text=dpi_props.unit)



            camera_border = layout.column()

            camera_border.prop(dpi_props, "set_camera_borders",text="Set Camera Border (Only with even bleeding)")

            components = layout.column()
            
            line_top = components.row(align=True)
            line_top.prop(dpi_props, "bleed_top")
            label = line_top.row(align=True)
            label.alignment = "RIGHT"
            label.label(text=dpi_props.unit)

            line = components.row(align=True)
            line.prop(dpi_props, "bleed_left")
            label = line.row(align=True)
            label.alignment = "RIGHT"
            label.label(text=dpi_props.unit)

            line = components.row(align=True)
            line.prop(dpi_props, "bleed_right")
            label = line.row(align=True)
            label.alignment = "RIGHT"
            label.label(text=dpi_props.unit)

            line = components.row(align=True)
            line.prop(dpi_props, "bleed_bottom")
            label = line.row(align=True)
            label.alignment = "RIGHT"
            label.label(text=dpi_props.unit)



            if not dpi_props.bleed_linked:
                
                prop.enabled = False
                camera_border.enabled = False   
                
            else:  
                components.enabled = False     
                
                      
                pass
               

            

         
                    
                





class DPI_SETTINGS_sync_size(bpy.types.Operator):
    bl_idname = "dpi_settings.sync_size"
    bl_label = "Apply"
    bl_description = "Converts your image size to pixels and updates the Blender Render Output settings"
    bl_options = {"UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene
        dpi_props = scene.dpi_props

        # Convert Inches to Centimeters (necessary to DPI formula)
        dimensions = calculate_dimensions(dpi_props.width,dpi_props.height)
        #width_cm = convert_inch_to_cm(dpi_props.width,)
        #height_cm = convert_inch_to_cm(dpi_props.height)
        print(dimensions)
        # Get DPI value for each side
        dpi = dpi_props.dpi
        width_px = convert_dpi_to_px(dimensions["width"], dpi)
        height_px = convert_dpi_to_px(dimensions["height"], dpi)

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




class DpiSettingSwitchDimensions(bpy.types.Operator):
    bl_idname = "wm.dpi_settings_switch_dimensions"
    bl_label = "Switch Dimensions in DPI Settings Panel"

    def execute(self, context):
        width = bpy.context.scene.dpi_props.width
        height = bpy.context.scene.dpi_props.height

        bpy.context.scene.dpi_props.width = height
        bpy.context.scene.dpi_props.height = width
        return {'FINISHED'}


# Load/unload addon into Blender
classes = (
    GI_SceneProperties,
    DPI_SETTINGS_sync_size,
    OBJECT_MT_dpi_settings_presets,
    AddPresetDpiSettings,
    DpiSettingSwitchDimensions,
    DpiSettingsPanel,
    DpiSettingsBleedPanel
)

def register():
    dpi_preset_folder_setup()

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

    dpi_preset_subdir = "dpi_settings_presets"    
    dpi_preset_directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", dpi_preset_subdir)

    shutil.rmtree(dpi_preset_directory)



if __name__ == "__main__":
    register()
