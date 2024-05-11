'''
Copyright (C) 2023-2024 Filip Dráber
draberf@gmail.com

This file is part of Node Exporter to SVG.

    Node Exporter to SVG is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses>.
'''

import bpy
from re import search
import xml.etree.ElementTree as ET
from math import pi, inf

from . import categories
from . import constants
from . import widgets
from . import methods

from .header import UIHeader
from .marker import UIShape


def getImageWidgetString(socket: bpy.types.NodeSocket) -> str:
    """Returns an appropriate string representation of an object pointed to by socket."""

    if not socket.default_value: return ""
    if socket.default_value.source in ['FILE', 'SEQUENCE', 'MOVIE']:
        return socket.default_value.filepath
    return socket.default_value.source


def getObjectName(socket):
    if not socket.default_value: return ""
    return socket.default_value.name

def value_socket(socket) -> widgets.Widget:
    """Returns the representation of a value-type socket based on it being a factor subtype."""

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
    'VECTOR': lambda socket: widgets.Vector(name=socket.name, values=socket.default_value),
    'ROTATION': lambda socket: widgets.Vector(name=socket.name, values=socket.default_value, elem_class=widgets.Angle),
    'INT': lambda socket: value_socket(socket),
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
    'CUSTOM': lambda socket: widgets.Label(text=socket.name),
    'MENU': lambda socket: widgets.String(value=socket.default_value)
}

def widgetFactory(socket) -> widgets.Widget:
    """Returns a Widget representing a socket."""
    
    if socket.is_output:
        return widgets.Label(text=socket.name, alignment='R')

    if socket.is_linked or socket.hide_value:
        return widgets.Label(text=socket.name)

    return SOCKET_WIDGET_DEFS[socket.type](socket)

class UINode():

    is_frame = False

    def __init__(self, node: bpy.types.Node, colors = {}, args = {}) -> None:
        
        self.w, self.h = node.dimensions
        self.w *= constants.NODE_DIM_RATIO
        self.h *= constants.NODE_DIM_RATIO
        self.x =  node.location[0]
        self.y = -node.location[1]

        self.muted = node.mute

    def svg(self, header_opacity=60, use_gradient=False) -> None | ET.Element:
        return None
    
    # return the Node's socket anchor absolute positions + shape
    def getAnchors(self):
            return {
                k:(self.x + x, self.y + y, shape) for k, (x, y, shape) in self.anchors.items()
            }



class UINodeSpecified(UINode):
    
    def __init__(self, node: bpy.types.Node, colors={}, args={}) -> None:
        super().__init__(node, colors, args)

        # load specification
        self.is_placeholder = False
        if not node.bl_idname in categories.NODE_SPECIFICATIONS:
            self.specification = categories.NODE_SPECIFICATIONS['PlaceholderNode']
            print(f"WARNING: Node {node.bl_idname} does not have a default specification. Placeholder object will be used instead.")
            self.is_placeholder = True
        else:
            self.specification = categories.NODE_SPECIFICATIONS[node.bl_idname]

        # set display name
        self.name = node.name
        if node.label:
            self.name = node.label
        elif 'name_behavior' in self.specification:
            self.name = self.specification['name_behavior'](node)
        elif search(r'.[0-9]{3}$', self.name): self.name = self.name[:-4]
        
        self.outputs = [output for output in node.outputs.values() if all([not output.hide, output.enabled, not output.is_unavailable])]
        self.inputs = [input for input in node.inputs.values() if all([not input.hide, input.enabled, not input.is_unavailable])]

        # set color class
        self.color_class = self.specification['class']
        if not self.color_class: self.color_class = self.specification['class_behavior'](node)
        try:
            self.uiheader = UIHeader(self.name, self.w, color=colors[self.color_class])
        except KeyError as KE:
            print(self.color_class)
            print(self.specification)
            print(colors.keys())
            raise KE

        # prepare anchors dictionary
        self.anchors = {}

    


# class wrapper for a single node
class UINodeRegular(UINodeSpecified):

    def __init__(self, node: bpy.types.Node, colors: {str}, args = {}):
        super().__init__(node, colors, args)
        
        # new Widget stack method + coords
        self.height_widget_pairs = []
        self.height = self.uiheader.height + constants.TOP_PADDING

        # for identifying widgets
        self.id = node.name.replace(' ', '_')

        def registerWidget(widget):
            self.height_widget_pairs.append((self.height, widget))
            self.height += widget.height() + constants.SOCKET_GAP

        def make_socket_widget(socket, is_offset):
            self.anchors[socket.as_pointer()] = (
                (self.w if is_offset else 0),
                self.height+constants.LINKED_SOCKET_HEIGHT/2,
                UIShape(socket))
            try:
                registerWidget(widgetFactory(socket))
            except AttributeError:
                raise Exception(node.name)

        # process outputs
        for out_socket in self.outputs:
            make_socket_widget(out_socket, True)
        
        # process props
        if self.specification:
            if 'props' in self.specification:
                try:
                    for widget in self.specification['props'](node, args):
                        if not widget: continue
                        registerWidget(widget)
                except:
                    print("Error when converting a prop of", node.name, "-- using Placeholder instead.")
                    registerWidget(widgets.Placeholder())

        # process inputs
        for in_socket in self.inputs:
            make_socket_widget(in_socket, False)

        # adjust node height
        self.h = max(self.h, self.height+constants.BOTTOM_PADDING)   

    def svg(self, header_opacity=60, use_gradient=False) -> ET.Element:
        supergroup = ET.Element('g', transform=f'translate({self.x},{self.y})', id=f'{self.id}')
        clip_rect = ET.Element('rect', attrib={
            'width':str(self.w),
            'height':str(self.h),
            'rx':widgets.PROPERTIES['corner_l'],
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
        group.extend([widget.prepend_id(f'{self.id}_{str(i)}').svg(width=self.w, y=height, use_gradient=use_gradient) for i, (height, widget) in enumerate(self.height_widget_pairs)])

        return supergroup

    def frame(self) -> ET.Element:
        frame_items = ET.Element('g')

        bg = ET.Element('rect', width=f"{self.w}", height=f"{self.h}")
        bg.set('class', 'nodeframe')

        frame_items.append(bg)

        return frame_items

class UIRedirectNode(UINode):

    def __init__(self, node: bpy.types.Node, colors = {}, args = {}):
        super().__init__(node, colors, args)
        
     
        self.name = "Redirect Node"

        self.muted = False

        self.w, self.h = 0, 0
        self.x =  node.location[0]
        self.y = -node.location[1]

        self.anchors = {node.inputs[0].as_pointer(): (0, 0, UIShape(node.inputs[0]))}
        self.anchors.update({output.as_pointer(): (0, 0, UIShape(output, render=False)) for output in node.outputs})


    def svg(self, *args, **kwargs):
        return None

class UIFrameNode(UINode):

    is_frame = True

    def __init__(self, node: bpy.types.Node, colors={}, args={}):
        super().__init__(node, colors, args)
        
        self.name = ""
        if node.label:
            self.name = node.label

        self.is_empty = True

        # placeholder values
        self.w, self.h = node.dimensions
        self.x =  node.location[0]
        self.y = -node.location[1]

        self.color = 'black' if not node.use_custom_color else methods.socketColorToSVGColor(node.color)

        self.children = []
        self.boundaries_set = False

        self.anchors = {}

        self.ptr = node.as_pointer()

    def updateOnTree(self, tree):

        if not self.ptr in tree:
            return
        
        min_x = inf
        max_x = -inf

        min_y = inf
        max_y = -inf

        for child in tree[self.ptr]:
            child.x += self.x
            child.y += self.y
            if child.is_frame:
                child.updateOnTree(tree)
                if child.is_empty:
                    continue
                else:
                    self.is_empty = False
            else:
                self.is_empty = False
            min_x = min(min_x, child.x)
            min_y = min(min_y, child.y)
            max_x = max(max_x, child.x+child.w)
            max_y = max(max_y, child.y+child.h)
            
        self.x = min_x - constants.FRAME_NODE_PADDING
        self.y = min_y - constants.FRAME_NODE_PADDING
        self.w = max_x - min_x + 2 * constants.FRAME_NODE_PADDING
        self.h = max_y - min_y + 2 * constants.FRAME_NODE_PADDING

    def svg(self) -> ET.Element:

        if self.is_empty: return None

        group = ET.Element('g', transform=f'translate({self.x},{self.y})')
        
        ET.SubElement(group, 'rect', attrib={
            'x': '0',
            'y': '0',
            'width': str(self.w),
            'height': str(self.h),
            'rx':widgets.PROPERTIES['corner_l'],
            'style':f'fill:{self.color};stroke:none;opacity:0.8'
        })

        if self.name:
            text = ET.SubElement(group, 'text', attrib={
                'x':str(self.w/2),
                'y':str(constants.LINKED_SOCKET_HEIGHT),
                'text-anchor':'middle'
            })
            text.text = self.name

        return group

class UIHiddenNode(UINodeSpecified):
    
    def __init__(self, node: bpy.types.Node, colors = {}, args={}):
        super().__init__(node, colors, args)
        
        # prepare anchors
        for i, (t, socket) in [*enumerate(zip(len(self.inputs)*['input'], self.inputs))]+[*enumerate(zip(len(self.outputs)*['output'], self.outputs))]:

            # calculate angle
            step = (pi/(len(self.inputs)+1)) if t == 'input' else -pi/(len(self.outputs)+1)
            angle = pi/2 + (i+1)*step

            # calculate position
            x, y = methods.polarToCartesian(self.h/2, -angle)

            x += (self.h/2) if t == 'input' else (self.w-self.h/2)
            y += self.h/2

            # add to anchor
            self.anchors[socket.as_pointer()] = (x, y, UIShape(socket))

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

        # add arrow
        ET.SubElement(group, 'use', href='#right_arrow', transform=f'translate(5,{self.h / 2 - 5})')

        # add name
        label = ET.SubElement(group, 'text', x='18', y=f"{self.h/2+3}")
        label.text = self.name

        return group
