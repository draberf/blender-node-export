import xml.etree.ElementTree as ET
from bpy import types
import importlib
from . import uinodes
importlib.reload(uinodes)

# constants: move to someplace later:
U = "px"
PADDING = 3

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"

def nodesToSvg(nodes: [types.Node], links: [types.NodeLink] = []):

    header = "<?xml version='1.0' encoding='utf-8'?>"

    doctype = "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"

    svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")

    # generation pass

    viewBox_minX, viewBox_minY = nodes[0].location
    viewBox_maxX, viewBox_maxY = nodes[0].location

    link_mapping = {}

    for i, node in enumerate(nodes):
        
        ui_node = uinodes.UINode(node)
        link_mapping.update(ui_node.get_socket_coords())

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
        ui = ui_node.svg()
        g.append(ui)

        # add group to svg
        svg.append(g)

    # add links
    for link in links:
        from_x, from_y = link_mapping[str(link.from_socket.as_pointer())]
        to_x, to_y = link_mapping[str(link.to_socket.as_pointer())]
        line = ET.Element('line',
                          x1=str(from_x),
                          y1=str(from_y),
                          x2=str(to_x),
                          y2=str(to_y),
                          style="stroke:rgb(0,0,0);stroke-width:5")
        svg.append(line)
        

    svg.set("viewBox", f"{viewBox_minX-PADDING} {viewBox_minY-PADDING} {viewBox_maxX-viewBox_minX+PADDING} {viewBox_maxY-viewBox_minY+PADDING}")

    tree = ET.ElementTree(svg)
    ET.indent(tree, '  ')
    # svg_string = ET.tostring(tree, encoding='unicode')
    # msg = '\n'.join([header, doctype, svg_string])

    #print(msg)

    with open(TARGET, "w") as f:
        f.write(header)
        f.write(doctype)
        tree.write(f, encoding='unicode')


if __name__=="__main__":

    nodesToSvg([])