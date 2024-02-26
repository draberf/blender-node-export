import xml.etree.ElementTree as ET
from bpy import types
import importlib
from . import uinodes
importlib.reload(uinodes)

# constants: move to someplace later:
U = "px"
PADDING = 3

TARGET = "D:\\skola_mit\\dp\\blender-node-export\\output.svg"

def nodesToSvg(nodetree: types.NodeTree, context):

    curving = context.preferences.themes[0].node_editor.noodle_curving
    nodes = nodetree.nodes
    links = nodetree.links

    svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")

    # generation pass

    viewBox_minX, viewBox_minY = nodes[0].location
    viewBox_maxX, viewBox_maxY = nodes[0].location

    link_mapping = {}
    ui_nodes = []
    ui_anchors = []

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
        uinode, anchors = ui_node.svg()
        ui_nodes.append(uinode)
        ui_anchors.extend(anchors)


    # add links
    fac = curving/10.0
    for link in links:
        from_x, from_y = link_mapping[str(link.from_socket.as_pointer())]
        to_x, to_y = link_mapping[str(link.to_socket.as_pointer())]
        diff_x = abs(to_x - from_x)
        line = ET.Element('path', d=f"M {from_x},{from_y} C {from_x + fac*diff_x},{from_y} {to_x - fac*diff_x},{to_y} {to_x},{to_y}",
                          style="stroke:rgb(0,0,0);stroke-width:2;fill:none")
        svg.append(line)

    svg.extend(ui_nodes)
    svg.extend(ui_anchors)        

    svg.set("viewBox", f"{viewBox_minX-PADDING} {viewBox_minY-PADDING} {viewBox_maxX-viewBox_minX+PADDING} {viewBox_maxY-viewBox_minY+PADDING}")

    # svg_string = ET.tostring(tree, encoding='unicode')
    # msg = '\n'.join([header, doctype, svg_string])

    #print(msg)

    return svg

if __name__=="__main__":

    nodesToSvg([])