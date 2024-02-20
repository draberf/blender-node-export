import importlib
from . import constants
importlib.reload(constants)

import bpy
import mathutils
import xml.etree.ElementTree as ET

def getFloatString(value: float, spaces: int = 5) -> str:

    s = str(value)[:5]
    s += (5-len(s))*"0"
    return s

def style() -> ET.Element:
    
    style_elem = ET.Element('style')

    style_elem.text = '\n'.join([
        ".nodeframe { fill: #333333 } ",
        "text { font-family: Sans, Arial; font-size: 0.6em; fill: white }"
        "rect { stroke: red; stroke-width: 0 }"
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
        return ET.Element('g')

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

    def get_socket_coords(self):
        self.socket_coords = {}
        for i, socket in enumerate(self.outputs()):
            self.socket_coords[str(socket.as_pointer())] = (self.x+self.w,self.y+(i+0.5)*constants.LINKED_SOCKET_HEIGHT + constants.HEADER_HEIGHT)
        for i, socket in enumerate(self.inputs()[::-1]):
            self.socket_coords[str(socket.as_pointer())] = (self.x, self.y+self.h-(i+0.5)*constants.LINKED_SOCKET_HEIGHT)
        return self.socket_coords

    def sockets_like(self) -> list[bpy.types.NodeSocket]:
        return self.outputs() + self.inputs()

    def outputs(self) -> list[bpy.types.NodeSocket]:
        return [output for output in self.node.outputs.values() if all([not output.hide, output.enabled, not output.is_unavailable])]
    
    def inputs(self) -> list[bpy.types.NodeSocket]:
        return [input for input in self.node.inputs.values() if all([not input.hide, input.enabled, not input.is_unavailable])]

    def svg(self) -> ET.Element:
        group = ET.Element('svg', x=f"{self.x}", y=f"{self.y}")
        
        # style
        group.append(style())

        # frame
        rect = self.frame()
        group.append(rect)


        # header
        uiheader = UIHeader(self.name, self.w)
        header_svg = uiheader.svg()

        group.append(header_svg)
        

        for i, socket in enumerate([output for output in self.outputs() if not output.hide]):
            uisocket = socketFactory(socket)
            svg = uisocket.svg(width=self.w)
            svg.set("transform", f"translate(0,{uiheader.height + i*uisocket.height})")
            group.append(svg)
        for i, socket in enumerate([input for input in self.inputs() if not input.hide]):
            uisocket = socketFactory(socket)
            svg = uisocket.svg(width=self.w)
            svg.set("transform", f"translate(0,{self.h - (len(self.inputs()) - i)*uisocket.height})")
            group.append(svg)
        return group

    def frame(self) -> ET.Element:
        frame_items = ET.Element('svg')

        bg = ET.Element('rect', width=f"{self.w}", height=f"{self.h}")
        bg.set('class', 'nodeframe')

        frame_items.append(bg)
        


        return frame_items


# class for SVG of a socket
class UISocket(UI):
    
    # constants: TODO change
    PADDING = 6

    def __init__(self, socket: bpy.types.NodeSocket, height: float = constants.LINKED_SOCKET_HEIGHT) -> None:
        self.socket = socket
        self.height = height
        self.name = socket.label if socket.label else socket.name

    # generic svg function
    def svg(self, width: float = 100) -> ET.Element:
        if self.socket.is_linked or self.socket.is_output:
            return self.svg_linked(width)
        else:
            return self.svg_unlinked(width)

    # generic linked version
    def svg_linked(self, width: float = 100) -> ET.Element:
        group = ET.Element('g', id=f"Socket {self.socket.name}")
        rect = ET.Element('rect', width=f"{width}", height=f"{self.height}", fill="none", stroke="none")
        group.append(rect)
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
        self.height = 4*height

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

        label = ET.Element('text', x=f"{self.PADDING}", y=f"{self.height/2}")
        label.text = self.name
        group.append(label)

        return group