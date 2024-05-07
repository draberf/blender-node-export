import bpy

from .constants import HEADER_OPACITY

class ExportPropertyGroup(bpy.types.AddonPreferences):
    bl_idname = __package__

    # toggle whether export should only include selected nodes
    export_selected_only: bpy.props.BoolProperty(name="Export Selected Only", default=False)

    # use rounded corners
    rounded_corners: bpy.props.BoolProperty(name="Rounded Corners", default=True)

    # graphical quality of certain elements
    fidelity: bpy.props.IntProperty(name="Element Fidelity", min=0, max=50, default=10)

    # use gradients for certain elements
    use_gradients: bpy.props.BoolProperty(name="Use Gradients", default=False)

    # use category defaults automatically
    use_theme_colors: bpy.props.BoolProperty(name="Use theme colors", default=True)

    # add outline to rectangles
    rect_outline:           bpy.props.FloatProperty(name="Outline Thickness", min=0, soft_max=10, default=0.3)
    rect_outline_color:     bpy.props.FloatVectorProperty(name="Outline Color", subtype='COLOR_GAMMA', min=0, max=1, size=4)

    # text colors
    use_generic_text:       bpy.props.BoolProperty(name="Use Generic Color", default=False)
    text_generic:           bpy.props.FloatVectorProperty(name="Generic",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    text_base:              bpy.props.FloatVectorProperty(name="Base",       subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_string:            bpy.props.FloatVectorProperty(name="String",     subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_true:      bpy.props.FloatVectorProperty(name="Bool True",  subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_false:     bpy.props.FloatVectorProperty(name="Bool False", subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_dropdown:          bpy.props.FloatVectorProperty(name="Dropdown",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_slider:            bpy.props.FloatVectorProperty(name="Slider",     subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # node element colors
    color_base:             bpy.props.FloatVectorProperty(name="Base",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_string_field:     bpy.props.FloatVectorProperty(name="String Field",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_dropdown:         bpy.props.FloatVectorProperty(name="Dropdown",      subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_false:       bpy.props.FloatVectorProperty(name="False",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_true:        bpy.props.FloatVectorProperty(name="True",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_checkmark:        bpy.props.FloatVectorProperty(name="Checkmark",     subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_field:      bpy.props.FloatVectorProperty(name="Value",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_progress:   bpy.props.FloatVectorProperty(name="Progress Bar",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_axis_x:           bpy.props.FloatVectorProperty(name="Axis X",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_y:           bpy.props.FloatVectorProperty(name="Axis Y",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_z:           bpy.props.FloatVectorProperty(name="Axis Z",        subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # colors of node headers
    header_color_input:         bpy.props.FloatVectorProperty(name="Input",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_output:        bpy.props.FloatVectorProperty(name="Output",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_shader:        bpy.props.FloatVectorProperty(name="Shader",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_texture:       bpy.props.FloatVectorProperty(name="Texture",   subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_color:         bpy.props.FloatVectorProperty(name="Color",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_vector:        bpy.props.FloatVectorProperty(name="Vector",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_converter:     bpy.props.FloatVectorProperty(name="Converter", subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_script:        bpy.props.FloatVectorProperty(name="Script",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_filter:        bpy.props.FloatVectorProperty(name="Filter",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_matte:         bpy.props.FloatVectorProperty(name="Matte",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_distor:        bpy.props.FloatVectorProperty(name="Distort",   subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_layout:        bpy.props.FloatVectorProperty(name="Layout",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_attribute:     bpy.props.FloatVectorProperty(name="Attribute", subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_geometry:      bpy.props.FloatVectorProperty(name="Geometry",  subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_group:         bpy.props.FloatVectorProperty(name="Group",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_layout:        bpy.props.FloatVectorProperty(name="Layout",    subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # opacity of header -- ADD HOVER INFO TO THIS
    header_opacity: bpy.props.FloatProperty(name="Header Opacity", subtype='PERCENTAGE', min=0, max=100, default=HEADER_OPACITY)

    # colors of nodes
    node_color: bpy.props.FloatVectorProperty(name="Base Color", subtype='COLOR', min=0, max=1)

    # config file mode
    config_mode:        bpy.props.EnumProperty(items=[
            ('SAVE', "Save", "Export a configuration file"),
            ('LOAD', "Load", "Import a configuration file"),
        ], name="Mode", default='LOAD')
    
    config_save_path:   bpy.props.StringProperty(name = "Save to", subtype='FILE_PATH')
    config_load_path:   bpy.props.StringProperty(name = "Load from", subtype='FILE_PATH')

    # target file to export into
    output: bpy.props.StringProperty(name = "Output", subtype='FILE_PATH')