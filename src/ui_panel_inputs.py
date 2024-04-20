import json

import bpy

from .uinodes import Converter
from .constants import IGNORE_PROPS, HEADER_OPACITY, ELEMENTS, TEXTS
from .categories import CATEGORY_NAMES
from .methods import getTextColors, getElementColors, getCategoryColors

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"



operators = []
panels = []

class ExportPropertyGroup(bpy.types.PropertyGroup):

    # toggle whether export should only include selected nodes
    export_selected_only: bpy.props.BoolProperty(name="Export Selected Only", default=False)

    # use rounded corners
    rounded_corners: bpy.props.BoolProperty(name="Rounded Corners", default=True)

    # graphical quality of certain elements
    fidelity: bpy.props.IntProperty(name="Element Fidelity", min=0, max=50, default=10)

    # use gradients for certain elements
    use_gradients: bpy.props.BoolProperty(name="Use Gradients", default=False)

    # use category defaults automatically
    use_theme_colors: bpy.props.BoolProperty(name="Use theme colors", default=False)

    # add outline to rectangles
    rect_outline:           bpy.props.FloatProperty(name="Outline Thickness", min=0, soft_max=10, default=0.3)
    rect_outline_color:     bpy.props.FloatVectorProperty(name="Outline Color", subtype='COLOR_GAMMA', min=0, max=1, size=4)

    # text colors
    use_generic_text:       bpy.props.BoolProperty(name="Use Generic Color", default=False)
    text_generic:           bpy.props.FloatVectorProperty(name="Generic",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    text_base:              bpy.props.FloatVectorProperty(name="Base",       subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_string:            bpy.props.FloatVectorProperty(name="String",     subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_true:      bpy.props.FloatVectorProperty(name="Bool True",  subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_boolean_false:     bpy.props.FloatVectorProperty(name="Bool False", subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_dropdown:          bpy.props.FloatVectorProperty(name="Dropdown",   subtype='COLOR_GAMMA', min=0, max=1, size=3)
    text_slider:            bpy.props.FloatVectorProperty(name="Slider",     subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # node element colors
    color_base:             bpy.props.FloatVectorProperty(name="Base",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_string_field:     bpy.props.FloatVectorProperty(name="String Field",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_dropdown:         bpy.props.FloatVectorProperty(name="Dropdown",      subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_false:       bpy.props.FloatVectorProperty(name="False",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_bool_true:        bpy.props.FloatVectorProperty(name="True",          subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_checkmark:        bpy.props.FloatVectorProperty(name="Checkmark",     subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_field:      bpy.props.FloatVectorProperty(name="Value",         subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_value_progress:   bpy.props.FloatVectorProperty(name="Progress Bar",  subtype='COLOR_GAMMA', min=0, max=1, size=4)
    color_axis_x:           bpy.props.FloatVectorProperty(name="Axis X",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_y:           bpy.props.FloatVectorProperty(name="Axis Y",        subtype='COLOR_GAMMA', min=0, max=1, size=3)
    color_axis_z:           bpy.props.FloatVectorProperty(name="Axis Z",        subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # colors of node headers
    header_color_input:         bpy.props.FloatVectorProperty(name="Input",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_output:        bpy.props.FloatVectorProperty(name="Output",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_shader:        bpy.props.FloatVectorProperty(name="Shader",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_texture:       bpy.props.FloatVectorProperty(name="Texture",   subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_color:         bpy.props.FloatVectorProperty(name="Color",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_vector:        bpy.props.FloatVectorProperty(name="Vector",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_converter:     bpy.props.FloatVectorProperty(name="Converter", subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_script:        bpy.props.FloatVectorProperty(name="Script",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_filter:        bpy.props.FloatVectorProperty(name="Filter",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_matte:         bpy.props.FloatVectorProperty(name="Matte",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_distor:        bpy.props.FloatVectorProperty(name="Distort",   subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_layout:        bpy.props.FloatVectorProperty(name="Layout",    subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_attribute:     bpy.props.FloatVectorProperty(name="Attribute", subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_geometry:      bpy.props.FloatVectorProperty(name="Geometry",  subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_group:         bpy.props.FloatVectorProperty(name="Group",     subtype='COLOR_GAMMA', min=0, max=1, size=3) 
    header_color_layout:        bpy.props.FloatVectorProperty(name="Layout",    subtype='COLOR_GAMMA', min=0, max=1, size=3)

    # opacity of header -- ADD HOVER INFO TO THIS
    header_opacity: bpy.props.FloatProperty(name="Header Opacity", subtype='PERCENTAGE', min=0, max=100, default=HEADER_OPACITY)

    # colors of nodes
    node_color: bpy.props.FloatVectorProperty(name="Base Color", subtype='COLOR', min=0, max=1)

    # config file mode
    config_mode:        bpy.props.EnumProperty(items=[
            ('SAVE', "Save", "Export a configuration file"),
            ('LOAD', "Load", "Import a configuration file"),
        ], name="Mode", default='LOAD')
    
    config_save_path:   bpy.props.StringProperty(name = "Save to", subtype='FILE_PATH')
    config_load_path:   bpy.props.StringProperty(name = "Load from", subtype='FILE_PATH')

    # target file to export into
    output: bpy.props.StringProperty(name = "Output", subtype='FILE_PATH')

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


        props = context.scene.export_svg_props

        header = "<?xml version='1.0' encoding='utf-8'?>"

        doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

        tree = Converter(context).convert()
        
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
        
        with open(bpy.path.abspath(context.scene.export_svg_props.config_save_path), "w+") as f:
            dump = json.dumps(dumpProperties(context.scene.export_svg_props), indent=4)
            f.write(dump)

            return {'FINISHED'}
operators.append(UIConfigExportOperator)

class UIConfigImportOperator(bpy.types.Operator):
    bl_idname = 'ui.config_import'
    bl_label = "Load"

    def execute(self, context):

        with open(bpy.path.abspath(context.scene.export_svg_props.config_load_path), "r+") as f:
            loadProperties(f.read(), context.scene.export_svg_props)

            return {'FINISHED'}
operators.append(UIConfigImportOperator)

### PANELS ###

class UIPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

class UIColorPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_color_parent'
    
    @classmethod
    def poll(cls, context):
        return not context.scene.export_svg_props.use_theme_colors


class UIParentPanel(UIPanel):
    bl_category = "Export"
    bl_idname = "NODE_EDITOR_PT_export_parent"
    bl_label = "Export to SVG"

    def draw(self, context):
        ...

panels.append(UIParentPanel)


class UIQualityPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = "NODE_EDITOR_PT_quality"
    bl_label = "Detail"

    def draw(self, context):
        
        layout = self.layout
        props = context.scene.export_svg_props

        layout.prop(props, 'fidelity')
        layout.prop(props, 'use_gradients')
        layout.prop(props, 'rounded_corners')
panels.append(UIQualityPanel)

class UIOutlinePanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = 'NODE_EDITOR_PT_outline'
    bl_label = "Outline"

    def draw(self, context):

        layout = self.layout
        props = context.scene.export_svg_props
        
        layout.prop(props, 'rect_outline')
        layout.prop(props, 'rect_outline_color')
panels.append(UIOutlinePanel)


class UIColorParentPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = 'NODE_EDITOR_PT_color_parent'
    bl_label = "Colors"


    def draw(self, context):
        layout = self.layout
        props = context.scene.export_svg_props

        layout.prop(props, 'use_theme_colors')

        row = layout.row()
        row.operator(
            operator='ui.color_reset',
            text="Reset Colors"
        )
        row.enabled = not props.use_theme_colors


panels.append(UIColorParentPanel)

class UIColorTextPanel(UIColorPanel):
    bl_idname = 'NODE_EDITOR_PT_color_text'
    bl_label = "Text"

    def draw(self, context):
        layout = self.layout
        props = context.scene.export_svg_props

        layout.prop(props, 'use_generic_text')

        row = layout.row()
        row.prop(props, 'text_generic')
        row.enabled = props.use_generic_text

        # skip first (-> generic)
        for name in TEXTS[1:]:
            row = layout.row()
            row.prop(props, 'text_'+name)
            row.enabled = not props.use_generic_text
panels.append(UIColorTextPanel)

class UIColorElemPanel(UIColorPanel):
    bl_idname = 'NODE_EDITOR_PT_elements'
    bl_label = "Elements"

    def draw(self, context):
        layout = self.layout
        props = context.scene.export_svg_props

        for color_name in ['color_'+elem for elem in ELEMENTS]:
            layout.prop(props, color_name)
panels.append(UIColorElemPanel)

class UIColorHeaderPanel(UIColorPanel):
    bl_idname = "NODE_EDITOR_PT_headers"
    bl_label = "Headers"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.export_svg_props

        # https://blender.stackexchange.com/questions/41387/how-to-deactivate-a-ui-element-in-an-add-on
        for color_name in ['header_color_'+name for name in CATEGORY_NAMES]+['header_opacity']:
            layout.prop(props, color_name)
panels.append(UIColorHeaderPanel)

class UIConfigPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = "NODE_EDITOR_PT_conf"
    bl_label = "Save/Load Configuration"

    def draw(self, context):
         
        layout = self.layout
        props = context.scene.export_svg_props

        layout.prop(props, 'config_mode', text="")

        save_row = layout.column()
        save_row.prop(props, 'config_save_path')
        save_row.operator('ui.config_export')
        
        load_row = layout.column()
        load_row.prop(props, 'config_load_path')
        load_row.operator('ui.config_import')

        # enable/disable
        save_row.enabled = (props.config_mode == 'SAVE')
        load_row.enabled = (props.config_mode == 'LOAD')

panels.append(UIConfigPanel)

class UIInspectPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = "NODE_EDITOR_PT_export"
    bl_label = "Export"

    def draw(self, context):

        layout = self.layout
        props = context.scene.export_svg_props

        row = layout.row()
        row.label(text="Export target")

        row = layout.row()
        row.prop(props, 'export_selected_only')

        row = layout.row()
        row.prop(props, 'output', text="")

        layout.operator(
            operator='ui.exporter',
            icon='NODETREE',
            text='Export'
        )

        #layout.operator(
        #    operator='ui.inspector',
        #    icon='NODE',
        #    text='Inspect Selected'
        #)
panels.append(UIInspectPanel)
