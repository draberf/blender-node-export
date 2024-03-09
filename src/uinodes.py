import importlib

from . import constants
from . import categories
from . import widgets

import bpy
import mathutils
import xml.etree.ElementTree as ET

MARKER_DEFS = {
    'circle': ('circle',{
                            'cx':f'{constants.MARKER_BOX_HALF}',
                            'cy':f'{constants.MARKER_BOX_HALF}',
                            'r':f'{constants.MARKER_SIZE/2}',
                            'class':'marker'
                            }),
    'square':('rect',{
                            'x':'0',
                            'y':'0',
                            'width':f'{constants.MARKER_SIZE}',
                            'height':f'{constants.MARKER_SIZE}',
                            'class':'marker'
                            }),
    'diamond':('polygon',{
                            'points':f'\
                            {constants.MARKER_LINE/2} {constants.MARKER_BOX_HALF} \
                            {constants.MARKER_BOX_HALF} {constants.MARKER_LINE/2} \
                            {constants.MARKER_SIZE+constants.MARKER_LINE/2} {constants.MARKER_BOX_HALF} \
                            {constants.MARKER_BOX_HALF} {constants.MARKER_SIZE+constants.MARKER_LINE/2} \
                            ',
                            'class':'marker'
                            }),
    'dot':('circle',{       
                            'cx':f'{constants.MARKER_BOX_HALF}',
                            'cy':f'{constants.MARKER_BOX_HALF}',
                            'r':f'{constants.MARKER_DOT_RADIUS}',
                            'class':'marker_dot'
                            })
    }

def getFloatString(value: float, spaces: int = 5) -> str:

    s = str(value)[:5]
    s += (5-len(s))*"0"
    return s

def style() -> ET.Element:
    
    style_elem = ET.Element('style')

    style_elem.text = '\n'.join([
        ".nodeframe { fill: #333333 } ",
        "text { font-family: Sans, Arial; font-size: 0.6em; fill: white }",
        ".marker { stroke-width: "+str(constants.MARKER_LINE)+"px; stroke: black}"
    ])

    return style_elem

def getImageWidgetString(socket):
    if not socket.default_value: return ""
    if socket.default_value.source in ['FILE', 'SEQUENCE', 'MOVIE']:
        return socket.default_value.filepath
    return socket.default_value.source

def getObjectName(socket):
    if not socket.default_value: return ""
    return socket.default_value.name

# convert unconnected input socket to widget
SOCKET_WIDGET_DEFS = {
    'VALUE': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=str(socket.default_value), align_right=True)
    ]),
    'RGBA': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.RGBA(color="#ff0000")
    ]),
    'VECTOR': lambda socket: widgets.Vector(name=socket.name, values=[getFloatString(f) for f in socket.default_value]),
    'INT': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=str(socket.default_value), align_right=True)
    ]),
    'IMAGE': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=getImageWidgetString(socket), align_right=True)
    ]),
    'OBJECT': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=socket.default_value.name, align_right=True)
    ]),
    'TEXTURE': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=socket.default_value.name, align_right=True)
    ]),
    'COLLECTION': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=socket.default_value.name, align_right=True)
    ]),
    'GEOMETRY': lambda socket: widgets.Label(text=socket.name, align_right=False),
    'MATERIAL': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=socket.default_value.name, align_right=True)
    ]),
    'STRING': lambda socket: widgets.Columns(wids=[
        widgets.Label(text=socket.name, align_right=False),
        widgets.Label(text=socket.default_value, align_right=True)
    ]),
    'BOOLEAN': lambda socket: widgets.Boolean(name=socket.name, value=socket.default_value)
}

def widgetFactory(socket) -> widgets.Widget:
    
    if socket.is_output or socket.is_linked:
        return widgets.Label(text=socket.name, align_right=True)

    return SOCKET_WIDGET_DEFS[socket.type](socket)

# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"
    
class Converter():

    def __init__(self, context) -> None:
        
        nodetree = context.space_data.node_tree
        self.colors = {k:blColorToSVGColor(v) for k, v in [
            (k, getattr(context.preferences.themes[0].node_editor, k)) for k in categories.category_to_node.keys()
        ]}

        self.nodes = []

        self.links = [
            (link.from_socket.as_pointer(), link.to_socket.as_pointer()) for link in nodetree.links
        ]

        self.curving = context.preferences.themes[0].node_editor.noodle_curving

        self.anchor_refs = {}


        self.vb_min_x = nodetree.nodes[0].location[0]
        self.vb_min_y = nodetree.nodes[0].location[1]
        self.vb_max_x = nodetree.nodes[0].location[0]
        self.vb_max_y = nodetree.nodes[0].location[1]


        for node in nodetree.nodes:
            
            # create node rep
            key = node.name
            if len(key) > 4:
                if node.name[-4] == '.': key = node.name[:-4]
            color = "gray"
            if key in categories.node_to_category.keys():
                color = self.colors[categories.node_to_category[key]]
            node_object = UINode(node, color)

            # update viewbox corners
            self.vb_min_x = min(self.vb_min_x, node_object.x)
            self.vb_min_y = min(self.vb_min_y, node_object.y)
            self.vb_max_x = max(self.vb_max_x, node_object.x+node_object.w)
            self.vb_max_y = max(self.vb_max_y, node_object.y+node_object.h)

            self.anchor_refs.update(node_object.anchors)
            self.nodes.append(node_object)

    def convert(self) -> ET.ElementTree:
        
        svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")
        svg.set('viewBox', ' '.join([str(f) for f in [
            self.vb_min_x,
            self.vb_min_y,
            self.vb_max_x-self.vb_min_x,
            self.vb_max_y-self.vb_min_y
        ]]))

        svg.append(style())

        # add symbols

        for sym_name, (elem_name, elem_attrs) in MARKER_DEFS.items():
            symbol = ET.SubElement(svg, 'symbol', id='marker_'+sym_name)
            ET.SubElement(symbol, elem_name, attrib=elem_attrs)

        # add links to final SVG
        fac = self.curving/10.0
        for link in self.links:
            
            from_x, from_y, from_anchor_object = self.anchor_refs[link[0]]
            to_x, to_y, _ = self.anchor_refs[link[1]]

            color1 = from_anchor_object.color

            diff_x = abs(to_x - from_x)
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {from_x + fac*diff_x},{from_y} {to_x - fac*diff_x},{to_y} {to_x},{to_y}",
                            style=f"stroke:#000000;stroke-width:4;fill:none")
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {from_x + fac*diff_x},{from_y} {to_x - fac*diff_x},{to_y} {to_x},{to_y}",
                            style=f"stroke:{color1};stroke-width:2;fill:none")

        # add nodes to final SVG
        svg.extend([node.svg() for node in self.nodes])

        # add anchors to final SVG
        svg.extend([anchor.svg(x=str(x-constants.MARKER_BOX_HALF), y=str(y-constants.MARKER_BOX_HALF)) for x, y, anchor in self.anchor_refs.values()])

        return ET.ElementTree(svg)

# class wrapper for a single node
class UINode():

    def __init__(self, node: bpy.types.Node, color_string: str):
        self.name = node.label if node.label else node.name
        self.w, self.h = node.dimensions
        self.w *= constants.NODE_DIM_RATIO
        self.h *= constants.NODE_DIM_RATIO
        self.x =  node.location[0]
        self.y = -node.location[1]
        self.outputs = [output for output in node.outputs.values() if all([not output.hide, output.enabled, not output.is_unavailable])]
        self.inputs = [input for input in node.inputs.values() if all([not input.hide, input.enabled, not input.is_unavailable])]

        print(self.inputs)

        self.anchors = {}

        # process header
        self.uiheader = UIHeader(self.name, self.w, color=color_string)


        # new Widget stack method + coords
        self.height_widget_pairs = []
        self.height = self.uiheader.height + constants.TOP_PADDING

        def register_widget(widget):
            self.height_widget_pairs.append((self.height, widget))
            self.height += widget.height() + constants.SOCKET_GAP

        def make_socket_widget(socket, is_offset):
            self.anchors[socket.as_pointer()] = (
                self.x + (self.w if is_offset else 0),
                self.y+self.height+constants.LINKED_SOCKET_HEIGHT/2,
                UIShape(socket))
            print("registering widget", widgetFactory(socket))
            register_widget(widgetFactory(socket))

        for out_socket in self.outputs:
            make_socket_widget(out_socket, True)
        
        register_widget(widgets.Placeholder())

        for in_socket in self.inputs:
            make_socket_widget(in_socket, False)

        # adjust node height
        self.h = max(self.h, self.height+constants.BOTTOM_PADDING)

        print(self.height_widget_pairs)


        ##### VVVV NO LONGER NEEDED VVVV ??

        # process sockets ahead of time
        self.uioutputs = [socketFactory(socket) for socket in self.outputs]
        self.uiinputs = [socketFactory(socket) for socket in self.inputs]


        self.output_coords = []
        next_output_coord = self.uiheader.height + constants.TOP_PADDING
        for output in self.uioutputs:
            self.output_coords.append(next_output_coord)
            next_output_coord += output.height + constants.SOCKET_GAP

        self.input_coords = []
        #TODO: padding from bottom is inconsistent across nodes👍👍
        next_input_coord = self.h - constants.TOP_PADDING
        for input in self.uiinputs[::-1]:
            next_input_coord -= input.height
            self.input_coords.append(next_input_coord)
            next_input_coord -= constants.SOCKET_GAP

        self.input_coords.reverse()


    def get_socket_coords(self):
        self.socket_coords = {}
        for coord, uisocket in zip(self.output_coords + self.input_coords, self.uioutputs + self.uiinputs):
            offset = 0 if not uisocket.socket.is_output else self.w
            self.socket_coords[str(uisocket.socket.as_pointer())] = (self.x+offset,self.y+coord+(0.5)*constants.LINKED_SOCKET_HEIGHT,constants.SOCKET_COLORS[uisocket.socket.type])
        return self.socket_coords

    def svg(self) -> ET.Element:
        group = ET.Element('svg', x=f"{self.x}", y=f"{self.y}")
        
        # frame
        rect = self.frame()
        group.append(rect)

        # header
        group.append(self.uiheader.svg())

        # new widgets rendering
        group.extend([widget.svg(width=self.w, y=str(height)) for height, widget in self.height_widget_pairs])

        return group

    def frame(self) -> ET.Element:
        frame_items = ET.Element('svg')

        bg = ET.Element('rect', width=f"{self.w}", height=f"{self.h}")
        bg.set('class', 'nodeframe')

        frame_items.append(bg)

        return frame_items

# class of SVG for a node header
class UIHeader():

    PADDING = 6

    def __init__(self, name, width=100, height=constants.HEADER_HEIGHT, color="gray"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color

    def svg(self) -> ET.Element:
        group = ET.Element('g', id=f"Header {self.name}")
        rect = ET.Element('rect', width=f"{self.width}", height=f"{self.height}")
        
        rect.set("fill", self.color)
        rect.set("stroke", "none")
        group.append(rect)

        label = ET.Element('text', x=f"{self.PADDING}", y=f"{self.height*3/4}")
        label.text = self.name
        group.append(label)

        return group
    
class UIShape():

    shapes = {
        "C": "circle",
        "D": "diamond",
        "S": "square"
    }

    def __init__(self, socket):
        self.shape = self.shapes[socket.display_shape[0]]
        self.has_dot = socket.display_shape[-1] == "T"
        self.color = constants.SOCKET_COLORS[socket.type]

    def svg(self, **kwargs):
        group = ET.Element('svg', attrib=kwargs)

        ET.SubElement(group, 'use', href=f'#marker_{self.shape}', fill=self.color)
        if self.has_dot: ET.SubElement(group, 'use', href=f'#marker_dot', fill='black', stroke='none')

        return group