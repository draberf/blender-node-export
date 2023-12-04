import bpy
import importlib

# unncessary later
import inspect

from . import node_to_svg
importlib.reload(node_to_svg)

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        # current material is accessed through bpy.context.material
        # presumably this always matches to Nodes on screen
        print(" === ")

        SELECT_ALL = True

        #nodes = bpy.context.selected_nodes

        #if SELECT_ALL:
        #    bpy.ops.node.select_all(action='INVERT')
        #    nodes += bpy.context.selected_nodes
        #    bpy.ops.node.select_all(action='INVERT')

        nodetree = context.space_data.edit_tree

        for node in nodetree.nodes:
            print(node.bl_idname)
            for socketname, socket in node.outputs.items():
                print("OUT:", socketname, socket, socket.type)
            for socketname, socket in node.inputs.items():
                print("IN:", socketname, socket, socket.type)
                    


        # node_to_svg.nodesToSvg(nodes)
        
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

if __name__=="__main__":
    pass