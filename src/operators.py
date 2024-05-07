import bpy, json

from .methods import getElementColors, getCategoryColors, getTextColors
from .constants import HEADER_OPACITY, IGNORE_PROPS, ELEMENTS, CATEGORY_NAMES, TEXTS
from .converter import Converter


operators = []

def resetColors(prop_group, context):

    for k, v in getElementColors(context).items():
        setattr(prop_group, k, v)

    for k, v in getCategoryColors(context).items():
        setattr(prop_group, k, v)

    for k, v in getTextColors(context).items():
        setattr(prop_group, k, v)
    
    prop_group.header_opacity = HEADER_OPACITY
    prop_group.use_generic_text = False
   

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"

    def execute(self, context):
        
        print("====")


        if not (nodes := context.selected_nodes):
            print("No selected node")
            return {'CANCELLED'}

        for node in nodes:
            print(">>>", node.bl_idname, node.name, node.dimensions)
            print("Inputs:")
            for input   in node.outputs:
                print(">", input.name, input.hide, input.enabled, input.is_unavailable)
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


        props = context.preferences.addons[__package__].preferences

        header = "<?xml version='1.0' encoding='utf-8'?>"

        doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

        tree = Converter(context).convert()
        
        with open(bpy.path.abspath(context.preferences.addons[__package__].preferences.output), "w+") as f:
            f.write(header)
            f.write(doctype)
            tree.write(f, encoding='unicode')

        return {'FINISHED'}
operators.append(UIExportOperator)

class UIColorResetOperator(bpy.types.Operator):
    bl_idname = 'ui.color_reset'
    bl_label = "Reset to Default"

    def execute(self, context):

        resetColors(context.preferences.addons[__package__].preferences, context)
        return {'FINISHED'}
operators.append(UIColorResetOperator)

def dumpProperties(group) -> dict:

    output = {
        'rounded_corners': group.rounded_corners,
        'fidelity': group.fidelity,
        'use_gradients': group.use_gradients,
        'rect_outline': group.rect_outline,
        'rect_outline_color': group.rect_outline_color[0:],
        'node_color': group.node_color[0:]
    }

    for name in ['color_'+x for x in ELEMENTS]:
        output[name] = getattr(group, name)[0:]

    for name in ['header_color_'+x for x in CATEGORY_NAMES]:
        output[name] = getattr(group, name)[0:]

    for name in ['text_'+x for x in TEXTS]:
        output[name] = getattr(group, name)[0:]

    return output

def loadProperties(json_string, group):
    
    for k, v in json.loads(json_string).items():
        setattr(group, k, v)

class UIConfigExportOperator(bpy.types.Operator):
    bl_idname = 'ui.config_export'
    bl_label = "Save"

    def execute(self, context):
        
        with open(bpy.path.abspath(context.preferences.addons[__package__].preferences.config_save_path), "w+") as f:
            dump = json.dumps(dumpProperties(context.preferences.addons[__package__].preferences), indent=4)
            f.write(dump)

            return {'FINISHED'}
operators.append(UIConfigExportOperator)

class UIConfigImportOperator(bpy.types.Operator):
    bl_idname = 'ui.config_import'
    bl_label = "Load"

    def execute(self, context):

        with open(bpy.path.abspath(context.preferences.addons[__package__].preferences.config_load_path), "r+") as f:
            loadProperties(f.read(), context.preferences.addons[__package__].preferences)

            return {'FINISHED'}
operators.append(UIConfigImportOperator)
