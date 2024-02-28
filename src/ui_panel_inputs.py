import bpy
import importlib

# unncessary later
import inspect
import xml.etree.ElementTree as ET


from . import uinodes
importlib.reload(uinodes)
from .uinodes import UINodeTree

from .constants import DEFAULT_PROPERTIES

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        
        print("====")

        print(bpy.types.UILayout)
        return {'FINISHED'}


        if not (nodes := context.selected_nodes):
            print("No selected node")
            return {'CANCELLED'}

        for node in nodes:

            print(node)
            print(dir(node.bl_rna))
            print(node.node_tree.name)
            continue

            print("Sockets:")
            for input in node.inputs:
                print(input.name + " " + input.type, [hex(round(val*255)) for val in input.draw_color(context, node)[:3]])
            print("Props:")
            for prop in node.bl_rna.properties[DEFAULT_PROPERTIES:]:
                print(prop.name + " " + prop.type + " " + prop.subtype)
                if prop.name == "Type": print(prop.type)
    
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

        nodetree = context.space_data.node_tree


        header = "<?xml version='1.0' encoding='utf-8'?>"

        doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"


        tree = ET.ElementTree(UINodeTree(nodetree, context).svg())
        
            
        with open(TARGET, "w") as f:
            f.write(header)
            f.write(doctype)
            tree.write(f, encoding='unicode')

        return {'FINISHED'}

class UIInspectPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Expoprt"
    bl_idname = "NODE_EDITOR_PT_exporter"
    bl_label = "Exporter"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout

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

if __name__=="__main__":
    pass