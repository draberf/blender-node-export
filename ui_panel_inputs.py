import bpy
import json

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        # current material is accessed through bpy.context.material
        # presumably this always matches to Nodes on screen
        print(" === ")
        preselected = bpy.context.selected_nodes
        bpy.ops.node.select_all(action='INVERT')
        nodes = preselected + bpy.context.selected_nodes
        bpy.ops.node.select_all(action='INVERT')
        for node in nodes:
            if (label := node.label) != "":
                print(label)
            else:
                print(node.name)
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
