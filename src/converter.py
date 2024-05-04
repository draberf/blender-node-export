import importlib

from . import constants
from . import categories
from . import widgets
from . import methods
from . import node

import bpy
import xml.etree.ElementTree as ET

from colorsys import rgb_to_hsv, hsv_to_rgb
from math import sin, cos, pi
from re import search

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
    'right':('polyline',{
        'points': '5 2 8 5 5 8',
        'class': 'arrow'
    }),
    'down':('polyline', {
        'points': '2 5 5 8 8 5',
        'class': 'arrow'
    })
}

def style(colors) -> ET.Element:
    
    style_elem = ET.Element('style')

    style_elem.text = '\n'.join([

        # texts
        "text { font-family: sans-serif, arial; font-size: 10px; fill: "+colors['text_base']+" }",
        ".string text { fill: "+colors['text_string']+" }",
        ".bool_true  text { fill: "+colors['text_boolean_true'] +" }",
        ".bool_false text { fill: "+colors['text_boolean_false']+" }",
        ".dropdown text { fill: "+colors['text_dropdown']+" }",
        ".value text { fill: "+colors['text_slider']+" }",

        # corners
        ".corner_l { rx:" + colors['round_l'] + " }",
        ".corner_s { rx:" + colors['round_s'] + " }",

        # generic
        "rect { stroke-width:"+str(colors['outline_thickness'])+";stroke:"+colors['outline_color']+" }",
        ".nodeframe { fill:"+colors['color_base']+" } ",
        ".marker { stroke-width: "+str(constants.MARKER_LINE)+"px; stroke: black}",
        ".arrow { stroke-width: 1; stroke: white; fill:none}",
        
        # booleans
        ".checkmark { stroke:"+colors['color_checkmark']+" } ",
        ".bool_false {fill:"+colors['color_bool_false']+"}",
        ".bool_true  {fill:"+colors['color_bool_true'] +"}",

        # values
        ".value_bar {fill:"+colors['color_value_field']+"}",
        ".progress_bar {fill:"+colors['color_value_progress']+"}",

        # strings
        ".string { fill:"+colors['color_string_field']+"}",

        # dropdowns
        ".dropdown { fill:"+colors['color_dropdown']+"}",

        # axes
        ".axis_x {stroke:"+colors['color_axis_x']+"}",
        ".axis_y {stroke:"+colors['color_axis_y']+"}",
        ".axis_z {stroke:"+colors['color_axis_z']+"}",
        ".axis_w {"+"stroke:black"+"}",
    ])

    return style_elem


def nodeFactory(n, colors, args) -> node.UINode:

    match n.bl_idname:
        case 'NodeFrame':
            return node.UIFrameNode(n)
        case 'NodeReroute':
            return node.UIRedirectNode(n, colors=colors)
        case _:
            if n.hide: return node.UIHiddenNode(n, colors=colors, args=args)
            return node.UINodeRegular(n, colors=colors, args=args)

class Converter():

    def __init__(self, context) -> None:
        
        # obtain node tree
        nodetree = context.space_data.node_tree

        # obtain properties
        props = context.scene.export_svg_props

        self.colors = methods.getConfigurationFromContext(context)

        self.quality = props.fidelity
        self.use_gradient = props.use_gradients

        widget_args = {
            'quality': self.quality,
            'use_gradient': self.use_gradient,
            'corner_s': '3px' if props.rounded_corners else '0',
            'corner_l': '5px' if props.rounded_corners else '0', 
        }

        widgets.PROPERTIES = widget_args

        self.nodes = []
        self.node_frames = []

        self.links = [
            (link.from_socket.as_pointer(), link.to_socket.as_pointer(), False) for link in nodetree.links
        ]

        self.curving = context.preferences.themes[0].node_editor.noodle_curving

        self.anchor_refs = {}

        filtered_nodes = nodetree.nodes if not props.export_selected_only else [n for n in nodetree.nodes if n.select]
        if not filtered_nodes:
            filtered_nodes = nodetree.nodes


        # process Nodes, including nesting into Frames
        top_level = []
        frame_children = {}

        for n in filtered_nodes:

            node_object = nodeFactory(n, self.colors, args=widget_args)

            if n.parent:
                ptr = n.parent.as_pointer()
                if not ptr in frame_children:
                    frame_children[ptr] = [node_object]
                else:
                    frame_children[ptr].append(node_object)
            else:
                # non-nested, fine
                top_level.append(node_object)

            if n.mute:
                self.links.extend([(link.from_socket.as_pointer(), link.to_socket.as_pointer(), True) for link in n.internal_links])
        
        print(top_level)
        print(frame_children)
        for node_object in top_level:
            if node_object.is_frame():
                node_object.updateOnTree(frame_children)
                self.node_frames.append(node_object)
            else:
                self.nodes.append(node_object)
                self.anchor_refs.update(node_object.getAnchors())

        for frame_contents in frame_children.values():
            for node_object in frame_contents:
                if node_object.is_frame():
                    self.node_frames.append(node_object)
                else:
                    self.nodes.append(node_object)
                    self.anchor_refs.update(node_object.getAnchors())

        # if any frame is actually empty, drop it from further consideration
        self.node_frames = [nf for nf in self.node_frames if not nf.is_empty]

    def makeDefs(self) -> ET.Element:

        defs = ET.Element('defs')

        defs.append(style(self.colors))

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
        ### add 'cloud' over gradient
        cloud_lin = ET.SubElement(color_wheel, 'linearGradient', id='cloud_gradient_linear')
        ET.SubElement(cloud_lin, 'stop', attrib={'offset':   '0', 'stop-opacity':'1'  , 'stop-color':'white'})
        ET.SubElement(cloud_lin, 'stop', attrib={'offset': '0.6', 'stop-opacity':'0.5', 'stop-color':'white'})
        ET.SubElement(cloud_lin, 'stop', attrib={'offset': '1.0', 'stop-opacity':'0'  , 'stop-color':'white'})
        cloud = ET.SubElement(color_wheel, 'radialGradient', attrib={
            'id':'cloud_gradient',
            'xlink:href':'#cloud_gradient_linear',
            'cx':'0',
            'cy':'0',
            'fx':'0',
            'fy':'0',
            'r':'50',
            'gradientUnits':'userSpaceOnUse'
        })
        radius=50
        grp = ET.SubElement(color_wheel, 'g', transform=f'translate({radius},{radius})')
        steps=2*self.quality
        def angleToCoords(angle):
            return radius*cos(angle), radius*sin(angle)
        for i in range(steps):
            angle_start = i*2*pi/steps
            angle_end = (i+1)*2*pi/steps
            point1_x, point1_y = angleToCoords(angle_start)
            point2_x, point2_y = angleToCoords(angle_end)
            color = methods.socketColorToSVGColor(hsv_to_rgb((0.75 + i/steps), 1.0, 1.0))
            fill = color
            if self.use_gradient:
                next_color = methods.socketColorToSVGColor(hsv_to_rgb((0.75 + (i+1)/steps), 1.0, 1.0))
                grad = ET.SubElement(grp, 'linearGradient', id=f'color_wheel_grad_{i}', gradientUnits='userSpaceOnUse', x1=str(point1_x), x2=str(point2_x), y1=str(point1_y), y2=str(point2_y))
                ET.SubElement(grad, 'stop', attrib={'offset':'0%', 'stop-color':color})
                ET.SubElement(grad, 'stop', attrib={'offset':'100%', 'stop-color':next_color})
                fill = f'url(#color_wheel_grad_{i})'
            ET.SubElement(grp, 'polygon', points=f"0 0 {point1_x} {point1_y} {point2_x} {point2_y}", style=f"fill:{fill}; stroke:none")
        ET.SubElement(grp, 'circle', cx='0', cy='0', r=str(radius), fill='url(#cloud_gradient)')

        ## hue correct gradient
        grad = ET.SubElement(defs, 'linearGradient', id='hc_grad', x1='0', x2='1', y1='0', y2='0')
        for i in range(7):
            prog = i/6.0
            ET.SubElement(grad, 'stop', attrib={'offset':  str(prog), 'stop-color':methods.socketColorToSVGColor(hsv_to_rgb(prog, 1.0, 1.0))})


        return defs


    def convert(self) -> ET.ElementTree:
        
        svg = ET.Element('svg', attrib={
            'version':'1.1',
            'xmlns':'http://www.w3.org/2000/svg',
            'xmlns:xlink':'http://www.w3.org/1999/xlink'
        })

        svg.append(self.makeDefs())


        # add node frames to final SVG
        for frame in self.node_frames:
            out = frame.svg()
            if out: svg.append(out)

        n = (self.nodes+self.node_frames)[0]
        self.vb_min_x = n.x
        self.vb_min_y = n.y
        self.vb_max_x = n.x+n.w
        self.vb_max_y = n.y+n.h

        for n in (self.nodes+self.node_frames)[1:]:
            
            self.vb_min_x = min(self.vb_min_x, n.x)
            self.vb_min_y = min(self.vb_min_y, n.y)
            self.vb_max_x = max(self.vb_max_x, n.x+n.w)
            self.vb_max_y = max(self.vb_max_y, n.y+n.h)


        # update viewbox based on rendered links
        svg_w = self.vb_max_x-self.vb_min_x
        svg_h = self.vb_max_y-self.vb_min_y

        # add links to final SVG
        fac = self.curving/10.0
        for link in self.links:
            
            if not link[0] in self.anchor_refs or not link[1] in self.anchor_refs: continue
            from_x, from_y, from_anchor_object = self.anchor_refs[link[0]]
            to_x, to_y, _ = self.anchor_refs[link[1]]
            is_muted = link[2]

            opacity = '1' if not is_muted else '0.2'

            color1 = from_anchor_object.color

            diff_x = abs(to_x - from_x)
            control_x1 = from_x + fac*diff_x
            control_x2 = to_x - fac*diff_x

            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {control_x1},{from_y} {control_x2},{to_y} {to_x},{to_y}",
                            style=f"stroke:#000000;stroke-width:4;fill:none;opacity:{opacity}")
            ET.SubElement(svg, 'path', d=f"M {from_x},{from_y} C {control_x1},{from_y} {control_x2},{to_y} {to_x},{to_y}",
                            style=f"stroke:{color1};stroke-width:2;fill:none;opacity:{opacity}")
            
            if self.curving > 0 and control_x1 > control_x2:
                x1, x2 = methods.getBezierExtrema(from_x, control_x1, control_x2, to_x)
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
        for n in self.nodes:
            out = n.svg(self.colors['header_opacity'], use_gradient=self.use_gradient)
            if out: svg.append(out)

        # add anchors to final SVG
        for x, y, anchor in self.anchor_refs.values():
            out = anchor.svg(x=str(x-constants.MARKER_BOX_HALF), y=str(y-constants.MARKER_BOX_HALF))
            if not out: continue
            svg.append(out)

        tree = ET.ElementTree(svg)
        ET.indent(tree)

        return tree
