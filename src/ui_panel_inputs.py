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
        links = []
        for link in nodetree.links:
            print("From Socket ID", link.from_socket.as_pointer())
            print("  To Socket ID", link.to_socket.as_pointer())
            links.append((link.from_socket.as_pointer(), link.to_socket.as_pointer()))

        for node in nodetree.nodes:
            print(node)
            break
            for socketname, socket in node.outputs.items():
                print("OUT:", "socketname", socketname,
                      "bl_idname", socket.bl_idname,
                      "bl_label", socket.bl_label,
                      "description", socket.description,
                      "label", socket.label,
                      "name", socket.name,
                      "id", socket.id_data)
                for link_from, link_to in links:
                    if socket.as_pointer() == link_from:
                        print(">> Connects to", link_to)
            for socketname, socket in node.inputs.items():
                print("IN:", "socketname", socketname,
                      "bl_idname", socket.bl_idname,
                      "bl_label", socket.bl_label,
                      "description", socket.description,
                      "label", socket.label,
                      "name", socket.name,
                      "id", socket.id_data)
                    

        node_to_svg.nodesToSvg(nodetree.nodes)
        
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