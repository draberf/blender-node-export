# ratio of actual node frame dimensions to the bpy object
NODE_DIM_RATIO = 0.8

# specific heights
HEADER_HEIGHT = 20
TOP_PADDING = 6.5
SOCKET_GAP = 5.6
BOTTOM_PADDING = 13.5

LINKED_SOCKET_HEIGHT = 16

SOCKET_TEXT_HEIGHT = 11

# colors
HEADER_COLOR = "red"

# properties to skip
DEFAULT_PROPERTIES = 0
IGNORE_PROPS = [
    "rna_type", "type", "location", "width",
    "width_hidden", "height", "dimensions", "name",
    "label", "inputs", "outputs", "internal_links",
    "parent", "use_custom_color", "color", "select",
    "show_options", "show_preview", "hide", "mute",
    "show_texture", "bl_idname", "bl_label",
    "bl_description", "bl_icon", "bl_static_type",
    "bl_width_default", "bl_width_min",
    "bl_width_max", "bl_height_default",
    "bl_height_min", "bl_height_max"
]

# colors
SOCKET_COLORS = {
    "CUSTOM": "#333333",
    "VALUE": "#a1a1a1",
    "INT": "#598c5c",
    "BOOLEAN": "#cca6d6",
    "VECTOR": "#6363c7",
    "ROTATION": "#ff00ff",
    "STRING": "#70b2ff",
    "RGBA": "#c7c729",
    "SHADER": "#633763",
    "OBJECT": "#ed9e5c",
    "IMAGE": "#633863",
    "GEOMETRY": "#00d6a3",
    "COLLECTION": "#f5f5f5",
    "TEXTURE": "#9e4fa3",
    "MATERIAL": "#eb7582"
}

# size of node anchor markers
MARKER_SIZE = 7
MARKER_LINE = 1
MARKER_BOX_HALF = (MARKER_SIZE+MARKER_LINE)/2
MARKER_DOT_RADIUS = 1

# padding of the final tree viewbox
VIEWBOX_PADDING = 3
