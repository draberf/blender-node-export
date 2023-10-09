import bpy
import pickle

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        # current material is accessed through bpy.context.material
        # presumably this always matches to Nodes on screen
        nodes = bpy.context.material.node_tree.nodes
        node = nodes[-1]
        print("name", node.name)
        print("bl_label", node.bl_label)
        print("bl_idname", node.bl_idname)
        print("label", node.label)
        return {'FINISHED'}
    
class UIPickleNodeOperator(bpy.types.Operator):
    bl_idname = "ui.pickler"
    bl_label = "Pickler"

    def execute(self, context):
        node = bpy.context.material.node_tree.nodes[-1]
        with open("node_export.pkl", 'wb') as f:
            pickle.dump(node, f)
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
        self.layout.label(text="Inspect")
        self.layout.operator(
            operator='ui.inspector',
            icon='NODETREE',
            text='Inspect'
        )

bpy.utils.register_class(UIInspectOperator)
bpy.utils.register_class(UIInspectPanel)
