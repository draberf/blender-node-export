import importlib

from . import constants
importlib.reload(constants)

from . import categories

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
        "rect { stroke: red; stroke-width: 0 }",
        ".marker { stroke-width: "+str(constants.MARKER_LINE)+"px; stroke: black}"
    ])

    return style_elem


def socketFactory(socket: bpy.types.NodeSocket) -> 'UISocket':
    match socket.type:
        case "VALUE":
            return UISocketValue(socket)
        case "RGBA":
            return UISocketRGBA(socket)
        case "VECTOR":
            return UISocketVector(socket)
        case "INT":
            return UISocketInt(socket)
        case "IMAGE":
            return UISocketImage(socket)
        case "OBJECT":
            return UISocketObject(socket)
        case "TEXTURE":
            return UISocketTexture(socket)
        case "COLLECTION":
            return UISocketCollection(socket)
        case "GEOMETRY":
            return UISocketGeometry(socket)
        case "MATERIAL":
            return UISocketMaterial(socket)
        case "STRING":
            return UISocketString(socket)
        case "BOOLEAN":
            return UISocketBoolean(socket)
        case _:
            return UISocket(socket)


# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"
    

# encompassing SVG class
class UI:

    def svg(self):
        return ET.Element('svg')

class UINodeTree(UI):

    def __init__(self, nodetree, context) -> None:
        
        self.curving = context.preferences.themes[0].node_editor.noodle_curving
        self.nodes = nodetree.nodes
        self.links = nodetree.links


    def svg(self):
        
        PADDING = constants.VIEWBOX_PADDING

        svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")

        svg.append(style())

        # add symbols

        for sym_name, (elem_name, elem_attrs) in MARKER_DEFS.items():
            symbol = ET.SubElement(svg, 'symbol', id='marker_'+sym_name)
            ET.SubElement(symbol, elem_name, attrib=elem_attrs)

        


        viewBox_minX, viewBox_minY = self.nodes[0].location
        viewBox_maxX, viewBox_maxY = self.nodes[0].location

        link_mapping = {}
        ui_nodes = []
        ui_anchors = []

        for i, node in enumerate(self.nodes):
            
            ui_node = UINode(node)
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
        fac = self.curving/10.0
        for link in self.links:
            from_x, from_y = link_mapping[str(link.from_socket.as_pointer())]
            to_x, to_y = link_mapping[str(link.to_socket.as_pointer())]
            diff_x = abs(to_x - from_x)
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {from_x + fac*diff_x},{from_y} {to_x - fac*diff_x},{to_y} {to_x},{to_y}",
                            style="stroke:#000000;stroke-width:4;fill:none")
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {from_x + fac*diff_x},{from_y} {to_x - fac*diff_x},{to_y} {to_x},{to_y}",
                            style=f"stroke:#ffffff;stroke-width:2;fill:none")

        svg.extend(ui_nodes)
        svg.extend(ui_anchors)        

        svg.set("viewBox", f"{viewBox_minX-PADDING} {viewBox_minY-PADDING} {viewBox_maxX-viewBox_minX+PADDING} {viewBox_maxY-viewBox_minY+PADDING}")

        return svg        

# class wrapper for a single node
class UINode(UI):

    def __init__(self, node: bpy.types.Node):
        self.node = node
        self.name = node.label if node.label else node.name
        self.w, self.h = node.dimensions
        self.w *= constants.NODE_DIM_RATIO
        self.h *= constants.NODE_DIM_RATIO
        self.x =  node.location[0]
        self.y = -node.location[1]
        self.sockets = self.sockets_like()
        self.socket_count = len(self.sockets)
        self.socket_coords = {}

        # process header
        self.uiheader = UIHeader(self.name, self.w)

        # process sockets ahead of time
        self.uioutputs = [socketFactory(socket) for socket in self.outputs()]
        self.uiinputs = [socketFactory(socket) for socket in self.inputs()]


        self.output_coords = []
        next_output_coord = self.uiheader.height + constants.TOP_PADDING
        for output in self.uioutputs:
            self.output_coords.append(next_output_coord)
            next_output_coord += output.height + constants.SOCKET_GAP

        self.input_coords = []
        next_input_coord = self.h - constants.BOTTOM_PADDING
        for input in self.uiinputs[::-1]:
            next_input_coord -= input.height
            self.input_coords.append(next_input_coord)
            next_input_coord -= constants.SOCKET_GAP

        self.input_coords.reverse()


    def get_socket_coords(self):
        self.socket_coords = {}
        for coord, uisocket in zip(self.output_coords + self.input_coords, self.uioutputs + self.uiinputs):
            offset = 0 if not uisocket.socket.is_output else self.w
            self.socket_coords[str(uisocket.socket.as_pointer())] = (self.x+offset,self.y+coord+(0.5)*constants.LINKED_SOCKET_HEIGHT)
        return self.socket_coords

    def sockets_like(self) -> list[bpy.types.NodeSocket]:
        return self.outputs() + self.inputs()

    def outputs(self) -> list[bpy.types.NodeSocket]:
        return [output for output in self.node.outputs.values() if all([not output.hide, output.enabled, not output.is_unavailable])]
    
    def inputs(self) -> list[bpy.types.NodeSocket]:
        return [input for input in self.node.inputs.values() if all([not input.hide, input.enabled, not input.is_unavailable])]

    def svg(self) -> ET.Element:
        group = ET.Element('svg', x=f"{self.x}", y=f"{self.y}")
        
        # frame
        rect = self.frame()
        group.append(rect)


        # header
        uiheader = self.uiheader
        header_svg = uiheader.svg()

        # anchors
        anchorlist = []

        group.append(header_svg)
        
        for coord, uisocket in zip(self.output_coords, self.uioutputs):
            svg, anchor = uisocket.svg(width=self.w)
            anchor.set("x", str(self.x + self.w - constants.MARKER_SIZE/2))
            anchor.set("y", str(self.y + coord + constants.LINKED_SOCKET_HEIGHT/2 - constants.MARKER_BOX_HALF))
            anchorlist.append(anchor)
            svg.set("y", str(coord))
            group.append(svg)

        for coord, uisocket in zip(self.input_coords, self.uiinputs):
            svg, anchor = uisocket.svg(width=self.w)
            anchor.set("x", str(self.x - constants.MARKER_SIZE/2))
            anchor.set("y", str(self.y + coord + constants.LINKED_SOCKET_HEIGHT/2 - constants.MARKER_BOX_HALF))
            anchorlist.append(anchor)
            svg.set("y", str(coord))
            group.append(svg)

        print(anchorlist)
        return group, anchorlist

    def frame(self) -> ET.Element:
        frame_items = ET.Element('svg')

        bg = ET.Element('rect', width=f"{self.w}", height=f"{self.h}")
        bg.set('class', 'nodeframe')

        frame_items.append(bg)
        


        return frame_items


# class for SVG of a socket
class UISocket(UI):
    
    # constants: TODO change
    PADDING = 10

    def __init__(self, socket: bpy.types.NodeSocket, height: float = constants.LINKED_SOCKET_HEIGHT) -> None:
        self.socket = socket
        self.height = height
        self.name = socket.label if socket.label else socket.name

    # generic svg function
    def svg(self, width: float = 100) -> ET.Element:
        if self.socket.is_linked or self.socket.is_output or self.socket.hide_value:
            return self.svg_linked(width), UIShape(self.socket).svg()
        else:
            return self.svg_unlinked(width), UIShape(self.socket).svg()

    # generic linked version
    def svg_linked(self, width: float = 100) -> ET.Element:
        group = ET.Element('svg', id=f"Socket {self.socket.name}")
        # p272
        label = ET.Element('text')
        label.text = self.name
        label.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        if self.socket.is_output:
            label.set("text-anchor", "end")
            label.set("x", f"{width - self.PADDING}")
        else:
            label.set("x", f"{self.PADDING}")
        group.append(label)
        return group

    # specific unlinked version (varies from socket to socket)
    def svg_unlinked(self, width: float = 100) -> ET.Element:
        return self.svg_linked(width)
        
    

# SVG socket subclass: VALUE
class UISocketValue(UISocket):

    def svg_unlinked(self,width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        value = ET.Element('text')
        value.text = getFloatString(self.socket.default_value)
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: RGBA
class UISocketRGBA(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        color_rect = ET.Element('rect')
        color_rect.set("x", str(0.45*width))
        color_rect.set("y", "0")
        color_rect.set("width", str(0.5*width))
        color_rect.set("height", str(self.height))
        color_rect.set("style", "stroke-width: 0")
        color_rect.set("fill", "rgb("+",".join([str(round(x*255)) for x in self.socket.default_value[:3]])+")")
        group.append(color_rect)
        return group
    
# SVG socket subclass: VECTOR
class UISocketVector(UISocket):

    def __init__(self, socket: bpy.types.NodeSocket, height: float = constants.LINKED_SOCKET_HEIGHT) -> None:
        super().__init__(socket, height)
        self.height = 4*height if not self.socket.hide_value else height

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        for i, val in enumerate(self.socket.default_value):
            value = ET.Element('text')
            value.text = getFloatString(val)
            value.set("y", f"{(i+1)*constants.LINKED_SOCKET_HEIGHT + constants.SOCKET_TEXT_HEIGHT}")
            value.set("text-anchor", "end")
            value.set("x", f"{width - self.PADDING}")
            group.append(value)
        return group

# SVG socket subclass: INT
class UISocketInt(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        value = ET.Element('text')
        value.text = str(self.socket.default_value)
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: IMAGE
class UISocketImage(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        if not self.socket.default_value:
            return group
        value = ET.Element('text')
        # check enum
        match self.socket.default_value.source:
            case 'FILE' | 'SEQUENCE' | 'MOVIE':
                value.text = self.socket.default_value.filepath
            case _:
                value.text = self.socket.default_value.source
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: OBJECT
class UISocketObject(UISocket):
    
    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        value = ET.Element('text')
        value.text = self.socket.default_value.name
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: TEXTURE
class UISocketTexture(UISocket):
    
    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        if not self.socket.default_value: return group
        value = ET.Element('text')
        value.text = self.socket.default_value.name
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: COLLECTION
class UISocketCollection(UISocket):
    
    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        if not self.socket.default_value: return group
        value = ET.Element('text')
        value.text = self.socket.default_value.name
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: GEOMETRY
class UISocketGeometry(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        return super().svg_unlinked(width)

# SVG socket subclass: MATERIAL
class UISocketMaterial(UISocket):
    
    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        if not self.socket.default_value: return group
        value = ET.Element('text')
        value.text = self.socket.default_value.name
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group

# SVG socket subclass: STRING
class UISocketString(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        value = ET.Element('text')
        value.text = self.socket.default_value
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
        return group
    
# SVG socket subclass: BOOLEAN
class UISocketBoolean(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        group[0].set("x", f"{self.PADDING + constants.LINKED_SOCKET_HEIGHT}")
        rect = ET.Element('rect')
        rect.set('x', f"{self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('y', f"{constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('width',  f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        rect.set('height', f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        #rect.set('class', 'bool_rect')
        rect.set('stroke', 'none')
        group.append(rect)

        if self.socket.default_value:
            rect.set('fill', '#7777dd')
            check = ET.Element('polyline', fill='none', stroke='white')
            check.set('stroke-width', "1")
            check.set('points', f"{self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.4}, {constants.LINKED_SOCKET_HEIGHT*0.5},\
                      {self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.5}, {constants.LINKED_SOCKET_HEIGHT*0.6},\
                        {self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.7}, {constants.LINKED_SOCKET_HEIGHT*0.3}")
            group.append(check)
        else:
            rect.set('fill', '#222222')
        
        return group


# class of SVG for a node header
class UIHeader(UI):

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
    
class UIShape(UI):

    shapes = {
        "C": "circle",
        "D": "diamond",
        "S": "square"
    }

    def __init__(self, socket):
        self.shape = self.shapes[socket.display_shape[0]]
        self.has_dot = socket.display_shape[-1] == "T"
        self.color = constants.SOCKET_COLORS[socket.type]

    def svg(self):
        group = ET.Element('svg')

        ET.SubElement(group, 'use', href=f'#marker_{self.shape}', fill=self.color)
        if self.has_dot: ET.SubElement(group, 'use', href=f'#marker_dot', fill='black', stroke='none')

        return group
        return ET.Element('rect', width=f"{constants.MARKER_SIZE}", height=f"{constants.MARKER_SIZE}", fill=self.color, stroke="none")