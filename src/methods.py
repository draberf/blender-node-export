import mathutils

# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"

def socketColorToSVGColor(color: list[float]) -> str:
    return "rgb("+",".join([str(round(x*255)) for x in color[:3]])+")"

def enumName(node, enum_name):
    return node.bl_rna.properties[enum_name].enum_items[getattr(node, enum_name)].name