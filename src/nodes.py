import bpy
import xml.etree.ElementTree as ET

class UI:

    def svg(self):
        return ET.Element('g')

class UINode(UI):
    
    node : bpy.types.Node

class UISocket(UI):
    
    socket : bpy.types.NodeSocket

    def svg(self):
        group = ET.Element('g')
        label = ...

