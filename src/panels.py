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

import bpy

from .constants import ELEMENTS, TEXTS, SOCKET_COLORS
from .categories import CATEGORY_NAMES

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"


panels = []

### PANELS ###

class UIPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

class UIColorPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_color_parent'
    
    @classmethod
    def poll(cls, context):
        return not context.preferences.addons[__package__].preferences.use_theme_colors


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
        props = context.preferences.addons[__package__].preferences

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
        props = context.preferences.addons[__package__].preferences
        
        layout.prop(props, 'rect_outline')
        layout.prop(props, 'rect_outline_color')
panels.append(UIOutlinePanel)


class UIColorParentPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = 'NODE_EDITOR_PT_color_parent'
    bl_label = "Colors"


    def draw(self, context):
        layout = self.layout
        props = context.preferences.addons[__package__].preferences

        layout.prop(props, 'use_theme_colors')

        row = layout.row()
        row.operator(
            operator='ui.color_reset',
        )
        row.enabled = not props.use_theme_colors


panels.append(UIColorParentPanel)

class UIColorTextPanel(UIColorPanel):
    bl_idname = 'NODE_EDITOR_PT_color_text'
    bl_label = "Text"

    def draw(self, context):
        layout = self.layout
        props = context.preferences.addons[__package__].preferences

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
        props = context.preferences.addons[__package__].preferences

        for color_name in ['color_'+elem for elem in ELEMENTS]:
            layout.prop(props, color_name)
panels.append(UIColorElemPanel)

class UIColorHeaderPanel(UIColorPanel):
    bl_idname = "NODE_EDITOR_PT_headers"
    bl_label = "Headers"
    
    def draw(self, context):
        layout = self.layout
        props = context.preferences.addons[__package__].preferences

        # https://blender.stackexchange.com/questions/41387/how-to-deactivate-a-ui-element-in-an-add-on
        for color_name in ['header_color_'+name for name in CATEGORY_NAMES]+['header_opacity']:
            layout.prop(props, color_name)
panels.append(UIColorHeaderPanel)

class UIColorSocketPanel(UIColorPanel):
    bl_idname = "NODE_EDITOR_PT_sockets"
    bl_label = "Sockets"

    def draw(self, context):
        layout = self.layout
        props = context.preferences.addons[__package__].preferences

        layout.prop(props, 'use_generic_socket')
        
        for color_name in ['socket_color_'+name.lower() for name in SOCKET_COLORS.keys()]:
            row = layout.row()
            row.prop(props, color_name)
            if color_name == 'socket_color_generic': row.enabled = props.use_generic_socket
            else: row.enabled = not props.use_generic_socket
panels.append(UIColorSocketPanel)

class UIConfigPanel(UIPanel):
    bl_parent_id = 'NODE_EDITOR_PT_export_parent'
    bl_idname = "NODE_EDITOR_PT_conf"
    bl_label = "Save/Load Configuration"

    def draw(self, context):
         
        layout = self.layout
        props = context.preferences.addons[__package__].preferences

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
        props = context.preferences.addons[__package__].preferences

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

        layout.operator(
            operator='ui.inspector',
            icon='NODE',
            text='Inspect Selected'
        )

        layout.operator(
            operator='ui.test_size',
            icon='NODE',
            text='Test Size'
        )
panels.append(UIInspectPanel)
