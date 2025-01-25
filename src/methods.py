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

import mathutils
import cmath
import bpy
from math import sqrt

from .constants import HEADER_OPACITY, CATEGORY_NAMES, TEXTS, ELEMENTS, ROUND_CORNER, SOCKET_COLORS

# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"
def colorCorrect(value: float) -> float:
    if bpy.data.scenes[0].display_settings.display_device == 'sRGB': return linearRGBtoSRGB(value)
    return value


# based on: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_color.c
# (which is Blender's source code)
# it is distributed under the same license as this add-on
def linearRGBtoSRGB(value: float) -> float:
  if value < 0.0031308:
    return 0.0 if value < 0.0 else value * 12.92

  return 1.055 * value**(1.0 / 2.4) - 0.055


def socketColorToSVGColor(color: list[float], corrected=True) -> str:
    if corrected:
        return "rgb("+",".join([str(round(x*255)) for x in color[:3]])+")"
    
    return "rgb("+",".join([str(round(colorCorrect(x)*255)) for x in color[:3]])+")"
    

def enumName(node: bpy.types.Node, enum_name: str) -> str:
    return node.bl_rna.properties[enum_name].enum_items[getattr(node, enum_name)].name

def getFloatString(value: float, decimal_points: int = 3) -> str:

    if decimal_points == 3:
        return f'{value:.3f}'

    rounded = round(abs(value)*(10**decimal_points))
    s = ('-' if value<0 else '')+('0' if abs(value)<1 else '')+str(rounded)[:-decimal_points]+'.'+str(rounded)[-decimal_points:]
    return s

def cartesianToPolar(x: float, y: float) -> tuple[float, float]:
    return cmath.polar(complex(x, y))

def polarToCartesian(rho: float, phi: float) -> tuple[float, float]:
    return (z := cmath.rect(rho, phi)).real, z.imag

def solveQuadratic(a: float, b: float, c: float) -> tuple[float, float]:
    sqrt_d = sqrt(b**2 - 4*a*c)
    return ((-b+sqrt_d)/(2*a), (-b-sqrt_d)/(2*a))

def getBezierExtrema(x0: float, x1: float, x2: float, x3: float) -> tuple[float, float]:
    
    bezier = lambda t: (1-t)**3*x0 + 3*(1-t)**2*t*x1 + 3*(1-t)*t**2*x2 + t**3*x3
    
    try:
        t1, t2 = solveQuadratic((-3*x0 + 9*x1 - 9*x2 + 3*x3)/100.0, (6*x0 - 12*x1 + 6*x2)/100.0, (-3*x0 + 3*x1)/100.0)
    except Exception as e:
        print(x0, x1, x2, x3)
        raise e
    return (
        bezier(t1),
        bezier(t2)
    )


def getTextColors(context):
    text_colors = {}
    theme = context.preferences.themes[0]
    text_colors['text_generic']         = theme.node_editor.space.text
    text_colors['text_base']            = theme.node_editor.space.text
    text_colors['text_string']          = theme.user_interface.wcol_text.text
    text_colors['text_boolean_true']    = theme.user_interface.wcol_option.text_sel
    text_colors['text_boolean_false']   = theme.user_interface.wcol_option.text
    text_colors['text_dropdown']        = theme.user_interface.wcol_menu.text
    text_colors['text_slider']          = theme.user_interface.wcol_numslider.text
    
    return text_colors

def getElementColors(context):
    elem_colors = {}
    theme = context.preferences.themes[0]
    elem_colors['color_base'] = theme.node_editor.node_backdrop
    elem_colors['color_string_field'] = theme.user_interface.wcol_text.inner
    elem_colors['color_dropdown'] = theme.user_interface.wcol_menu.inner
    elem_colors['color_bool_false'] = theme.user_interface.wcol_option.inner
    elem_colors['color_bool_true'] = theme.user_interface.wcol_option.inner_sel
    elem_colors['color_checkmark'] = theme.user_interface.wcol_option.item
    elem_colors['color_value_field'] = theme.user_interface.wcol_numslider.inner
    elem_colors['color_value_progress'] = theme.user_interface.wcol_numslider.item
    elem_colors['color_axis_x'] = theme.user_interface.axis_x
    elem_colors['color_axis_y'] = theme.user_interface.axis_y
    elem_colors['color_axis_z'] = theme.user_interface.axis_z
    elem_colors['color_text'] = theme.user_interface.wcol_regular.text
    elem_colors['color_background'] = theme.node_editor.space.back

    return elem_colors

def getCategoryColors(context):
    theme = context.preferences.themes[0]
    return {'header_color_'+name:getattr(theme.node_editor, name+'_node') for name in CATEGORY_NAMES}

def getSocketColors():
    elem_colors = {}
    for key, value in SOCKET_COLORS.items():
        elem_colors['socket_color_'+key.lower()] = value
    return elem_colors

def getConfigurationFromContext(context) -> dict:
    
    output = {}
    
    theme = context.preferences.themes[0]
    props = context.preferences.addons[__package__].preferences

    # Details

    output['fidelity'] = props.fidelity
    output['use_gradients'] = props.use_gradients
    output['round_l'] = str(ROUND_CORNER) if props.rounded_corners else '0'
    output['round_s'] = '3px' if props.rounded_corners else '0'

    # Outline
    output['outline_thickness'] = props.rect_outline
    output['outline_color']     = socketColorToSVGColor(props.rect_outline_color)

    # Color

    if props.use_theme_colors:
        # Text
        for k, v in getTextColors(context).items():
            output[k] = socketColorToSVGColor(v)

        # Elements
        for k, v in getElementColors(context).items():
            output[k] = socketColorToSVGColor(v)

        cat_colors = getCategoryColors(context)
        for name in CATEGORY_NAMES:
            output[name+'_node'] = socketColorToSVGColor(cat_colors['header_color_'+name])

        # Sockets
        output.update(getSocketColors())

    else:
        # Text
        for name in TEXTS[1:]:
            color = props.text_generic if props.use_generic_text else getattr(props, 'text_'+name)
            output['text_'+name] = socketColorToSVGColor(color)

        # Elements
        for name in ELEMENTS:
            output['color_'+name] = socketColorToSVGColor(getattr(props, 'color_'+name))

        # Headers
        for name in CATEGORY_NAMES:
            output[name+'_node'] = socketColorToSVGColor(getattr(props, 'header_color_'+name))

        for name in SOCKET_COLORS.keys():
            color = props.socket_color_generic if props.use_generic_socket else getattr(props, 'socket_color_'+name.lower())
            output['socket_color_'+name.lower()] = socketColorToSVGColor(color)

    output['noodliness'] = theme.node_editor.noodle_curving
    output['header_opacity'] = HEADER_OPACITY

    return output

def insertIntoSortedByKey(e, arr, key) -> list:
    
    if not arr: return [e]

    if len(arr) == 1:
        if key(e) > key(arr[0]): return arr + [e]
        else: return [e] + arr
    
    midpoint = len(arr) // 2

    if key(e) > key(arr[midpoint-1]):
        if key(e) < key(arr[midpoint]):
            return arr[:midpoint] + [e] + arr[midpoint:]
        else:
            return arr[:midpoint+1] + insertIntoSortedByKey(e, arr[midpoint+1:], key)
    else:
        return insertIntoSortedByKey(e, arr[:midpoint-1], key) + arr[midpoint-1:]

def colorStringToArray(color: str) -> tuple[float, float, float]:
    arr = []

    for i in range(1,6,2):
        arr.append(int(color[i:i+2], 16)/256)

    return arr