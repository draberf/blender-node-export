import xml.etree.ElementTree as ET
from . import constants

from .methods import getFloatString

DEFAULT_WIDTH = 100.0
DEFAULT_PADDING = 0.06

class Widget():
    
    css_classname = 'widget'
    
    def __init__(self) -> None:
        ...
    
    def height(self) -> float:
        return 0.0

    def svg(self, width=DEFAULT_WIDTH, attrib={}, x=0, resize=True) -> ET.Element:
        attrib['class'] = self.__class__.css_classname
        self.width = width*(1-2*DEFAULT_PADDING) if resize else width
        if resize:
            self.width = width*(1-2*DEFAULT_PADDING)
            attrib['x'] = str(x+width*DEFAULT_PADDING)
        else:
            self.width = width
            attrib['x'] = str(x)
            
        attrib['width'] = str(self.width)
        attrib['height'] = str(self.height())
        attrib['viewBox'] = f"0 0 {self.width} {self.height()}"
        return ET.Element('svg', attrib=attrib)

class Empty(Widget):

    def height(self) -> float:
        return 0
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}) -> ET.Element:
        return super().svg(width=width, attrib=attrib)

class Placeholder(Widget):
    
    css_classname = 'placeholder'


    def height(self) -> float:
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:
        grp = super().svg(width=width, attrib=attrib, **kwargs)
        rect = ET.SubElement(grp, 'rect', x='0',   y ='0', width=str(self.width), height=str(self.height()))
        line1 = ET.SubElement(grp, 'line', x1='0', y1='0', x2=str(self.width), y2=str(self.height()))
        line2 = ET.SubElement(grp, 'line', x1='0', y1=str(self.height()), x2=str(self.width), y2='0')
        for elem in [rect, line1, line2]:        
            elem.set('fill', 'none')
            elem.set('stroke', '#cccccc')
            elem.set('stroke-width', '0.5')
        return grp


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

    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:
        grp = super().svg(width=width, attrib=attrib, **kwargs)
        label = ET.SubElement(grp, 'text', y=str(constants.SOCKET_TEXT_HEIGHT))
        label.text = self.text
        match self.alignment:
            case 'L':
                label.set('x', '0')
            case 'C' | 'M':
                label.set('text-anchor', 'middle')
                label.set('x', str(self.width/2.0))
            case 'R':
                label.set('text-anchor', 'end')
                label.set('x', str(self.width))
        return grp
    
class Boolean(Widget):

    css_classname = 'boolean'


    def __init__(self, name="", value=False) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def height(self) -> ET.Element:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:
        grp = super().svg(width, attrib, **kwargs)

        # add rectangle for checkbox
        rect = ET.SubElement(grp, 'rect')
        rect.set('x', str(constants.LINKED_SOCKET_HEIGHT*0.2))
        rect.set('y', str(constants.LINKED_SOCKET_HEIGHT*0.2))
        rect.set('width',  str(constants.LINKED_SOCKET_HEIGHT*0.6))
        rect.set('height', str(constants.LINKED_SOCKET_HEIGHT*0.6))
        rect.set('stroke', 'none')

        # add value to rectangle, draw checkmark
        if self.value:
            rect.set('fill', '#7777dd')
            check = ET.SubElement(grp,'polyline', fill='none', stroke='white')
            check.set('stroke-width', "1")
            check.set('points', f"{constants.LINKED_SOCKET_HEIGHT*0.4}, {constants.LINKED_SOCKET_HEIGHT*0.5},\
                      {constants.LINKED_SOCKET_HEIGHT*0.5}, {constants.LINKED_SOCKET_HEIGHT*0.6},\
                        {constants.LINKED_SOCKET_HEIGHT*0.7}, {constants.LINKED_SOCKET_HEIGHT*0.3}")
        else:
            rect.set('fill', '#222222')

        # add nameplate (svg offset by button width)
        grp.append(Label(text=self.name).svg(width=self.width-constants.LINKED_SOCKET_HEIGHT, x=constants.LINKED_SOCKET_HEIGHT))
        return grp

class Columns(Widget):
    
    css_classname = 'columns'
    
    def __init__(self, wids=[], ratios=[], resize_override=True) -> None:
        self.elems = wids
        self.resize_override = resize_override
        super().__init__()

        self.ratio_sum = sum(ratios)
        self.ratios = ratios

    def height(self) -> float:
        return max([elem.height() for elem in self.elems])

    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:

        grp = super().svg(width=width, attrib=attrib, **kwargs)
        col_width = self.width/len(self.elems)
        offset=0.0
        for i, elem in enumerate(self.elems):
            elem_width = col_width if not self.ratios else self.width*self.ratios[i]/self.ratio_sum
            grp.append(elem.svg(width=elem_width, x=offset, resize=self.resize_override))
            offset += elem_width
        return grp

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

    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs):
        grp = super().svg(width=width, attrib=attrib, **kwargs)

        PADDING = 15.0

        rect = ET.SubElement(grp, 'rect', attrib={
            'x': '0',
            'y': '0',
            'width': str(self.width),
            'height': str(self.height()),
            'style': 'fill:#545454'
        })

        # progressive paint in
        if self.minmax:
            lo, hi = self.minmax
            proportion = (float(self.value)-lo)/(hi-lo)
            if proportion >= 1.0: rect.set('style', 'fill:#7777dd')
            elif proportion >= 0.0:
                ET.SubElement(grp, 'rect', attrib={
                    'x': '0',
                    'y': '0',
                    'width': str(self.width*proportion),
                    'height': str(self.height()),
                    'style': 'fill:#7777dd'
                })

        # label
        if not self.name:
            grp.append(Label(str(self.value), alignment='C').svg(width=self.width-2*PADDING, x=PADDING, resize=False))
        else:
            grp.append(Label(self.name).svg(width=(self.width/2.0)-PADDING, x=PADDING, resize=False))
            grp.append(Label(str(self.value), alignment='R').svg(width=(self.width/2.0)-PADDING, x=self.width/2.0, resize=False))

        # arrows
        ET.SubElement(grp, 'use', href='#left_arrow',  x='3', y=str(self.height()/2.0-5.0))
        ET.SubElement(grp, 'use', href='#right_arrow', x=str(self.width-13.0), y=str(self.height()/2.0-5.0))

        return grp

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

    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:
        grp = super().svg(width, attrib=attrib, **kwargs)
        color_rect = ET.SubElement(grp, 'rect')
        color_rect.set('x', '0')
        color_rect.set('y', '0')
        color_rect.set('width', str(width))
        color_rect.set('height', str(self.height()))
        color_rect.set('style', 'stroke-width: 0')
        color_rect.set('fill', self.color)
        return grp
    
class Vector(Widget):

    css_classname = 'vector'

    def __init__(self, name="", values=[0,0,0]) -> None:
        super().__init__()
        self.name = name
        self.values = values

    def height(self):
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs) -> ET.Element:
        grp = super().svg(width=width, attrib=attrib, **kwargs)

        grp.append(Label(text=self.name).svg(width=self.width, resize=False))
        for i, value in enumerate(self.values):
            grp.append(Value(value=value).svg(width=self.width, attrib={'y':str((i+1)*constants.LINKED_SOCKET_HEIGHT)}, resize=False))
        
        return grp

class LabeledDropdown(Widget):

    css_classname = 'columns'

    MIN_LABEL_WIDTH = 40

    def __init__(self, name="", value="") -> None:
        super().__init__()

        self.name = name
        self.value = value

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs):
        grp = super().svg(width=width, attrib=attrib, **kwargs)

        widths = [max(0.25*self.width, self.MIN_LABEL_WIDTH), min(0.75*self.width, self.width-self.MIN_LABEL_WIDTH)]

        grp.append(Label(self.name).svg(width=widths[0], resize=False))
        grp.append(Dropdown(self.value).svg(width=widths[1], x=widths[0], resize=False))

        return grp

class Dropdown(Widget):

    css_classname = 'dropdown'

    def __init__(self, value="") -> None:
        super().__init__()

        self.value = value

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs):
        grp = super().svg(width=width, attrib=attrib, **kwargs)

        rect = ET.SubElement(grp, 'rect',
                      x='0', y='0',
                      width=str(self.width), height=str(self.height()))

        vee = ET.SubElement(grp, 'use', href='#down_arrow', x=str(self.width*0.8), y=str(self.height()/2.0-6.0))
        
        grp.append(Label(text=self.value).svg(width=self.width))

        return grp

class ColorPickerNew(Widget):

    css_classname = 'color_picker'

    def __init__(self, exp_width=0, color=[0,0,0], **kwargs) -> None:
        kwargs.update({'exp_width':exp_width, 'color':color})
        super().__init__(**kwargs)

    def height(self):
        return self.kwargs['exp_width']*0.8
    
    def svg(self, width=DEFAULT_WIDTH, **attrs):
        grp = super().svg(width=width, **attrs)
        
        ET.SubElement(grp, 'use', href='#color_wheel')
        ET.SubElement(grp, 'rect', attrib={
            'x': str(0.81*self.kwargs['exp_width']),
            'y': '0',
            'width': str(0.18*self.kwargs['exp_width']),
            'height': str(self.height())
        })
        ...

class ColorPicker(Placeholder):
    ...

class Object(Placeholder):
    ...

class UVMap(Placeholder):
    ...

class SelectBar(Widget):
    
    css_classname = 'selectbar'

    def __init__(self, options=[], select_index=0) -> None:
        super().__init__()
        self.options=options
        self.select_index=select_index

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, **kwargs):
        grp = super().svg(width=width, attrib=attrib, **kwargs)
        
        w = self.width/len(self.options)
        for i, opt in enumerate(self.options):
            color = '#545454' if i != self.select_index else '#7777dd'
            rect = ET.SubElement(grp, 'rect')
            rect.set('x', str(i*w))
            rect.set('y', '0')
            rect.set('width', str(w))
            rect.set('height', str(self.height()))
            rect.set('style', f"fill:{color}")
            
            grp.append(Label(opt, alignment='C').svg(width=w, x=i*w))
        
        return grp


class FloatFac(Placeholder):
    ...

class Image(Placeholder):
    ...

class IES(Placeholder):
    ...

class File(Placeholder):
    ...

class Curves(Placeholder):
    ...

class Ramp(Placeholder):
    ...

class Script(Placeholder):
    ...

class Texture(Placeholder):
    ...

class Mapping(Placeholder):
    ...

class Tracking(Placeholder):
    ...

class Material(Placeholder):
    ...

class Font(Placeholder):
    ...

class MovieClip(Placeholder):
    ...

class Scene(Placeholder):
    ...

class String(Widget):

    def __init__(self, value="", name="") -> None:
        super().__init__()
        self.value = value
        self.name = name

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, attrib={}, x=0, resize=True) -> ET.Element:
        grp = super().svg(width, attrib, x, resize)

        if self.name:
            grp.append(FortySixty(wids=[
                Label(text=self.name),
                String(self.value)
            ], resize_override=False).svg(width=self.width, resize=False))
        else:
            rect = ET.SubElement(grp, 'rect', attrib={
                'x': '0',
                'y': '0',
                'width': str(self.width),
                'height': str(self.height()),
                'style': 'fill:black'
            })
            
            grp.append(Label(text=self.value).svg(width=self.width))

        return grp