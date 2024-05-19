'''
Copyright (C) 2023-2024 Filip Dráber
draberf@gmail.com

This file is part of Node Exporter to SVG.

    Node Exporter to SVG is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses>.
'''

import bpy, json
import xml.etree.ElementTree as ET

from .methods import getElementColors, getCategoryColors, getTextColors, getSocketColors, colorStringToArray
from .constants import HEADER_OPACITY, IGNORE_PROPS, ELEMENTS, CATEGORY_NAMES, TEXTS, SOCKET_COLORS
from .converter import Converter


operators = []

def resetColors(prop_group, context):

    for k, v in getElementColors(context).items():
        setattr(prop_group, k, v)

    for k, v in getCategoryColors(context).items():
        setattr(prop_group, k, v)

    for k, v in getTextColors(context).items():
        setattr(prop_group, k, v)

    for k, v in getSocketColors().items():
        setattr(prop_group, k, colorStringToArray(v))
    
    prop_group.header_opacity = HEADER_OPACITY
    prop_group.use_generic_text = False
   

class UIInspectOperator(bpy.types.Operator):
    bl_idname = "ui.inspector"
    bl_label = "Inspector"
    bl_description = "Inspects selected Nodes, printing required information (based on implementation)"

    def execute(self, context):
        
        print("====")

        for obj, name in zip([context.region], ['Region']):
            print(name)
            for prop in obj.bl_rna.properties:
                print('>>', prop.name, getattr(obj, prop.identifier))


        if not (nodes := context.selected_nodes):
            print("No selected node")
            return {'CANCELLED'}

        for node in nodes:
            print(node.location)
            print(context.region.view2d.view_to_region(*node.location))

        return {'FINISHED'}


        for node in nodes:
            print("")
            print(">>>", node.bl_idname, node.name, node.dimensions)
            print("Inputs:")
            for input   in node.outputs:
                break
                print(">", input.name, input.hide, input.enabled, input.is_unavailable)
                for prop in input.bl_rna.properties:
                    print(">>", prop.name, getattr(input, prop.identifier))
                        
            for input in node.inputs:
                break
                print(">", input.name)
                for prop in input.bl_rna.properties:
                    print(">>>", prop, prop.type, prop.subtype, "name", prop.name, '    ', getattr(input, prop.identifier))



            print("Props:")
            for prop in node.bl_rna.properties:
                if prop.identifier in IGNORE_PROPS: continue
                print(">", prop, prop.type, prop.subtype, "name", prop.name)
                for attr in prop.bl_rna.properties:
                    print("> >", attr, ":  ", getattr(prop, attr.identifier))
    
        return {'FINISHED'}
operators.append(UIInspectOperator)

class UIExportOperator(bpy.types.Operator):
    bl_idname = "ui.exporter"
    bl_label = "Exporter"
    bl_description = "Exports Node graph as a vector image to target file."
    
    def execute(self, context):


        props = context.preferences.addons[__package__].preferences

        header = b"<?xml version='1.0' encoding='utf-8'?>"

        doctype = b"<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

        tree = Converter(context).convert()
        
        abs_path = bpy.path.abspath(context.preferences.addons[__package__].preferences.output)

        with open(abs_path, "wb") as f:
            f.write(header)
            f.write(doctype)
            tree.write(f)

        def draw(self, _):
            self.layout.label(text = f'Succesfully exported graph to {abs_path}.')

        context.window_manager.popup_menu(draw, title='Success', icon = 'INFO')

        return {'FINISHED'}
operators.append(UIExportOperator)

class UIColorResetOperator(bpy.types.Operator):
    bl_idname = 'ui.color_reset'
    bl_label = "Reset to Default"
    bl_description = "Resets colors to default (in Preferences > Themes)"

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

    for name in ['socket_color_'+x.lower() for x in SOCKET_COLORS.keys()]:
        output[name] = getattr(group, name)[0:]

    return output

def loadProperties(json_string, group):
    
    for k, v in json.loads(json_string).items():
        setattr(group, k, v)

class UIConfigExportOperator(bpy.types.Operator):
    bl_idname = 'ui.config_export'
    bl_label = "Save"
    bl_description = "Saves current configuration to target file"

    def execute(self, context):
        
        with open(bpy.path.abspath(context.preferences.addons[__package__].preferences.config_save_path), "w+") as f:
            dump = json.dumps(dumpProperties(context.preferences.addons[__package__].preferences), indent=4)
            f.write(dump)

            return {'FINISHED'}
operators.append(UIConfigExportOperator)

class UIConfigImportOperator(bpy.types.Operator):
    bl_idname = 'ui.config_import'
    bl_label = "Load"
    bl_description = "Changes configuration to that in target file"

    def execute(self, context):

        with open(bpy.path.abspath(context.preferences.addons[__package__].preferences.config_load_path), "r+") as f:
            loadProperties(f.read(), context.preferences.addons[__package__].preferences)

            return {'FINISHED'}
operators.append(UIConfigImportOperator)

class UIAllNodesSizeOperator(bpy.types.Operator):
    bl_idname = 'ui.test_size'
    bl_label = 'Test size'
    bl_description = "Finds the size of each Node's SVG representation"

    def execute(self, context):

        prefs = context.preferences.addons[__package__].preferences
        
        old_select = prefs.export_selected_only

        prefs.export_selected_only = True

        abs_path = bpy.path.abspath(context.preferences.addons[__package__].preferences.output )

        with open(abs_path, "w+") as f:

            for node in [n for n in context.space_data.node_tree.nodes if n.select]:
                bpy.ops.node.select_all(action='DESELECT')
                node.select = True

                tree = Converter(context).convert()
                tree.getroot().remove(tree.getroot()[0])
                ET.indent(tree)
                s = ET.tostring(tree.getroot())
                f.write(node.bl_idname+','+str(len(s.split(b'\n')))+','+str(len(s))+'\n')

                

        prefs.export_selected_only = old_select

        return {'FINISHED'}
operators.append(UIAllNodesSizeOperator)

class UITimeOperator(bpy.types.Operator):
    bl_idname = 'ui.test_time'
    bl_label = 'Test time'
    bl_description = "Profiles export of the selected Nodes."

    def execute(self, context):
        
        import cProfile

        profile = cProfile.Profile(builtins=False)

        profile.enable()

        for _ in range(10000):
            bpy.ops.ui.exporter()

        profile.disable()

        #profile.dump_stats(bpy.path.abspath(context.preferences.addons[__package__].preferences.output+'_stats.txt'))
        profile.print_stats()

        return {'FINISHED'}
operators.append(UITimeOperator)

class UINodeImportOperator(bpy.types.Operator):
    bl_idname = 'ui.import_nodes'
    bl_label = 'Import Nodes'
    bl_description = "Imports Node layout from a previously exported file."

    def execute(self, context):

        props = context.preferences.addons[__package__].preferences
        
        graph = context.space_data.node_tree

        tree = ET.parse(props.import_file)
        root = tree.getroot()

        for g in root.findall('{http://www.w3.org/2000/svg}g'):
            if 'class' in g.attrib:
                if g.attrib['class'] != 'spec_node': continue
            else:
                continue
            meta = g.find('{http://www.w3.org/2000/svg}metadata')
            meta_info = json.loads(meta.text)

            new_node = graph.nodes.new(type=meta_info['type'])
            new_node.location = meta_info['x'], meta_info['y']

        return {'FINISHED'}
operators.append(UINodeImportOperator)

