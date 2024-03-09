import xml.etree.ElementTree as ET
from . import constants

DEFAULT_WIDTH = 100

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
    
    req_kwargs = []

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
    
    req_kwargs = ['text', 'align_right']

    def height(self) -> float:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(width, **attrs)
        label = ET.SubElement(grp, 'text', y=f"{constants.SOCKET_TEXT_HEIGHT}")
        label.text = self.kwargs['text']
        if self.kwargs['align_right']:
            label.set('text-anchor', 'end')
            label.set('x', str(width - constants.SOCKET_TEXT_PADDING))
        else:
            label.set('x', str(constants.SOCKET_TEXT_PADDING))
        return grp
    
class Boolean(Widget):

    req_kwargs = ['name', 'value']


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
    
    req_kwargs = ['wids']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.elems = kwargs['wids']

    def height(self) -> float:
        return max([elem.height() for elem in self.elems])

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        col_width = width/len(self.elems)
        grp = super().svg(width=width, **attrs)
        grp.extend([elem.svg(width=col_width, x=str(i*col_width)) for (i, elem) in enumerate(self.elems)])
        return grp

class Value(Widget):

    req_kwargs = ['name', 'value']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.wid = Columns(wids=[
            Label(text=kwargs['name'], align_right=False),
            Label(text=kwargs['value'], align_right=True)
        ])

    def height(self):
        return self.wid.height()

    def svg(self, width=DEFAULT_WIDTH, **attrs):
        return self.wid.svg(width=DEFAULT_WIDTH, **attrs)    

class RGBA(Widget):

    req_kwags = ['color']

    def height(self):
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(**attrs)
        color_rect = ET.SubElement(grp, 'rect')
        color_rect.set('x', str(0.1*width))
        color_rect.set('y', "0")
        color_rect.set('width', str(0.8*width))
        color_rect.set('height', str(self.height()))
        color_rect.set('style', 'stroke-width: 0')
        color_rect.set('fill', self.kwargs['color'])
        return grp
    
class Vector(Widget):

    req_kwargs = ['name', 'values']

    def height(self):
        return 4*constants.LINKED_SOCKET_HEIGHT
    
    def svg(self, width=DEFAULT_WIDTH, **attrs) -> ET.Element:
        grp = super().svg(**attrs)

        grp.append(Label(text=self.kwargs['name'], align_right=False).svg(width=width, y="0"))
        for i, value in enumerate(self.kwargs['values']):
            grp.append(Label(text=str(value), align_right=True).svg(width=width, y=str(i*constants.LINKED_SOCKET_HEIGHT)))
        
        return grp
    
    

