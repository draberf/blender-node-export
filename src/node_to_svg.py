import xml.etree.ElementTree as ET
from bpy import types

def nodesToSvg(nodes: types.Node):

    header = "<?xml version='1.0' encoding='utf-8'?>"

    doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

    svg = ET.Element('svg', width="20cm", height="8cm", version="1.1", xmlns="http://www.w3.org/2000/svg")
    
    # preprocess pass
    # can be swapped with callbacks or something

    min_x, min_y = 0, 0
    for i, node in enumerate(nodes):
        x, y = node.location
        min_x = min(min_x, x)
        min_y = min(min_y, y)


    # generation pass

    for i, node in enumerate(nodes):
        g = ET.Element('g', id=f"{node.bl_name}_{i}")
        text = ET.Element('text')
        text.text = node.bl_name
        g.append(text)
        svg.append(g)
    svg_string = ET.tostring(svg, encoding='unicode')

    print('\n'.join([header, doctype, svg_string]))

if __name__=="__main__":

    nodesToSvg([])