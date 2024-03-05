import xml.etree.ElementTree as ET
from . import constants

class Widget():
    
    req_kwargs = []
    css_classname = 'widget'
    
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        for kwarg in self.__class__.req_kwargs:
            if kwarg not in kwargs: raise AttributeError(f"Attribute {kwarg} not specified for Widget of class {__class__}")

    def svg(self, **attrs) -> ET.Element:
        attrs.update({'class': 'widget'})
        return ET.Element('svg', attrib=attrs)

class Empty(Widget):

    def height(self) -> float:
        return 0
    
    def svg(self, **attrs) -> ET.Element:
        return super().svg(**attrs)

class NamePlate(Widget):
    
    req_kwargs = ['width', 'name', 'align_right']

    def height(self) -> float:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, **attrs) -> ET.Element:
        grp = super().svg(**attrs)
        label = ET.SubElement(grp, 'text', y=f"{constants.SOCKET_TEXT_HEIGHT}")
        label.text = self.kwargs['name']
        if self.kwargs['align_right']:
            label.set('text-anchor', 'end')
            label.set('x', str(self.kwargs["width"] - constants.SOCKET_TEXT_PADDING))
        else:
            offset = 0 if 'offset' not in self.kwargs else self.kwargs['offset']
            label.set('x', str(constants.SOCKET_TEXT_PADDING + offset))
        return grp
    
class Boolean(Widget):

    req_kwargs = ['width', 'name', 'value']


    def __init__(self, **kwargs) -> None:
        if (w := kwargs['width']) < constants.LINKED_SOCKET_HEIGHT:
            return ValueError(f"Width value of {w} too small for Boolean widget.")
        super().__init__(**kwargs)
    
    def height(self) -> ET.Element:
        return constants.LINKED_SOCKET_HEIGHT

    def svg(self, **attrs) -> ET.Element:
        grp = super().svg(**attrs)

        # add rectangle for checkbox
        rect = ET.SubElement(grp, 'rect')
        rect.set('x', f"{self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('y', f"{constants.LINKED_SOCKET_HEIGHT*0.2}")
        rect.set('width',  f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        rect.set('height', f"{constants.LINKED_SOCKET_HEIGHT*0.6}")
        rect.set('stroke', 'none')

        # add value to rectangle, draw checkmark
        if self.kwargs['value']:
            rect.set('fill', '#7777dd')
            check = ET.SubElement(grp,'polyline', fill='none', stroke='white')
            check.set('stroke-width', "1")
            check.set('points', f"{self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.4}, {constants.LINKED_SOCKET_HEIGHT*0.5},\
                      {self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.5}, {constants.LINKED_SOCKET_HEIGHT*0.6},\
                        {self.PADDING + constants.LINKED_SOCKET_HEIGHT*0.7}, {constants.LINKED_SOCKET_HEIGHT*0.3}")
        else:
            rect.set('fill', '#222222')

        # add nameplate
        grp.append(NamePlate(width=self.kwargs['width']-constants.LINKED_SOCKET_HEIGHT, name=self.kwargs['name'], align_right=False, offset=constants.LINKED_SOCKET_HEIGHT))

class Gridlike(Widget):
    
    req_kwargs = ['width', 'widpairs', 'columns']

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rows = []
        self.col_width = self.kwargs['width']/self.kwargs['columns']
        new_row = []
        for i, widpair in enumerate(self.kwargs['widpairs']):
            if i > 0 and i % self.kwargs['columns']:
                self.rows.append(new_row)
                new_row = []
            wtype, wp_kwargs = widpair
            new_row.append(wtype(width=self.col_width, **wp_kwargs))

    def height(self) -> float:
        sum([
            max([elem.height() for elem in row]) for row in self.rows
        ])

    def svg(self, **attrs) -> ET.Element:
        grp = super().svg(**attrs)
        height = 0
        for row in self.rows:
            for ii, elem in enumerate(row):
                grp.append(elem.svg(x=ii*self.col_width, y=height))
            height += max([elem.height() for elem in row])
        return grp



