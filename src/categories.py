# node.name -- needs to remove .### in case of multiple nodes

from . import widgets
from .methods import socketColorToSVGColor, enumName, getFloatString
from .constants import IGNORE_PROPS

CATEGORY_NAMES = (
    'input',
    'output',
    'shader',
    'texture',
    'color',
    'vector',
    'converter',
    'script',
    'filter',
    'matte',
    'distor',
    'layout',
    'attribute',
    'geometry',
    'group',
    'layout'
)


CHANNEL_MATTE_OPTS = {
    'RGB': ['R', 'G', 'B'],
    'HSV': ['H', 'S', 'V'],
    'YUV': ['Y', 'U', 'V'],
    'YCC': ['Y', 'Cr', 'Cb']
}

def dropdown(node, prop, label="") -> widgets.Widget:
    if not label:
        return widgets.Dropdown(value=enumName(node, prop))
    else:
        return widgets.LabeledDropdown(name=label, value=enumName(node, prop))


def selectBar(node, prop) -> widgets.Widget:
    options = [option.name for option in node.bl_rna.properties[prop].enum_items]
    try:
        index = [option.identifier for option in node.bl_rna.properties[prop].enum_items].index(getattr(node, prop))
    except ValueError as ve:
        for key, item in node.bl_rna.properties[prop].enum_items.items():
            print(">>", key, item.name)
        raise ve
    return widgets.SelectBar(options=options, select_index=index)

def object(object) -> widgets.Widget:
    if not object: return widgets.String(name="Object:", value="")
    return widgets.String(name="Object:", value=object.name)

def image(image) -> widgets.Widget:
    if not image: return widgets.SelectBar(["+ New", "Open"], -1)
    return widgets.String(value=image.name)

def curve(curving, type='VALUE', sampling=40) -> widgets.Widget:
    
    def evaluate_curve_n(n):
        pairs = []
        for N in range(sampling+1):
            x = curving.clip_min_x + N * (curving.clip_max_x-curving.clip_min_x) * (1.0 / sampling)
            y = curving.evaluate(curving.curves[n], x)
            calc_y = (y-curving.clip_min_y) / (curving.clip_max_y-curving.clip_min_y)
            pairs.append((
                (x-curving.clip_min_x) / (curving.clip_max_x-curving.clip_min_x),
                2 * calc_y - 1 if type == 'CORRECT' else calc_y
            ))
        return pairs
    
    match type:
        case "VALUE":
            points = evaluate_curve_n(0)
            return widgets.Curves(curves=[('black', points, False)])
        case "CRGB":
            return widgets.Curves(curves=[
                ('#222222', evaluate_curve_n(3), True),
                *[(color, evaluate_curve_n(N), False) for N, color in enumerate(['red', 'green', 'blue'])]
            ])
        case "XYZ":
            return widgets.Curves(curves=[
                (color, evaluate_curve_n(N), False) for N, color in enumerate(['red', 'green', 'blue'])
            ])
        case "CORRECT":
            return widgets.Curves(curves=[
                (color, evaluate_curve_n(N), False) for N, color in enumerate(['red', 'green', 'blue'])
            ], hue_background=True)
        case _:
            print(f"WARNING: Undefined curve type {type}.")
            return widgets.Curves(curves=[('black'), evaluate_curve_n(0), False])

def ramp(node, n=50) -> widgets.Ramp:

    color_mode = node.color_ramp.color_mode
    interpolation = enumName(node.color_ramp, 'interpolation' if color_mode == 'RGB' else 'hue_interpolation') 

    return widgets.Ramp(color_mode=color_mode,
                        interpolation=interpolation,
                        stops=[(element.position, element.color) for element in node.color_ramp.elements],
                        evals=[node.color_ramp.evaluate(min(i/n, 1.0)) for i in range(n+1)])

def generateCustomProps(node):
    
    wids = []
    
    for prop in node.bl_rna.properties:
        if not prop.identifier: continue
        if prop.identifier in IGNORE_PROPS: continue

        try:
            match prop.type:
                case 'BOOLEAN':
                    wids.append(widgets.Boolean(name=prop.name, value=getattr(node, prop.identifier)))
                case 'INT':
                    wids.extend([
                        widgets.Label(text=prop.name),
                        widgets.Value(value=getattr(node, prop.identifier))
                    ])
                case 'FLOAT':
                    wids.extend([
                        widgets.Label(text=prop.name),
                        widgets.Float(value=getattr(node, prop.identifier))
                    ])
                case 'STRING':
                    wids.extend([
                        widgets.Label(text=prop.name),
                        widgets.String(value=getattr(node, prop.identifier))
                    ])
                case 'ENUM':
                    print([item for item in node.bl_rna.properties.items()])
                    print('>>>>>', prop.identifier)
                    wids.extend([
                        widgets.Label(text=prop.name),
                        dropdown(node, prop.identifier)
                    ])
                case 'POINTER' | 'COLLECTION':
                    obj = getattr(node, prop.identifier)
                    obj_name = ""
                    if obj:
                        if 'name' in obj.bl_rna.properties:
                            obj_name = obj.name
                    wids.extend([
                        widgets.Label(text=prop.name),
                        widgets.String(value=obj_name)
                    ])
        except:
            wids.extend([
                widgets.Label(text=prop.name),
                widgets.Placeholder()
            ])
    
    return wids

CATEGORIES = [name+'_node' for name in CATEGORY_NAMES]

node_specifications = {

    ### COMPOSITOR NODES ###

    # Compositor > Input

    'CompositorNodeBokehImage': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder(),
            widgets.Value(name="Flaps", value=node.flaps),
            widgets.Angle(name="Angle", value=node.angle),
            widgets.Float(name="Rounding", value=node.rounding),
            widgets.Float(name="Catadioptric", value=node.catadioptric),
            widgets.Float(name="Lens Shift", value=node.shift, minmax=(-1.0,1.0))
        ]
    },
    'CompositorNodeImage': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder() if node.image else None,
            image(node.image),
            *([
                dropdown(node.image, 'source'),
                widgets.LabeledDropdown(name="Color Space", value="") if not node.image.colorspace_settings.name else dropdown(node.image.colorspace_settings, 'name', label="Color Space"),
                dropdown(node.image, 'alpha_mode', label="Alpha")
            ] if node.image else []),
        ]
    },
    'CompositorNodeMask': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.String(value="" if not node.mask else node.mask.name),
            widgets.Boolean(name="Feather", value=node.use_feather),
            dropdown(node, 'size_source'),
            widgets.Float(name="X", value=node.size_x) if node.size_source != 'SCENE' else None,
            widgets.Float(name="Y", value=node.size_y) if node.size_source != 'SCENE' else None,
            widgets.Boolean(name="Motion Blur", value=node.use_motion_blur),
            widgets.Value(name="Samples", value=node.motion_blur_samples) if node.use_motion_blur else None,
            widgets.Float(name="Shutter", value=node.motion_blur_shutter) if node.use_motion_blur else None
        ]
    },
    'CompositorNodeMovieClip': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder(),
            widgets.String(value="" if not node.clip else node.clip.name)
        ]
    },
    'CompositorNodeRLayers': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.String(value="" if not node.scene else node.scene.name),
            widgets.Dropdown(value=node.layer) if node.scene else None
        ]
    },
    'CompositorNodeRGB': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.ColorPicker(color=node.outputs[0].default_value),
            widgets.RGBA(color=socketColorToSVGColor(node.outputs[0].default_value))
        ]
    },
    'CompositorNodeSceneTime': {
        'class': 'input_node'
    },
    'CompositorNodeTexture': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Placeholder(),
            widgets.String(value="" if not node.texture else node.texture.name),
        ]
    },
    'CompositorNodeTime': {
        'class': 'input_node',
        'props': lambda node: [
            curve(node.curve, type='VALUE'),
            widgets.Value(name="Start", value=node.frame_start),
            widgets.Value(name="End", value=node.frame_end)
        ]
    },
    'CompositorNodeTrackPos': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.String(value="" if not node.clip else node.clip.name),
            *([
                widgets.String(value=node.tracking_object),
                widgets.String(value=node.track_name),
                dropdown(node, 'position', label="Position:"),
                widgets.Value(name="Frame", value=node.frame_relative) if node.position == 'RELATIVE_FRAME' else None
            ] if node.clip else [])
        ]
    },
    'CompositorNodeValue': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Float(name="", value=node.outputs[0].default_value)
        ]
    },

    # Compositor > Output

    'CompositorNodeComposite': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Alpha", value=node.use_alpha)
        ]
    },
    'CompositorNodeOutputFile': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Label(text="Base Path:"),
            widgets.File()
        ]
    },
    'CompositorNodeLevels': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'channel')
        ]
    },
    'CompositorNodeSplitViewer': {
        'class': 'output_node',
        'props': lambda node: [
            selectBar(node, 'axis'), # axis
            widgets.Value(name="Factor", value=node.factor)
        ]
    },
    'CompositorNodeViewer': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Alpha", value=node.use_alpha)
        ]
    },

    # Compositor > Color

    'CompositorNodeAlphaOver': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Convert Premultiplied", value=node.use_premultiply),
            widgets.Float(name="Premultiplied", value=node.premul, minmax=(0.0,1.0))
        ]
    },
    'CompositorNodeBrightContrast': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Convert Premultiplied", value=node.use_premultiply)
        ]
    },
    'CompositorNodeColorBalance': {
        'class': 'color_node',
        'props': lambda node: [
            dropdown(node, 'correction_method', label="Correction Formula:"),
            widgets.Columns(wids=[
                widgets.ColorPicker(color=node.lift),
                widgets.ColorPicker(color=node.gamma),
                widgets.ColorPicker(color=node.gain),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Lift:"), widgets.RGBA(color=socketColorToSVGColor(node.lift)),
                widgets.Label(text="Gamma:"), widgets.RGBA(color=socketColorToSVGColor(node.gamma)),
                widgets.Label(text="Gain:"), widgets.RGBA(color=socketColorToSVGColor(node.gain)),
            ])
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
                widgets.Label(text=""),
                widgets.Label(text="Saturation"),
                widgets.Label(text="Contrast"),
                widgets.Label(text="Gamma"),
                widgets.Label(text="Gain"),
                widgets.Label(text="Lift"),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Master"),
                widgets.Float(value=node.master_saturation, minmax=(0.0,4.0)),
                widgets.Float(value=node.master_contrast, minmax=(0.0,4.0)),
                widgets.Float(value=node.master_gamma, minmax=(0.0,4.0)),
                widgets.Float(value=node.master_gain, minmax=(0.0,4.0)),
                widgets.Float(value=node.master_lift, minmax=(-1.0,1.0)),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Highlights"),
                widgets.Float(value=node.highlights_saturation, minmax=(0.0,4.0)),
                widgets.Float(value=node.highlights_contrast, minmax=(0.0,4.0)),
                widgets.Float(value=node.highlights_gamma, minmax=(0.0,4.0)),
                widgets.Float(value=node.highlights_gain, minmax=(0.0,4.0)),
                widgets.Float(value=node.highlights_lift, minmax=(-1.0,1.0)),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Midtones"),
                widgets.Float(value=node.midtones_saturation, minmax=(0.0,4.0)),
                widgets.Float(value=node.midtones_contrast, minmax=(0.0,4.0)),
                widgets.Float(value=node.midtones_gamma, minmax=(0.0,4.0)),
                widgets.Float(value=node.midtones_gain, minmax=(0.0,4.0)),
                widgets.Float(value=node.midtones_lift, minmax=(-1.0,1.0)),
            ]),
            widgets.Columns(wids=[
                widgets.Label(text="Shadows"),
                widgets.Float(value=node.shadows_saturation, minmax=(0.0,4.0)),
                widgets.Float(value=node.shadows_contrast, minmax=(0.0,4.0)),
                widgets.Float(value=node.shadows_gamma, minmax=(0.0,4.0)),
                widgets.Float(value=node.shadows_gain, minmax=(0.0,4.0)),
                widgets.Float(value=node.shadows_lift, minmax=(-1.0,1.0)),
            ]),
            widgets.Columns(wids=[
                widgets.Float(name="Midtones Start", value=node.midtones_start, minmax=(0.0,1.0)),
                widgets.Float(name="Midtones End", value=node.midtones_end, minmax=(0.0,1.0))
            ])
        ]
    },
    'CompositorNodeExposure': {
        'class': 'color_node'
    },
    'CompositorNodeGamma': {
        'class': 'color_node'
    },
    'CompositorNodeHueCorrect': {
        'class': 'color_node',
        'props': lambda node: [
            curve(node.mapping, 'CORRECT')
        ]
    },
    'CompositorNodeHueSat': {
        'class': 'color_node'
    },
    'CompositorNodeInvert': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="RGB", value=node.invert_rgb),
            widgets.Boolean(name="Alpha", value=node.invert_alpha)
        ]
    },
    'CompositorNodeMixRGB': {
        'class': 'color_node',
        'props': lambda node: [
            dropdown(node, 'blend_type'),
            widgets.Boolean(name="Alpha", value=node.use_alpha),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'CompositorNodePosterize': {
        'class': 'color_node'
    },
    'CompositorNodeCurveRGB': {
        'class': 'color_node',
        'props': lambda node: [
            curve(node.mapping, type='CRGB')
        ]
    },
    'CompositorNodeTonemap': {
        'class': 'color_node',
        'props': lambda node: [
            dropdown(node, 'tonemap_type'),
            *([
                widgets.Float(name="Intensity", value=node.intensity),
                widgets.Float(name="Contrast", value=node.contrast, minmax=(0.0,1.0)),
                widgets.Float(name="Adaptation", value=node.adaptation, minmax=(0.0,1.0)),
                widgets.Float(name="Color Correction", value=node.correction, minmax=(0.0,1.0))
            ] if node.tonemap_type == "RD_PHOTORECEPTOR" else []),
            *([
                widgets.Float(name="Key", value=node.key, minmax=(0.0,1.0)),
                widgets.Float(name="Offset", value=node.offset),
                widgets.Float(name="Gamma", value=node.gamma),
            ] if node.tonemap_type == "RH_SIMPLE" else [])
        ]
    },
    'CompositorNodeZcombine': {
        'class': 'color_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Alpha", value=node.use_alpha),
            widgets.Boolean(name="Anti-Alias Z", value=node.use_antialias_z)
        ]
    },

    # Compositor > Converter

    'CompositorNodePremulKey': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mapping'),
        ]
    },
    'CompositorNodeConvertColorSpace': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'from_color_space', "From:"),
            dropdown(node, 'to_color_space', "To:")
        ]
    },
    'CompositorNodeValToRGB': {
        'class': 'converter_node',
        'props': lambda node: [
            ramp(node)
        ]
    },
    'CompositorNodeCombineColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode'),
            dropdown(node, 'ycc_mode') if node.mode == "YCC" else None
        ]
    },
    'CompositorNodeCombineXYZ': {
        'class': 'converter_node',
    },
    'CompositorNodeIDMask': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Value(name="Index", value=node.index),
            widgets.Boolean(name="Anti-Aliasing", value=node.use_antialiasing)
        ]
    },
    'CompositorNodeMath': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'operation'),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ],
        'name_behavior': lambda node: enumName(node, 'operation')
    },
    'CompositorNodeRGBToBW': {
        'class': 'converter_node'
    },
    'CompositorNodeSeparateColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode'),
            dropdown(node, 'ycc_mode') if node.mode == 'YCC' else None
        ]
    },
    'CompositorNodeSeparateXYZ': {
        'class': 'converter_node'
    },
    'CompositorNodeSetAlpha': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode', label="Mode:")
        ]
    },
    'CompositorNodeSwitchView': {
        'class': 'converter_node'
    },

    # Compositor > Filter

    'CompositorNodeAntiAliasing': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Float(name="Threshold", value=node.threshold, minmax=(0.0,1.0)),
            widgets.Float(name="Contrast Limit", value=node.contrast_limit, minmax=(0.0,1.0)),
            widgets.Float(name="Corner Rounding", value=node.corner_rounding, minmax=(0.0,1.0))
        ]
    },
    'CompositorNodeBilateralblur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Iterations", value=node.iterations),
            widgets.Float(name="Color Sigma", value=node.iterations),
            widgets.Float(name="Space Sigma", value=node.iterations),
        ]
    },
    'CompositorNodeBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            dropdown(node, 'filter_type'),
            *([
                widgets.Boolean(name="Variable Size", value=node.use_variable_size),
                widgets.Boolean(name="Bokeh", value=node.use_bokeh) if not node.use_variable_size else None,
                widgets.Boolean(name="Gamma", value=node.use_gamma_correction)
            ] if node.filter_type != 'FAST_GAUSS' else []),
            widgets.Boolean(name="Relative", value=node.use_relative),
            *([
                widgets.Label(text="Aspect Correction"),
                selectBar(node, 'aspect_correction'),
                widgets.Float(name="X", value=node.factor_x, minmax=(0.0,100.0)),
                widgets.Float(name="Y", value=node.factor_y, minmax=(0.0,100.0))
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
    'CompositorNodeDefocus': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Label(text="Bokeh Type:"),
            dropdown(node, 'bokeh'),
            widgets.Angle(name="Angle", value=node.angle),
            widgets.Boolean(name="Gamma Correction", value=node.use_gamma_correction),
            widgets.Float(name="F-Stop", value=node.f_stop),
            widgets.Float(name="Max Blur", value=node.blur_max),
            widgets.Float(name="Threshold", value=node.threshold),
            widgets.Boolean(name="Preview", value=node.use_preview),
            widgets.String(value="" if not node.scene else node.scene.name),
            widgets.Boolean(name="Use Z-Buffer", value=node.use_zbuffer),
            widgets.Float(name="Z-Scale", value=node.z_scale)
        ]
    },
    'CompositorNodeDenoise': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Label(text="Prefilter"),
            dropdown(node, 'prefilter'),
            widgets.Boolean(name="HDR", value=node.use_hdr)
        ]
    },
    'CompositorNodeDilateErode': {
        'class': 'filter_node',
        'props': lambda node: [
            dropdown(node, 'mode', label="Mode:"),
            widgets.Value(name="Distance", value=node.distance),
            widgets.Float(name="Edge", value=node.edge) if node.mode == 'THRESHOLD' else None,
            dropdown(node, 'falloff', label="Falloff:") if node.mode == 'FEATHER' else None
        ]
    },
    'CompositorNodeDBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Iterations", value=node.iterations),
            #widgets.Boolean(name="Wrap", value=node.use_wrap),
            widgets.Label(text="Center:"),
            widgets.Float(name="X", value=node.center_x),
            widgets.Float(name="Y", value=node.center_y),
            widgets.Float(name="Distance", value=node.distance),
            widgets.Angle(name="Angle", value=node.angle),
            widgets.Angle(name="Spin", value=node.spin),
            widgets.Float(name="Zoom", value=node.zoom)
        ]
    },
    'CompositorNodeFilter': {
        'class': 'filter_node',
        'props': lambda node: [
            dropdown(node, 'filter_type')
        ],
        'name_behavior': lambda node: enumName(node, 'filter_type')
    },
    'CompositorNodeGlare': {
        'class': 'filter_node',
        'props': lambda node: [
            dropdown(node, 'glare_type'),
            dropdown(node, 'quality'),
            widgets.Value(name="Iterations", value=node.iterations) if node.glare_type != 'FOG_GLOW' else None,
            # color modulation
            widgets.Float(name="Color Modulation", value=node.color_modulation, minmax=(0.0,1.0)) if node.glare_type == 'GHOSTS' or node.glare_type == 'STREAKS' else None,
            widgets.Float(name="Mix", value=node.mix),
            widgets.Value(name="Threshold", value=node.threshold),
            *([
                widgets.Value(name="Streaks", value=node.streaks),
                widgets.Angle(name="Angle Offset", value=node.angle_offset),
            ] if node.glare_type == 'STREAKS' else []),
            widgets.Float(name="Size", value=node.size) if node.glare_type == 'FOG_GLOW' else None,
            widgets.Float(name="Fade", value=node.fade, minmax=(0.75, 1.0)) if node.glare_type == 'STREAKS' or node.glare_type == 'SIMPLE_STAR' else None, # fade
            widgets.Boolean(name="Rotate 45", value=node.use_rotate_45) if node.glare_type == 'SIMPLE_STAR' else None
        ]
    },
    'CompositorNodeInpaint': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Distance", value=node.distance)
        ]
    },
    'CompositorNodePixelate': {
        'class': 'filter_node'
    },
    'CompositorNodeSunBeams': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Float(value=node.source[0]),
                widgets.Float(value=node.source[1])
            ], resize_override=False),
            widgets.Float(name="Ray Length", value=node.ray_length, minmax=(0.0,1.0))
        ]
    },
    'CompositorNodeVecBlur': {
        'class': 'filter_node',
        'props': lambda node: [
            widgets.Value(name="Samples", value=node.samples),
            widgets.Value(name="Blur", value=getFloatString(node.factor, decimal_points=2)),
            widgets.Label(text="Speed:"),
            widgets.Value(name="Min", value=node.speed_min),
            widgets.Value(name="Max", value=node.speed_max),
            widgets.Boolean(name="Curved", value=node.use_curved)
        ]
    },

    # Compositor > Vector

    'CompositorNodeMapRange': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    'CompositorNodeMapValue': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Label(text="Offset:"),
            widgets.Float(name="", value=node.offset),
            widgets.Label(text="Size:"),
            widgets.Float(name="", value=node.size),
            widgets.Boolean(name="Use Minimum", value=node.use_min),
            widgets.Float(name="", value=node.min),
            widgets.Boolean(name="Use Maximum", value=node.use_max),
            widgets.Float(name="", value=node.max)
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
    'CompositorNodeCurveVec': {
        'class': 'vector_node',
        'props': lambda node: [
            curve(node.mapping, type='XYZ')
        ]
    },

    # Compositor > Matte

    'CompositorNodeBoxMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Float(name="", value=node.x),
                widgets.Float(name="", value=node.y)
            ]),
            widgets.Columns(wids=[
                widgets.Float(name="", value=node.width, minmax=(0.0,2.0)),
                widgets.Float(name="", value=node.height, minmax=(0.0,2.0))
            ], resize_override=False),
            widgets.Angle(name="Rotation", value=node.rotation),
            dropdown(node, 'mask_type', label="Mask Type:")
        ]
    },
    'CompositorNodeChannelMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Label(text="Color Space:"),
            selectBar(node, 'color_space'),
            widgets.Label(text="Key Channel:"),
            widgets.SelectBar(options=CHANNEL_MATTE_OPTS[node.color_space], select_index=CHANNEL_MATTE_OPTS[node.color_space].index(node.matte_channel)),
            dropdown(node, 'limit_method', "Algorithm:"),
            widgets.Label(text="Limiting Channel:"),
            widgets.SelectBar(options=CHANNEL_MATTE_OPTS[node.color_space], select_index=CHANNEL_MATTE_OPTS[node.color_space].index(node.limit_channel)) if node.limit_method == 'SINGLE' else None,
            widgets.Float(name="High", value=node.limit_max, minmax=(0.0, 1.0)),
            widgets.Float(name="Low", value=node.limit_min, minmax=(0.0, 1.0))
        ]
    },
    'CompositorNodeChromaMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Angle(name="Aceptance", value=node.tolerance),
            widgets.Angle(name="Cutoff", value=node.threshold),
            widgets.Float(name="Falloff", value=node.gain, minmax=(0.0,1.0))
        ]
    },
    
    
    'CompositorNodeColorMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Float(name="H", value=node.color_hue, minmax=(0.0,1.0)),
            widgets.Float(name="S", value=node.color_saturation, minmax=(0.0,1.0)),
            widgets.Float(name="V", value=node.color_value, minmax=(0.0,1.0))
        ]
    },
    'CompositorNodeColorSpill': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Label(text="Despill Channel"),
            selectBar(node, 'channel'),
            dropdown(node, 'limit_method', label="Algorithm:"),
            *([
                widgets.Label(text="Limiting Channel:"),
                selectBar(node, 'limit_channel')
            ] if node.limit_method == 'SIMPLE' else []),
            widgets.Float(name="Ratio", value=node.ratio, minmax=(0.5,1.5)),
            widgets.Boolean(name="Unspill", value=node.use_unspill),
            *([
                widgets.Float(name="R", value=node.unspill_red, minmax=(0.5,1.5)),
                widgets.Float(name="G", value=node.unspill_green, minmax=(0.5,1.5)),
                widgets.Float(name="B", value=node.unspill_blue, minmax=(0.5,1.5))
            ] if node.use_unspill else [])
        ]
    },
    'CompositorNodeCryptomatteV2': {
        'class': 'matte_node',
        'props': lambda node: [
            selectBar(node, 'source'),
            widgets.Scene(value="" if not node.scene else node.scene.name) if node.source == 'SCENE' else None,
            widgets.Image(value="" if not node.image else node.image.name) if node.source == 'IMAGE' else None,
            *([
                dropdown(node.image, 'source'),
                *([
                    widgets.Value(name="Frames", value=node.frame_duration),
                    widgets.Value(name="Start Frame", value=node.frame_start),
                    widgets.Value(name="Offset", value=node.frame_offset),
                    widgets.Boolean(name="Cyclic", value=node.use_cyclic),
                    widgets.Boolean(name="Auto-Refresh", value=node.use_auto_refresh)
                ] if node.image.source in ['SEQUENCE', 'MOVIE'] else [])
            ] if node.image else []),
            widgets.Dropdown(value=node.layer_name),
            widgets.Label(text="Matte ID:"),
            widgets.String(value=node.matte_id)
        ]
    },
    'CompositorNodeCryptomatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Label(text="Matte Objects:"),
            widgets.String(value=node.matte_id)
        ]
    },
    'CompositorNodeDiffMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Float(name="Tolerance", value=node.tolerance, minmax=(0.0,1.0)),
            widgets.Float(name="Falloff", value=node.tolerance, minmax=(0.0,1.0))
        ]
    },
    'CompositorNodeDistanceMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Float(name="Tolerance", value=node.tolerance, minmax=(0.0,1.0)),
            widgets.Float(name="Falloff", value=node.tolerance, minmax=(0.0,1.0)),
            widgets.Label(text="Color Space:"),
            selectBar(node, 'channel')
        ]
    },
    'CompositorNodeDoubleEdgeMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Label(text="Inner Edge:"),
            widgets.Dropdown(value=enumName(node, 'inner_mode')),
            widgets.Label(text="Buffer Edge:"),
            widgets.Dropdown(value=enumName(node, 'edge_mode')),
        ]
    },
    'CompositorNodeEllipseMask': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Float(name="X", value=node.x),
                widgets.Float(name="Y", value=node.y)
            ]),
            widgets.Columns(wids=[
                widgets.Float(name="", value=node.width, minmax=(0.0,2.0)),
                widgets.Float(name="", value=node.height, minmax=(0.0,2.0))
            ], resize_override=False),
            widgets.Angle(name="Rotation", value=node.rotation),
            dropdown(node, 'mask_type', label="Mask Type:"),
        ]
    },
    'CompositorNodeKeying': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Value(name="Pre Blur", value=node.blur_pre),
            widgets.Float(name="Screen Balance", value=node.screen_balance, minmax=(0.0,1.0)), #screen_balance
            widgets.Float(name="Despill Factor", value=node.despill_factor, minmax=(0.0,1.0)), #despill_factor
            widgets.Float(name="Despill Balance", value=node.despill_balance, minmax=(0.0,1.0)), #despill_balance
            widgets.Value(name="Edge Kernel Radius", value=node.edge_kernel_radius),
            widgets.Float(name="Edge Kernel Tolerance", value=node.edge_kernel_tolerance, minmax=(0.0,1.0)), #edge kernel tolerance
            widgets.Float(name="Clip Black", value=node.clip_black, minmax=(0.0,1.0)), #clip_black
            widgets.Float(name="Clip White", value=node.clip_white, minmax=(0.0,1.0)), #clip_white
            widgets.Value(name="Dilate/Erode", value=node.dilate_distance),
            dropdown(node, 'feather_falloff', label="Feather Falloff"),
            widgets.Value(name="Feather Distance", value=node.feather_distance),
            widgets.Value(name="Post Blur", value=node.blur_post)
        ]
    },
    'CompositorNodeKeyingScreen': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Tracking(value="" if not node.clip else node.clip.name),
            widgets.Object(value=node.tracking_object) if node.clip else None
        ]
    },
    'CompositorNodeLumaMatte': {
        'class': 'matte_node',
        'props': lambda node: [
            widgets.Float(name="High", value=node.limit_max, minmax=(0.0,1.0)), #limit_max
            widgets.Float(name="Low", value=node.limit_min, minmax=(0.0,1.0)) #limit_min
        ]
    },

    # Compositor > Distort

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
                widgets.Float(name="Left", value=node.rel_min_x),
                widgets.Float(name="Right", value=node.rel_max_x),
                widgets.Float(name="Up", value=node.rel_min_y),
                widgets.Float(name="Down", value=node.rel_max_y)
            ] if node.relative else [])
        ]
    },
    'CompositorNodeDisplace': {
        'class': 'distor_node'
    },
    'CompositorNodeFlip': {
        'class': 'distor_node',
        'props': lambda node: [
            dropdown(node, 'axis')
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
    'CompositorNodeMapUV': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Value(name="Alpha", value=node.alpha, minmax=(0,100))
        ]
    },
    'CompositorNodeMovieDistortion': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.MovieClip(value="" if not node.clip else node.clip.name),
            dropdown(node, 'distortion_type'),
        ],
        'name_behavior': lambda node: "Undistortion" if node.distortion_type == 'UNDISTORT' else "Distortion"
    },
    'CompositorNodePlaneTrackDeform': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.MovieClip(value="" if not node.clip else node.clip.name),
            *([
                widgets.Object(value=node.tracking_object),
                widgets.Tracking(value=node.plane_track_name)
            ] if node.clip else []),
            widgets.Boolean(name="Motion Blur", value=node.use_motion_blur),
            *([
                widgets.Value(name="Samples", value=node.motion_blur_samples),
                widgets.Float(name="Shutter", value=node.motion_blur_shutter)
            ] if node.use_motion_blur else [])
        ]
    },
    'CompositorNodeRotate': {
        'class': 'distor_node',
        'props': lambda node: [
            dropdown(node, 'filter_type')
        ]
    },
    'CompositorNodeScale': {
        'class': 'distor_node',
        'props': lambda node: [
            dropdown(node, 'space'),
            *([
                selectBar(node, 'frame_method'),
                widgets.Columns(wids=[
                    widgets.Float(name="", value=node.offset_x),
                    widgets.Float(name="", value=node.offset_y)
                ])
            ] if node.space == 'RENDER_SIZE' else [])
        ]
    },
    'CompositorNodeStabilize': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.MovieClip(value="" if not node.clip else node.clip.name),
            *([
                dropdown(node, 'filter_type'),
                widgets.Boolean(name="Invert", value=node.invert)
            ] if node.clip else [])
        ]
    },
    'CompositorNodeTransform': {
        'class': 'distor_node',
        'props': lambda node: [
            dropdown(node, 'filter_type'),
        ]
    },
    'CompositorNodeTranslate': {
        'class': 'distor_node',
        'props': lambda node: [
            widgets.Boolean(name="Relative", value=node.use_relative),
            dropdown(node, 'wrap_axis', label="Wrapping:")
        ]
    },

    # Compositor > Switch

    'CompositorNodeSwitch': {
        'class': 'switch_node',
        'props': lambda node: [
            widgets.Boolean(name="Switch", value=node.check)
        ]
    },



    ### GEOMETRY NODES ###

    # Geometry > Attribute

    'GeometryNodeAttributeStatistic': {
        'class': 'attribute_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeCaptureAttribute': {
        'class': 'attribute_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeAttributeDomainSize': {
        'class': 'attribute_node',
        'props': lambda node: [
            dropdown(node, 'component')
        ]
    },
    'GeometryNodeRemoveAttribute': {
        'class': 'attribute_node'
    },
    'GeometryNodeStoreNamedAttribute': {
        'class': 'attribute_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain')
        ]
    },


    # Geometry > Color

    # ShaderNodeValToRGB
    'FunctionNodeCombineColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    # ShaderNodeMix
    # ShaderNodeRGBCurve
    'FunctionNodeSeparateColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },

    # Geometry > Curve

    'GeometryNodeCurveLength': {
        'class': 'geometry_node'
    },
    'GeometryNodeCurveToMesh': {
        'class': 'geometry_node'
    },
    'GeometryNodeCurveToPoints': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeDeformCurvesOnSurface': {
        'class': 'geometry_node'
    },
    'GeometryNodeFillCurve': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeFilletCurve': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeResampleCurve': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeReverseCurve': {
        'class': 'geometry_node'
    },
    'GeometryNodeSampleCurve': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            selectBar(node, 'mode'), #mode
            widgets.Boolean(name="All Curves", value=node.use_all_curves)
        ]
    },
    'GeometryNodeSubdivideCurve': {
        'class': 'geometry_node'
    },
    'GeometryNodeTrimCurve': {
        'class': 'geometry_node',
        'props': lambda node: [
            selectBar(node, 'mode')
        ]
    },

    # Geometry > Curve Primitives

    'GeometryNodeCurveArc': {
        'class': 'geometry_node',
        'props': lambda node: [
            selectBar(node, 'mode')
        ]
    },
    'GeometryNodeCurvePrimitiveBezierSegment': {
        'class': 'geometry_node',
        'props': lambda node: [
            selectBar(node, 'mode')
        ]
    },
    'GeometryNodeCurvePrimitiveCircle': {
        'class': 'geometry_node',
        'props': lambda node: [
            selectBar(node, 'mode')
        ]
    },
    'GeometryNodeCurvePrimitiveLine': {
        'class': 'geometry_node',
        'props': lambda node: [
            selectBar(node, 'mode')
        ]
    },
    'GeometryNodeCurveSpiral': {
        'class': 'geometry_node'
    },
    'GeometryNodeCurveQuadraticBezier': {
        'class': 'geometry_node'
    },
    'GeometryNodeCurvePrimitiveQuadrilateral': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeCurveStar': {
        'class': 'geometry_node'
    },

    # Geometry > Curve Topology

    'GeometryNodeOffsetPointInCurve': {
        'class': 'input_node'
    },
    'GeometryNodeCurveOfPoint': {
        'class': 'input_node'
    },
    'GeometryNodePointsOfCurve': {
        'class': 'input_node'
    },

    # Geometry > Geometry

    'GeometryNodeBoundBox': {
        'class': 'geometry_node'
    },
    'GeometryNodeConvexHull': {
        'class': 'geometry_node'
    },
    'GeometryNodeDeleteGeometry': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode'),
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeDuplicateElements': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeProximity': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'target_element')
        ]
    },
    'GeometryNodeGeometryToInstance': {
        'class': 'geometry_node'
    },
    'GeometryNodeJoinGeometry': {
        'class': 'geometry_node'
    },
    'GeometryNodeMergeByDistance': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeRaycast': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'mapping')
        ]
    },
    'GeometryNodeSampleIndex': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain'),
            widgets.Boolean(name="Clamp", value=node.clamp)
        ]
    },
    'GeometryNodeSampleNearest': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeSeparateComponents': {
        'class': 'geometry_node',
    },
    'GeometryNodeSeparateGeometry': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'domain')
        ]
    },
    'GeometryNodeTransform': {
        'class': 'geometry_node'
    },
    'GeometryNodeSetID': {
        'class': 'geometry_node'
    },
    'GeometryNodeSetPosition': {
        'class': 'geometry_node'
    },

    # Geometry > Input

     'FunctionNodeInputBool': {
        'class': 'input_node'
    },
    'GeometryNodeCollectionInfo': {
        'class': 'input_node',
        'props': lambda node: [
            selectBar(node, 'transform_space')
        ]
    },
    'FunctionNodeInputColor': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.ColorPicker(color=node.outputs[0].default_value),
            widgets.RGBA(color=socketColorToSVGColor(node.outputs[0].default_value))
        ]
    },
    'FunctionNodeInputInt': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="", value=node.outputs[0].default_value)
        ]
    },
    'GeometryNodeIsViewport': {
        'class': 'input_node'
    },
    'GeometryNodeInputMaterial': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Material(value="" if not node.material else node.material.name)
        ]
    },
    'GeometryNodeObjectInfo': {
        'class': 'input_node',
        'props': lambda node: [
            selectBar(node, 'transform_space')
        ]
    },
    'GeometryNodeSelfObject': {
        'class': 'input_node'
    },
    'FunctionNodeInputString': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.String(value=node.outputs[0].default_value)
        ]
    },
    # ShaderNodeValue    
    'FunctionNodeInputVector': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Float(name="X", value=node.outputs[0].default_value[0]),
            widgets.Float(name="Y", value=node.outputs[0].default_value[1]),
            widgets.Float(name="Z", value=node.outputs[0].default_value[2]),
        ]
    },
    'GeometryNodeInputID': {
        'class': 'input_node'
    },
    'GeometryNodeInputIndex': {
        'class': 'input_node'
    },
    'GeometryNodeInputNamedAttribute': {
        'class': 'input_node',
        'props': lambda node: [
            dropdown(node, 'data_type')
        ]
    },
    'GeometryNodeInputNormal': {
        'class': 'input_node'
    },
    'GeometryNodeInputPosition': {
        'class': 'input_node'
    },
    'GeometryNodeInputRadius': {
        'class': 'input_node'
    },
    'GeometryNodeInputSceneTime': {
        'class': 'input_node'
    },
    
    # Geometry > Instances

    'GeometryNodeInstanceOnPoints': {
        'class': 'geometry_node'
    },
    'GeometryNodeInstancesToPoints': {
        'class': 'geometry_node'
    },
    'GeometryNodeRealizeInstances': {
        'class': 'geometry_node'
    },
    'GeometryNodeRotateInstances': {
        'class': 'geometry_node'
    },
    'GeometryNodeScaleInstances': {
        'class': 'geometry_node'
    },
    'GeometryNodeTranslateInstances': {
        'class': 'geometry_node'
    },
    'GeometryNodeInputInstanceRotation': {
        'class': 'input_node'
    },
    'GeometryNodeInputInstanceScale': {
        'class': 'input_node'
    },

    # Geometry > Material

    'GeometryNodeReplaceMaterial': {
        'class': 'geometry_node'
    },
    'GeometryNodeInputMaterialIndex': {
        'class': 'input_node'
    },
    'GeometryNodeMaterialSelection': {
        'class': 'geometry_node'
    },
    'GeometryNodeSetMaterial': {
        'class': 'geometry_node'
    },
    'GeometryNodeSetMaterialIndex': {
        'class': 'geometry_node'
    },

    # Geometry > Mesh

    'GeometryNodeDualMesh': {
        'class': 'geometry_node'
    },
    'GeometryNodeEdgePathsToCurves': {
        'class': 'geometry_node'
    },
    'GeometryNodeEdgePathsToSelection': {
        'class': 'input_node'
    },
    'GeometryNodeExtrudeMesh': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeFlipFaces': {
        'class': 'geometry_node',
    },
    'GeometryNodeMeshBoolean': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'operation')
        ]
    },
    'GeometryNodeMeshToCurve': {
        'class': 'geometry_node',
    },
    'GeometryNodeMeshToPoints': {
        'class': 'geometry_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'mode'))
        ]
    },
    'GeometryNodeMeshToVolume': {
        'class': 'geometry_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                widgets.Label(text="Resolution", alignment='R'),
                widgets.Dropdown(value=enumName(node, 'resolution_mode'))
            ])
        ]
    },
    'GeometryNodeSampleNearestSurface': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'data_type')
        ]
    },
    'GeometryNodeSampleUVSurface': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'data_type')
        ]
    },
    'GeometryNodeScaleElements': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'domain'),
            dropdown(node, 'scale_mode')
        ]
    },
    'GeometryNodeSplitEdges': {
        'class': 'geometry_node'
    },
    'GeometryNodeSubdivideMesh': {
        'class': 'geometry_node'
    },
    'GeometryNodeSubdivisionSurface': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'uv_smooth'),
            dropdown(node, 'boundary_smooth'),
        ]
    },
    'GeometryNodeTriangulate': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'quad_method'),
            dropdown(node, 'ngon_method')
        ]
    },
    'GeometryNodeInputMeshEdgeAngle': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshEdgeNeighbors': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshEdgeVertices': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshFaceArea': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshFaceNeighbors': {
        'class': 'input_node'
    },
    'GeometryNodeMeshFaceSetBoundaries': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshFaceIsPlanar': {
        'class': 'input_node'
    },
    'GeometryNodeInputShadeSmooth': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshIsland': {
        'class': 'input_node'
    },
    'GeometryNodeInputShortestEdgePaths': {
        'class': 'input_node'
    },
    'GeometryNodeInputMeshVertexNeighbors': {
        'class': 'input_node'
    },
    'GeometryNodeSetShadeSmooth': {
        'class': 'geometry_node'
    },

    # Geometry > Mesh Primitives

    'GeometryNodeMeshCone': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'fill_type', label="Fill Type:")
        ]
    },
    'GeometryNodeMeshCube': {
        'class': 'geometry_node'
    },
    'GeometryNodeMeshCylinder': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'fill_type', label="Fill Type:")
        ]
    },
    'GeometryNodeMeshGrid': {
        'class': 'geometry_node'
    },
    'GeometryNodeMeshIcoSphere': {
        'class': 'geometry_node'
    },
    'GeometryNodeMeshCircle': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'fill_type', label="Fill Type:")
        ]
    },
    'GeometryNodeMeshLine': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode'),
            dropdown(node, 'count_mode') if node.mode == 'END_POINTS' else None
        ]
    },
    'GeometryNodeMeshUVSphere': {
        'class': 'geometry_node',
    },

    # Geometry > Mesh Topology

    'GeometryNodeCornersOfFace': {
        'class': 'input_node'
    },
    'GeometryNodeCornersOfVertex': {
        'class': 'input_node'
    },
    'GeometryNodeEdgesOfCorner': {
        'class': 'input_node'
    },
    'GeometryNodeEdgesOfVertex': {
        'class': 'input_node'
    },
    'GeometryNodeFaceOfCorner': {
        'class': 'input_node'
    },
    'GeometryNodeOffsetCornerInFace': {
        'class': 'input_node'
    },
    'GeometryNodeVertexOfCorner': {
        'class': 'input_node'
    },

    # Geometry > Output

    'GeometryNodeViewer': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'domain')
        ]
    },

    # Geometry > Point

    'GeometryNodeDistributePointsInVolume': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'GeometryNodeDistributePointsOnFaces': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'distribute_method')
        ]
    },
    'GeometryNodePoints': {
        'class': 'geometry_node'
    },
    'GeometryNodePointsToVertices': {
        'class': 'geometry_node'
    },
    'GeometryNodePointsToVolume': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'resolution_mode', label="Resolution:")
        ]
    },
    'GeometryNodeSetPointRadius': {
        'class': 'geometry_node'
    },
    
    # Geometry > Text

    'GeometryNodeStringJoin': {
        'class': 'converter_node'
    },
    'FunctionNodeReplaceString': {
        'class': 'converter_node'
    },
    'FunctionNodeSliceString': {
        'class': 'converter_node'
    },
    'FunctionNodeStringLength': {
        'class': 'converter_node'
    },
    'GeometryNodeStringToCurves': {
        'class': 'geometry_node',
        'props': lambda node: [
            widgets.Font(),
            dropdown(node, 'overflow'),
            dropdown(node, 'align_x'),
            dropdown(node, 'align_y'),
            dropdown(node, 'pivot_mode', label="Pivot Point:")
        ]
    },
    'FunctionNodeValueToString': {
        'class': 'converter_node'
    },
    'FunctionNodeInputSpecialCharacters': {
        'class': 'input_node'
    },

    # Geometry > Texture

    # ShaderNodeTexBrick
    # ShaderNodeTexChecker
    # ShaderNodeTexGradient
    'GeometryNodeImageTexture': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'interpolation'),
            dropdown(node, 'extension')
        ]
    },
    # ShaderNodeTexMagic
    # ShaderNodeTexMusgrave
    # ShaderNodeTexNoise
    # ShaderNodeTexVoronoi
    # ShaderNodeTexWave
    # ShaderNodeTexWhiteNoise

    # Geometry > Utilities

    'GeometryNodeAccumulateField': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain')
        ]
    },
    'FunctionNodeAlignEulerToVector': {
        'class': 'converter_node',
        'props': lambda node: [
            selectBar(node, 'axis'),
            dropdown(node, 'pivot_axis', label="Pivot")
        ]
    },
    'FunctionNodeBooleanMath': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'operation')
        ],
        'name_behavior': lambda node: enumName(node, 'operation')
    },
    # ShaderNodeClamp
    'FunctionNodeCompare': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'mode') if node.data_type == 'VECTOR' else None,
            dropdown(node, 'operation'),
        ],
        'name_behavior': lambda node: enumName(node, 'operation')
    },
    'GeometryNodeFieldAtIndex': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain'),
        ]
    },
    # ShaderNodeFloatCurve
    'FunctionNodeFloatToInt': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.Dropdown(value=enumName(node, 'rounding_mode'))
        ],
        'name_behavior': lambda node: enumName(node, 'rounding_mode')
    },
    'GeometryNodeFieldOnDomain': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'domain'),
        ]
    },
    # ShaderNodeMapRange
    # ShaderNodeMath
    # ShaderNodeMix
    'FunctionNodeRandomValue': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'data_type')
        ]
    },
    'FunctionNodeRotateEuler': {
        'class': 'converter_node',
        'props': lambda node: [
            widgets.SelectBar(["Axis Angle", "Euler"], 0 if node.type == 'AXIS_ANGLE' else 1), ## needs to be specified due to override
            selectBar(node, 'space')
        ]
    },
    'GeometryNodeSwitch': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'input_type')
        ]
    },

    # Geometry > UV

    'GeometryNodeUVPackIslands': {
        'class': 'converter_node'
    },
    'GeometryNodeUVUnwrap': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'method')
        ]
    },

    # Geometry > Vector

    # ShaderNodeCombineXYZ
    # ShaderNodeSeparateXYZ
    # ShaderNodeCurve
    # ShaderNodeVectorMath
    # ShaderNodeVectorRotate

    # Geometry > Volume

    'GeometryNodeVolumeCube': {
        'class': 'geometry_node'
    },
    'GeometryNodeVolumeToMesh': {
        'class': 'geometry_node',
        'props': lambda node: [
            dropdown(node, 'resolution_mode', "Resolution:")
        ]
    },


    ### NODE GROUPS ###

    'NodeGroupInput': {
        'class': 'group_node'
    },
    'NodeGroupOutput': {
        'class': 'group_node'
    },


    ### SHADER NODES ###

    'ShaderNodeGroup': {
        'class': 'group_node',
        'props': lambda node: [
            widgets.String(value=node.node_tree.name)
        ]
    },

    # Shader > Input

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
            dropdown(node, 'attribute_type', label="Type:"),
            widgets.String(name="Name:", value=node.attribute_name)
        ]
    },
    'ShaderNodeBevel': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Value(name="Samples", value=str(node.samples))
        ]
    },
    'ShaderNodeCameraData': {
        'class': 'input_node',
    },
    'ShaderNodeVertexColor': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.String(value=node.layer_name)
        ]
    },
        'ShaderNodeHairInfo': {
        'class': 'input_node',
    },
    'ShaderNodeFresnel': {
        'class': 'input_node',
    },
    'ShaderNodeNewGeometry': {
        'class': 'input_node',
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
    'ShaderNodeParticleInfo': {
        'class': 'input_node'
    },
    'ShaderNodePointInfo': {
        'class': 'input_node'
    },
    'ShaderNodeRGB': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.ColorPicker(color=node.outputs[0].default_value),
            widgets.RGBA(color=socketColorToSVGColor(node.outputs[0].default_value))
        ]
    },
    'ShaderNodeTangent': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Columns(wids=[
                dropdown(node, 'direction_type'),
                selectBar(node, 'axis')
            ])
        ]
    },
    'ShaderNodeTexCoord': {
        'class': 'input_node',
        'props': lambda node: [
            object(node.object),
            widgets.Boolean(name="From Instancer", value=node.from_instancer)
        ]
    },
    'ShaderNodeUVMap': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="From Instancer", value=node.from_instancer),
            widgets.UVMap(value=node.uv_map)
        ]
    },
    'ShaderNodeValue': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Float(name="", value=node.outputs[0].default_value)
        ]
    },
    'ShaderNodeVolumeInfo': {
        'class': 'input_node'
    },
    'ShaderNodeWireframe': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="Pixel Size", value=node.use_pixel_size)
        ]
    },

    'ShaderNodeUVAlongStroke': {
        'class': 'input_node',
        'props': lambda node: [
            widgets.Boolean(name="Use Tips", value=node.use_tips)
        ]
    },

    # Shader > Output

    'ShaderNodeOutputAOV': {
        'class': 'output_node',
        'props': lambda node: [
            widgets.String(name="Name:", value=node.name)
        ],
        'name_behavior': lambda _: 'AOV Output'
    },

    'ShaderNodeOutputLight': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'target')
        ]
    },

    'ShaderNodeOutputMaterial': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'target')
        ]
    },

    'ShaderNodeOutputWorld': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'target')
        ]
    },

    'ShaderNodeOutputLineStyle': {
        'class': 'output_node',
        'props': lambda node: [
            dropdown(node, 'blend_type'),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },

    # Shader > Shader

    'ShaderNodeAddShader': {
        'class': 'shader_node'
    },

    'ShaderNodeBsdfAnisotropic': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'distribution')
        ]
    },

    'ShaderNodeBsdfDiffuse': {
        'class': 'shader_node',
    },
    'ShaderNodeEmission': {
        'class': 'shader_node'
    },
    'ShaderNodeBsdfGlass': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'distribution')
        ]
    },
    'ShaderNodeBsdfGlossy': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'distribution')
        ]
    },

    'ShaderNodeBsdfHair': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'component')
        ]
    },

    'ShaderNodeHoldout': {
        'class': 'shader_node'
    },
    'ShaderNodeMixShader': {
        'class': 'shader_node'
    },
    'ShaderNodeBsdfPrincipled': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'distribution'),
            dropdown(node, 'subsurface_method')
        ]
    },

    'ShaderNodeBsdfHairPrincipled': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'parametrization')
        ]
    },

    'ShaderNodeVolumePrincipled': {
        'class': 'shader_node'
    },
    'ShaderNodeBsdfRefraction': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'distribution')
        ]
    },
    'ShaderNodeEeveeSpecular': {
        'class': 'shader_node'
    },
    'ShaderNodeSubsurfaceScattering': {
        'class': 'shader_node',
        'props': lambda node: [
            dropdown(node, 'falloff')
        ]
    },

    'ShaderNodeBsdfToon': {
        'class': 'shader_node'
    },

    'ShaderNodeBsdfTranslucent': {
        'class': 'shader_node'
    },
    'ShaderNodeBsdfTransparent': {
        'class': 'shader_node'
    },

    'ShaderNodeBsdfVelvet': {
        'class': 'shader_node'
    },

    'ShaderNodeVolumeAbsorption': {
        'class': 'shader_node'
    },
    'ShaderNodeVolumeScatter': {
        'class': 'shader_node'
    },

    'ShaderNodeBackground': {
        'class': 'shader_node'
    },

    # Shader > Texture

    'ShaderNodeTexBrick': {
        'class': 'texture_node',
        'props': lambda node: [
            widgets.Float(name="Offset", value=node.offset, minmax=(0.0, 1.0)),
            widgets.Value(name="Frequency", value=node.offset_frequency),
            widgets.Float(name="Squash", value=node.squash),
            widgets.Value(name="Frequency", value=node.squash_frequency)
        ]
    },
    'ShaderNodeTexChecker': {
        'class': 'texture_node'
    },    
    'ShaderNodeTexEnvironment': {
        'class': 'texture_node',
        'props': lambda node: [
            image(node.image),
            dropdown(node, 'interpolation'),
            dropdown(node, 'projection'),
            *([
                dropdown(node.image, 'source'),
                widgets.LabeledDropdown(name="Color Space", value="") if not node.image.colorspace_settings.name else dropdown(node.image.colorspace_settings, 'name', label="Color Space"),
                dropdown(node.image, 'alpha_mode', label="Alpha")
            ] if node.image else [])
        ],
        'name_behavior': lambda node: "Environment Texture" if not node.image else node.image.name
    },
    'ShaderNodeTexGradient': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'gradient_type')
        ]
    },
    'ShaderNodeTexIES': {
        'class': 'texture_node',
        'props': lambda node: [
            selectBar(node, 'mode'),
            widgets.IES(value="" if not node.ies else node.ies.name) if node.mode == 'INTERNAL' else widgets.File(value=node.filepath)
        ]
    },
    'ShaderNodeTexImage': {
        'class': 'texture_node',
        'props': lambda node: [
            image(node.image),
            dropdown(node, 'interpolation'),
            dropdown(node, 'projection'),
            dropdown(node, 'extension'),
            *([
                dropdown(node.image, 'source'),
                widgets.LabeledDropdown(name="Color Space", value="") if not node.image.colorspace_settings.name else dropdown(node.image.colorspace_settings, 'name', label="Color Space"),
                dropdown(node.image, 'alpha_mode', label="Alpha")
            ] if node.image else [])
        ],
        'name_behavior': lambda node: "Image Texture" if not node.image else node.image.name
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
            dropdown(node, 'musgrave_dimensions'),
            dropdown(node, 'musgrave_type')
        ]
    },
    'ShaderNodeTexNoise': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'noise_dimensions')
        ]
    },
    'ShaderNodeTexPointDensity': {
        'class': 'texture_node',
        'props': lambda node: [
            selectBar(node, 'point_source'),
            widgets.String(value="" if not node.object else node.object.name, name="Object:"),
            widgets.String(value="" if not node.particle_system else node.particle_system.name, name="Particle System:"),
            dropdown(node, 'space', "Space:"),
            widgets.Float(name="Radius", value=node.radius),
            dropdown(node, 'interpolation', "Interpolation:"),
            widgets.Value(name="Resolution", value=node.resolution),
            dropdown(node, 'particle_color_source' if node.point_source[0] == 'P' else 'vertex_color_source', "Color Source:")
        ]
    },
    'ShaderNodeTexSky': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'sky_type'),
            *([
                widgets.Sphere(values=node.sun_direction),
                widgets.Float(name="Turbidity", value=node.turbidity)
            ] if node.sky_type[0] == 'P' else []),
            *([
                widgets.Sphere(values=node.sun_direction),
                widgets.Float(name="Turbidity", value=node.turbidity),
                widgets.Float(name="Ground Albedo", value=node.ground_albedo, minmax=(0.0, 1.0))
            ] if node.sky_type[0] == 'H' else []),
            *([
                widgets.Boolean(name="Sun Disc", value=node.sun_disc),
                *([
                    widgets.Float(name="Sun Size", value=node.sun_size),
                    widgets.Float(name="Sun Intensity", value=node.sun_intensity)
                ] if node.sun_disc else []),
                widgets.Float(name="Sun Elevation", value=node.sun_elevation),
                widgets.Float(name="Sun Rotation", value=node.sun_rotation),
                widgets.Float(name="Altitude", value=node.altitude),
                widgets.Float(name="Air", value=node.air_density, minmax=(0.0, 10.0)),
                widgets.Float(name="Dust", value=node.dust_density, minmax=(0.0, 10.0)),
                widgets.Float(name="Ozone", value=node.ozone_density, minmax=(0.0, 10.0))
            ] if node.sky_type[0] == 'N' else [])
        ]
    },
    'ShaderNodeTexVoronoi': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'voronoi_dimensions'),
            dropdown(node, 'feature'),
            dropdown(node, 'distance') if node.voronoi_dimensions != '1D' and node.feature not in ['DISTANCE_TO_EDGE', 'N_SPHERE_RADIUS'] else None
        ]
    },
    'ShaderNodeTexWave': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'wave_type'),
            dropdown(node, 'rings_direction') if node.wave_type[0] == "R" else dropdown(node, 'bands_direction'),
            dropdown(node, 'wave_profile')
        ]
    },
    'ShaderNodeTexWhiteNoise': {
        'class': 'texture_node',
        'props': lambda node: [
            dropdown(node, 'noise_dimensions')
        ]
    },

    # Shader > Color

    'ShaderNodeBrightContrast': {
        'class': 'color_node'
    },
    'ShaderNodeGamma': {
        'class': 'color_node'
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
    'ShaderNodeMix': {
        'class': None,
        'class_behavior': lambda node: {
            'FLOAT': 'converter_node',
            'VECTOR': 'vector_node',
            'RGBA': 'color_node',
            'ROTATION': 'vector_node'
        }[node.data_type],
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'factor_mode') if node.data_type == 'VECTOR' else None,
            *([
                dropdown(node, 'blend_type'),
                widgets.Boolean(name="Clamp Result", value=node.clamp_result)
            ] if node.data_type == 'RGBA' else []),
            widgets.Boolean(name="Clamp Factor", value=node.clamp_factor),
        ],
        'name_behavior': lambda node: "Mix" if node.data_type != 'RGBA' else enumName(node, 'blend_type')
    },
    'ShaderNodeRGBCurve': {
        'class': 'color_node',
        'props': lambda node: [
            curve(node.mapping, type="CRGB")
        ]
    },

    # Shader > Vector

    'ShaderNodeBump': {
        'class': 'vector_node',
        'props': lambda node: [
            widgets.Boolean(name="Invert", value=node.invert)
        ]
    },
    'ShaderNodeDisplacement': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'space')
        ]
    },
    'ShaderNodeMapping': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'vector_type', "Type:")
        ]
    },
    'ShaderNodeNormalMap': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'space'),
            widgets.UVMap() if node.space ==  'TANGENT' else None
        ]
    },
    'ShaderNodeVectorCurve': {
        'class': 'vector_node',
        'props': lambda node: [
            curve(node.mapping, type='XYZ')
        ]
    },
    'ShaderNodeVectorDisplacement': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'space')
        ]
    },
    'ShaderNodeVectorRotate': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'rotation_type', "Type:"),
            widgets.Boolean(name="Invert", value=node.invert)
        ]
    },
    'ShaderNodeVectorTransform': {
        'class': 'vector_node',
        'props': lambda node: [
            selectBar(node, 'vector_type'),
            dropdown(node, 'convert_from'),
            dropdown(node, 'convert_to')
        ]
    },

    # Shader > Converter

    'ShaderNodeBlackbody': {
        'class': 'converter_node'
    },
    'ShaderNodeClamp': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'clamp_type')
        ]
    },
    'ShaderNodeValToRGB': {
        'class': 'converter_node',
        'props': lambda node: [
            ramp(node)
        ]
    },
    'ShaderNodeCombineColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'ShaderNodeCombineXYZ': {
        'class': 'converter_node'
    },
    'ShaderNodeFloatCurve': {
        'class': 'converter_node',
        'props': lambda node: [
            curve(node.mapping)
        ]
    },
    'ShaderNodeMapRange': {
        'class': None,
        'class_behavior': lambda node: 'converter_node' if node.data_type[0] == "F" else 'vector_node',
        'props': lambda node: [
            dropdown(node, 'data_type'),
            dropdown(node, 'interpolation_type'),
            widgets.Boolean(name="Clamp", value=node.clamp) if node.data_type[-1] == "R" else None
        ]
    },
    'ShaderNodeMath': {
        'class': 'converter_node',
        'name_behavior': lambda node: enumName(node, 'operation'),
        'props': lambda node: [
            dropdown(node, 'operation'),
            widgets.Boolean(name="Clamp", value=node.use_clamp)
        ]
    },
    # ShaderNodeMix,
    'ShaderNodeRGBToBW': {
        'class': 'converter_node',
    },
    'ShaderNodeSeparateColor': {
        'class': 'converter_node',
        'props': lambda node: [
            dropdown(node, 'mode')
        ]
    },
    'ShaderNodeSeparateXYZ': {
        'class': 'converter_node'
    },
    'ShaderNodeShaderToRGB': {
        'class': 'converter_node'
    },
    'ShaderNodeVectorMath': {
        'class': 'vector_node',
        'props': lambda node: [
            dropdown(node, 'operation')
        ],
        'name_behavior': lambda node: node.operation
    },
    'ShaderNodeWavelength': {
        'class': 'converter_node'
    },

    # Shader > Script

    'ShaderNodeScript': {
        'class': 'script_node',
        'props': lambda node: [
            selectBar(node, 'mode'),
            widgets.Script(value="" if not node.script else node.script.name) if node.mode[0] == "I" else widgets.File(node.filepath)
        ]
    },


    ### PLACEHOLDER ###

    'PlaceholderNode': {
        'class': 'script_node',
        'props': lambda node: generateCustomProps(node)
    }

}