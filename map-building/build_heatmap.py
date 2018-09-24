import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, 'C:/Users/admin/Desktop/Daniel/_diploma_Lazers/Libs/Measurement Lib')
sys.path.insert(0, 'C:/Users/admin/Desktop/Daniel/_diploma_Lazers/Libs/Signal Processing Lib')

from devices.FileVirtualDevice import FileVirtualDevice
from signal_processors.ACFSignalProcessor import ACFSignalProcessor
from signal_processors.RFSignalProcessor import RFSignalProcessor
from signal_processors.OSSignalProcessor import OSSignalProcessor


premade_measurement_folder_path = 'C:/Users/admin/Desktop/Daniel/_diploma_Lazers/I1_I2_Level_0/'
#premade_measurement_folder_path = '/home/jonathan/Coding/Python/_diploma_Lazers/Projects/NN Laser Control/Map Generator/measurements/gauss_up_left/I1_I2_generated/'
# premade_measurement_folder_path = '/dev/shm/I1_I2_generated/'

constraints = {
	'I1_min' : 0.0,
	'I1_max' : 0.0,
	'I2_min' : 0.0,
	'I2_max' : 0.0
	}
values = {
	'I1' : 4.0,
	'I2' : 4.0
	}

acf_dev = FileVirtualDevice('ACF', constraints, values, premade_measurement_folder_path,
 file_type = 'txt', delimiter = '\t')
rf_dev = FileVirtualDevice('RF', constraints, values, premade_measurement_folder_path,
 file_type = 'txt', delimiter = '\t')
# os_dev = FileVirtualDevice('OS', constraints, values, premade_measurement_folder_path, [None, 1080])

acf_sp = ACFSignalProcessor()
rf_sp = RFSignalProcessor()
os_sp = OSSignalProcessor()

def get_point_value():
	# acf_x, acf_y = acf_dev.get_acf()
	# os_x, os_y = os_dev.get_os()
	rf_x, rf_y = rf_dev.get_rf()

	# acf_fwhm = acf_sp.get_acf_env_fwhm(time=acf_x, acf=acf_y)
	# acf_coh = acf_sp.get_acf_coh(time=acf_x, acf=acf_y)
	rf_con = rf_sp.get_contrast(rf_x, rf_y)

	value = 0
	value = rf_con

	return value
	# return acf_coh
	# return acf_coh * acf_fwhm

	# return np.amax(acf_y)

step = 0.1

I1_space = np.arange(constraints['I1_min'], constraints['I1_max'] + step, step)
I1_number = int((constraints['I1_max'] + step - constraints['I1_min']) / step)
I2_space = np.arange(constraints['I2_min'], constraints['I2_max'] + step, step)
I2_number = int((constraints['I2_max'] + step - constraints['I2_min']) / step)

grid = np.zeros((I1_number, I2_number))

for i1 in range(I1_number):
	for i2 in range(I2_number):
		values['I1'] = I1_space[i1]
		values['I2'] = I2_space[i2]
		value = get_point_value()
		print('%.2f' % I1_space[i1], '%.2f' % I2_space[i2])
		grid[i1, i2] = value


x_labels = []
for el in I1_space[::2]:
	x_labels.append("%.1f" % el)
y_labels = []
for el in I2_space[::2]:
	y_labels.append("%.1f" % el)
plt.imshow(grid, interpolation='nearest')
plt.xticks(np.arange(0, I1_number, 2.0), x_labels, fontsize = 6)
plt.yticks(np.arange(0, I2_number, 2.0), y_labels, fontsize = 6)
plt.colorbar()
plt.show()