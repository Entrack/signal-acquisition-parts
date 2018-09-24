import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pathlib2 as pathlib
import copy

'''
To use this script,
fill config.txt with the following currents (without numbers in brackets):
(0) Measurement Lib path
//(1) Serial Laser Control Lib path
(2) Signal Processing Lib path
//(3) File Manager Lib path
//(4) First laser diode serial port
//(5) Second laser diode serial port
(6) Path to the folder for saving data
(7) Premade data folder path

'''

# LOADING CONFIG
def load_config():
	with open('config.cfg') as config:
		return [line.strip() for line in config.readlines()]

try:
	config = load_config()
	measurement_lib_path = config[0]
	serial_laser_control_lib_path = config[1]
	signal_processing_lib_path = config[2]
	data_saving_folder = config[6]
	premade_measurement_folder_path = config[7]
except:
	raise Exception("Unable to read data from config.cfg" + " \n" +
		"See the script's head to see how fill in config file")

sys.path.insert(0, measurement_lib_path)
sys.path.insert(0, signal_processing_lib_path)

from devices.FileVirtualDevice import FileVirtualDevice
from signal_processors.ACFSignalProcessor import ACFSignalProcessor
from signal_processors.RFSignalProcessor import RFSignalProcessor
from signal_processors.OSSignalProcessor import OSSignalProcessor
from signal_processors.OSCSignalProcessor import OSCSignalProcessor

def get_feature_function_name_from_tuple(feature_function_tuple):
	name = feature_function_tuple[0].__name__
	if 'get_' in name:
		name = name.replace('get_', '')
	name += '_' + 'by'
	for arg_name in feature_function_tuple[1]:
		name += '_' + str(arg_name)
	return name

def convert_feature_list_to_dict(feature_list):
	feature_dict = {}
	for el in feature_list:
		feature_name = get_feature_function_name_from_tuple(el)
		feature_dict[feature_name] = el
	return feature_dict

constraints = {
	'I1_min' : 0.0,
	'I1_max' : 0.0,
	'I2_min' : 0.0,
	'I2_max' : 0.0
	}
currents = {
	'I1' : 0.0,
	'I2' : 0.0
	}

# supported_devices = ['ACF']#, 'RF', 'RF_WIDE', 'OS', 'OSC']
supported_devices = ['ACF', 'RF', 'RF_WIDE', 'OS', 'OSC']
delimiter = ','
file_type = 'csv'

devices = {}
for idx, device in enumerate(supported_devices):
	try:
		prev_constraints = copy.deepcopy(constraints)
		devices[device.lower()] = FileVirtualDevice(device, constraints, currents, premade_measurement_folder_path, 
			file_type = file_type, delimiter = delimiter)
		if not idx == 0:
			for key in constraints:
				if not constraints[key] == prev_constraints[key]:
					raise Exception('Current bounds does not match')

	except Exception as e:
		print(e)
		print('Cannot open some of the files from the folder you specified')
		print('Check if config.cfg was filled in correctly and the folder contains all the measurements script needs')
		exit(0)

acf_sp = ACFSignalProcessor()
rf_sp = RFSignalProcessor()
os_sp = OSSignalProcessor()
osc_sp = OSCSignalProcessor()

step = 0.1

# constraints = {
# 	'I1_min' : 1.0,
# 	'I1_max' : 1.0,
# 	'I2_min' : 1.0,
# 	'I2_max' : 8.0
# 	}

I1_space = np.arange(constraints['I1_min'], constraints['I1_max'] + step, step)
I1_number = int((constraints['I1_max'] + step - constraints['I1_min']) / step)
I2_space = np.arange(constraints['I2_min'], constraints['I2_max'] + step, step)
I2_number = int((constraints['I2_max'] + step - constraints['I2_min']) / step)

grid = np.zeros((I1_number, I2_number))

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
final_data_saving_folder = data_saving_folder + '\extracted_features' + '_' + str(timestamp) + '\\'
pathlib.Path(final_data_saving_folder).mkdir(parents = True, exist_ok = True)
maps_saving_folder = final_data_saving_folder + '\maps' + '\\'
pathlib.Path(maps_saving_folder).mkdir(parents = True, exist_ok = True)
feature_file_path = final_data_saving_folder + 'features' + '.txt' # + '_' + str(timestamp) + ".txt"
feature_file = open(feature_file_path,"w+")
failures_file_path = final_data_saving_folder + 'failures' + ".txt"
failure_file = open(failures_file_path,"w+")

def log_failure(I1, I2, message = ""):
	error_message = '%.2f' % I1 + ' ' + '%.2f' % I2 + ' ' + message + '\n'
	print(error_message)
	failure_file.write(error_message)

# HERE YOU PUT THE FUNCTIONS THAT WILL EXTRACT THE FINAL FEATURES YOU NEED
# pointer to the function : array of args it needs
# feature_functions_list = [
# 	(acf_sp.get_acf_coh, ('acf_x', 'acf_y'))
# ]
feature_functions_list = [
	(acf_sp.get_acf_env_fwhm, ('acf_x', 'acf_y')),
	(acf_sp.get_acf_coh, ('acf_x', 'acf_y')),
	(rf_sp.get_contrast, ('rf_x', 'rf_y')),
	(os_sp.get_power, ('os_x', 'os_y')),
	(os_sp.get_signal_power, ('os_x', 'os_y')),
	(os_sp.get_raman_power, ('os_x', 'os_y')),
	(os_sp.get_signal_rms, ('os_x', 'os_y')),
	(os_sp.get_raman_rms, ('os_x', 'os_y')),
	(os_sp.get_power, ('osc_av_os_x', 'osc_av_os_y')),
	(os_sp.get_signal_power, ('osc_av_os_x', 'osc_av_os_y')),
	(os_sp.get_raman_power, ('osc_av_os_x', 'osc_av_os_y')),
	(os_sp.get_signal_rms, ('osc_av_os_x', 'osc_av_os_y')),
	(os_sp.get_raman_rms, ('osc_av_os_x', 'osc_av_os_y')),
	(osc_sp.get_mean, ('osc_os_sig_pow_fluct')),
	(osc_sp.get_mean, ('osc_os_ram_pow_fluct')),
	(osc_sp.get_std, ('osc_os_sig_pow_fluct')),
	(osc_sp.get_std, ('osc_os_ram_pow_fluct'))
]

feature_functions = convert_feature_list_to_dict(feature_functions_list)


# HERE YOU PUT FUNCTIONS THAT WILL EXTRACT ARGUMENTS FOR THE FUNCTIONS THAT PROCESS THEM INTO FINAL FEATURES
def extract_data_from_signals(data, I1, I2):
	# this pile of shit was put here to tell in which function exactly the code breaks
	# you can remove all the try catch blocks if you don't need this
	try:
		wl_c, _ = os_sp.get_wl_c(data['os_x'], data['os_y'])
	except:
		log_failure(I1, I2, 'get_wl_c')
		raise Exception('Cannot extract data from signal')
	try:
		rf_freq_rep = rf_sp.get_rf_freq_rep(data['rf_x'], data['rf_y'])
	except:
		log_failure(I1, I2, 'get_rf_freq_rep')
		raise Exception('Cannot extract data from signal')
	try:
		osc_map, wl_map = osc_sp.get_dft_map(data['osc_x'], data['osc_y'], wl_c, rf_freq_rep)
	except:
		log_failure(I1, I2, 'get_dft_map')
		raise Exception('Cannot extract data from signal')
	try:
		data['osc_av_os_y'], data['osc_av_os_x'] = osc_sp.get_average_osc(osc_map, wl_map)
	except:
		log_failure(I1, I2, 'get_average_osc')
		raise Exception('Cannot extract data from signal')
	try:
		data['osc_os_sig_pow_fluct'], data['osc_os_ram_pow_fluct'], data['osc_os_sig_pow_fluct'], data['osc_os_ram_pow_fluct'] = os_sp.get_dft_fluctuations(osc_map, wl_map)
	except:
		log_failure(I1, I2, 'get_dft_fluctuations')
		raise Exception('Cannot extract data from signal')


feature_maps = {}
for name in feature_functions:
	feature_maps[name] = np.zeros((I1_number, I2_number))

def get_point_values(I1, I2):
	value_list = []
	data = {}
	
	for device_name in devices:
		try:
			data[device_name + '_x'], data[device_name + '_y'] = devices[device_name].get_measurement() 
		except Exception as e:
			print(e)
			print('Cannot read data from the point', 'I1: %.2f' % I1, 'I2: %.2f' % I2)
			exit(0)

	try:
		extract_data_from_signals(data, I1, I2)
	except:
		log_failure(I1, I2, "Cannot process this point. Skipping it")
		raise Exception('Point processing error')

	value_list.append('%.2f' % I1)
	value_list.append('%.2f' % I2)

	for feature_function_name in feature_functions:
		feature_function = feature_functions[feature_function_name][0]
		arg_name_list = feature_functions[feature_function_name][1]
		args = []
		if not type(arg_name_list) is str:
			for arg_name in arg_name_list:
				args.append(data[arg_name])
		else:
			args.append(data[arg_name_list])
		try:
			feature_value = feature_function(*args)
			value_list.append(feature_value)
			I1_idx = np.where(I1_space == I1)[0][0]
			I2_idx = np.where(I2_space == I2)[0][0]
			feature_maps[feature_function_name][I1_idx, I2_idx] = feature_value
		except Exception as e:
			print(e)
			error_message = ('Cannot process function ' + str(feature_function.__name__)
			 + ' on the point ' + 'I1: %.2f ' % I1 + 'I2: %.2f ' % I2)
			log_failure(I1, I2, error_message)
			print('Setting this value to zero')
			value_list.append(0.0)

	return value_list

def write_feature_str(values):
	feature_str = ""
	for feature in values:
		feature_str += str(feature) + ' '
	feature_file.write(feature_str + '\n')

def add_header(feature_functions):
	header = 'I1' + ' ' + 'I2' + ' '
	for name in feature_functions:
		header += name + ' '
	feature_file.write(header + '\n')

def main():
	# read this data with np.genfromtxt option 'skip_header = 1'
	add_header(feature_functions)
	for i1 in range(I1_number):
		for i2 in range(I2_number):
			currents['I1'] = I1_space[i1]
			currents['I2'] = I2_space[i2]
			print('Processing:', '%.2f' % currents['I1'], '%.2f' % currents['I2'])
			try:
				values = get_point_values(currents['I1'], currents['I2'])
			except:
				continue
			# print(values)
			write_feature_str(values)
	for feature_name in feature_maps:
		# x_labels = []
		# for el in I1_space[::2]:
		# 	x_labels.append("%.1f" % el)
		# y_labels = []
		# for el in I2_space[::2]:
		# 	y_labels.append("%.1f" % el)
		fig = plt.figure()
		plt.imshow(np.flipud(feature_maps[feature_name]), interpolation='none')
		plt.colorbar()
		# plt.xticks(np.arange(0, I1_number, 2.0), x_labels, fontsize = 6)
		# plt.yticks(np.arange(0, I2_number, 2.0), y_labels, fontsize = 6)
		plt.xticks([])
		plt.yticks([])
		fig.savefig(maps_saving_folder + feature_name + '.png', dpi = 1000)
			
main()



























# x_labels = []
# for el in I1_space[::2]:
# 	x_labels.append("%.1f" % el)
# y_labels = []
# for el in I2_space[::2]:
# 	y_labels.append("%.1f" % el)
# plt.imshow(grid, interpolation='nearest')
# plt.xticks(np.arange(0, I1_number, 2.0), x_labels, fontsize = 6)
# plt.yticks(np.arange(0, I2_number, 2.0), y_labels, fontsize = 6)
# plt.colorbar()
# plt.show()