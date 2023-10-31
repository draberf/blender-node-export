# source: https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo


bl_info = {
    "name": "Node Exporter to SVG",
    "description": "Adds operator to export a node tree into an SVG image",
    "author": "Filip Dráber",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "Node Editor",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
import src.ui_panel_inputs

def register():
    bpy.utils.register_class(src.ui_panel_inputs.UIInspectOperator)
    bpy.utils.register_class(src.ui_panel_inputs.UIInspectPanel)

def unregister():
    pass

