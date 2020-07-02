import argparse, os
from commonUtils import mkdirs, savePickle, fileExist


class opts():
	def __init__(self):
		self.parser = argparse.ArgumentParser()
		self.initialized = False

	def initialize(self):
		#Global
		self.parser.add_argument('--datasetPath', default='dataset/', help='path to your data set')
		self.parser.add_argument('--resultPath', default='cleanedObjs', help='path for the stimuli')
		self.parser.add_argument('--harshPolish', type=int, default=0, choices=[0, 1], help='Whether or not to apply heavy smoothing for objects')

		self.initialized = True

	def parse(self):
		if not self.initialized:
			self.initialize()
		self.opt = self.parser.parse_args()

		# Some manual intervention!
		if self.opt.datasetPath[len(self.opt.datasetPath)-1] != '/':
			self.opt.datasetPath = self.opt.datasetPath + '/'

		if self.opt.resultPath[len(self.opt.resultPath)-1] != '/':
			self.opt.resultPath = self.opt.resultPath + '/'
			


		if not fileExist(self.opt.datasetPath):
			print ("==> Error: Please make sure you place your obj files in '{0:s}[Category Name]' and then re-run the code".format(self.opt.datasetPath))
			exit()

		if not fileExist(self.opt.resultPath):
			mkdirs(self.opt.resultPath)

		self.opt.harshPolish = self.opt.harshPolish == 1 and True or False


		args = vars(self.opt)

		print('------------ Options -------------')
		for k, v in sorted(args.items()):
			print('%s: %s' % (str(k), str(v)))
		print('-------------- End ----------------')

		savePickle(filePath='opt.pkl', data=self.opt)

	    # save the options on disk
		file_name = os.path.join(os.getcwd(), 'opt_train.txt')
		with open(file_name, 'wt') as opt_file:
			opt_file.write('------------ Options -------------\n')
			for k, v in sorted(args.items()):
				opt_file.write('%s: %s\n' % (str(k), str(v)))
			opt_file.write('-------------- End ----------------\n')

		return self.opt