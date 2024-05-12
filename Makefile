zip:
	mkdir blender-node-export
	cp ./src/*.py blender-node-export
	zip -r blender-node-export.zip blender-node-export

	rm -r blender-node-export