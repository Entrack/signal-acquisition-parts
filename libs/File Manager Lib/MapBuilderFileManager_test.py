from file_managers.MapBuilderFileManager import MapBuilderFileManager
import numpy as np

def test_map_builder_file_manager():
	fm = MapBuilderFileManager('/home/jonathan/Documents/file_manager_test/', 'modename')
	x = np.array([[1, 2, 3]])
	y = np.array([[4, 5, 6]])

	fm.save_acf(2.28, 2.28, x, y)

	fm.save_map(np.concatenate((x, y)), (0.0, 1.0, 0.0, 1.0))

	print('testing', 'map_builder_file_manager')

test_map_builder_file_manager()