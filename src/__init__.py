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

bl_info = {
    "name": "Node Exporter to SVG",
    "description": "Adds operator to export a node tree into an SVG image",
    "author": "Filip Dráber",
    "version": (0, 3, 2),
    "blender": (4, 1, 0),
    "location": "Node Editor",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
from . import property_group, panels, operators
import sys, importlib
to_reload = [module for (m_name, module) in sys.modules.items() if m_name.startswith(__package__)]
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