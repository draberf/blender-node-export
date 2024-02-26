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

# this helps with reloads
# https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts/28505#28505
if "bpy" in locals():
    files = [
        "constants", "node_to_svg", "ui_panel_inputs", "uinodes"
    ]
    import importlib
    for file in files:
        if file in locals():
            importlib.reload(eval(file))
        else:
            print(f"file {file} not in locals")
            print(locals())

import bpy
from .src import ui_panel_inputs
import sys, importlib
to_reload = [module for (m_name, module) in sys.modules.items() if m_name[:len("NodeExportToSVG.src.")] == "NodeExportToSVG.src."]
for module in to_reload:
    importlib.reload(module)

def register():
    bpy.utils.register_class(ui_panel_inputs.UIInspectOperator)
    bpy.utils.register_class(ui_panel_inputs.UIExportOperator)
    bpy.utils.register_class(ui_panel_inputs.UIInspectPanel)

def unregister():
    bpy.utils.unregister_class(ui_panel_inputs.UIInspectOperator)
    bpy.utils.unregister_class(ui_panel_inputs.UIExportOperator)
    bpy.utils.unregister_class(ui_panel_inputs.UIInspectPanel)