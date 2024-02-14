import importlib
from . import constants
importlib.reload(constants)

import bpy
import mathutils
import xml.etree.ElementTree as ET

def socketFactory(socket: bpy.types.Socket) -> 'UISocket':
    match socket.type:
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

    HEADER_HEIGHT = 25

    def __init__(self, node: bpy.types.Node):
        self.node = node
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

        # frame
        rect = ET.Element('rect', width=f"{self.w}", height=f"{self.h}", fill=blColorToSVGColor(self.node.color), stroke="black")
        rect.set("stroke-width", "5")

        group.append(rect)

        # header
        uiheader = UIHeader(self.node.name, self.w)
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
        label.text = self.socket.name
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
    
class UISocketVector(UISocket):

    def svg_unlinked(self, width: float = 100) -> ET.Element:
        group = self.svg_linked(width)
        value = ET.Element('text')
        value.text = "(" + ', '.join([getFloatString(val) for val in self.socket.default_value]) + ")"
        value.set("y", f"{constants.SOCKET_TEXT_HEIGHT}")
        value.set("text-anchor", "end")
        value.set("x", f"{width - self.PADDING}")
        group.append(value)
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