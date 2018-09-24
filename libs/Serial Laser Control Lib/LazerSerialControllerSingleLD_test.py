from lazer_serial_controllers.LazerSerialControllerSingleLD import LazerSerialControllerSingleLD
import time

'''
To use this script, 
fill config.txt with the following values (without numbers in brackets):
(0) Diode controller serial port

'''

# LOADING CONFIG
def load_config():
	with open('config.cfg') as config:
		return [line.strip() for line in config.readlines()]

try:
	config = load_config()
	diode_serial_port = config[0]
except:
	raise Exception("Unable to read data from config.cfg" + " \n" +
		"See the script's head to see how fill in config file")



def test_single_ld():
	dev = LazerSerialControllerSingleLD(diode_serial_port)

	print()
	print('Current value is', dev.get_current())
	print('Temperature value is', dev.get_temperature())
	print()

	print('Current is set to', dev.set_current(1.0))
	print('Current value is', dev.get_current())
	print()

	time_to_set_current = 4.0
	print('Scanning current to ', dev.scan_current(2.0, time_to_set_current))
	for i in range(int(time_to_set_current) + 1):
		if dev.is_scanning_current():
			print('Current is now scaning')
			print('Current value is', dev.get_current())
		else:
			print('Current scan completed')
		time.sleep(1)

test_single_ld()