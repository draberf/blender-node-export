# blender-node-export
A Blender extension to export Node Graphs to SVG

# Installation
For curated archives to install through Blender's add-on manager, go to the [Release tags](https://github.com/draberf/blender-node-export/tags).

For a custom install, download the repository and run `make` to create a .zip archive.

To install the add-on into Blender, you can use Blender's built-in add-on manager: Edit > Preferences > Add-ons > Install... and select the .zip archive. Check the box next to the newly-added add-on in the list (You can find it under Import-Export, or by name 'Node Exporter To SVG').

# Usage
Once installed, you can access the add-on in the Toolbar in any Node editor. The Toolbar is on the right edge of the editor, and you can show/hide it with the `N` key. The add-on is under the Export tab.

To export the current Node graph, navigate to the Export to SVG > Export panel, write the path to the desired output file in the text field (you can also select it using the File button next to it), and press the Export button.

## Generic Options

**Export > Export Selected Only** -- Only selected Nodes and their mutual links will be exported. If the option is checked but no Node is selected, the whole graph is exported.

**Detail > Element Quality** -- Certain widgets (Color Picker, Ramp, Curves) are only imitated in the SVG. This setting lets you choose the quality of the imitation at the cost of larger output file.

**Detail > Use Gradients** -- Add gradients to certain widgets (Color Picker, Ramp) to improve their appearance at the cost of larger output file.

**Outline** -- Define the outline of rectangular elements in the output.

**Save/Load Configuration** -- Export your current options to a configuration file ("Save"), or overwrite your current options with new ones from a configuration file ("Load").

## Color Options

**Colors > Use Theme colors** -- The output's appearance will imitate your Blender Theme. While this box is checked, all the other options are ignored and hidden from the user interface.

**Colors > Reset to Default** -- Reset all custom colors to those defined by your Blender Theme.

**Colors > Text** -- Adjust the colors of all text elements. The 'bool' colors refer to the checkmark of boolean checkboxes.

**Colors > Text > Use generic text colors** -- All text elements in the output will be rendered using the same color ("Generic").

**Colors > Elements** -- Adjust the colors of various elements in the output. 'False' and 'True' refer to the color of the boolean checkbox. All the 'Axis' colors affect the appearance of graphs.

**Colors > Headers** -- Adjust the colors of the top bars of each regular/hidden Node.

**Colors > Sockets** -- Adjust the colors of markers and wires for specific value types.

**Colors > Sockets > Use generic socket color** -- All scockets in the output will be rendered using the same color ("Generic"), for example for minimalist visual styles.