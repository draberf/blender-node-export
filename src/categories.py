# node.name -- needs to remove .### in case of multiple nodes

from . import widgets
from .methods import socketColorToSVGColor, enumName



category_to_node = {    
    "input_node": [
        "Ambient Occlusion",
        "Attribute",
        "Bevel",
        "Bokeh Image",
        "Boolean",
        "Camera Data",
        "Collection Info",
        "Color",
        "Color Attribute",
        "Corners of Face",
        "Corners of Vertex",
        "Curve Handle Positions",
        "Curve of Point",
        "Curve Tangent",
        "Curve Tilt",
        "Curves Info",
        "Endpoint Selection",
        "Edge Angle",
        "Edge Neighbors",
        "Edge Paths to Selection",
        "Edge Vertices",
        "Edges of Corner",
        "Edges of Vertex",
        "Face Area",
        "Face Neighbors",
        "Face of Corner",
        "Face Set Boundaries",
        "Fresnel",
        "Geometry",
        "Handle Type Selection",
        "Image",
        "Instance Rotation",
        "Instance Scale",
        "Integer",
        "Is Face Planar",           # change
        "Is Shade Smooth",
        "Is Spline Cyclic",
        "Is Viewport",
        "Layer Weight",
        "Light Path",
        "Mask",
        "Material",
        "Material Index",
        "Mesh Island",
        "Movie Clip",
        "Object Info",
        "Offset Corner in Face",
        "Offset Point in Curve",
        "Particle Info",
        "Points of Curve",
        "Point Info",
        "Render Layers",
        "RGB",
        "Scene Time",
        "Self Object",
        "Shortest Edge Paths",
        "Special Characters",
        "Spline Length",
        "Spline Parameter",
        "Spline Resolution",
        "String"
        "Tangent",
        "Texture",
        "Texture Coordinate",
        "Time Curve",
        "Track Position",
        "UV Map",
        "Value",
        "Vertex Neighbors",
        "Vertex of Corner",
        "Volume Info",
        "Wireframe"
    ],
    "output_node": [
        "AOV Output",
        "Composite",
        "File Output",
        "Levels",
        "Material Output",
        "Split Viewer",
        "Viewer"
    ],
    "shader_node": [
        "Add Shader",
        "Diffuse BSDF",
        "Emission",
        "Glass BSDF",
        "Glossy BSDF",
        "Holdout",
        "Mix Shader",
        "Principled BSDF",
        "Principled Volume",
        "Refraction BSDF",
        "Specular BSDF",
        "Subsurface Scattering",
        "Translucent BSDF",
        "Transparent BSDF",
        "Volume Absorption",
        "Volume Scatter"
    ],
    "texture_node": [
        "Brick Texture",
        "Checker Texture",
        "Environment Texture",
        "Gradient Texture",
        "IES Texture",
        "Image Texture",
        "Magic Texture",
        "Musgrave Texture",
        "Noise Texture",
        "Point Density",
        "Sky Texture",
        "Voronoi Texture",
        "Wave Texture",
        "White Noise Texture"
    ],
    "color_node": [
        "Alpha Over",
        "Bright/Contrast",
        "Color Balance",
        "Color Correction",
        "Exposure",
        "Gamma",
        "Hue Correct",
        "Hue Saturation Value",
        "Invert",
        "Light Falloff",
        "Mix",
        "Mix Color",
        "RGB Curves",
        "Posterize",
        "Tonemap",
        "Z Combine"
    ],
    "vector_node": [
        "Bump",
        "Displacement",
        "Map Range",
        "Map Value",
        "Mapping",
        "Normal",
        "Normal Map",
        "Normalize",
        "Vector Curves",
        "Vector Displacement",
        "Vector Math",          # changes
        "Vector Rotate",
        "Vector Transform"
    ],
    "converter_node": [
        "Accumulate Field",
        "Align Euler to Vector",
        "Alpha Convert",
        "Blackbody",
        "Boolean",              # changes
        "Clamp",
        "ColorRamp",
        "Combine Color",
        "Combine XYZ",
        "Compare",              # changes
        "Convert Colorspace",
        "Field at Index",
        "Float Curve",
        "Float to Integer",     # changes
        "ID Mask",
        "Interpolate Domain",
        "Join Strings",
        "Map Range",
        "Math",                 # chagnes
        "Mix",
        "Pack UV Islands",
        "Random Value",
        "Replace String",
        "RGB to BW",
        "Rotate Euler",
        "Separate Color",
        "Separate XYZ",
        "Set Alpha",
        "Shader to RGB",
        "Slice String",
        "String Length",
        "Switch",
        "Switch View",
        "UV Unwrap",
        "Value to String",
        "Wavelength"
    ],
    "script_node": [
        "Script"
    ],
    "filter_node": [
        "Anti-Aliasing",
        "Bilateral Blur",
        "Blur",
        "Bokeh Blur",
        "Defocus",
        "Denoise",
        "Despeckle",
        "Dilate/Erode",
        "Directional Blur",
        "Filter",               # changes
    ],
    "matte_node": [
        "Box Mask",
        "Channel Key",
        "Chroma Key",
        "Color Key",
        "Color Spill",
        "Cryptomatte",
        "Cryptomatte (Legacy)",
        "Difference Key",
        "Distance Key",
        "Double Edge Mask",
        "Ellipse Mask",
        "Keying",
        "Keying Screen",
        "Luminance Key"
    ],
    "distor_node": [
        "Corner Pin",
        "Crop",
        "Displace",
        "Flip",
        "Lens Distortion",
        "Map UV",
        "Movie Distortion",
        "Plane Track Deform",
        "Rotate",
        "Scale",
        "Stabilize 2D",
        "Transform",
        "Translate"
    ],
    "layout_node": [
        "Switch"
    ],
    "attribute_node": [
        "Attribute Statistic",
        "Capture Attribute",
        "Domain Size",
        "Remove Named Attribute",
        "Store Named Attribute"
    ],
    "geometry_node": [
        "Arc",
        "Bezier Segment",
        "Bounding Box",
        "Cone",
        "Convex Hull",
        "Cube",
        "Curve Circle",
        "Curve Length",
        "Curve Line",
        "Curve Spiral",             # change
        "Curve to Mesh",
        "Curve to Points",
        "Cylinder",
        "Deform Curves on Surface",
        "Delete Geometry",
        "Distribute Points in Volume",
        "Distribute Points on Faces",
        "Dual Mesh",
        "Duplicate Elements",
        "Edge Paths to Curves",
        "Extrude Mesh",
        "Fill Curve",
        "Fillet Curve",
        "Flip Faces",
        "Geometry Proximity",
        "Geometry to Instance",
        "Grid",
        "Group Input",
        "Group Output",
        "Ico Sphere",
        "Instance on Points",
        "Instances on Points",
        "Join Geometry",
        "Material Selection",
        "Merge by Distance",
        "Mesh Boolean",
        "Mesh Circle",
        "Mesh Line",
        "Mesh to Curve",
        "Mesh to Points",
        "Mesh to Volume",
        "Points",
        "Points to Vertices",
        "Points to Volume",
        "Quadratic Bezier",
        "Quadrilateral",
        "Raycast",
        "Realize Instances",
        "Replace Material",
        "Resample Curve",
        "Reverse Curve",
        "Sample Curve",
        "Sample Index",
        "Sample Nearest",
        "Sample Nearest Surface",
        "Sample UV Surface",
        "Scale Elements",
        "Scale Instances",
        "Separate Components",
        "Separate Geometry",
        "Set Curve Normal",
        "Set Curve Radius",
        "Set Curve Tilt",
        "Set Handle Positions",
        "Set Handle Type",
        "Set ID",
        "Set Material",
        "Set Material Index",
        "Set Point Radius",
        "Set Position",
        "Set Shade Smooth",
        "Set Spline Cyclic",
        "Set Spline Resolution",
        "Set Spline Type",
        "Split Edges",
        "Star",
        "String to Curves",
        "Subdivide Curve",
        "Subdivide Mesh",
        "Subdivision Surface",
        "Transform",
        "Translate Instances",
        "Triangulate",
        "Trim Curve",
        "UV Sphere",
        "Volume Cube",
        "Volume to Mesh"
    ]
}

node_to_category = {}
for c, nodes in category_to_node.items():
    node_to_category.update({node:c for node in nodes})

node_specifications = {
    'CompositorNodeAlphaOver': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Convert Premultiplied", value=node.use_premultiply),
            widgets.FloatFac()
        ]
    },
    'CompositorNodeAntiAliasing': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.FloatFac(),
            widgets.FloatFac(),
            widgets.FloatFac()
        ]
    },
    'CompositorNodeBilateralBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Iterations", value=node.iterations),
            widgets.Value(name="Color Sigma", value=node.iterations),
            widgets.Value(name="Space Sigma", value=node.iterations),
        ]
    },
    'CompositorNodeBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'filter_type')),
            *([
                widgets.Boolean(name="Variable Size", value=node.use_variable_size),
                widgets.Boolean(name="Bokeh", value=node.use_bokeh) if not node.use_variable_size else None,
                widgets.Boolean(name="Gamma", value=node.use_gamma_correction)
            ] if node.filter_type != 'FAST_GAUSS' else []),
            widgets.Boolean(name="Relative", value=node.use_relative),
            *([
                widgets.Label(text="Aspect Correction", align_right=False),
                widgets.SelectBar(),
                widgets.FloatFac(),
                widgets.FloatFac()
            ] if node.use_relative else []),
            *([
                widgets.Value(name="X", value=node.size_x),
                widgets.Value(name="Y", value=node.size_y)
            ] if not node.use_relative else []),
            widgets.Boolean(name="Extend Bounds", value=node.use_extended_bounds)
        ]
    },
    'CompositorNodeBokehBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Boolean(name="Variable Size", value=node.use_variable_size),
            widgets.Value(name="Max Blur", value=node.blur_max),
            widgets.Boolean(name="Extend Bounds", value=node.use_extended_bounds)
        ]
    },
    'CompositorNodeBokehImage': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="Flaps", value=node.flaps),
            widgets.Value(name="Angle", value=node.angle),
            widgets.Value(name="Rounding", value=node.rounding),
            widgets.Value(name="Catadioptric", value=node.catadioptric),
            widgets.Value(name="Rounding", value=node.rounding),
            widgets.FloatFac()
        ]
    },
    'CompositorNodeBoxMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Value(name="", value=node.x),
                widgets.Value(name="", value=node.y)
            ]),
            widgets.Columns(wids=[
                widgets.FloatFac(),
                widgets.FloatFac()
            ]),
            widgets.Value(name="Rotation", value=node.rotation),
            widgets.Columns(wids=[
                widgets.Label(text="Mask Type:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'mask_type'))
            ])
        ]
    },
    'CompositorNodeBrightContrast': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Convert Premultiplied", value=node.use_premultiply)
        ]
    },
    'CompositorNodeChannelMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeChromaMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Value(name="Aceptance", value=node.tolerance),
            widgets.Value(name="Cutoff", value=node.threshold),
            widgets.Value(name="Falloff", value=node.gain)
        ]
    },
    'CompositorNodeColorBalance': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Correction Formula:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'correction_method'))
            ]),
            widgets.Placeholder()
        ]
    },
    'CompositorNodeColorCorrection': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Boolean(name="Red", value=node.red),
                widgets.Boolean(name="Green", value=node.green),
                widgets.Boolean(name="Blue", value=node.blue),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="", align_right=False),
                widgets.Label(text="Saturation", align_right=False),
                widgets.Label(text="Contrast", align_right=False),
                widgets.Label(text="Gamma", align_right=False),
                widgets.Label(text="Gain", align_right=False),
                widgets.Label(text="Lift", align_right=False),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Master", align_right=False),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Highlights", align_right=False),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Midtones", align_right=False),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Shadows", align_right=False),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
            ]),
            widgets.Columns(wids=[
                widgets.FloatFac(),
                widgets.FloatFac()
            ])
        ]
    },
    'CompositorNodeColorMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.FloatFac(),
            widgets.FloatFac(),
            widgets.FloatFac()
        ]
    },
    'CompositorNodeColorSpill': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Value(text="Despill Channel", align_right=False),
            widgets.SelectBar(),
            widgets.Columns(wids=[
                widgets.Label(text="Algorithm", align_right=False),
                widgets.Dropdown(value=enumName(node, 'limit_method'))
            ]),
            *([
                widgets.Label(text="Limiting Channel:", align_right=False),
                widgets.SelectBar()
            ] if node.limit_method == 'SIMPLE' else []),
            widgets.FloatFac(), # ratio
            widgets.Boolean(name="Unspill", value=node.use_unspill),
            *([
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac()
            ] if node.use_unspill else [])
        ]
    },
    'CompositorNodeCombineColor': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'mode')),
            widgets.Dropdown(value=enumName(node, 'ycc_mode')) if node.mode == "YCC" else None
        ]
    },
    'CompositorNodeCombineXYZ': {
        'class': 'converter_node',
    },
    'CompositorNodeConvertColorSpace': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="From:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'from_color_space'))
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="To:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'to_color_space'))
            ])
        ]
    },
    'CompositorNodeCornerPin': {
        'class': 'distor_node'
    },
    'CompositorNodeCrop': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Boolean(name="Crop Image Size", value=node.use_crop_size),
            widgets.Boolean(name="Relative", value=node.relative),
            *([
                widgets.Value(name="Left", value=node.min_x),
                widgets.Value(name="Right", value=node.max_x),
                widgets.Value(name="Up", value=node.min_y),
                widgets.Value(name="Down", value=node.max_y)
            ] if not node.relative else []),
            *([
                widgets.Value(name="Left", value=node.rel_min_x),
                widgets.Value(name="Right", value=node.rel_max_x),
                widgets.Value(name="Up", value=node.rel_min_y),
                widgets.Value(name="Down", value=node.rel_max_y)
            ] if node.relative else [])
        ]
    },
    'CompositorNodeCryptomatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeCryptomatteV2': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeCurveRGB': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeCurveVec': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Curves()
        ]
    },
    'CompositorNodeDefocus': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Label(text="Bokeh Type:", align_right=False),
            widgets.Dropdown(value=enumName(node, 'bokeh')),
            widgets.Value(name="Angle", value=node.angle),
            widgets.Boolean(name="Gamma Correction", value=node.use_gamma_correction),
            widgets.Value(name="F-Stop", value=node.f_stop),
            widgets.Value(name="Max Blur", value=node.blur_max),
            widgets.Value(name="Threshold", value=node.threshold),
            widgets.Boolean(name="Preview", value=node.use_preview),
            widgets.Scene(),
            widgets.Boolean(name="Use Z-Buffer", value=node.use_zbuffer),
            widgets.Value(name="Z-Scale", value=node.z_scale)
        ]
    },
    'CompositorNodeDenoise': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Label(text="Prefilter", align_right=False),
            widgets.Dropdown(enumName(node, 'prefilter')),
            widgets.Boolean(name="HDR", value=node.use_hdr)
        ]
    },
    'CompositorNodeDiffMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.FloatFac(),
            widgets.FloatFac()
        ]
    },
    'CompositorNodeDilateErode': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Mode:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'mode'))
            ]),
            widgets.Value(name="Distance", value=node.distance),
            widgets.Value(name="Edge", value=node.edge) if node.mode == 'THRESHOLD' else None,
            widgets.Columns(wids=[
                widgets.Label(text="Falloff", align_right=False),
                widgets.Dropdown(value=enumName(node, 'falloff'))
            ]) if node.mode == 'FEATHER' else None
        ]
    },
    'CompositorNodeDisplace': {
        'class': 'distor_node'
    },
    'CompositorNodeDistanceMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.FloatFac(),
            widgets.FloatFac(),
            widgets.Label(text="Color Space:", align_right=False),
            widgets.SelectBar()
        ]
    },
    'CompositorNodeDoubleEdgeMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Label(text="Inner Edge:", align_right=False),
            widgets.Dropdown(value=enumName(node, 'inner_mode')),
            widgets.Label(text="Buffer Edge:", align_right=False),
            widgets.Dropdown(value=enumName(node, 'edge_mode')),
        ]
    },
    'CompositorNodeDBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Iterations", value=node.iterations),
            widgets.Boolean(name="Wrap", value=node.use_wrap),
            widgets.Label(text="Center:", align_right=False),
            widgets.Value(name="X", value=node.center_x),
            widgets.Value(name="Y", value=node.center_y),
            widgets.Value(name="Distance", value=node.distance),
            widgets.Value(name="Angle", value=node.angle),
            widgets.Value(name="Spin", value=node.spin),
            widgets.Value(name="Zoom", value=node.zoom)
        ]
    },
    'CompositorNodeEllipseMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Value(name="X", value=node.x),
                widgets.Value(name="Y", value=node.y)
            ]),
            widgets.Columns(wids=[
                widgets.FloatFac(),
                widgets.FloatFac()
            ]),
            widgets.Value(name="Rotation", value=node.rotation),
            widgets.Columns(wids=[
                widgets.Label(text="Mask Type:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'mask_type'))
            ])
        ]
    },
    'CompositorNodeExposure': {
        'class': 'color_node'
    },
    'CompositorNodeFilter': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'filter_type'))
        ],
        'name_behavior': lambda node: enumName(node, 'filter_type')
    },
    'CompositorNodeFlip': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'axis'))
        ]
    },
    'CompositorNodeGamma': {
        'class': 'color_node'
    },
    'CompositorNodeGlare': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'glare_type')),
            widgets.Dropdown(value=enumName(node, 'quality')),
            widgets.Value(name="Iterations", value=node.iterations) if node.glare_type != 'FOG_GLOW' else None,
            # color modulation
            widgets.FloatFac() if node.glare_type == 'GHOSTS' or node.glare_type == 'STREAKS' else None,
            widgets.Value(name="Mix", value=node.mix),
            widgets.Value(name="Threshold", value=node.threshold),
            *([
                widgets.Value(name="Streaks", value=node.streaks),
                widgets.Value(name="Angle Offset", value=node.angle_offset),
            ] if node.glare_type == 'STREAKS' else []),
            widgets.Value(name="Size", value=node.size) if node.glare_type == 'FOG_GLOW' else None,
            widgets.FloatFac() if node.glare_type == 'STREAKS' or node.glare_type == 'SIMPLE_STAR' else None, # fade
            widgets.Boolean(name="Rotate 45", value=node.use_rotate_45) if node.glare_type == 'SIMPLE_STAR' else None
        ]
    },
    'CompositorNodeHueCorrect': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Mapping()
        ]
    },
    'CompositorNodeHueSat': {
        'class': 'color_node'
    },
    'CompositorNodeIDMask': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Value(name="Index", value=node.index),
            widgets.Boolean(name="Anti-Aliasing", value=node.use_antialiasing)
        ]
    },
    'CompositorNodeImage': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeInpaint': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Distance", value=node.distance)
        ]
    },
    'CompositorNodeInvert': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="RGB", value=node.invert_rgb),
            widgets.Boolean(name="Alpha", value=node.invert_alpha)
        ]
    },
    'CompositorNodeKeying': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Value(name="Pre Blur", value=node.blur_pre),
            widgets.FloatFac(), #screen_balance
            widgets.FloatFac(), #despill_factor
            widgets.FloatFac(), #despill_balance
            widgets.Value(name="Edge Kernel Radius", value=node.edge_kernel_radius),
            widgets.FloatFac(), #edge kernel tolerance
            widgets.FloatFac(), #clip_black
            widgets.FloatFac(), #clip_white
            widgets.Value(name="Dilate/Erode", value=node.dilate_distance),
            widgets.Columns(wids=[
                widgets.Label(text="Feather Falloff", align_right=False),
                widgets.Dropdown(value=enumName(node, 'feather_falloff'))
            ]),
            widgets.Value(name="Feather Distance", value=node.feather_distance),
            widgets.Value(name="Post Blur", value=node.blur_post)
        ]
    },
    'CompositorNodeKeyingScreen': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Tracking()
        ]
    },
    'CompositorNodeLensdist': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Boolean(name="Projector", value=node.use_projector),
            widgets.Boolean(name="Jitter", value=node.use_jitter),
            widgets.Boolean(name="Fit", value=node.use_fit),
        ]
    },
    'CompositorNodeLuminance': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.FloatFac(), #limit_max
            widgets.FloatFac() #limit_min
        ]
    },
    'CompositorNodeMapRange': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'CompositorNodeMapUV': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Value(name="Alpha", value=node.alpha)
        ]
    },
    'CompositorNodeMapValue': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Label(text="Offset:", align_right=False),
            widgets.Value(name="", value=node.offset),
            widgets.Label(text="Size:", align_right=False),
            widgets.Value(name="", value=node.size),
            widgets.Boolean(name="Use Minimum", value=node.use_min),
            widgets.Value(name="", value=node.min),
            widgets.Boolean(name="Use Maximum", value=node.use_max),
            widgets.Value(name="", value=node.max)
        ]
    },
    'CompositorNodeMask': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder(),
            widgets.Boolean(name="Feather", value=node.use_feather),
            widgets.Dropdown(value=enumName(node, 'size_source')),
            widgets.Value(name="X", value=node.size_x) if node.size_source != 'SCENE' else None,
            widgets.Value(name="Y", value=node.size_y) if node.size_source != 'SCENE' else None,
            widgets.Boolean(name="Motion Blur", value=node.use_motion_blur),
            widgets.Value(name="Samples", value=node.motion_blur_samples) if node.use_motion_blur else None,
            widgets.Value(name="Shutter", value=node.motion_blur_shutter) if node.use_motion_blur else None
        ]
    },
    'CompositorNodeMath': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'operation')),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ],
        'name_behavior': lambda node: enumName(node, 'operation')
    },
    'CompositorNodeMovieDistortion': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeNormal': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeNormalize': {
        'class': 'vector_node'
    },
    'CompositorShaderNodeMixRGB': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'blend_type')),
            widgets.Boolean(name="Alpha", value=node.use_alpha),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'CompositorNodePixelate': {
        'class': 'filter_node'
    },
    'CompositorNodePosterize': {
        'class': 'color_node'
    },
    'CompositorNodePremulKey': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'mapping'))
        ]
    },
    'ComopositorNodeRGB': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.ColorPicker(),
            widgets.RGBA(color=socketColorToSVGColor(node.outputs[0].default_value))
        ]
    },
    'CompositorNodeRGBCurves': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeRGBToBW': {
        'class': 'color_node'
    },
    'CompositorNodeRLayers': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeSeparateColor': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'mode')),
            widgets.Dropdown(value=enumName(node, 'ycc_mode')) if node.mode == 'YCC' else None
        ]
    },
    'CompositorNodeSeparateXYZ': {
        'class': 'converter_node'
    },
    'CompositorNodeSetAlpha': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Mode:", align_right=False),
                widgets.Dropdown(value=enumName(node, 'mode'))
            ])
        ]
    },
    'CompositorNodeSunBeams': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeSwitchView': {
        'class': 'converter_node'
    },
    'CompositorNodeTexture': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Texture()
        ]
    },
    'CompositorNodeTonemap': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'tonemap_type')),
            *([
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac(),
                widgets.FloatFac()
            ] if node.tonemap_type == "RD_PHOTORECEPTOR" else []),
            *([
                widgets.FloatFac(),
                widgets.Value(name="Offset", value=node.offset),
                widgets.Value(name="Gamma", value=node.gamma),
            ] if node.tonemap_type == "RH_SIMPLE" else [])
        ]
    },
    'CompositorNodeSceneTime': {
        'class': 'input_node'
    },
    'CompositorNodeTimeCurve': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Curves(),
            widgets.Value(name="Start", value=node.frame_start),
            widgets.Value(name="End", value=node.frame_end)
        ]
    },
    'CompositorNodeTrackPos': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'CompositorNodeValToRGB': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Ramp()
        ]
    },
    'CompositorNodeValue': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="", value=node.outputs[0].default_value)
        ]
    },
    'CompositorNodeVecBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Samples", value=node.samples),
            widgets.Value(name="Blur", value=node.factor),
            widgets.Label(text="Speed:", align_right=False),
            widgets.Value(name="Min", value=node.speed_min),
            widgets.Value(name="Max", value=node.speed_max),
            widgets.Boolean(name="Curved", value=node.use_curved)
        ]
    },
    'CompositorNodeZcombine': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Alpha", value=node.use_alpha),
            widgets.Boolean(name="Anti-Alias Z", value=node.use_antialias_z)
        ]
    },

    ### SHADER NODES ###


    'ShaderNodeAddShader': {
        'class': 'shader_node'
    },
    'ShaderNodeAmbientOcclusion': {
        'class': 'input_node',
        "props": lambda node: [
            widgets.Value(name="Samples", value=str(node.samples)),
            widgets.Boolean(name="Inside", value=node.inside),
            widgets.Boolean(name="Only Local", value=node.only_local)
        ]
    },
    'ShaderNodeAttribute': {
        'class': 'input_node',
        "props": lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Type:", align_right=False),
                widgets.Dropdown(value=node.attribute_type)
            ]),
            widgets.Value(name="Name:", value=node.attribute_name)
        ]
    },
    'ShaderNodeBackground': {
        'class': 'shader_node'
    },
    'ShaderNodeBevel': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="Samples", value=str(node.samples))
        ]
    },
    'ShaderNodeBlackbody': {
        'class': 'converter_node'
    },
    'ShaderNodeBrightContrast': {
        'class': 'color_node'
    },
    'ShaderNodeBsdfDiffuse': {
        'class': 'shader_node',
    },
    'ShaderNodeBsdfGlass': {
        'class': 'shader_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.distribution)
        ]
    },
    'ShaderNodeBsdfGlossy': {
        'class': 'shader_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.distribution)
        ]
    },
    'ShaderNodeBsdfPrincipled': {
        'class': 'shader_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.distribution),
            widgets.Dropdown(value=node.subsurface_method)
        ]
    },
    'ShaderNodeBsdfRefraction': {
        'class': 'shader_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.distribution)
        ]
    },
    'ShaderNodeBsdfTranslucent': {
        'class': 'shader_node'
    },
    'ShaderNodeBsdfTransparent': {
        'class': 'shader_node'
    },
    'ShaderNodeBump': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Boolean(name="Invert", value=node.invert)
        ]
    },
    'ShaderNodeCameraData': {
        'class': 'input_node',
    },
    'ShaderNodeClamp': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.clamp_type)
        ]
    },
    'ShaderNodeColorRamp': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Ramp()
        ]
    },
    'ShaderNodeCombineColor': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.mode)
        ]
    },
    'ShaderNodeCombineXYZ': {
        'class': 'converter_node'
    },
    'ShaderNodeDisplacement': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.space)
        ]
    },
    'ShaderNodeEeveeSpecular': {
        'class': 'shader_node'
    },
    'ShaderNodeEmission': {
        'class': 'shader_node'
    },
    'ShaderNodeFloatCurve': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Curves()
        ]
    },
    'ShaderNodeFresnel': {
        'class': 'input_node',
    },
    'ShaderNodeGamma': {
        'class': 'color_node'
    },
    'ShaderNodeHairInfo': {
        'class': 'input_node',
    },
    'ShaderNodeHoldout': {
        'class': 'shader_node'
    },
    'ShaderNodeHueSaturation': {
        'class': 'color_node'
    },
    'ShaderNodeInvert': {
        'class': 'color_node'
    },
    'ShaderNodeLightFalloff': {
        'class': 'color_node'
    },
    'ShaderNodeMapping': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Type:", align_right=False),
                widgets.Dropdown(value=node.vector_type)
            ])
        ]
    },
    'ShaderNodeMapRange': {
        'class': None,
        'class_behavior': lambda node: 'converter_node' if node.data_type[0] == "F" else 'vector_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.data_type),
            widgets.Dropdown(value=node.interpolation_type),
            widgets.Boolean(name="Clamp", value=node.clamp) if node.data_type[-1] == "R" else None
        ]
    },
    'ShaderNodeMath': {
        'class': 'converter_node',
        'name_behavior': lambda node: node.operation,
        'props': lambda node: [
            widgets.Dropdown(value=node.operation),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'ShaderNodeMix': {
        'class': None,
        'class_behavior': lambda node: {
            'FLOAT': 'converter_node',
            'VECTOR': 'vector_node',
            'RGBA': 'color_node',
            'ROTATION': 'vector_node'
        }[node.data_type],
        'props': lambda node: [
            widgets.Dropdown(value=node.data_type),
            widgets.Placeholder(),
            widgets.Boolean(name="Clamp Factor", value=node.clamp_factor),
        ]
    },
    'ShaderNodeMixShader': {
        'class': 'shader_node'
    },
    'ShaderNodeNewGeometry': {
        'class': 'input_node',
    },
    'ShaderNodeNormalMap': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.space),
            widgets.UVMap() if node.space[0] == "T" else None
        ]
    },
    'ShaderNodeLayerWeight': {
        'class': 'input_node'
    },
    'ShaderNodeLightPath': {
        'class': 'input_node'
    },
    'ShaderNodeObjectInfo': {
        'class': 'input_node'
    },
    'ShaderNodeOutputAOV': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Value(name="Name:", value=node.name)
        ]
    },
    'ShaderNodeOutputMaterial': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.target)
        ]
    },
    'ShaderNodeOutputLineStyle': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.blend_type),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'ShaderNodeOutputWorld': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.target)
        ]
    },
    'ShaderNodeParticleInfo': {
        'class': 'input_node'
    },
    'ShaderNodePointInfo': {
        'class': 'input_node'
    },
    'ShaderNodeRGB': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.ColorPicker(),
            widgets.RGBA(color=socketColorToSVGColor(node.outputs[0].default_value))
        ]
    },
    'ShaderNodeRGBCurve': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Curves()
        ]
    },
    'ShaderNodeRGBToBW': {
        'class': 'converter_node',
    },
    'ShaderNodeScript': {
        'class': 'script_node',
        'props': lambda node: [
            widgets.SelectBar(),
            widgets.Script() if node.mode[0] == "I" else widgets.File()
        ]
    },
    'ShaderNodeSeparateColor': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.mode)
        ]
    },
    'ShaderNodeSeparateXYZ': {
        'class': 'converter_node'
    },
    'ShaderNodeShaderToRGB': {
        'class': 'converter_node'
    },
    'ShaderNodeSubsurfaceScattering': {
        'class': 'shader_node'
    },
    'ShaderNodeTangent': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Dropdown(value=node.direction_type),
                widgets.SelectBar()
            ])
        ]
    },
    'ShaderNodeTexBrick': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.FloatFac(),
            widgets.Value(name="Frequency", value=node.offset_frequency),
            widgets.Value(name="Squash", value=node.squash),
            widgets.Value(name="Frequency", value=node.squash_frequency)
        ]
    },
    'ShaderNodeTexChecker': {
        'class': 'texture_node'
    },
    'ShaderNodeTexCoord': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Object:", align_right=False),
                widgets.Object()
            ]),
            widgets.Boolean(name="From Instancer", value=node.from_instancer)
        ]
    },
    'ShaderNodeTexEnvironment': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Image(),
            widgets.Dropdown(value=node.interpolation),
            widgets.Dropdown(value=node.projection)
        ]
    },
    'ShaderNodeTexGradient': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.gradient_type)
        ]
    },
    'ShaderNodeTexIES': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.SelectBar(),
            widgets.IES() if node.mode == 'INTERNAL' else widgets.File()
        ]
    },
    'ShaderNodeTexImage': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Image(),
            widgets.Dropdown(value=node.interpolation),
            widgets.Dropdown(value=node.projection),
            widgets.Dropdown(value=node.extension),
        ]
    },
    'ShaderNodeTexMagic': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Value(name="Depth", value=node.turbulence_depth)
        ]
    },
    'ShaderNodeTexMusgrave': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.musgrave_dimensions),
            widgets.Dropdown(value=node.musgrave_type)
        ]
    },
    'ShaderNodeTexNoise': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.noise_dimensions)
        ]
    },
    'ShaderNodeTexPointDensity': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.SelectBar(value=node.point_source),
            widgets.Object(),
            widgets.Dropdown(value=node.space),
            widgets.Value(name="Radius", value=node.radius),
            widgets.Dropdown(value=node.interpolation),
            widgets.Value(name="Resolution", value=node.resolution),
            widgets.Dropdown(value=node.particle_color_source) if node.point_source[0] == "P" else widgets.Dropdown(value=node.vertex_color_source)
        ]
    },
    'ShaderNodeTexSky': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'ShaderNodeTexVoronoi': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Placeholder()
        ]
    },
    'ShaderNodeTexWave': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.wave_type),
            widgets.Dropdown(value=node.rings_direction) if node.wave_type[0] == "R" else widgets.Dropdown(node.bands_direction),
            widgets.Dropdown(value=node.wave_profile)
        ]
    },
    'ShaderNodeTexWhiteNoise': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.noise_dimensions)
        ]
    },
    'ShaderNodeUVAlongStroke': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Tips", value=node.use_tips)
        ]
    },
    'ShaderNodeUVMap': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="From Instancer", value=node.from_instancer),
            widgets.UVMap()
        ]
    },
    'ShaderNodeValue': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="", value=node.outputs[0].default_value)
        ]
    },
    'ShaderNodeVectorCurve': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Curves()
        ]
    },
    'ShaderNodeVectorDisplacement': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.space)
        ]
    },
    'ShaderNodeVectorMath': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Dropdown(value=node.operation)
        ],
        'name_behavior': lambda node: node.operation
    },
    'ShaderNodeVectorRotate': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Type:", align_right=False),
                widgets.Dropdown(value=node.rotation_type)
            ]),
            widgets.Boolean(name="Invert", value=node.invert)
        ]
    },
    'ShaderNodeVectorTransform': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.SelectBar(),
            widgets.Dropdown(value=node.convert_from),
            widgets.Dropdown(value=node.convert_to)
        ]
    },
    'ShaderNodeVertexColor': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Label(text=node.layer_name, align_right=True)
        ]
    },
    'ShaderNodeVolumeAbsorption': {
        'class': 'shader_node'
    },
    'ShaderNodeVolumeInfo': {
        'class': 'input_node'
    },
    'ShaderNodeVolumePrincipled': {
        'class': 'shader_node'
    },
    'ShaderNodeVolumeScatter': {
        'class': 'shader_node'
    },
    'ShaderNodeWavelength': {
        'class': 'converter_node'
    },
    'ShaderNodeWireframe': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="Pixel Size", value=node.use_pixel_size)
        ]
    }
}