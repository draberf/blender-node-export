# node.name -- needs to remove .### in case of multiple nodes

from . import widgets

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
    "ShaderNodeAmbientOcclusion": {
        "props": lambda node: [
            widgets.Value(name="Samples", value=str(node.samples)),
            widgets.Boolean(name="Inside", value=node.inside),
            widgets.Boolean(name="Only Local", value=node.only_local)
        ]
    },
    "ShaderNodeAttribute": {
        "props": lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Type:", align_right=False),
                widgets.Dropdown(value=node.attribute_type)
            ]),
            widgets.Value(name="Name:", value=node.attribute_name)
        ]
    },
    "ShaderNodeBevel": {
        "props": lambda node: [
            widgets.Value(name="Samples", value=str(node.samples))
        ]
    },
    "ShaderNodeOutputAOV": {
        "props": lambda node: [
            widgets.Value(name="Name:", value=node.name)
        ]
    },
    "ShaderNodeOutputMaterial": {
        "props": lambda node: [
            widgets.Dropdown(value=node.target)
        ]
    },
    "ShaderNodeRGB": {
        "props": lambda node: [
            widgets.RGBA(color="#ffcc00")
        ]
    },
    "ShaderNodeTangent": {
        "props": lambda node: [
            widgets.Columns(wids=[
                widgets.Dropdown(value=node.direction_type),
                widgets.Label(text=(node.axis if node.direction_type[0]=="R" else node.uv_map), align_right=True)
            ])
        ]
    },
    "ShaderNodeTexCoord": {
        "props": lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Object:", align_right=False),
                widgets.Label(text="" if not node.object else node.object.name, align_right=True)
            ]),
            widgets.Boolean(name="From Instancer", value=node.from_instancer)
        ]
    },
    "ShaderNodeVertexColor": {
        "props": lambda node: [
            widgets.Label(text=node.layer_name, align_right=True)
        ]
    },
}