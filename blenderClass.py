import os, importlib
import numpy as np



class Blender(object):
	def __init__(self):

		self.cwd = os.getcwd() + "/"

		self.importBlender()
		self.scene = self.bpy.context.scene


		# General rendering settings
		self.renderingEngine('blender')

		# Some memory management
		self.scene.render.use_free_image_textures = True
		self.bpy.context.user_preferences.edit.undo_steps = 0
		self.bpy.context.user_preferences.edit.undo_memory_limit = 60
		self.bpy.context.user_preferences.edit.use_global_undo = False


	def importBlender(self):
		self.bpy = importlib.import_module("bpy")
		global Vector
		from mathutils import Vector

	def setupScene(self):

		self.activateLayer([0])
		self.cleanScene()


	def removeDataBlocks(self, removeAll=False, counter=None):
		# Removes unlinked data blocks and prevents memory leakage
		if counter is not None:
			counter.value += 1

		toRemove = [block for block in self.bpy.data.meshes if block.users == 0]
		for block in toRemove:
			self.bpy.data.meshes.remove(block, do_unlink=True)

		toRemove = [block for block in self.bpy.data.materials if block.users == 0]
		for block in toRemove:
			self.bpy.data.materials.remove(block, do_unlink=True)

		toRemove = [block for block in self.bpy.data.textures if block.users == 0]
		for block in toRemove:
			self.bpy.data.textures.remove(block, do_unlink=True)

		toRemove = [block for block in self.bpy.data.images if block.users == 0]
		for block in toRemove:
			self.bpy.data.images.remove(block, do_unlink=True)

		if removeAll:
			toRemove = [block for block in self.bpy.data.cameras if block.users == 0]
			for block in toRemove:
				self.bpy.data.cameras.remove(block, do_unlink=True)

			toRemove = [block for block in self.bpy.data.lamps if block.users == 0]
			for block in toRemove:
				self.bpy.data.lamps.remove(block, do_unlink=True)
		
		if counter is not None:
			counter.value -= 1


	
	def cleanScene(self):
		self.killLamps()
		self.killMeshes()
		self.killCameras()
		self.removeDataBlocks(removeAll=True)

	
	def killMeshes(self, layer = -1):
		for obj in self.scene.objects:
			if obj.type == 'MESH' and obj.layers[layer != -1 and layer or self.activeLayer[0]]:
				obj.select = True
			else:
				obj.select = False
		self.bpy.ops.object.delete()

	
	def killCameras(self):
		for obj in self.scene.objects:
			if obj.type == 'CAMERA' and obj.layers[self.activeLayer[0]]:
				obj.select = True
			else:
				obj.select = False
		self.bpy.ops.object.delete()

	
	def killLamps(self):
		for obj in self.scene.objects:
			if obj.type == 'LAMP' and obj.layers[self.activeLayer[0]]:
				obj.select = True
			else:
				obj.select = False
		self.bpy.ops.object.delete()

	
	def joinMeshes(self, meshName):

		selectedObjs = []
		for obj in self.scene.objects:
			if obj.type == 'MESH' and obj.layers[self.activeLayer[0]]:
				obj.select = True
				selectedObjs.append(obj.name) # Just filling this up
				self.scene.objects.active = obj
			else:
				obj.select = False
		if len (selectedObjs) > 1:
			self.bpy.ops.object.join()
		self.scene.objects.active.name = meshName
		self.scene.objects.active.data.name = meshName

	
	def polishShape(self, harsh):
		# Set harsh to True if to simplify the mesh significantly. Such mesh simplification will result in detailedness loss of the shapes

		self.bpy.ops.object.mode_set(mode='EDIT')
		self.bpy.ops.mesh.normals_make_consistent(inside=False)
		if not harsh:
			self.bpy.ops.mesh.remove_doubles(threshold=0.0004)
			self.bpy.ops.mesh.dissolve_limited(angle_limit=0.000227) # 0.013 degrees
		else:
			self.bpy.ops.mesh.dissolve_limited(angle_limit=0.02) # ~1.14 degrees
			self.triangulateFaces()
			self.bpy.ops.mesh.dissolve_limited(angle_limit=0.02) # ~1.14 degrees
			# self.bpy.ops.mesh.fill_holes(sides=3)
		self.triangulateFaces()
		self.bpy.ops.mesh.normals_make_consistent(inside=False)
		self.bpy.ops.object.mode_set(mode='OBJECT')
		self.activeObj.data.use_auto_smooth = False

	def fixNormals(self):
		self.bpy.ops.object.mode_set(mode='EDIT')
		self.bpy.ops.mesh.normals_make_consistent(inside=False)
		self.bpy.ops.object.mode_set(mode='OBJECT')

	
	def triangulateFaces(self):
		# Expects a shape to have been selected in the scene
		self.bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

	def applyTransformation(self, scale, rotation, location=False):
		self.bpy.ops.object.transform_apply(location = location, scale = scale, rotation = rotation)

	def loadObj(self, objPath):
		self.bpy.ops.import_scene.obj(filepath=objPath, split_mode="OFF", use_smooth_groups=False, use_edges=False, axis_forward='-Z', axis_up='Y')

	def polishObj(self, objPath, polish=True, harshPolish=False, recenter=False, rotVec=None, objSavePath=''):

		layerIdx = 1
		if layerIdx == 1:
			self.renderingEngine('blender')
			meshName = 'theMeshBlender'

		self.activateLayer([layerIdx]) # For rendering RGBs (layerIdx == 1). For rendering depth maps or Normals using Cycles (layerIdx == 2)
		self.loadObj(objPath=objPath)
		self.joinMeshes(meshName=meshName) #Useful only if split_mode is equated to 'ON' otherwise objects are already joined by the time they are imported
		self.activeCurrentObj()
		self.fixNormals()
		if polish:
			self.activeObj.modifiers.new('Solidify', 'SOLIDIFY')
			self.activeObj.modifiers[0].thickness = -0.0001
			self.activeObj.modifiers[0].use_quality_normals = True
			self.activeObj.modifiers[0].use_rim = True
				# self.activeObj.modifiers[0].use_rim_only = True
			self.polishShape(harsh=harshPolish)
		self.bpy.ops.object.shade_smooth()

		if recenter:
			self.bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
			self.bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
			self.activeObj.location = Vector((0, 0, 0))

		self.applyTransformation(scale=False, rotation=True)
		if rotVec is not None:
			self.rotateObject(rotVec=rotVec)
		self.scene.update()

		if objSavePath == '':
			print ('==> Error: You need to speficy the path where the Obj file is going to be saved')
			exit()
		self.saveObj(objSavePath=objSavePath)

	def rotateObject(self, rotVec, meshName='theMeshBlender'):
		rot = np.radians(rotVec)
		self.activateMesh(meshName=meshName)
		self.activeObj.rotation_euler = Vector(rot)
		self.scene.update()

	def saveObj(self, objSavePath):
		self.bpy.ops.export_scene.obj(
                filepath=objSavePath, 
                check_existing=False, 
                axis_forward='-Z', 
                axis_up='Y', 
                use_selection=True, 
                use_animation=False, 
                use_mesh_modifiers=True, 
                use_edges=False, 
                use_smooth_groups=False, 
                use_smooth_groups_bitflags=False, 
                use_normals=False, 
                use_uvs=False, 
                use_materials=False, 
                use_triangles=True, 
                use_nurbs=False, 
                use_vertex_groups=False, 
                use_blen_objects=True, 
                group_by_object=False, 
                group_by_material=False, 
                keep_vertex_order=True, 
                global_scale=1, 
                path_mode='AUTO')


	def activateLayer(self, layersToSwitchTo):
		#layersToSwitchTo is a List containing integers in the range [0, 19]
		for i in range(20):
			if i in layersToSwitchTo:
				self.scene.layers[i] = True
			
		for i in range(20):
			if i not in layersToSwitchTo:
				self.scene.layers[i] = False
		self.activeLayer = layersToSwitchTo

	def activeCurrentObj(self):
		self.activeObj = self.scene.objects.active

	def activateMesh(self, meshName, layerIdx=-1):
		for obj in self.scene.objects:
			if ((obj.type == 'MESH' or obj.type == 'CAMERA') and obj.name == meshName and obj.layers[layerIdx != -1 and layerIdx or self.activeLayer[0]]) or ((obj.type == 'MESH' or obj.type == 'CAMERA') and obj.name == meshName):
				obj.select = True
				self.scene.objects.active = obj
			else:
				obj.select = False
		self.activeCurrentObj()

	def renderingEngine(self, renderEng):
		self.renderer = renderEng == 'blender' and 'BLENDER_RENDER' or 'CYCLES'
		self.scene.render.engine = self.renderer