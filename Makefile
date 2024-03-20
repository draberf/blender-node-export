zip:
	mkdir blender-node-export
	mkdir blender-node-export/src
	cp __init__.py blender-node-export
	cp ./src/*.py blender-node-export/src
	zip -r blender-node-export_alpha.zip blender-node-export

	sed -i "/TESTING/d" blender-node-export/__init__.py
	zip -r blender-node-export_alpha_no_testing.zip blender-node-export

	rm -r blender-node-export