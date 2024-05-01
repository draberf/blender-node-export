import xml.etree.ElementTree as ET

from . import constants

# class of SVG for a node header
class UIHeader():

    PADDING = 18

    def __init__(self, name, width=100, height=constants.HEADER_HEIGHT, color="gray"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color

    def svg(self, opacity=60) -> ET.Element:
        group = ET.Element('g', id=f"Header {self.name}")
        
        ET.SubElement(group, 'rect', attrib={
            'width':f'{self.width}',
            'height':f'{self.height}',
            'opacity':str(opacity/100),
            'fill':self.color,
            'stroke':'none'
        })

        ET.SubElement(group, 'use', href='#down_arrow', transform='translate(5,5)')
        
        label = ET.SubElement(group, 'text', x=f"{self.PADDING}", y=f"{self.height*3/4}")
        label.text = self.name

        return group
    