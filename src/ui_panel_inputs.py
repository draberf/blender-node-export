import bpy
import importlib


from . import uinodes
importlib.reload(uinodes)
from .uinodes import Converter

from .constants import IGNORE_PROPS

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"


class ExportPropertyGroup(bpy.types.PropertyGroup):

    
    export_selected_only: bpy.props.BoolProperty(name="Export Selected Only", default=False)
    output: bpy.props.StringProperty(name = "Output", subtype='FILE_PATH')



class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        
        print("====")

        props = context.scene.export_svg_props

        props.export_selected_only = False

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


        tree = Converter(context, selected_only=props.export_selected_only).convert()
        
        with open(bpy.path.abspath(context.scene.export_svg_props.output), "w+") as f:
            f.write(header)
            f.write(doctype)
            tree.write(f, encoding='unicode')

        return {'FINISHED'}

class UIInspectPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Export"
    bl_idname = "NODE_EDITOR_PT_exporter"
    bl_label = "Exporter"


    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):

        layout = self.layout
        props = context.scene.export_svg_props

        row = layout.row()
        row.prop(props, 'export_selected_only')

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