# source: https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo


bl_info = {
    "name": "Node Exporter to SVG",
    "description": "Adds operator to export a node tree into an SVG image",
    "author": "Filip Dráber",
    "version": (0, 2, 3),
    "blender": (3, 4, 0),
    "location": "Node Editor",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

# this helps with reloads
# https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts/28505#28505
if "bpy" in locals():
    files = [
        'constants', 'methods', 'widgets',
        'categories', 'header', 'shape',
        'node', 'converter', 'property_group',
        'panels', 'operators'
    ]
    import importlib
    for file in files:
        if file in locals():
            importlib.reload(eval(file))
        else:
            print(f"file {file} not in locals")
            print(locals())

import bpy
from . import property_group, panels, operators
import sys, importlib
print(sys.modules.items())
to_reload = [module for (m_name, module) in sys.modules.items() if m_name[:len(__package__)] == __package__]
for module in to_reload:
    importlib.reload(module)

def register():

    # register properties
    bpy.utils.register_class(property_group.ExportPropertyGroup)

    for cls in operators.operators+panels.panels:
        bpy.utils.register_class(cls)

def unregister():

    # unregister properties
    bpy.utils.unregister_class(property_group.ExportPropertyGroup)

    for cls in operators.operators+panels.panels:
        bpy.utils.unregister_class(cls)