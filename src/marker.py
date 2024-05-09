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