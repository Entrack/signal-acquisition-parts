from file_managers.SignalFileManager import SignalFileManager
import numpy as np
import matplotlib.pyplot as plt

class MapBuilderFileManager(SignalFileManager):
	def __init__(self, *args, **kwargs):
		super(MapBuilderFileManager, self).__init__(*args, **kwargs)
		self.map_folder_path = ''
		self.init_map_folder()		

	def init_map_folder(self):
		self.map_folder_path = (self.measurements_folder_path + 
		self.get_data_time_folder_name() + '/' + 'map_' + self.mode + '/')
		self.create_folder(self.map_folder_path)

	def save_map(self, array, I_ranges):
		self.save_map_csv(array)
		self.save_map_png(array, I_ranges)

	def save_map_csv(self, array):
		path = self.map_folder_path + 'map'
		print(path)
		np.savetxt(path, array, delimiter=",", fmt = self.fmt)

	def save_map_png(self, array, I_ranges):
		fig, ax = plt.subplots()
		heatmap = ax.pcolor(array, cmap=plt.cm.inferno)
		fig.colorbar(heatmap)
		plt.xticks([])
		plt.yticks([])
		ax.set_aspect(1)
		plt.xlabel('I1 range is from ' + str(I_ranges[0]) + ' to ' + str(I_ranges[1]))
		plt.ylabel('I2 range is from ' + str(I_ranges[2]) + ' to ' + str(I_ranges[3]))
		plt.show()