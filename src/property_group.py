'''
Copyright (C) 2023-2024 Filip Dráber
draberf@gmail.com

This file is part of Node Exporter to SVG.

    Node Exporter to SVG is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses>.
'''

import bpy

from .constants import HEADER_OPACITY, PAGES

class ExportPropertyGroup(bpy.types.AddonPreferences):
    bl_idname = __package__

    # toggle whether export should only include selected nodes
    export_selected_only: bpy.props.BoolProperty(
        name="Export Selected Only",
        description="Limit export only to selected Nodes and their links. (Exports everything if nothing is selected.)",
        default=False
    )

    # toggle whether export should exclude nodes outside viewport
    export_viewport_only: bpy.props.BoolProperty(
        name="Limit by Viewport",
        description="Only include Nodes fully inside the current viewport.",
        default=False
    )

    # use rounded corners
    rounded_corners: bpy.props.BoolProperty(
        name="Round Corners",
        description="Add round corners to elements",
        default=True
    )

    # leave background transparent
    transparent_background: bpy.props.BoolProperty(
        name="Transparent Background",
        description="Leave background transparent",
        default=True
    )

    # graphical quality of certain elements
    fidelity: bpy.props.IntProperty(
        name="Element Quality",
        description="Control the quality of complex UI widgets (2-50)",
        min=2, max=50, default=10
    )

    # use gradients for certain elements
    use_gradients: bpy.props.BoolProperty(
        name="Use Gradients",
        description="Use gradients for Color Picker and Ramp widgets",
        default=False
    )

    # use category defaults automatically
    use_theme_colors: bpy.props.BoolProperty(
        name="Use Theme colors",
        description="Use colors defined in Preferences > Themes",
        default=True
    )

    # add outline to rectangles
    rect_outline:           bpy.props.FloatProperty(
        name="Outline Thickness",
        description="Define thickness of element outlines",
        min=0, soft_max=10, default=0.3
    )
    rect_outline_color:     bpy.props.FloatVectorProperty(
        name="Outline Color",
        description="Define color of element outlines",
        subtype='COLOR_GAMMA', min=0, max=1, size=4
    )

    # text colors
    use_generic_text:       bpy.props.BoolProperty(
        name="Use generic text color",
        description="Use the same (\"Generic\") color for all Text elements",
        default=False
    )
    text_generic:           bpy.props.FloatVectorProperty(name="Generic",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    text_base:              bpy.props.FloatVectorProperty(name="Base",       subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_string:            bpy.props.FloatVectorProperty(name="String",     subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_true:      bpy.props.FloatVectorProperty(name="Bool True",  subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_false:     bpy.props.FloatVectorProperty(name="Bool False", subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_dropdown:          bpy.props.FloatVectorProperty(name="Dropdown",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_slider:            bpy.props.FloatVectorProperty(name="Slider",     subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # node element colors
    color_base:             bpy.props.FloatVectorProperty(name="Base",              subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_string_field:     bpy.props.FloatVectorProperty(name="String Field",      subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_dropdown:         bpy.props.FloatVectorProperty(name="Dropdown",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_false:       bpy.props.FloatVectorProperty(name="False",             subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_true:        bpy.props.FloatVectorProperty(name="True",              subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_checkmark:        bpy.props.FloatVectorProperty(name="Checkmark",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_field:      bpy.props.FloatVectorProperty(name="Value",             subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_progress:   bpy.props.FloatVectorProperty(name="Progress Bar",      subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_axis_x:           bpy.props.FloatVectorProperty(name="Axis X",            subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_y:           bpy.props.FloatVectorProperty(name="Axis Y",            subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_z:           bpy.props.FloatVectorProperty(name="Axis Z",            subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_background:       bpy.props.FloatVectorProperty(name="Background Color",  subtype='COLOR',       min=0, max=1, size=3)

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

    # socket colors
    use_generic_socket:         bpy.props.BoolProperty(
        name="Use generic socket color",
        description="Use the same (\"Generic\") color for all socket marker",
        default=False
    )

    socket_color_generic:       bpy.props.FloatVectorProperty(name="Generic",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_custom:        bpy.props.FloatVectorProperty(name="Custom",    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_value:         bpy.props.FloatVectorProperty(name="Value",     subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_int:           bpy.props.FloatVectorProperty(name="Int",       subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_boolean:       bpy.props.FloatVectorProperty(name="Boolean",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_vector:        bpy.props.FloatVectorProperty(name="Vector",    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_rotation:      bpy.props.FloatVectorProperty(name="Rotation",  subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_menu:          bpy.props.FloatVectorProperty(name="Menu",      subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_string:        bpy.props.FloatVectorProperty(name="String",    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_rgba:          bpy.props.FloatVectorProperty(name="RGBa"  ,    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_shader:        bpy.props.FloatVectorProperty(name="Shader",    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_object:        bpy.props.FloatVectorProperty(name="Object",    subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_image:         bpy.props.FloatVectorProperty(name="Image",     subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_geometry:      bpy.props.FloatVectorProperty(name="Geometry",  subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_collection:    bpy.props.FloatVectorProperty(name="Collection",subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_texture:       bpy.props.FloatVectorProperty(name="Texture",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    socket_color_material:      bpy.props.FloatVectorProperty(name="Material",  subtype='COLOR_GAMMA', min=0, max=1, size=3)


    # colors of nodes
    node_color: bpy.props.FloatVectorProperty(name="Base Color", subtype='COLOR', min=0, max=1)


    # config file mode
    config_mode:        bpy.props.EnumProperty(
        items=[
            ('SAVE', "Save", "Export a configuration file"),
            ('LOAD', "Load", "Import a configuration file"),
        ],
        description="Choose between saving and loading a configuration file",
        name="Mode", default='LOAD')
    
    config_save_path:   bpy.props.StringProperty(
        name = "Save to",
        description = "Target file name to save configuration to",
        subtype='FILE_PATH'
    )
    config_load_path:   bpy.props.StringProperty(
        name = "Load from",
        description = "File name to load configuration from",
        subtype='FILE_PATH'
    )

    # target file to export into
    output: bpy.props.StringProperty(
        name = "Output",
        description = "Target file name to export graph to",
        subtype='FILE_PATH'
    )

    # export size properties

    export_dimensions_enum: bpy.props.EnumProperty(
        items=[
            ('DEFAULT', "Default", "Use default export size"),
            ('CUSTOM', "Custom", "Specify custom width or height"),
            ('PAGE', "Page", "Fit output to page"),
        ],
        description = "Specify size of the output",
        name = "Size", default='DEFAULT'
    )

    export_dim_custom_select: bpy.props.EnumProperty(
        items=[
            ('WIDTH', "Width", "Define the output width"),
            ('HEIGHT', "Height", "Define the output height")
        ],
        description = "Choose whether the output's height or width is specified",
        name = "Output dimension", default='WIDTH'
    )

    export_dim_custom_width: bpy.props.IntProperty(
        name="Width",
        description="Width of the output (in pixels)",
        subtype='UNSIGNED'
    )

    export_dim_custom_height: bpy.props.IntProperty(
        name="Height",
        description="Height of the output (in pixels)",
        subtype='UNSIGNED'
    )

    export_dim_page_margins: bpy.props.FloatProperty(
        name="Margins",
        description="Reduce output size by proportion of page dimensions",
        subtype="PERCENTAGE",
        default=28, soft_min=0, soft_max=100
    )

    export_dim_page_landscape: bpy.props.BoolProperty(
        name="Landscape",
        description="Use landscape mode instead of portrait"
    )

    export_dim_page_type: bpy.props.EnumProperty(
        name="Format",
        description="Choose page format",
        items=[
            (page, page, "") for page in PAGES.keys()
        ], default='A4'
    )

    # target file to export into
    import_file: bpy.props.StringProperty(
        name = "Import",
        description = "Source file of Node graph",
        subtype='FILE_PATH'
    )