import numpy as np
import matplotlib.pyplot as plt

signals_folder = '/home/jonathan/Coding/Python/_diploma_Lazers/Projects/NN Laser Control/Map Generator/measurements/gauss_up_left/I1_I2_generated/ACF/'
variable = 'ACF'
I1 = 4.0
I2 = 4.0

def plot_signal(I1, I2):
	file_name = str(variable).lower() + '_' + '%.2f' % I1 + '_' + '%.2f' % I2 + '.csv'
	signal = np.genfromtxt(signals_folder + file_name, delimiter = ',')
	plt.plot(signal[:, 0], signal[:, 1])
	plt.show()

plot_signal(I1, I2)