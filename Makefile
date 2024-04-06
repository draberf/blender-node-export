zip:
	mkdir blender-node-export
	mkdir blender-node-export/src
	cp __init__.py blender-node-export
	cp ./src/*.py blender-node-export/src
	zip -r blender-node-export_beta_0_1_2.zip blender-node-export

	rm -r blender-node-export