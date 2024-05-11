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
    