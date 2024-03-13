import xml.etree.ElementTree as ET
from . import constants

DEFAULT_WIDTH = 100.0

class Widget():
    
    req_kwargs = []
    css_classname = 'widget'
    
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        for kwarg in self.__class__.req_kwargs:
            if kwarg not in kwargs: raise AttributeError(f"Attribute {kwarg} not specified for Widget of class {__class__}")

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        attrs.update({'class': self.__class__.css_classname})
        return ET.Element('svg', attrib=attrs)

class Empty(Widget):

    def height(self) -> float:
        return 0
    
    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        return super().svg(width, **attrs)

class Placeholder(Widget):
    
    css_classname = 'placeholder'


    def height(self) -> float:
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width, **attrs)
        rect = ET.SubElement(grp, 'rect', x=str(0.1*width), y=str(0.1*self.height()), width=str(0.8*width), height=str(0.8*self.height()))
        line1 = ET.SubElement(grp, 'line', x1=str(0.1*width), y1=str(0.1*self.height()), x2=str(0.9*width), y2=str(0.9*self.height()))
        line2 = ET.SubElement(grp, 'line', x1=str(0.1*width), y1=str(0.9*self.height()), x2=str(0.9*width), y2=str(0.1*self.height()))
        for elem in [rect, line1, line2]:        
            elem.set('fill', 'none')
            elem.set('stroke', '#cccccc')
            elem.set('stroke-width', '0.5')
        return grp


class Label(Widget):

    css_classname = 'label'


    def __init__(self, text="", align_right=False, **kwargs) -> None:
        kwargs.update({'text': text, 'align_right': align_right})
        super().__init__(**kwargs)

    def height(self) -> float:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width, **attrs)
        label = ET.SubElement(grp, 'text', y=f"{constants.SOCKET_TEXT_HEIGHT}")
        label.text = str(self.kwargs['text'])
        if self.kwargs['align_right']:
            label.set('text-anchor', 'end')
            label.set('x', str(width - constants.SOCKET_TEXT_PADDING))
        else:
            label.set('x', str(constants.SOCKET_TEXT_PADDING))
        return grp
    
class Boolean(Widget):

    css_classname = 'boolean'


    def __init__(self, name="", value=False, **kwargs) -> None:
        kwargs.update({'name': name, 'value':value})
        super().__init__(**kwargs)

    def height(self) -> ET.Element:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width, **attrs)

        if width < constants.LINKED_SOCKET_HEIGHT:
            return ValueError(f"Width value of {width} too small for Boolean widget.")

        # add rectangle for checkbox
        rect = ET.SubElement(grp, 'rect')
        rect.set('x', f"{constants.SOCKET_TEXT_PADDING + constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('y', f"{constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('width',  f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        rect.set('height', f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        rect.set('stroke', 'none')

        # add value to rectangle, draw checkmark
        if self.kwargs['value']:
            rect.set('fill', '#7777dd')
            check = ET.SubElement(grp,'polyline', fill='none', stroke='white')
            check.set('stroke-width', "1")
            check.set('points', f"{constants.SOCKET_TEXT_PADDING + constants.LINKED_SOCKET_HEIGHT*0.4}, {constants.LINKED_SOCKET_HEIGHT*0.5},\
                      {constants.SOCKET_TEXT_PADDING + constants.LINKED_SOCKET_HEIGHT*0.5}, {constants.LINKED_SOCKET_HEIGHT*0.6},\
                        {constants.SOCKET_TEXT_PADDING + constants.LINKED_SOCKET_HEIGHT*0.7}, {constants.LINKED_SOCKET_HEIGHT*0.3}")
        else:
            rect.set('fill', '#222222')

        # add nameplate (svg offset by button width)
        grp.append(Label(width=width-constants.LINKED_SOCKET_HEIGHT, text=self.kwargs['name'], align_right=False).svg(x=str(constants.LINKED_SOCKET_HEIGHT)))
        return grp

class Columns(Widget):
    
    css_classname = 'columns'
    
    def __init__(self, wids=[], ratios=[], **kwargs) -> None:
        kwargs.update({'wids': wids})
        super().__init__(**kwargs)

        self.ratio_sum = sum(ratios)
        self.ratios = ratios

        self.elems = kwargs['wids']

    def height(self) -> float:
        return max([elem.height() for elem in self.elems])

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:

        col_width = width/len(self.elems)
        grp = super().svg(width=width, **attrs)
        offset=0.0
        for i, elem in enumerate(self.elems):
            elem_width = col_width if not self.ratios else width*self.ratios[i]/self.ratio_sum
            grp.append(elem.svg(width=elem_width, x=str(offset)))
            offset += elem_width
        return grp

class Value(Widget):

    # color: #545454

    css_classname = 'value'

    def __init__(self, name="", value=0, **kwargs) -> None:
        kwargs.update({'name':name, 'value':value})
        super().__init__(**kwargs)
        self.wid = Columns(wids=[
            Label(text=kwargs['name'], align_right=False),
            Label(text=kwargs['value'], align_right=True)
        ])

    def height(self):
        return self.wid.height()

    def svg(self, width=DEFAULT_WIDTH, **attrs):
        grp = super().svg(width, **attrs)

        ET.SubElement(grp, 'rect', attrib={
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(self.height()),
            'style': 'fill:#545454'
        })

        grp.extend([elem for elem in self.wid.svg(width=0.9*width, x=str(0.05*width), **attrs)])

        return grp

class RGBA(Widget):

    css_classname = 'rgba'

    def __init__(self, color="gray", **kwargs) -> None:
        kwargs.update({'color':color})
        super().__init__(**kwargs)

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width, **attrs)
        color_rect = ET.SubElement(grp, 'rect')
        color_rect.set('x', str(0.1*width))
        color_rect.set('y', "0")
        color_rect.set('width', str(0.8*width))
        color_rect.set('height', str(self.height()))
        color_rect.set('style', 'stroke-width: 0')
        color_rect.set('fill', self.kwargs['color'])
        return grp
    
class Vector(Widget):

    css_classname = 'vector'

    def __init__(self, name="", values=[0,0,0], **kwargs) -> None:
        kwargs.update({'name':name, 'values':values})
        super().__init__(**kwargs)

    def height(self):
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width=width, **attrs)

        grp.append(Label(text=self.kwargs['name'], align_right=False).svg(width=width, y="0"))
        for i, value in enumerate(self.kwargs['values']):
            grp.append(Label(text=str(value), align_right=True).svg(width=width, y=str(i*constants.LINKED_SOCKET_HEIGHT)))
        
        return grp

class LabeledDropdown(Widget):

    css_classname = 'columns'

    MIN_LABEL_WIDTH = 40

    def __init__(self, name="", value="", **kwargs) -> None:
        super().__init__(**kwargs)

        self.name = name
        self.value = value

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs):
        grp = super().svg(width=width, **attrs)

        widths = [max(0.25*width, self.MIN_LABEL_WIDTH), min(0.75*width, width-self.MIN_LABEL_WIDTH)]

        grp.append(Label(self.name).svg(widths[0]))
        grp.append(Dropdown(self.value).svg(widths[1], x=str(widths[0])))

        return grp

class Dropdown(Widget):

    css_classname = 'dropdown'

    def __init__(self, value="", **kwargs) -> None:
        kwargs.update({'value':value})
        super().__init__(**kwargs)

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs):
        grp = super().svg(width=width, **attrs)

        rect = ET.SubElement(grp, 'rect',
                      x=str(0.05*width), y=str(0.05*self.height()),
                      width=str(0.9*width), height=str(0.9*self.height()))

        vee = ET.SubElement(grp, 'polyline',
                      points=f"\
                        {0.82*width} {0.4*self.height()} \
                        {0.85*width} {0.6*self.height()} \
                        {0.88*width} {0.4*self.height()}",
                        stroke="white")
        
        grp.append(Label(text=self.kwargs['value'], align_right=False).svg(width=width, x=str(0.1*width)))

        vee.set('stroke-width', "1")

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

    def __init__(self, options=[], select_index=0, **kwargs) -> None:
        self.options=options
        self.select_index=select_index
        super().__init__(**kwargs)

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs):
        grp = super().svg(width=width, **attrs)
        
        w = width/len(self.options)
        for i, opt in enumerate(self.options):
            color = '#545454' if i != self.select_index else '#7777dd'
            rect = ET.SubElement(grp, 'rect')
            rect.set('x', str(i*w))
            rect.set('y', '0')
            rect.set('width', str(w))
            rect.set('height', str(self.height()))
            rect.set('style', f"fill:{color}")
            
            grp.append(Label(opt, x=str(i*w)).svg(width=w, x=str(i*w)))
        
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