from file_managers.FileManager import FileManager

import numpy as np
import pathlib2 as pathlib
import datetime

class SignalFileManager(FileManager):
	def __init__(self, measurements_folder_path = '', mode = 'mode_unknown', experiment_folder_name = None, *args, **kwargs):
		super(SignalFileManager, self).__init__(*args, **kwargs)
		print('SignalFileManager __init__ was called')
		''' Path should be in a standart format, i.e. end with "/" symbol'''
		self.measurements_folder_path = measurements_folder_path
		self.mode = mode
		self.experiment_folder_name = experiment_folder_name

		self.supported_variables = ['ACF', 'RF', 'OS', 'OSC', 'RF_WIDE']
		self.variables_paths = {}
		self.precision = '%.12f'

		self.now = datetime.datetime.now()
		self.init_folders()
		print(self.__class__.__name__, 'inited!')

	def init_folders(self):
		for variable in self.supported_variables:
			path = self.form_path_string(variable)
			self.set_variable_path(variable, path)
			self.create_folder(path)

	def create_folder(self, path):
		pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

	def form_path_string(self, variable):
		return (self.measurements_folder_path + 
			self.get_experiment_folder_name(variable) +
			'/' + 'I1_I2_' + self.mode +
			'/' + variable + '/')

	def get_experiment_folder_name(self, variable):
		experiment_folder_name = ""
		if self.experiment_folder_name is None:
			experiment_folder_name = self.get_data_time_folder_name()
		else:
			experiment_folder_name = self.experiment_folder_name
		return experiment_folder_name

	def get_data_time_folder_name(self):
		return self.now.strftime("%Y-%m-%d_%H-%M")

	def set_variable_path(self, variable, path):
		self.variables_paths[variable] = path

	def save_variable(self, variable, I1, I2, x, y):
		if self.check_variable(variable):
			#file = self.create_file(variable, I1, I2)
			path = self.variables_paths[variable] + self.form_variable_file_name(variable, I1, I2)
			np.savetxt(path, np.column_stack((x, y)), delimiter=",", fmt = self.precision)

	def save_acf(self, I1, I2, x, y):
		self.save_variable('ACF', I1, I2, x, y)

	def save_rf(self, I1, I2, x, y):
		self.save_variable('RF', I1, I2, x, y)

	def save_os(self, I1, I2, x, y):
		self.save_variable('OS', I1, I2, x, y)

	def save_osc(self, I1, I2, x, y):
		self.save_variable('OSC', I1, I2, x, y)

	def save_rf_wide(self, I1, I2, x, y):
		self.save_variable('RF_WIDE', I1, I2, x, y)

	def form_variable_file_name(self, variable, I1, I2):
		return (str(variable).lower() + '_' + '%.2f' % I1 + '_' + '%.2f' % I2 + '.csv')

	# def create_file(self, file_name):
	# 	with open(self.variables_paths[variable] + file_name) as file:
	# 		return file

	def check_variable(self, variable):
		is_supported = True
		if not variable in self.supported_variables:
			print("Variable '" + str(variable) + "'", 'is not supported')
			is_supported = False
		return is_supported