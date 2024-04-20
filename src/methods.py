import mathutils
import cmath
import bpy
from math import sqrt

from .constants import HEADER_OPACITY, CATEGORY_NAMES, TEXTS, ELEMENTS

# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"

# from https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_color.c
def colorCorrect(value: float) -> float:
    if bpy.data.scenes[0].display_settings.display_device == 'sRGB': return linearRGBtoSRGB(value)
    return value

def linearRGBtoSRGB(value: float) -> float:
  if value < 0.0031308:
    return 0.0 if value < 0.0 else value * 12.92

  return 1.055 * value**(1.0 / 2.4) - 0.055


def socketColorToSVGColor(color: list[float], corrected=True) -> str:
    if corrected:
        return "rgb("+",".join([str(round(x*255)) for x in color[:3]])+")"
    
    return "rgb("+",".join([str(round(colorCorrect(x)*255)) for x in color[:3]])+")"
    

def enumName(node, enum_name):
    return node.bl_rna.properties[enum_name].enum_items[getattr(node, enum_name)].name

def getFloatString(value: float, decimal_points: int = 3) -> str:

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
        print(t1, t2)
    except Exception as e:
        print(x0, x1, x2, x3)
        raise e
    return (
        bezier(t1),
        bezier(t2)
    )


def getColorsFromPreferences(context) -> dict[list[float]]:
    
    output = {}
    
    theme = context.preferences.themes[0]

    output['color_base'] = theme.node_editor.node_backdrop
    output['color_string_field'] = theme.user_interface.wcol_text.inner
    output['color_bool_false'] = theme.user_interface.wcol_option.inner
    output['color_bool_true'] = theme.user_interface.wcol_option.inner_sel
    output['color_value_field'] = theme.user_interface.wcol_numslider.inner
    output['color_value_progress'] = theme.user_interface.wcol_numslider.item
    output['color_axis_x'] = theme.user_interface.axis_x
    output['color_axis_y'] = theme.user_interface.axis_y
    output['color_axis_z'] = theme.user_interface.axis_z
    output['color_text'] = theme.user_interface.wcol_regular.text

    output['noodliness'] = theme.node_editor.noodle_curving
    output['header_opacity'] = HEADER_OPACITY

    for name in CATEGORY_NAMES:
       output['header_color_'+name] = getattr(theme.node_editor, name+'_node')

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
    

