from file_managers.SignalFileManager import SignalFileManager
import numpy as np

def test_signal_file_manager():
	fm = SignalFileManager('/home/jonathan/Documents/file_manager_test/', 'modename')
	x = np.array([[1, 2, 3]])
	y = np.array([[4, 5, 6]])

	fm.save_acf(2.28, 2.28, x, y)

	print('testing', 'signal_file_manager')

test_signal_file_manager()