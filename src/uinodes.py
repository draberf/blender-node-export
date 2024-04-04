import importlib

from . import constants
from . import categories
from . import widgets
from . import methods

import bpy
import xml.etree.ElementTree as ET

from colorsys import rgb_to_hsv, hsv_to_rgb
from math import sin, cos, pi

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

ARROW_DEFS = {
    'left':('polyline',{
        'points': '5 2 2 5 5 8',
        'class': 'arrow'
    }),
    'right':('polyline',{
        'points': '5 2 8 5 5 8',
        'class': 'arrow'
    }),
    'down':('polyline', {
        'points': '2 5 5 8 8 5',
        'class': 'arrow'
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
        ".marker { stroke-width: "+str(constants.MARKER_LINE)+"px; stroke: black}",
        ".arrow { stroke-width: 1; stroke: white; fill:none}"
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

def value_socket(socket) -> widgets.Widget:
    prop = socket.bl_rna.properties['default_value']
    if prop.subtype == 'FACTOR':
        return widgets.Float(socket.name, socket.default_value, minmax=(prop.soft_min, prop.soft_max))
    else:
        return widgets.Float(socket.name, socket.default_value)

# convert unconnected input socket to widget
SOCKET_WIDGET_DEFS = {
    'VALUE': lambda socket: value_socket(socket),
    'FLOAT': lambda socket: widgets.Float(name=socket.name, value=socket.default_value),
    'RGBA': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.RGBA(color="rgb("+",".join([str(round(x*255)) for x in socket.default_value[:3]])+")")
    ]),
    'VECTOR': lambda socket: widgets.Vector(name=socket.name, values=socket.default_value) if not socket.hide_value else widgets.Label(text=socket.name),
    'INT': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.Label(text=str(socket.default_value), alignment='R')
    ]),
    'IMAGE': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.Label(text=getImageWidgetString(socket), alignment='R')
    ]),
    'OBJECT': lambda socket: widgets.String(value="" if not socket.default_value else socket.default_value.name),
    'TEXTURE': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.Label(text=getObjectName(socket), alignment='R')
    ]),
    'COLLECTION': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.Label(text=getObjectName(socket), alignment='R')
    ]),
    'GEOMETRY': lambda socket: widgets.Label(text=socket.name),
    'SHADER': lambda socket: widgets.Label(text=socket.name),
    'MATERIAL': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.Label(text=getObjectName(socket), alignment='R')
    ]),
    'STRING': lambda socket: widgets.String(value=socket.default_value, name=socket.name),
    'BOOLEAN': lambda socket: widgets.Boolean(name=socket.name, value=socket.default_value),
    'CUSTOM': lambda socket: widgets.Label(text=socket.name)
}

def widgetFactory(socket) -> widgets.Widget:
    
    if socket.is_output or socket.is_linked:
        return widgets.Label(text=socket.name, alignment='R')

    return SOCKET_WIDGET_DEFS[socket.type](socket)

def nodeFactory(node, colors) -> 'UINode':

    match node.bl_idname:
        case 'NodeFrame':
            return UIFrameNode(node)
        case 'NodeReroute':
            return UIRedirectNode(node, colors=colors)
        case _:
            return UINode(node, colors=colors)

class Converter():

    def __init__(self, context) -> None:
        
        nodetree = context.space_data.node_tree
        self.colors = {k:methods.blColorToSVGColor(v) for k, v in [
            (k, getattr(context.preferences.themes[0].node_editor, k)) for k in categories.CATEGORIES
        ]}
        self.colors.update({'switch_node': 'gray'})

        self.nodes = []
        self.node_frames = []

        self.links = [
            (link.from_socket.as_pointer(), link.to_socket.as_pointer(), False) for link in nodetree.links
        ]

        self.curving = context.preferences.themes[0].node_editor.noodle_curving

        self.anchor_refs = {}


        self.vb_min_x =  nodetree.nodes[0].location[0]
        self.vb_min_y = -nodetree.nodes[0].location[1]
        self.vb_max_x =  nodetree.nodes[0].location[0]
        self.vb_max_y = -nodetree.nodes[0].location[1]


        frame_ptrs = {}
        frame_children = {}
        for node in nodetree.nodes:

            print(node.bl_idname, node.as_pointer())
            
            node_object = nodeFactory(node, self.colors)


            self.anchor_refs.update(node_object.anchors)
            if node.bl_idname == 'NodeFrame':
                self.node_frames.append(node_object)
                frame_ptrs[node.as_pointer()] = node_object
            else:
                self.nodes.append(node_object)

            print(node.parent)
            if node.parent:
                ptr = node.parent.as_pointer()
                if not ptr in frame_children:
                    frame_children[ptr] = [node_object]
                else:
                    frame_children[ptr].append(node_object)
                print(frame_children)

            if node.mute:
                self.links.extend([(link.from_socket.as_pointer(), link.to_socket.as_pointer(), True) for link in node.internal_links])

        # process frame sizes
        for ptr, frame in frame_ptrs.items():
            if ptr in frame_children:
                frame.children = frame_children[ptr]

        for frame in frame_ptrs.values():
            frame.updateDimensions()

    def makeDefs(self) -> ET.Element:

        defs = ET.Element('defs')

        defs.append(style())

        # add symbols

        ## markers
        for sym_name, (elem_name, elem_attrs) in MARKER_DEFS.items():
            symbol = ET.SubElement(defs, 'symbol', id='marker_'+sym_name)
            ET.SubElement(symbol, elem_name, attrib=elem_attrs)

        ## arrows
        for sym_name, (elem_name, elem_attrs) in ARROW_DEFS.items():
            symbol = ET.SubElement(defs, 'symbol', id=sym_name+'_arrow')
            arrow = ET.SubElement(symbol, elem_name, attrib=elem_attrs)

        ## color wheel
        color_wheel = ET.SubElement(defs, 'symbol', id='color_wheel')
        grp = ET.SubElement(color_wheel, 'svg', viewBox='-50 -50 100 100', width='90', height='90')
        steps=24
        def angleToCoords(angle, radius):
            return radius*cos(angle), radius*sin(angle)
        for i in range(24):
            point1_x, point1_y = angleToCoords(i*2*pi/steps, 50)
            point2_x, point2_y = angleToCoords((i+1)*2*pi/steps, 50)
            color = methods.socketColorToSVGColor(hsv_to_rgb((0.75 + i/steps), 1.0, 1.0))
            ET.SubElement(grp, 'polygon', points=f"0 0 {point1_x} {point1_y} {point2_x} {point2_y}", style=f"fill:{color}; stroke:none")

        ## hue correct gradient
        grad = ET.SubElement(defs, 'linearGradient', id='hc_grad', x1='0', x2='1', y1='0', y2='0')
        for i in range(7):
            prog = i/6.0
            ET.SubElement(grad, 'stop', attrib={'offset':  str(prog), 'stop-color':methods.socketColorToSVGColor(hsv_to_rgb(prog, 1.0, 1.0))})


        return defs


    def convert(self) -> ET.ElementTree:
        
        svg = ET.Element('svg', version="1.1", xmlns="http://www.w3.org/2000/svg")

        svg.append(self.makeDefs())


        # add node frames to final SVG
        for frame in self.node_frames:
            svg.append(frame.svg())

        for node in self.nodes+self.node_frames:
            
            self.vb_min_x = min(self.vb_min_x, node.x)
            self.vb_min_y = min(self.vb_min_y, node.y)
            self.vb_max_x = max(self.vb_max_x, node.x+node.w)
            self.vb_max_y = max(self.vb_max_y, node.y+node.h)


        # update viewbox based on rendered links
        svg_w = self.vb_max_x-self.vb_min_x
        svg_h = self.vb_max_y-self.vb_min_y

        # add links to final SVG
        fac = self.curving/10.0
        for link in self.links:
            
            from_x, from_y, from_anchor_object = self.anchor_refs[link[0]]
            to_x, to_y, _ = self.anchor_refs[link[1]]
            is_muted = link[2]

            opacity = '100%' if not is_muted else '20%'

            color1 = from_anchor_object.color

            diff_x = abs(to_x - from_x)
            control_x1 = from_x + fac*diff_x
            control_x2 = to_x - fac*diff_x

            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {control_x1},{from_y} {control_x2},{to_y} {to_x},{to_y}",
                            style=f"stroke:#000000;stroke-width:4;fill:none;opacity:{opacity}")
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {control_x1},{from_y} {control_x2},{to_y} {to_x},{to_y}",
                            style=f"stroke:{color1};stroke-width:2;fill:none;opacity:{opacity}")
            
            if self.curving > 0 and from_x > to_x:
                x1, x2 = methods.getBezierExtrema(from_x, control_x1, control_x2, to_x)
                print(x1, x2)
                self.vb_min_x = min(self.vb_min_x, min(x1, x2))
                svg_w = max(svg_w, max(x1-self.vb_min_x, x2-self.vb_min_x))



        svg.set('width',  str(svg_w))
        svg.set('height', str(svg_h))
        svg.set('viewBox', ' '.join([str(f) for f in [
            self.vb_min_x - constants.VIEWBOX_PADDING,
            self.vb_min_y - constants.VIEWBOX_PADDING,
            svg_w + 2*constants.VIEWBOX_PADDING,
            svg_h + 2*constants.VIEWBOX_PADDING
        ]]))        

        # add nodes to final SVG
        for node in self.nodes:
            try:
                out = node.svg()
                if out: svg.append(out)
            except Exception as e:
                print(node.name)
                raise e

        # add anchors to final SVG
        for x, y, anchor in self.anchor_refs.values():
            out = anchor.svg(x=str(x-constants.MARKER_BOX_HALF), y=str(y-constants.MARKER_BOX_HALF))
            if not out: continue
            svg.append(out)

        tree = ET.ElementTree(svg)
        ET.indent(tree)

        return tree

# class wrapper for a single node
class UINode():

    def __init__(self, node: bpy.types.Node, colors: {str}):
        specification = {}
        self.is_placeholder = False
        if not node.bl_idname in categories.node_specifications:
            specification = categories.node_specifications['PlaceholderNode']
            self.is_placeholder = True
        else:
            specification = categories.node_specifications[node.bl_idname]

        self.name = node.name
        if node.label:
            self.name = node.label
        elif 'name_behavior' in specification:
            self.name = specification['name_behavior'](node)
        self.w, self.h = node.dimensions
        self.w *= constants.NODE_DIM_RATIO
        self.h *= constants.NODE_DIM_RATIO
        self.x =  node.location[0]
        self.y = -node.location[1]
        if node.parent:
            self.x += node.parent.location[0]
            self.y -= node.parent.location[1]
        self.outputs = [output for output in node.outputs.values() if all([not output.hide, output.enabled, not output.is_unavailable])]
        self.inputs = [input for input in node.inputs.values() if all([not input.hide, input.enabled, not input.is_unavailable])]

        self.muted = node.mute
        

        self.anchors = {}


        # process header
        if not self.is_placeholder:
            self.color_class = specification['class'] if specification['class'] else specification['class_behavior'](node)
        else:
            print(f"WARNING: Node {node.bl_idname} does not have a default specification. Placeholder object will be used instead.")
            self.color_class = 'switch_node'

        self.uiheader = UIHeader(self.name, self.w, color=colors[self.color_class])


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
            try:
                register_widget(widgetFactory(socket))
            except AttributeError:
                raise Exception(node.name)


        for out_socket in self.outputs:
            make_socket_widget(out_socket, True)
        
        if specification:
            if 'props' in specification:
                for widget in specification['props'](node):
                    if not widget: continue
                    register_widget(widget)
        else:
            register_widget(widgets.Placeholder())

        for in_socket in self.inputs:
            make_socket_widget(in_socket, False)

        # adjust node height
        self.h = max(self.h, self.height+constants.BOTTOM_PADDING)

    def is_frame(self) -> bool:
        return False


    def svg(self) -> ET.Element:
        group = ET.Element('svg', x=f"{self.x}", y=f"{self.y}", width=str(self.w), height=str(self.h), viewBox=f"0 0 {self.w} {self.h}")
        if self.muted: group.set('opacity', '50%')
        
        # frame
        rect = self.frame()
        group.append(rect)

        # header
        group.append(self.uiheader.svg())

        # new widgets rendering
        group.extend([widget.svg(width=self.w, attrib={'y':str(height)}) for height, widget in self.height_widget_pairs])

        return group

    def frame(self) -> ET.Element:
        frame_items = ET.Element('svg')

        bg = ET.Element('rect', width=f"{self.w}", height=f"{self.h}")
        bg.set('class', 'nodeframe')

        frame_items.append(bg)

        return frame_items

class UIRedirectNode(UINode):

    def __init__(self, node: bpy.types.Node, colors: str):
        
        self.name = "Redirect Node"

        self.muted = False

        self.w, self.h = 0, 0
        self.x =  node.location[0]
        self.y = -node.location[1]
        if node.parent:
            self.x += node.parent.location[0]
            self.y -= node.parent.location[1]

        self.anchors = {node.inputs[0].as_pointer(): (self.x, self.y, UIShape(node.inputs[0]))}
        self.anchors.update({output.as_pointer(): (self.x, self.y, UIShape(output, render=False)) for output in node.outputs})
    
    def svg(self):
        return None

class UIFrameNode(UINode):

    def __init__(self, node: bpy.types.Node):
        
        self.name = ""
        if node.label:
            self.name = node.label

        self.w, self.h = node.dimensions
        self.w *= constants.NODE_DIM_RATIO
        self.h *= constants.NODE_DIM_RATIO
        self.x =  node.location[0] - self.w/2 + 70.0
        self.y = -node.location[1] - self.h/2 + 50.0
        if node.parent:
            self.x += node.parent.location[0]
            self.y -= node.parent.location[1]

        self.color = 'black' if not node.use_custom_color else methods.socketColorToSVGColor(node.color)

        self.children = []
        self.boundaries_set = False

        self.anchors = {}

    def is_frame(self) -> bool:
        return True
    
    def updateDimensions(self) -> None:
        
        if self.boundaries_set: return
        
        for node in self.children:
            if node.is_frame():
                node.updateDimensions()
            self.x = min(self.x, node.x-40)
            self.y = min(self.y, node.y-40)
            self.w = max(self.w, (node.x+node.w)-self.x+40)
            self.h = max(self.h, (node.y+node.h)-self.y+40)

        self.boundaries_set = True


    def svg(self) -> ET.Element:
        group = ET.Element('svg', x=f"{self.x}", y=f"{self.y}", width=str(self.w), height=str(self.h), viewBox=f"0 0 {self.w} {self.h}")
        
        ET.SubElement(group, 'rect', attrib={
            'x': '0',
            'y': '0',
            'width': str(self.w),
            'height': str(self.h),
            'style':f'fill:{self.color};stroke:none'
        })

        if self.name:
            text = ET.SubElement(group, 'text', attrib={
                'x':str(self.w/2),
                'y':str(constants.LINKED_SOCKET_HEIGHT),
                'text-anchor':'middle'
            })
            text.text = self.name

        return group

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
        rect = ET.SubElement(group, 'rect', attrib={
            'width':f'{self.width}',
            'height':f'{self.height}',
            'opacity':'60%',
            'fill':self.color,
            'stroke':'none'
        })
        
        label = ET.SubElement(group, 'text', x=f"{self.PADDING}", y=f"{self.height*3/4}")
        label.text = self.name

        return group
    
class UIShape():

    shapes = {
        "C": "circle",
        "D": "diamond",
        "S": "square"
    }

    def __init__(self, socket, render=True):
        self.shape = self.shapes[socket.display_shape[0]]
        self.has_dot = socket.display_shape[-1] == "T"
        self.color = constants.SOCKET_COLORS[socket.type]
        self.render = render

    def svg(self, **kwargs):
        if not self.render: return None
        group = ET.Element('svg', attrib=kwargs)

        ET.SubElement(group, 'use', href=f'#marker_{self.shape}', fill=self.color)
        if self.has_dot: ET.SubElement(group, 'use', href='#marker_dot', fill='black', stroke='none')

        return group