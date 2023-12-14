import bpy
import mathutils
import xml.etree.ElementTree as ET

# in: mathutils.Color with r, g, b, methods
# out: color representation in SVG-compliant format
def blColorToSVGColor(color: mathutils.Color) -> str:
    r, g, b = color.r, color.g, color.b
    # compliant with specification at p85
    return "rgb("+",".join([str(round(x*255)) for x in [r,g,b]])+")"
    

class UI:

    def svg(self):
        return ET.Element('g')

class UINode(UI):

    node : bpy.types.Node
    w : float
    h : float
    x : float
    y : float

    HEADER_HEIGHT = 25

    def __init__(self, node: bpy.types.Node):
        self.node = node
        self.w, self.h = node.dimensions
        self.x =  node.location[0]
        self.y = -node.location[1]
        self.sockets = self.sockets_like()
        self.socket_count = len(self.sockets)

    def sockets_like(self) -> [bpy.types.NodeSocket]:
        return self.node.outputs.values() + self.node.inputs.values()

    def outputs(self) -> [bpy.types.NodeSocket]:
        return self.node.outputs.values()
    
    def inputs(self) -> [bpy.types.NodeSocket]:
        return self.node.inputs.values()

    def svg(self) -> ET.Element:
        group = ET.Element('g', transform=f"translate({self.x},{self.y})")

        # frame
        rect = ET.Element('rect', width=f"{self.w}", height=f"{self.h}", fill="gray", stroke="black")
        rect.set("stroke-width", "5")
        group.append(rect)

        # header
        uiheader = UIHeader(self.node.name, self.w)
        header_svg = uiheader.svg()

        group.append(header_svg)
        

        for i, socket in enumerate([output for output in self.outputs() if not output.hide]):
            uisocket = UISocket(socket, width=self.w)
            svg = uisocket.svg()
            svg.set("transform", f"translate(0,{uiheader.height + i*uisocket.height})")
            group.append(svg)
        for i, socket in enumerate([input for input in self.inputs() if not input.hide]):
            uisocket = UISocket(socket, width=self.w)
            svg = uisocket.svg()
            svg.set("transform", f"translate(0,{self.h - (len(self.inputs()) + i)*uisocket.height})")
            group.append(svg)
        return group

class UISocket(UI):
    
    PADDING = 6

    socket : bpy.types.NodeSocket
    width : float
    height : float

    def __init__(self, socket: bpy.types.NodeSocket, width: float = 100, height: float = 25) -> None:
        self.socket = socket
        self.width = width
        self.height = height

    def svg(self) -> ET.Element:
        group = ET.Element('g', id=f"Socket {self.socket.name}")
        rect = ET.Element('rect', width=f"{self.width}", height=f"{self.height}", fill="none", stroke="black")
        rect.set("stroke-width", "5")
        group.append(rect)
        # p272
        label = ET.Element('text', x=f"{self.PADDING}", y=f"{self.height/2}")
        label.text = self.socket.name
        group.append(label)
        return group
    
class UIHeader(UI):

    PADDING = 6

    def __init__(self, name, width=100, height=20, color="gray"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color

    def svg(self) -> ET.Element:
        group = ET.Element('g', id=f"Header {self.name}")
        rect = ET.Element('rect', width=f"{self.width}", height=f"{self.height}")
        
        rect.set("fill", self.color)
        rect.set("stroke", "black")
        rect.set("stroke-width", "5")
        group.append(rect)

        label = ET.Element('text', x=f"{self.PADDING}", y=f"{self.height/2}")
        label.text = self.name
        group.append(label)

        return group