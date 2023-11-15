import xml.etree.ElementTree as ET
from bpy import types

# constants: move to someplace later:
U = "px"
PADDING = 3

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"

def nodesToSvg(nodes: types.Node):

    header = "<?xml version='1.0' encoding='utf-8'?>"

    doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

    svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")

    # generation pass

    viewBox_minX, viewBox_minY = nodes[0].location
    viewBox_maxX, viewBox_maxY = nodes[0].location

    for i, node in enumerate(nodes):
        
        # create group
        g = ET.Element('g', id=f"{node.name}_{i}")
        w, h = node.dimensions
        x = node.location[0]
        y = -node.location[1]

        viewBox_minX = min(viewBox_minX, x)
        viewBox_minY = min(viewBox_minY, y)

        viewBox_maxX = max(viewBox_maxX, x+w)
        viewBox_maxY = max(viewBox_maxY, y+h)

        # create frame
        frame = ET.Element('rect', x=f"{x}", y=f"{y}", width=f"{w}", height=f"{h}")
        g.append(frame)

        # add group to svg
        svg.append(g)

    svg.set("viewBox", f"{viewBox_minX-PADDING} {viewBox_minY-PADDING} {viewBox_maxX-viewBox_minX+PADDING} {viewBox_maxY-viewBox_minY+PADDING}")

    svg_string = ET.tostring(svg, encoding='unicode')
    msg = '\n'.join([header, doctype, svg_string])

    print(msg)

    with open(TARGET, "w") as f:
        f.write(msg)

if __name__=="__main__":

    nodesToSvg([])