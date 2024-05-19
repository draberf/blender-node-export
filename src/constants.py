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

from math import floor

# ratio of actual node frame dimensions to the bpy object
NODE_DIM_RATIO = 0.8

# specific heights
HEADER_HEIGHT = 20
TOP_PADDING = 6.5
SOCKET_GAP = 5.6
BOTTOM_PADDING = 13.5

LINKED_SOCKET_HEIGHT = 16
SOCKET_TEXT_PADDING = 10

SOCKET_TEXT_HEIGHT = 11

# colors
HEADER_OPACITY = 38

# properties to skip
DEFAULT_PROPERTIES = 0
IGNORE_PROPS = [
    "rna_type", "type", "location", "width",
    "width_hidden", "height", "dimensions", "name",
    "label", "inputs", "outputs", "internal_links",
    "parent", "use_custom_color", "color", "select",
    "show_options", "show_preview", "hide", "mute",
    "show_texture", "bl_idname", "bl_label",
    "bl_description", "bl_icon", "bl_static_type",
    "bl_width_default", "bl_width_min",
    "bl_width_max", "bl_height_default",
    "bl_height_min", "bl_height_max"
]

# colors
SOCKET_COLORS = {
    'GENERIC': '#ffffff',
    'CUSTOM': '#333333',
    'VALUE': '#a1a1a1',
    'INT': '#598c5c',
    'BOOLEAN': '#cca6d6',
    'VECTOR': '#6363c7',
    'ROTATION': '#ff00ff',
    'MENU': '#666666',
    'STRING': '#70b2ff',
    'RGBA': '#c7c729',
    'SHADER': '#633763',
    'OBJECT': '#ed9e5c',
    'IMAGE': '#633863',
    'GEOMETRY': '#00d6a3',
    'COLLECTION': '#f5f5f5',
    'TEXTURE': '#9e4fa3',
    'MATERIAL': '#eb7582'
}

# size of node anchor markers
MARKER_SIZE = 7
MARKER_LINE = 1
MARKER_BOX_HALF = (MARKER_SIZE+MARKER_LINE)/2
MARKER_DOT_RADIUS = 1

# padding of the final tree viewbox
VIEWBOX_PADDING = 10


CATEGORY_NAMES = (
    'input',
    'output',
    'shader',
    'texture',
    'color',
    'vector',
    'converter',
    'script',
    'filter',
    'matte',
    'distor',
    'layout',
    'attribute',
    'geometry',
    'group'
)

ELEMENTS = (
    'base', 'string_field', 'dropdown',
    'bool_false', 'bool_true', 'checkmark',
    'value_field', 'value_progress',
    'axis_x', 'axis_y', 'axis_z'
)

TEXTS = (
    'generic', 'base', 'string',
    'boolean_true', 'boolean_false',
    'slider', 'dropdown'
)

ROUND_CORNER = 5

FRAME_NODE_PADDING = 30

PAGES = {}
PAGES.update({
        k:(floor(787.5*(1.618**i)),1274*(1.618**i)) for k, i in zip(['A5', 'A4', 'A3', 'A2', 'A1', 'A0'], range(-1, 5))
    })