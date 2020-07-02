from commonUtils import mkdir, fileExist, getFilesList
from blenderClass import Blender
from multiprocessing import Process

class Clean():
	def __init__(self, opt):
		self.opt = opt

		self.datasetPath = opt.datasetPath
		self.harshPolish = opt.harshPolish

		# Initialize the Blender class
		self.blender = Blender()
		self.blender.setupScene()

	def cleanShapes(self):
		categoryPaths = getFilesList(self.datasetPath, onlyDir=True)
		cleanedObjParentPath = self.datasetPath + 'cleaned'
		categoryPaths = [path for path in categoryPaths if cleanedObjParentPath not in path]

		for catPath in categoryPaths:
			objPaths = getFilesList(catPath, fileType='obj', forceSort=True)

			catName = catPath.split('/')[-1]
			print ("==> Fixing Normals for shapes of category {0:s}".format(catName))

			cleanedObjCatPath = cleanedObjParentPath + '/' + catName
			mkdir(cleanedObjCatPath)

			processes = []
			cleanedObjPaths = []
			objPathSplit = objPaths[0].split('/')
			for i, objPath in enumerate(objPaths):
				objPathSplit = objPath.split('/')
				cleanedObjPaths.append(cleanedObjCatPath + '/' + objPathSplit[-1].split('.')[0] + '.obj')
				if not fileExist(cleanedObjPaths[-1]):
					processes.append(Process(target=self.blender.polishObj, kwargs={'objPath': objPath, 'harshPolish': self.harshPolish, 'objSavePath': cleanedObjPaths[-1]}))

				if len(processes) > 0 and (len(processes) == 5 or i == len(objPaths)-1):
					for proc in processes:
						proc.start()

					for proc in processes:
						proc.join()
					processes = []
		return cleanedObjPaths