import xml.etree.ElementTree as ET

from . import constants


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