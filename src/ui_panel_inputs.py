import bpy

from .uinodes import Converter
from .constants import IGNORE_PROPS, HEADER_OPACITY, ELEMENTS
from .categories import CATEGORY_NAMES

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"



operators = []
panels = []

class ExportPropertyGroup(bpy.types.PropertyGroup):

    # toggle whether export should only include selected nodes
    export_selected_only: bpy.props.BoolProperty(name="Export Selected Only", default=False)

    # use category defaults automatically
    use_theme_colors: bpy.props.BoolProperty(name="Use theme colors", default=False)

    # node element colors
    color_base:             bpy.props.FloatVectorProperty(name="Base",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_string_field:     bpy.props.FloatVectorProperty(name="String Field",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_false:       bpy.props.FloatVectorProperty(name="False",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_true:        bpy.props.FloatVectorProperty(name="True",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_field:      bpy.props.FloatVectorProperty(name="Value",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_progress:   bpy.props.FloatVectorProperty(name="Progress Bar",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_axis_x:           bpy.props.FloatVectorProperty(name="Axis X",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_y:           bpy.props.FloatVectorProperty(name="Axis Y",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_z:           bpy.props.FloatVectorProperty(name="Axis Z",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_text:             bpy.props.FloatVectorProperty(name="Text",          subtype='COLOR_GAMMA', min=0, max=1, size=3)

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

    # outline settings
    outline_thickness: bpy.props.FloatProperty(name="Outline Thickness", min=0, max=10)
    outline_color: bpy.props.FloatVectorProperty(name="Outline Color", subtype='COLOR', min=0, max=1)

    # target file to export into
    output: bpy.props.StringProperty(name = "Output", subtype='FILE_PATH')

def resetColors(prop_group, context):

    theme = context.preferences.themes[0]

    # theme.user_interace
    prop_group.color_base = theme.node_editor.node_backdrop
    prop_group.color_string_field = theme.user_interface.wcol_text.inner
    prop_group.color_bool_false = theme.user_interface.wcol_option.inner
    prop_group.color_bool_true = theme.user_interface.wcol_option.inner_sel
    prop_group.color_value_field = theme.user_interface.wcol_numslider.inner
    prop_group.color_value_progress = theme.user_interface.wcol_numslider.item
    prop_group.color_axis_x = theme.user_interface.axis_x
    prop_group.color_axis_y = theme.user_interface.axis_y
    prop_group.color_axis_z = theme.user_interface.axis_z
    prop_group.color_text = theme.user_interface.wcol_regular.text

    prop_group.header_opacity = HEADER_OPACITY
    for name in CATEGORY_NAMES:
        setattr(prop_group, 'header_color_'+name, getattr(theme.node_editor, name+'_node'))

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        
        print("====")


        if not (nodes := context.selected_nodes):
            print("No selected node")
            return {'CANCELLED'}

        for node in nodes:

            print(">>>", node.bl_idname, node.name)
            print("Inputs:")
            for input in node.outputs:
                print(">", input.name)
                if input.type == 'RGBA':
                    for prop in input.bl_rna.properties:
                        print(">>>", prop, prop.type, prop.subtype, "name", prop.name)
                        
            for input in node.inputs:
                print(">", input.name)
                if input.type == 'RGBA':
                    for prop in input.bl_rna.properties:
                        print(">>>", prop, prop.type, prop.subtype, "name", prop.name)



            print("Props:")
            for prop in node.bl_rna.properties:
                if prop.identifier in IGNORE_PROPS: continue
                print(">", prop, prop.type, prop.subtype, "name", prop.name)
                if prop.type == "ENUM":
                    for key, item in prop.enum_items.items():
                        print(">>", key, item.name, item.identifier)
                #for attr in prop.bl_rna.properties:
                #    print("> >", attr, ":  ", getattr(prop, attr.identifier))
    
        return {'FINISHED'}
operators.append(UIInspectOperator)

class UIExportOperator(bpy.types.Operator):
    bl_idname = "ui.exporter"
    bl_label = "Exporter"
    
    def execute(self, context):


        props = context.scene.export_svg_props

        header = "<?xml version='1.0' encoding='utf-8'?>"

        doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"


        tree = Converter(context,
                         selected_only=props.export_selected_only,
                         use_default_colors=props.use_theme_colors,
                         custom_colors={
                             name+'_node':getattr(props, 'header_color_'+name) for name in CATEGORY_NAMES
                         },
                         header_opacity=props.header_opacity
                         ).convert()
        
        with open(bpy.path.abspath(context.scene.export_svg_props.output), "w+") as f:
            f.write(header)
            f.write(doctype)
            tree.write(f, encoding='unicode')

        return {'FINISHED'}
operators.append(UIExportOperator)

class UIColorResetOperator(bpy.types.Operator):
    bl_idname = 'ui.color_reset'
    bl_label = "Reset Colors"

    def execute(self, context):

        resetColors(context.scene.export_svg_props, context)
        return {'FINISHED'}

operators.append(UIColorResetOperator)

class UIPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

class UIParentPanel(UIPanel):
    bl_category = "Export"
    bl_idname = "NODE_EDITOR_PT_export_parent"
    bl_label = "Export to SVG"

    def draw(self, context):
        ...

panels.append(UIParentPanel)

class UIColorPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_label = "Colors"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.export_svg_props

        layout.prop(props, 'use_theme_colors')


        # https://blender.stackexchange.com/questions/41387/how-to-deactivate-a-ui-element-in-an-add-on
        for color_name in ['color_'+elem for elem in ELEMENTS]+['header_color_'+name for name in CATEGORY_NAMES]+['header_opacity']:
            row = layout.row()
            row.prop(props, color_name)
            row.enabled = not props.use_theme_colors

        layout.operator(
            operator='ui.color_reset',
            text='Reset Colors'
        )

panels.append(UIColorPanel)


class UIInspectPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_label = "Export"

    def draw(self, context):

        layout = self.layout
        props = context.scene.export_svg_props

        row = layout.row()
        row.label(text="Export target")

        row = layout.row()
        row.prop(props, 'export_selected_only')

        row = layout.row()
        row.prop(props, 'output', text="")

        layout.operator(
            operator='ui.exporter',
            icon='NODETREE',
            text='Export'
        )

        layout.operator(
            operator='ui.inspector',
            icon='NODE',
            text='Inspect Selected'
        )
panels.append(UIInspectPanel)
