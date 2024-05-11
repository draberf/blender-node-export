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

class UIShape():

    shapes = {
        "C": "circle",
        "D": "diamond",
        "S": "square"
    }

    def __init__(self, socket, render=True):
        self.shape = self.shapes[socket.display_shape[0]]
        self.has_dot = socket.display_shape[-1] == "T"
        self.type = socket.type.lower()
        self.render = render

    def svg(self, x=0, y=0):
        if not self.render: return None
        group = ET.Element('g', attrib={
            'transform':f'translate({x},{y})',
            'class':'marker'
        })

        ET.SubElement(group, 'use', attrib={
            'href':f'#marker_{self.shape}',
            'class':self.type
        })
        if self.has_dot: ET.SubElement(group, 'use', href='#marker_dot', stroke='none')

        return group