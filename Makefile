zip:
	mkdir blender-node-export
	cp ./src/*.py blender-node-export
	zip -r blender-node-export_beta_0_3_0.zip blender-node-export

	rm -r blender-node-export