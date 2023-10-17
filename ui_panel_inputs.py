import bpy
import json

# from node_to_svg import nodesToSvg

import xml.etree.ElementTree as ET

def nodesToSvg(nodes: bpy.types.Node):

    header = "<?xml version='1.0' encoding='utf-8'?>"

    doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

    svg = ET.Element('svg', width="20cm", height="8cm", version="1.1", xmlns="http://www.w3.org/2000/svg")
    for i, node in enumerate(nodes):
        g = ET.Element('g', id=f"{node.name}_{i}")
        text = ET.Element('text', x="1cm", y=f"{1+2*i}cm")
        text.text = node.name
        g.append(text)
        svg.append(g)
    svg_string = ET.tostring(svg, encoding='unicode')

    print('\n'.join([header, doctype, svg_string]))

if __name__=="__main__":

    nodesToSvg([])

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        # current material is accessed through bpy.context.material
        # presumably this always matches to Nodes on screen
        print(" === ")

        SELECT_ALL = True

        nodes = bpy.context.selected_nodes

        if SELECT_ALL:
            bpy.ops.node.select_all(action='INVERT')
            nodes += bpy.context.selected_nodes
            bpy.ops.node.select_all(action='INVERT')
        
        nodesToSvg(nodes)
        
        return {'FINISHED'}

class UIInspectPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Inspect"
    bl_idname = "NODE_EDITOR_PT_inspector"
    bl_label = "Inspector"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Inspect")
        box.operator(
            operator='ui.inspector',
            icon='NODETREE',
            text='Inspect'
        )

bpy.utils.register_class(UIInspectOperator)
bpy.utils.register_class(UIInspectPanel)
