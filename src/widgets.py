import xml.etree.ElementTree as ET
from . import constants

from math import pi

from .methods import getFloatString, polarToCartesian, socketColorToSVGColor, enumName, insertIntoSortedByKey
from .constants import IGNORE_PROPS

from colorsys import rgb_to_hsv

# convert unconnected input socket to widget

DEFAULT_WIDTH = 100.0
DEFAULT_PADDING = 0.06


def dropdown(node, prop, label="") -> 'Widget':
    if not label:
        return Dropdown(value=enumName(node, prop))
    else:
        return LabeledDropdown(name=label, value=enumName(node, prop))


def selectBar(node, prop) -> 'Widget':
    options = [option.name for option in node.bl_rna.properties[prop].enum_items]
    try:
        index = [option.identifier for option in node.bl_rna.properties[prop].enum_items].index(getattr(node, prop))
    except ValueError as ve:
        for key, item in node.bl_rna.properties[prop].enum_items.items():
            print(">>", key, item.name)
        raise ve
    return SelectBar(options=options, select_index=index)

def object(object) -> 'Widget':
    if not object: return String(name="Object:", value="")
    return String(name="Object:", value=object.name)

def image(image) -> 'Widget':
    if not image: return SelectBar(["+ New", "Open"], -1)
    return String(value=image.name)

def curve(curving, type='VALUE', sampling=40) -> 'Widget':
    
    def evaluate_curve_n(n):
        pairs = []
        # we can skip outermost values as they are part of curve map points
        for N in range(1, sampling):
            x = curving.clip_min_x + N * (curving.clip_max_x-curving.clip_min_x) * (1.0 / sampling)
            y = curving.evaluate(curving.curves[n], x)
            pairs.append((x, y))

        
        # insert points
        for curve_point in curving.curves[n].points:
            point_x, point_y = curve_point.location
            pairs = insertIntoSortedByKey((point_x, point_y), pairs, lambda x: x[0])

        # normalize
        norm_pairs = []
        for x, y in pairs:
            calc_y = (y-curving.clip_min_y) / (curving.clip_max_y-curving.clip_min_y)
            norm_pairs.append((
                (x-curving.clip_min_x) / (curving.clip_max_x-curving.clip_min_x),
                2 * calc_y - 1 if type == 'CORRECT' else calc_y
            ))

        return norm_pairs
                    
    
    match type:
        case "VALUE":
            points = evaluate_curve_n(0)
            return Curves(curves=[('axis_w', points, True)])
        case "CRGB":
            return Curves(curves=[
                ('axis_w', evaluate_curve_n(3), True),
                *[(color, evaluate_curve_n(N), False) for N, color in enumerate(['axis_x', 'axis_y', 'axis_z'])]
            ])
        case "XYZ":
            return Curves(curves=[
                (color, evaluate_curve_n(N), False) for N, color in enumerate(['axis_x', 'axis_y', 'axis_z'])
            ])
        case "CORRECT":
            return Curves(curves=[
                (color, evaluate_curve_n(N), False) for N, color in enumerate(['axis_x', 'axis_y', 'axis_z'])
            ], hue_background=True)
        case _:
            print(f"WARNING: Undefined curve type {type}.")
            return Curves(curves=[('axis_w'), evaluate_curve_n(0), False])

def ramp(node, n=50) -> 'Ramp':

    color_mode = node.color_ramp.color_mode
    interpolation = enumName(node.color_ramp, 'interpolation' if color_mode == 'RGB' else 'hue_interpolation') 

    evals = [(i/n, node.color_ramp.evaluate(min(i/n, 1.0))) for i in range(n+1)]

    stops=[(element.position, element.color[:3]) for element in node.color_ramp.elements]
    for stop in stops:
        evals = insertIntoSortedByKey(stop, evals, key=lambda x: x[0])

    return Ramp(color_mode=color_mode,
                        interpolation=interpolation,
                        stops=stops,
                        evals=evals)

def generateCustomProps(node):
    
    wids = []
    
    for prop in node.bl_rna.properties:
        if not prop.identifier: continue
        if prop.identifier in IGNORE_PROPS: continue

        try:
            match prop.type:
                case 'BOOLEAN':
                    wids.append(Boolean(name=prop.name, value=getattr(node, prop.identifier)))
                case 'INT':
                    wids.extend([
                        Label(text=prop.name),
                        Value(value=getattr(node, prop.identifier))
                    ])
                case 'FLOAT':
                    wids.extend([
                        Label(text=prop.name),
                        Float(value=getattr(node, prop.identifier))
                    ])
                case 'STRING':
                    wids.extend([
                        Label(text=prop.name),
                        String(value=getattr(node, prop.identifier))
                    ])
                case 'ENUM':
                    wids.extend([
                        Label(text=prop.name),
                        dropdown(node, prop.identifier)
                    ])
                case 'POINTER' | 'COLLECTION':
                    obj = getattr(node, prop.identifier)
                    obj_name = ""
                    if obj:
                        if 'name' in obj.bl_rna.properties:
                            obj_name = obj.name
                    wids.extend([
                        Label(text=prop.name),
                        String(value=obj_name)
                    ])
        except:
            wids.extend([
                Label(text=prop.name),
                Placeholder()
            ])
    
    return wids

class Widget():
    
    css_classname = 'widget'
    
    def __init__(self, id_prefix='') -> None:
        self.id = self.css_classname

    def prepend_id(self, prefix) -> 'Widget':
        self.id = prefix + '_' + self.id
        return self
    
    def height(self) -> float:
        return 0.0

    def fill_svg(self, elem, width=0) -> None:
        return

    def svg(self, x=0, y=0, width=0, resize=True, **kwargs) -> ET.Element:
        
        if resize:
            return self.svg(x=x+DEFAULT_PADDING*width, y=y, width=(1-2*DEFAULT_PADDING)*width, resize=False, **kwargs)
        
        print(self.id)

        self.kwargs = kwargs
        
        elem = ET.Element('g', id=self.id)
        clip_id = self.id+'_clip'
        g_id = self.id+'_g'
        clip = ET.SubElement(elem, 'clipPath', id=clip_id)
        ET.SubElement(clip, 'rect', attrib={
            'x':'0',
            'y':'0',
            'width':str(width),
            'height':str(self.height()),
            'rx':'3' if self.kwargs['rounded_corners'] else '0',
            'ry':'3' if self.kwargs['rounded_corners'] else '0'
        })
        g = ET.SubElement(elem, 'g', id=g_id, attrib={
            'class':self.css_classname,
            'clip-path': f'url(#{clip_id}) '
            })
        self.fill_svg(g, width=width)
        elem.set('transform',f'translate({x},{y})')
        return elem

class Empty(Widget):
    ...    

class Placeholder(Widget):
    
    css_classname = 'placeholder'

    def __init__(self, **_) -> None:
        super().__init__()

    def height(self) -> float:
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=0) -> ET.Element:
        rect = ET.SubElement(elem, 'rect', x='0',   y ='0', width=str(width), height=str(self.height()))
        line1 = ET.SubElement(elem, 'line', x1='0', y1='0', x2=str(width), y2=str(self.height()))
        line2 = ET.SubElement(elem, 'line', x1='0', y1=str(self.height()), x2=str(width), y2='0')
        for elem in [rect, line1, line2]:        
            elem.set('fill', 'none')
            elem.set('style', 'stroke:#cccccc;stroke-width:0.5')

class Label(Widget):

    css_classname = 'label'


    def __init__(self, text="", alignment='L') -> None:
        super().__init__()
        self.text = text
        if alignment.upper() not in ['L', 'C', 'R']:
            raise ValueError(f"Label alignment value must be one of L, C, M, and R (got {alignment})")
        self.alignment = alignment

    def height(self) -> float:
        return constants.LINKED_SOCKET_HEIGHT

    def fill_svg(self, elem, width=0) -> ET.Element:        
        label = ET.SubElement(elem, 'text', y=str(constants.SOCKET_TEXT_HEIGHT))
        label.text = self.text
        match self.alignment:
            case 'L':
                label.set('x', '0')
            case 'C' | 'M':
                label.set('text-anchor', 'middle')
                label.set('x', str(width/2.0))
            case 'R':
                label.set('text-anchor', 'end')
                label.set('x', str(width))
    
class Boolean(Widget):

    css_classname = 'boolean'


    def __init__(self, name="", value=False) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def height(self) -> ET.Element:
        return constants.LINKED_SOCKET_HEIGHT

    def fill_svg(self, elem, width=0) -> ET.Element:

        elem.set('class', 'bool_true' if self.value else 'bool_false')

        # add rectangle for checkbox
        rect = ET.SubElement(elem, 'rect', attrib={
            'x':        str(constants.LINKED_SOCKET_HEIGHT*0.2),
            'y':        str(constants.LINKED_SOCKET_HEIGHT*0.2),
            'width':    str(constants.LINKED_SOCKET_HEIGHT*0.6),
            'height':   str(constants.LINKED_SOCKET_HEIGHT*0.6),
            'stroke':   'none'
        })

        # add value to rectangle, draw checkmark
        if self.value:
            rect.set('class', 'bool_true')
            check = ET.SubElement(elem,'polyline', fill='none', stroke='white')
            check.set('stroke-width', "1")
            check.set('class', 'checkmark')
            check.set('points', f"{constants.LINKED_SOCKET_HEIGHT*0.4}, {constants.LINKED_SOCKET_HEIGHT*0.5},\
                      {constants.LINKED_SOCKET_HEIGHT*0.5}, {constants.LINKED_SOCKET_HEIGHT*0.6},\
                        {constants.LINKED_SOCKET_HEIGHT*0.7}, {constants.LINKED_SOCKET_HEIGHT*0.3}")
        else:
            rect.set('class', 'bool_false')

        # add nameplate (svg offset by button width)
        elem.append(Label(text=self.name).prepend_id(self.id).svg(width=width-constants.LINKED_SOCKET_HEIGHT, x=constants.LINKED_SOCKET_HEIGHT, rounded_corners=self.kwargs['rounded_corners']))

class Columns(Widget):
    
    css_classname = 'columns'
    
    def __init__(self, wids=[], ratios=[], resize_override=True) -> None:
        super().__init__()
        self.wids = wids
        self.resize_override = resize_override

        self.ratio_sum = sum(ratios)
        self.ratios = ratios

    def prepend_id(self, prefix) -> Widget:
        self.id = prefix + '_' + self.id
        for i, wid in enumerate(self.wids):
            wid.prepend_id(self.id+'_col'+str(i))
        return self

    def height(self) -> float:
        return max([elem.height() for elem in self.wids])

    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        col_width = width/len(self.wids)
        offset=0.0
        for i, wid in enumerate(self.wids):
            widget_width = col_width if not self.ratios else width*self.ratios[i]/self.ratio_sum
            elem.append(wid.svg(width=widget_width, x=offset, resize=self.resize_override, rounded_corners=self.kwargs['rounded_corners']))
            offset += widget_width

class FortySixty(Columns):

    def __init__(self, wids=[], ratios=[0.4, 0.6], resize_override=False) -> None:
        super().__init__(wids, ratios, resize_override)


class Value(Widget):

    # color: #545454

    css_classname = 'value'

    def __init__(self, name="", value=0, minmax=None) -> None:
        self.name = name
        self.value = value
        self.minmax = minmax
        super().__init__()

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT

    def fill_svg(self, elem, width=DEFAULT_WIDTH):

        PADDING = 15.0

        rect = ET.SubElement(elem, 'rect', attrib={
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(self.height()),
            'class': 'value_bar'
        })

        # progressive paint in
        if self.minmax:
            lo, hi = self.minmax
            proportion = (float(self.value)-lo)/(hi-lo)
            if proportion >= 1.0: rect.set('class', 'progress_bar')
            elif proportion >= 0.0:
                ET.SubElement(elem, 'rect', attrib={
                    'x': '0',
                    'y': '0',
                    'width': str(width*proportion),
                    'height': str(self.height()),
                    'class': 'progress_bar'
                })

        # label
        if not self.name:
            elem.append(Label(str(self.value), alignment='C').prepend_id(self.id).svg(width=width-2*PADDING, x=PADDING, resize=False, rounded_corners=self.kwargs['rounded_corners']))
        else:
            elem.append(Label(self.name).prepend_id(self.id).svg(width=(width/2.0)-PADDING, x=PADDING, resize=False, rounded_corners=self.kwargs['rounded_corners']))
            elem.append(Label(str(self.value), alignment='R').prepend_id(self.id).svg(width=(width/2.0)-PADDING, x=width/2.0, resize=False, rounded_corners=self.kwargs['rounded_corners']))

class Float(Value):

    def __init__(self, name="", value=0, minmax=None) -> None:
        super().__init__(name, value, minmax)
        self.value = getFloatString(value)

class RGBA(Widget):

    css_classname = 'rgba'

    def __init__(self, color="gray") -> None:
        super().__init__()
        self.color = color

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT

    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:
        color_rect = ET.SubElement(elem, 'rect')
        color_rect.set('x', '0')
        color_rect.set('y', '0')
        color_rect.set('width', str(width))
        color_rect.set('height', str(self.height()))
        color_rect.set('fill', self.color)
    
class Vector(Widget):

    css_classname = 'vector'

    def __init__(self, name="", values=[0,0,0]) -> None:
        super().__init__()
        self.name = name
        self.values = values

    def height(self):
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        elem.append(Label(text=self.name).prepend_id(self.id).svg(width=width, resize=False, rounded_corners=self.kwargs['rounded_corners']))
        for i, value in enumerate(self.values):
            elem.append(Float(value=value).prepend_id(self.id).svg(width=width, y=(i+1)*constants.LINKED_SOCKET_HEIGHT, resize=False, rounded_corners=self.kwargs['rounded_corners']))
        
class LabeledDropdown(Widget):

    css_classname = 'labeled_dropdown'

    MIN_LABEL_WIDTH = 40

    def __init__(self, name="", value="") -> None:
        super().__init__()

        self.name = name
        self.value = value

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH):

        widths = [max(0.25*width, self.MIN_LABEL_WIDTH), min(0.75*width, width-self.MIN_LABEL_WIDTH)]

        elem.append(Label(self.name).prepend_id(self.id).svg(width=widths[0], resize=False, rounded_corners=self.kwargs['rounded_corners']))
        elem.append(Dropdown(self.value).prepend_id(self.id).svg(width=widths[1], x=widths[0], resize=False, rounded_corners=self.kwargs['rounded_corners']))

class Dropdown(Widget):

    css_classname = 'dropdown'

    def __init__(self, value="") -> None:
        super().__init__()

        self.value = value

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH):

        ET.SubElement(elem, 'rect', attrib={
                      'x':'0',
                      'y':'0',
                      'width':str(width),
                      'height':str(self.height()),
                      'class':'dropdown'
        })
        

        ET.SubElement(elem, 'use', href='#down_arrow', x=str(width-20.0), y=str(self.height()/2.0-6.0))
        
        elem.append(Label(text=self.value).prepend_id(self.id).svg(width=width, rounded_corners=self.kwargs['rounded_corners']))

class ColorPicker(Widget):
    
    css_classname = 'picker'

    def __init__(self, color=[1.0,0.0,0.0], **kwargs) -> None:
        super().__init__(**kwargs)
        self.color = color

    def height(self) -> float:
        return 90.0
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        # unset clipping from super element
        elem.attrib.pop('clip-path')

        defs = ET.SubElement(elem, 'defs')
        grad = ET.SubElement(defs, 'linearGradient', id='vertical_grad', x1='0', x2='0', y1='0', y2=str(self.height()), gradientUnits='userSpaceOnUse')
        ET.SubElement(grad, 'stop', attrib={'offset':  '0%', 'stop-color':'white'})
        ET.SubElement(grad, 'stop', attrib={'offset':'100%', 'stop-color':'black'})

        bar_width = 10.0
        wheel_space = width-bar_width-2.0
        wheel_center_x = wheel_space/2.0
        wheel_center_y = self.height()/2.0
        wheel_width = min(wheel_space, self.height())
        scale_factor = wheel_width/100.0

        ET.SubElement(elem, 'rect', x=str(width-bar_width), y='0', width=str(bar_width), height=str(self.height()), style='fill:url(#vertical_grad)')

        ET.SubElement(elem, 'use', href='#color_wheel',transform=f'translate({wheel_center_x-wheel_width/2.0},{wheel_center_y-wheel_width/2.0}) scale({scale_factor})')

        r, g, b = self.color[:3]
        print(r, g, b)
        h, s, v = rgb_to_hsv(r, g, b)
        print(h, s, v)
        
        # marker on wheel
        polar = polarToCartesian(s, (h-0.75)*2*pi)
        x = wheel_center_x + polar[0]*(wheel_width/2)
        y = wheel_center_y + polar[1]*(wheel_width/2)
        ET.SubElement(elem, 'circle', cx=str(x), cy=str(y), r='2', style='fill:white; stroke:black; stroke-width:0.5')

        # marker on bar
        x = wheel_space + 2.0 + bar_width/2.0
        y = self.height()*(1.0-v)
        ET.SubElement(elem, 'circle', cx=str(x), cy=str(y), r='2', style='fill:white; stroke:black; stroke-width:0.5')


class SelectBar(Widget):
    
    css_classname = 'selectbar'

    def __init__(self, options=[], select_index=0) -> None:
        super().__init__()
        self.options=options
        self.select_index=select_index

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH):
        
        w = width/len(self.options)
        for i, opt in enumerate(self.options):
            color_class = 'value_bar' if i != self.select_index else 'progress_bar'
            rect = ET.SubElement(elem, 'rect')
            rect.set('x', str(i*w))
            rect.set('y', '0')
            rect.set('width', str(w))
            rect.set('height', str(self.height()))
            rect.set('style', f"fill:{color_class}")
            
            elem.append(Label(opt, alignment='C').prepend_id(self.id+'_'+str(i)).svg(width=w, x=i*w, rounded_corners=self.kwargs['rounded_corners']))
        

class Curves(Widget):
    
    css_classname = 'curves'

    def __init__(self, curves=[], hue_background=False) -> None:
        super().__init__()
        self.curves = curves
        self.hue_background = hue_background

    def height(self) -> float:
        return 8 * constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        ET.SubElement(elem, 'rect', attrib={
            'x':'0',
            'y':'0',
            'width':str(width),
            'height':str(self.height()),
            'class':'value_bar',
            'style':'fill:url(#hc_grad)' if self.hue_background else ''
        })

        for color, point_pairs, infill in self.curves:
            max_y = max(y for _, y in point_pairs)
            points = [(x*width, (max_y-y)*self.height()) for x, y in point_pairs]
            style_color = '' if infill else color
            fill =   color if infill else 'none'
            if infill: points.extend([(width, self.height()),(0, self.height())])
            ET.SubElement(elem, 'polyline' if not infill else 'polygon', attrib={
                'points':(' '.join([f'{x} {y}' for x, y in points])),
                'class':style_color,
                'style':f'stroke-width:1; fill:{fill}'
            })
        
        ET.SubElement(elem, 'rect', attrib={
            'x':'0',
            'y':'0',
            'width':str(width),
            'height':str(self.height()),
            'style':'fill:none; stroke:white; stroke-width:1'
        })

class Ramp(Widget):
    
    css_classname = 'ramp'

    def __init__(self, color_mode="RGB", interpolation="Ease", stops=[], evals=[[0.0,0.0,0.0]], use_gradient=False) -> None:
        super().__init__()
        self.stops=stops
        self.evals=evals
        self.use_gradient=use_gradient
        self.color_mode=color_mode
        self.interpolation=interpolation

    def height(self):
        return 3*constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        # ignore clipping
        elem.attrib.pop('clip-path')


        elem.append(
            Columns(wids=[
                Empty(),
                Empty(),
                Dropdown(value=self.color_mode),
                Dropdown(value=self.interpolation),
            ], resize_override=False).prepend_id(self.id).svg(width=width, resize=False, rounded_corners=self.kwargs['rounded_corners'])
        )

        if self.kwargs['use_gradient']:
            
            grad = ET.SubElement(elem, 'linearGradient', id='ramp_grad')
            for x, color in self.evals[:-1]:
                ET.SubElement(grad, 'stop', attrib={
                    'offset':str(x),
                    'stop-color':socketColorToSVGColor(color, corrected=False)
                })
            ET.SubElement(grad, 'stop', attrib={
                'offset':'1',
                'stop-color':socketColorToSVGColor(self.evals[-1][1], corrected=False)
            })
            ET.SubElement(elem, 'rect', attrib={
                'x':'0',
                'y':str(self.height()/3.0 + constants.SOCKET_GAP),
                'width':str(width),
                'height':str(self.height()/3.0),
                'style':f'fill:url(#ramp_grad);stroke-width:0'
            })

        else:
            for (start, color), (end, _) in zip(self.evals[:-1], self.evals[1:]):
                x_start = start * width
                bar_width = (end-start) * width
        
                color_string = str(socketColorToSVGColor(color, corrected=False))
                ET.SubElement(elem, 'rect', attrib={
                    'x':str(x_start),
                    'y':str(self.height()/3.0 + constants.SOCKET_GAP),
                    'width':str(bar_width),
                    'height':str(self.height()/3.0),
                    'style':f'fill:{color_string};stroke:{color_string};stroke-weight:0.1'
                })

        for x, color in self.stops:
            g = ET.SubElement(elem, 'g', attrib={'transform': f'translate({x*width-5}, {2*self.height()/3 - 2})'})
            ET.SubElement(g, 'polygon', attrib={
                'points': ' '.join([str(n) for n in [
                    5,  0,
                    0,  5,
                    0,  12,
                    10, 12,
                    10, 5
                ]]),
                'style':'fill:white;stroke:none'
            })
            ET.SubElement(g, 'rect', attrib={
                'x': '1',
                'y': '6',
                'width': '8',
                'height': '5',
                'style':f'fill:{socketColorToSVGColor(color)};stroke:black;stroke-width:0.2'
            })


class Texture(Placeholder):
    ...

class Mapping(Placeholder):
    ...

class Font(Placeholder):
    ...


class String(Widget):

    css_classname = 'string'

    def __init__(self, value="", name="") -> None:
        super().__init__()
        self.value = value
        self.name = name

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def fill_svg(self, elem, width=DEFAULT_WIDTH) -> ET.Element:

        if self.name:
            elem.append(FortySixty(wids=[
                Label(text=self.name),
                String(self.value)
            ], resize_override=False).prepend_id(self.id).svg(width=width, resize=False, rounded_corners=self.kwargs['rounded_corners']))
        else:
            rect = ET.SubElement(elem, 'rect', attrib={
                'x': '0',
                'y': '0',
                'width': str(width),
                'height': str(self.height()),
                'class': 'string'
            })
            
            elem.append(Label(text=self.value).prepend_id(self.id).svg(width=width, rounded_corners=self.kwargs['rounded_corners']))


class IES(String):
    ...

class Sphere(Placeholder):
    ...

class UVMap(String):
    ...

class Image(String):
    ...
    
class Scene(String):
    ...

class Tracking(String):
    ...

class Object(String):
    ...

class MovieClip(String):
    ...

class Material(String):
    ...

class Script(String):
    ...

class File(String):
    ...

class Angle(Float):

    def __init__(self, name="", value=0, minmax=None) -> None:
        super().__init__(name, value, minmax)
        self.value = getFloatString(value, decimal_points=1)+"%"
