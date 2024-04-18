import importlib

from . import constants
from . import categories
from . import widgets
from . import methods

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

def style(colors, outline) -> ET.Element:
    
    style_elem = ET.Element('style')

    style_elem.text = '\n'.join([
        "text { font-family: Sans, Arial; font-size: 0.6em; fill: "+colors['color_text']+" }",
        "rect { stroke-width:"+str(outline['thickness'])+";stroke:"+methods.socketColorToSVGColor(outline['color'])+" }"
        ".checkmark { stroke:"+colors['color_text']+" } ",
        ".nodeframe { fill:"+colors['color_base']+" } ",
        ".marker { stroke-width: "+str(constants.MARKER_LINE)+"px; stroke: black}",
        ".arrow { stroke-width: 1; stroke: white; fill:none}",
        ".string { fill:"+colors['color_string_field']+"}",
        ".bool_false {fill:"+colors['color_bool_false']+"}",
        ".bool_true  {fill:"+colors['color_bool_true'] +"}",
        ".value_bar {fill:"+colors['color_value_field']+"}",
        ".progress_bar {fill:"+colors['color_value_progress']+"}",
        ".axis_x {stroke:"+colors['color_axis_x']+"}",
        ".axis_y {stroke:"+colors['color_axis_y']+"}",
        ".axis_z {stroke:"+colors['color_axis_z']+"}",
        ".axis_w {"+"stroke:black"+"}",
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
        widgets.RGBA(color=methods.socketColorToSVGColor(socket.default_value[:3], corrected=socket.bl_rna.properties['default_value'].subtype == 'COLOR_GAMMA'))
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
    
    if socket.is_output:
        return widgets.Label(text=socket.name, alignment='R')

    if socket.is_linked:
        return widgets.Label(text=socket.name)

    return SOCKET_WIDGET_DEFS[socket.type](socket)

def nodeFactory(node, colors, args) -> 'UINode':

    match node.bl_idname:
        case 'NodeFrame':
            return UIFrameNode(node)
        case 'NodeReroute':
            return UIRedirectNode(node, colors=colors)
        case _:
            if node.hide: return UIHiddenNode(node, colors=colors, args=args)
            return UINode(node, colors=colors, args=args)

class Converter():

    def __init__(self, context) -> None:
        
        # obtain node tree
        nodetree = context.space_data.node_tree

        # obtain properties
        props = context.scene.export_svg_props

        self.colors = {}
        if props.use_theme_colors:
            prefs = methods.getColorsFromPreferences(context)
            self.colors = {name+'_node':methods.socketColorToSVGColor(prefs['header_color_'+name]) for name in constants.CATEGORY_NAMES}
            self.colors.update({'color_'+name:methods.socketColorToSVGColor(prefs['color_'+name]) for name in constants.ELEMENTS})
            self.colors['noodliness'] = prefs['noodliness']
            self.colors['header_opacity'] = prefs['header_opacity']
        else:
            self.colors = {name+'_node':methods.socketColorToSVGColor(getattr(props, 'header_color_'+name)) for name in constants.CATEGORY_NAMES}
            self.colors.update({'color_'+name:methods.socketColorToSVGColor(getattr(props, 'color_'+name)) for name in constants.ELEMENTS})
            self.colors['noodliness'] = context.preferences.themes[0].node_editor.noodle_curving
            self.colors['header_opacity'] = props.header_opacity
        
        self.outline = {
            'thickness':props.rect_outline if props.rect_outline > 0.005 else 0,
            'color':props.rect_outline_color
        }
        self.header_opacity = self.colors['header_opacity']

        self.rounded_corners = props.rounded_corners
        self.quality = props.fidelity
        self.use_gradient = props.use_gradients

        widget_args = {
            'rounded_corners': self.rounded_corners,
            'quality': self.quality,
            'use_gradient': self.use_gradient
        }

        self.nodes = []
        self.node_frames = []

        self.links = [
            (link.from_socket.as_pointer(), link.to_socket.as_pointer(), False) for link in nodetree.links
        ]

        self.curving = context.preferences.themes[0].node_editor.noodle_curving

        self.anchor_refs = {}

        filtered_nodes = nodetree.nodes if not props.export_selected_only else [node for node in nodetree.nodes if node.select]
        if not filtered_nodes:
            filtered_nodes = nodetree.nodes


        self.vb_min_x =  filtered_nodes[0].location[0]
        self.vb_min_y = -filtered_nodes[0].location[1]
        self.vb_max_x =  filtered_nodes[0].location[0]
        self.vb_max_y = -filtered_nodes[0].location[1]


        frame_ptrs = {}
        frame_children = {}
        for node in filtered_nodes:

            node_object = nodeFactory(node, self.colors, args=widget_args)


            self.anchor_refs.update(node_object.anchors)
            if node.bl_idname == 'NodeFrame':
                self.node_frames.append(node_object)
                frame_ptrs[node.as_pointer()] = node_object
            else:
                self.nodes.append(node_object)

            if node.parent:
                ptr = node.parent.as_pointer()
                if not ptr in frame_children:
                    frame_children[ptr] = [node_object]
                else:
                    frame_children[ptr].append(node_object)

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

        defs.append(style(self.colors, self.outline))

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
            
            if self.curving > 0 and from_x > to_x:
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
        for node in self.nodes:
            try:
                out = node.svg(self.header_opacity, use_gradient=self.use_gradient)
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

    def __init__(self, node: bpy.types.Node, colors: {str}, args = {}):
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
                for widget in specification['props'](node, args):
                    if not widget: continue
                    register_widget(widget)

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

# class of SVG for a node header
class UIHeader():

    PADDING = 6

    def __init__(self, name, width=100, height=constants.HEADER_HEIGHT, color="gray"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color

    def svg(self, opacity=60) -> ET.Element:
        group = ET.Element('g', id=f"Header {self.name}")
        rect = ET.SubElement(group, 'rect', attrib={
            'width':f'{self.width}',
            'height':f'{self.height}',
            'opacity':str(opacity/100),
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

    def svg(self, x=0, y=0):
        if not self.render: return None
        group = ET.Element('g', transform=f'translate({x},{y})')

        ET.SubElement(group, 'use', href=f'#marker_{self.shape}', fill=self.color)
        if self.has_dot: ET.SubElement(group, 'use', href='#marker_dot', fill='black', stroke='none')

        return group