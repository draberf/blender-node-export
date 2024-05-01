import bpy
from re import search
import xml.etree.ElementTree as ET
from math import pi

from . import categories
from . import constants
from . import widgets
from . import methods

from .header import UIHeader
from .marker import UIShape

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


SOCKET_WIDGET_DEFS = {
    'VALUE': lambda socket: value_socket(socket),
    'FLOAT': lambda socket: widgets.Float(name=socket.name, value=socket.default_value),
    'RGBA': lambda socket: widgets.FortySixty(wids=[
        widgets.Label(text=socket.name),
        widgets.RGBA(color=methods.socketColorToSVGColor(socket.default_value[:3], corrected=socket.bl_rna.properties['default_value'].subtype == 'COLOR_GAMMA'))
    ]),
    'VECTOR': lambda socket: widgets.Vector(name=socket.name, values=socket.default_value) if not socket.hide_value else widgets.Label(text=socket.name),
    'ROTATION': lambda socket: widgets.Vector(name=socket.name, values=socket.default_value) if not socket.hide_value else widgets.Label(text=socket.name),
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
    
    if socket.is_output:
        return widgets.Label(text=socket.name, alignment='R')

    if socket.is_linked:
        return widgets.Label(text=socket.name)

    return SOCKET_WIDGET_DEFS[socket.type](socket)

# class wrapper for a single node
class UINode():

    def __init__(self, node: bpy.types.Node, colors: {str}, args = {}):
        specification = {}
        self.is_placeholder = False
        if not node.bl_idname in categories.NODE_SPECIFICATIONS:
            specification = categories.NODE_SPECIFICATIONS['PlaceholderNode']
            print(f"WARNING: Node {node.bl_idname} does not have a default specification. Placeholder object will be used instead.")
            self.is_placeholder = True
        else:
            specification = categories.NODE_SPECIFICATIONS[node.bl_idname]

        self.name = node.name
        if node.label:
            self.name = node.label
        elif 'name_behavior' in specification:
            self.name = specification['name_behavior'](node)
        elif search(r'.[0-9]{3}$', self.name): self.name = self.name[:-4]
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
        
        # for identifying widgets
        self.id = node.name.replace(' ', '_')


        self.anchors = {}


        # process header
        if not self.is_placeholder:
            self.color_class = specification['class'] if specification['class'] else specification['class_behavior'](node)
        else:
            print(f"WARNING: Node {node.bl_idname} does not have a default specification. Placeholder object will be used instead.")
            self.color_class = 'layout_node'

        self.uiheader = UIHeader(self.name, self.w, color=colors[self.color_class])

        self.rounded_corners = False
        if 'rounded_corners' in args:
            if args['rounded_corners']:
                self.rounded_corners = True

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
                try:
                    for widget in specification['props'](node, args):
                        if not widget: continue
                        register_widget(widget)
                except:
                    print(node.name)
                    register_widget(widgets.Placeholder())

        for in_socket in self.inputs:
            make_socket_widget(in_socket, False)

        # adjust node height
        self.h = max(self.h, self.height+constants.BOTTOM_PADDING)

    def is_frame(self) -> bool:
        return False


    def svg(self, header_opacity=60, use_gradient=False) -> ET.Element:
        supergroup = ET.Element('g', transform=f'translate({self.x},{self.y})', id=f'{self.id}')
        clip_rect = ET.Element('rect', attrib={
            'width':str(self.w),
            'height':str(self.h),
            'rx':str(constants.ROUND_CORNER if self.rounded_corners else 0),
            'ry':str(constants.ROUND_CORNER if self.rounded_corners else 0),
            'style':'fill:none'
        })
        clip_id = f'{self.id}_super_clip'
        clip = ET.SubElement(supergroup, 'clipPath', id=clip_id)
        clip.append(clip_rect)
        group = ET.SubElement(supergroup, 'g', attrib={'clip-path':f'url(#{clip_id})'})
        supergroup.append(clip_rect)
        if self.muted: supergroup.set('opacity', '0.5')
        
        # frame
        rect = self.frame()
        group.append(rect)

        # header
        group.append(self.uiheader.svg(opacity=header_opacity))

        # new widgets rendering
        group.extend([widget.prepend_id(f'{self.id}_{str(i)}').svg(width=self.w, y=height, use_gradient=use_gradient, rounded_corners=self.rounded_corners) for i, (height, widget) in enumerate(self.height_widget_pairs)])

        return supergroup

    def frame(self) -> ET.Element:
        frame_items = ET.Element('g')

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
    
    def svg(self, *args, **kwargs):
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
        group = ET.Element('g', transform=f'translate({self.x},{self.y})')
        
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

class UIHiddenNode(UINode):
    
    def __init__(self, node: bpy.types.Node, colors: str, args={}):
        # name
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

        # color
        if not self.is_placeholder:
            self.color_class = specification['class'] if specification['class'] else specification['class_behavior'](node)
        else:
            print(f"WARNING: Node {node.bl_idname} does not have a default specification. Placeholder object will be used instead.")
            self.color_class = 'layout_node'
        self.color=colors[self.color_class]

        # position & size
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
        
        # for identifying widgets
        self.id = node.name.replace(' ', '_')


        # markers
        self.anchors = {}

        for i, (t, socket) in [*enumerate(zip(len(self.inputs)*['input'], self.inputs))]+[*enumerate(zip(len(self.outputs)*['output'], self.outputs))]:

            # calculate angle
            step = (pi/(len(self.inputs)+1)) if t == 'input' else -pi/(len(self.outputs)+1)
            angle = pi/2 + (i+1)*step

            # calculate position
            x, y = methods.polarToCartesian(self.h/2, -angle)

            print(t, x, y, step, angle)

            x += (self.h/2) if t == 'input' else (self.w-self.h/2)
            y += self.h/2

            # add to anchor
            self.anchors[socket.as_pointer()] = (self.x + x, self.y + y, UIShape(socket))

    def svg(self, header_opacity, use_gradient=False):

        # create group
        group = ET.Element('g', transform=f'translate({self.x},{self.y})', id=f'{self.id}')
        if self.muted: group.set('opacity', '0.5')
        
        # add round rectangle base
        ET.SubElement(group, 'rect', attrib={
            'width':str(self.w),
            'height':str(self.h),
            'rx':str(self.h/2),
            'ry':str(self.h/2),
            'class': 'nodeframe'
        })

        # add round rectangle opacity overlay
        ET.SubElement(group, 'rect', attrib={
            'width':str(self.w),
            'height':str(self.h),
            'rx':str(self.h/2),
            'ry':str(self.h/2),
            'opacity':str(header_opacity/100),
            'fill':self.color,
            'stroke':'none'
        })


        # add name
        label = ET.SubElement(group, 'text', x=f"{6}", y=f"{self.h/2+3}")
        label.text = self.name

        return group
