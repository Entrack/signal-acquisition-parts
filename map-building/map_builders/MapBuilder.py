import sys
from time import sleep

# LOADING CONFIG
def load_config():
	with open('config.cfg') as config:
		return [line.strip() for line in config.readlines()]

try:
	config = load_config()
	measurement_lib_path = config[0]
	serial_laser_control_lib_path = config[1]
	signal_processing_lib_path = config[2]
	file_manager_lib_path = config[3]
	first_laser_diode_serial_port = config[4]
	second_laser_diode_serial_port = config[5]
except:
	raise Exception("Unable to read data from config.cfg" + " \n" +
		"See the script's head to see how fill in config file")

# Path to Measurement Lib
sys.path.insert(0, measurement_lib_path)
# Path to Serial Laser Control Lib
sys.path.insert(0, serial_laser_control_lib_path)
# Path to Signal Processing Lib
sys.path.insert(0, signal_processing_lib_path)
# Path to File Manager Lib
sys.path.insert(0, file_manager_lib_path)

from devices.ACFDevice import ACFDevice
from devices.RF306BDevice import RF306BDevice
from devices.OSDevice import OSDevice
from devices.OSCDevice import OSCDevice

from lazer_serial_controllers.LazerSerialControllerSingleLD import LazerSerialControllerSingleLD

# from signal_processors.ACFSignalProcessor import ACFSignalProcessor
from signal_processors.RFSignalProcessor import RFSignalProcessor
from signal_processors.OSSignalProcessor import OSSignalProcessor

from file_managers.SignalFileManager import SignalFileManager
import numpy as np
import time

class MapBuilder():
	def __init__(self, measurements_folder_path, mode, time_to_scan_current = 1.0):
		self.acf_dev = ACFDevice()
		self.rf_dev = RF306BDevice()
		# self.set_rf_default_settings()
		self.os_dev = OSDevice()
		self.os_dev.set_start('1040nm')
		self.os_dev.set_stop('1200nm')
		self.os_dev.set_resolution('0.500nm')		 
		self.osc_dev = OSCDevice()
		self.osc_dev.set_samples_per_sec(6.25e9)
		self.osc_dev.set_sec_per_div(2e-6)
		self.ld1 = LazerSerialControllerSingleLD(first_laser_diode_serial_port)
		self.ld2 = LazerSerialControllerSingleLD(second_laser_diode_serial_port)
		# self.acf_sp = ACFSignalProcessor()
		self.rf_sp = RFSignalProcessor()
		self.os_sp = OSSignalProcessor()

		self.supported_modes = [
		'Level_0'
		]
		self.time_to_scan_current = time_to_scan_current
		self.is_scanning_current_poll_time = 0.05
		self.measurement_cycle_delay = 0.05
		self.min_shutdown_current = 2.0
		# this settings can be changed from build_map.py file
		self.min_rf_contrast = 30.0
		self.number_of_averagings = 3
		self.min_os_shutdown_power = 1e-5

		self.I_ranges = None
		self.I_steps = None
		self.mode = None

		self.currents_sequence = None


		self.set_mode(mode)
		self.file_manager = SignalFileManager(measurements_folder_path, mode)

		print('MapBuilder inited!')

	def set_rf_default_settings(self):
		self.rf_dev.set_cf(16.1e6)
		self.rf_dev.set_span(1e6)
		self.rf_dev.set_rbw(1e3)

	def set_rf_wide_settings(self):
		self.rf_dev.set_cf(50e6)
		self.rf_dev.set_span(100e6)
		self.rf_dev.set_rbw(10e3)

	def set_min_rf_contrast(self, value):
		self.min_rf_contrast = value

	def set_number_of_averagings(self, value):
		self.number_of_averagings = value

	def set_min_os_shutdown_power(self, value):
		self.min_os_shutdown_power = value

	def set_I_ranges(self, I_ranges):
		self.I_ranges = {}
		self.I_ranges['I1_min'] = I_ranges[0]
		self.I_ranges['I1_max'] = I_ranges[1]
		self.I_ranges['I2_min'] = I_ranges[2]
		self.I_ranges['I2_max'] = I_ranges[3]

	def set_I_steps(self, I_steps):
		self.I_steps = {}
		self.I_steps['I1'] = I_steps[0]
		self.I_steps['I2'] = I_steps[1]

	def set_time_to_scan_current(self, time):
		self.time_to_scan_current = time

	def set_mode(self, mode):
		if self.check_mode(mode):
			self.mode = mode

	def check_mode(self, mode):
		is_supported = True
		if mode not in self.supported_modes:
			is_supported = False
			error_string = ('Mode ' + str(mode) + ' is not supported' + '\n' + 
				'Supported modes: ' + str(self.supported_modes))
			raise ValueError(error_string)
		return is_supported

	def is_inited(self):
		is_inited = True
		if self.I_steps is None or self.I_ranges is None or self.mode is None:
			is_inited = False
			print('Some of the needed settings (I_ranges, I_steps, mode) were not given')
		return is_inited

	def create_currents_sequence(self):
		if not self.is_inited():
			exit(0)

		I1_space = np.arange(self.I_ranges['I1_min'], self.I_ranges['I1_max'] + self.I_steps['I1'], self.I_steps['I1'])
		I2_space = np.arange(self.I_ranges['I2_min'], self.I_ranges['I2_max'] + self.I_steps['I2'], self.I_steps['I2'])

		currents_sequence_list = []	

		up = True
		for I1 in I1_space:
			if up:
				for I2 in I2_space:
					currents_sequence_list.append((I1, I2))
				up = not up
			else:
				for I2 in reversed(I2_space):
					currents_sequence_list.append((I1, I2))
				up = not up
		self.currents_sequence = np.array(currents_sequence_list)

	def scan(self):
		self.create_currents_sequence()		

		for currents in self.currents_sequence:
			self.process_regime(currents)

		print('Scan completed')


	def process_regime(self, currents):
		print('Processing', currents)
		if self.mode is 'Level_0':
			self.process_Level_0(currents)		

	def process_Level_0(self, currents):
		I1 = currents[0]
		I2 = currents[1]
		self.ld1.scan_current(0.0, self.time_to_scan_current)
		self.ld2.scan_current(0.0, self.time_to_scan_current)
		self.wait_for_scan()
		self.ld1.scan_current(I1, self.time_to_scan_current)
		self.ld2.scan_current(I2, self.time_to_scan_current)
		self.wait_for_scan()

		self.measure_and_record(currents)

	def measure_and_record(self, currents):
		I1 = currents[0]
		I2 = currents[1]
		while True:
			try:
				acf_x, acf_y = self.acf_dev.get_acf()
				self.set_rf_default_settings()
				rf_x, rf_y = self.rf_dev.get_rf()
				self.set_rf_wide_settings()
				rf_w_x, rf_w_y = self.rf_dev.get_rf()
				os_x, os_y = self.os_dev.get_os()
				osc_x, osc_y = self.osc_dev.get_osc()
				break
			except KeyboardInterrupt:
				print('You pressed ctrl-c. Exiting...')
				exit(0)
			except Exception as e:
				print(e)
				print('Failed to take the measurement. Repeating once more...')
				sleep(self.measurement_cycle_delay)

		os_power = self.min_os_shutdown_power * 2
		os_power_tries = 0
		while os_power_tries <= 3:
			try:
				os_power_tries += 1
				os_power = self.os_sp.get_power(os_x, os_y)
				break
			except KeyboardInterrupt:
				print('You pressed ctrl-c. Exiting...')
				exit(0)
			except Exception as e:
				print(e)
				print('Failed to compute os power. Repeating once more...')
				sleep(self.measurement_cycle_delay)
				
		print('os_power:', os_power)
		if os_power < self.min_os_shutdown_power:
			if I1 > self.min_shutdown_current or I2 > self.min_shutdown_current:
				print('Too low OS power:', os_power)
				print('Shutting down...')
				self.ld1.scan_current(0.0, self.time_to_scan_current)
				self.ld2.scan_current(0.0, self.time_to_scan_current)
				self.wait_for_scan()
				exit(0) 

		rf_con = 0.0
		rf_con_tries = 0
		while rf_con_tries <= 3:
			try:
				rf_con_tries += 1
				rf_con = self.rf_sp.get_contrast(rf_x, rf_y)
				break
			except KeyboardInterrupt:
				print('You pressed ctrl-c. Exiting...')
				exit(0)
			except Exception as e:
				print(e)
				print('Failed to compute rf contrast. Repeating once more...')
				sleep(self.measurement_cycle_delay)

		print('rf_con:', rf_con)
		if rf_con < self.min_rf_contrast:
			self.file_manager.save_acf(I1, I2, acf_x, acf_y)
			self.file_manager.save_rf(I1, I2, rf_x, rf_y)
			self.file_manager.save_rf_wide(I1, I2, rf_w_x, rf_w_y)
			self.file_manager.save_os(I1, I2, os_x, os_y)
			self.file_manager.save_osc(I1, I2, osc_x, osc_y)
		else:
			for i in range(self.number_of_averagings):
				print('Measuring for averaging:', i, 'out of ', self.number_of_averagings)
				while True:
					try:
						acf_y_tmp = self.acf_dev.get_acf()[1]
						acf_y += acf_y_tmp
						break
					except KeyboardInterrupt:
						print('You pressed ctrl-c. Exiting...')
						exit(0)
					except:
						print('Failed to take the measurement. Repeating once more...')
						sleep(self.measurement_cycle_delay)
			if not self.number_of_averagings == 1:
				acf_y /= self.number_of_averagings
			self.file_manager.save_acf(I1, I2, acf_x, acf_y)
			self.file_manager.save_rf(I1, I2, rf_x, rf_y)
			self.file_manager.save_rf_wide(I1, I2, rf_w_x, rf_w_y)
			self.file_manager.save_os(I1, I2, os_x, os_y)
			self.file_manager.save_osc(I1, I2, osc_x, osc_y)

	def wait_for_scan(self):
		while True:
			if not self.ld1.is_scanning_current() and not self.ld2.is_scanning_current():
				break
			time.sleep(self.is_scanning_current_poll_time)