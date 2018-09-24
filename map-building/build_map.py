'''
To use this script,
fill config.txt with the following values (without numbers in brackets):
(0) Measurement Lib path
(1) Serial Laser Control Lib path
(2) Signal Processing Lib path
(3) File Manager Lib path
(4) First laser diode serial port
(5) Second laser diode serial port
(6) Path to the folder for saving measurements

'''

# LOADING CONFIG
def load_config():
	with open('config.cfg') as config:
		return [line.strip() for line in config.readlines()]

try:
	config = load_config()
	measurements_saving_folder = config[6]
except:
	raise Exception("Unable to read data from config.cfg" + " \n" +
		"See the script's head to see how fill in config file")



from map_builders.MapBuilder import MapBuilder

builder = MapBuilder(measurements_saving_folder, 'Level_0')

builder.set_I_ranges((1.0, 8.0, 1.0, 8.0))
builder.set_I_steps((0.1, 0.1))
builder.set_min_rf_contrast(25)
builder.set_number_of_averagings(5)

builder.scan()