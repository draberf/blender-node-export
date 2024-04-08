import bpy

from .uinodes import Converter
from .constants import IGNORE_PROPS
from .categories import CATEGORY_NAMES

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"

operators = []
panels = []

class ExportPropertyGroup(bpy.types.PropertyGroup):

    # toggle whether export should only include selected nodes
    export_selected_only: bpy.props.BoolProperty(name="Export Selected Only", default=False)

    # use category defaults automatically
    use_theme_colors: bpy.props.BoolProperty(name="Use theme colors", default=False)

    # colors of node headers
    node_colors_input: bpy.props.FloatVectorProperty(name="Input", subtype='COLOR', min=0, max=1) 
    node_colors_output: bpy.props.FloatVectorProperty(name="Output", subtype='COLOR', min=0, max=1) 
    node_colors_shader: bpy.props.FloatVectorProperty(name="Shader", subtype='COLOR', min=0, max=1) 
    node_colors_texture: bpy.props.FloatVectorProperty(name="Texture", subtype='COLOR', min=0, max=1) 
    node_colors_color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', min=0, max=1) 
    node_colors_vector: bpy.props.FloatVectorProperty(name="Vector", subtype='COLOR', min=0, max=1) 
    node_colors_converter: bpy.props.FloatVectorProperty(name="Converter", subtype='COLOR', min=0, max=1) 
    node_colors_script: bpy.props.FloatVectorProperty(name="Script", subtype='COLOR', min=0, max=1) 
    node_colors_filter: bpy.props.FloatVectorProperty(name="Filter", subtype='COLOR', min=0, max=1) 
    node_colors_matte: bpy.props.FloatVectorProperty(name="Matte", subtype='COLOR', min=0, max=1) 
    node_colors_distor: bpy.props.FloatVectorProperty(name="Distort", subtype='COLOR', min=0, max=1) 
    node_colors_layout: bpy.props.FloatVectorProperty(name="Layout", subtype='COLOR', min=0, max=1) 
    node_colors_attribute: bpy.props.FloatVectorProperty(name="Attribute", subtype='COLOR', min=0, max=1) 
    node_colors_geometry: bpy.props.FloatVectorProperty(name="Geometry", subtype='COLOR', min=0, max=1) 
    node_colors_group: bpy.props.FloatVectorProperty(name="Group", subtype='COLOR', min=0, max=1) 
    node_colors_layout: bpy.props.FloatVectorProperty(name="Layout", subtype='COLOR', min=0, max=1) 

    # opacity of header -- ADD HOVER INFO TO THIS


    # target file to export into
    output: bpy.props.StringProperty(name = "Output", subtype='FILE_PATH')

def resetColors(prop_group, context):
    for name in CATEGORY_NAMES:
        setattr(prop_group, 'node_colors_'+name, getattr(context.preferences.themes[0].node_editor, name+'_node'))

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
            #print("Sockets:")
            for input in node.inputs:
                print(">", input.name)
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

        #SELECT_ALL = True

        #nodes = bpy.context.selected_nodes

        #if SELECT_ALL:
        #    bpy.ops.node.select_all(action='INVERT')
        #    nodes += bpy.context.selected_nodes
        #    bpy.ops.node.select_all(action='INVERT')

        props = context.scene.export_svg_props

        header = "<?xml version='1.0' encoding='utf-8'?>"

        doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"


        tree = Converter(context,
                         selected_only=props.export_selected_only,
                         use_default_colors=props.use_theme_colors,
                         custom_colors={
                             name+'_node':getattr(props, 'node_colors_'+name) for name in CATEGORY_NAMES
                         }
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
        for name in CATEGORY_NAMES:
            row = layout.row()
            row.prop(props, 'node_colors_'+name)
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
