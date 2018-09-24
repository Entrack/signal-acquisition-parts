import serial

class LazerSerialControllerSingleLD():
	def __init__(self, serial_port, baudrate = 115200):
		''' 
		Used serial ports:
			LD1 Linux:		/dev/ttyUSB0
			LD2 Linux:		/dev/ttyUSB1
			LD1 Windows:	COM9
			LD2 Windows:	COM6
		'''
		self.ser = serial.Serial(serial_port)
		self.ser.baudrate = baudrate
		self.supported_variables = ['I', 'T']
		self.constraints = {
		'I_min' : 0.0,
		'I_max' : 8.0,
		'T_min' : 20.0,
		'T_max' : 40.0,
		't_min' : 0.0,
		't_max' : 3600.0
		}
		print('CurrentController inited!')

	def send(self, message):
		self.ser.write((message + '\r\n').encode())

	def receive(self):
		line = self.ser.readline()
		return line.decode('utf-8').rstrip()

	def get_value(self, message):
		value = None
		for variable in self.supported_variables:
			try:
				value = message.split()[message.split().index(variable) + 1]
			except:
				pass

		if value is None:
			print("Can't get current or temperature value from the message:", message)
		
		return value

	def receive_value(self):
		return self.get_value(self.receive())

	def query_message(self, variable, message):
		answer = None
		if self.check_variable(variable):
			self.send(message)
			anwser = self.receive_value()
		return anwser

	def value_to_str(self, value):
		string = '%.3f' % value
		if value < 10.0:
			string = ' ' + string
		return string

	def check_variable(self, variable):
		is_supported = True
		if not variable in self.supported_variables:
			print("Variable '" + str(variable) + "'", 'is not supported')
			is_supported = False
		return is_supported

	def restrict_value(self, variable, value):
		result = value
		try:
			min_value = self.constraints[str(variable) + '_min']
			if value < min_value:
				print('Restricting', variable, 'variable to', min_value)
				result = min_value
			max_value = self.constraints[str(variable) + '_max']
			if value > max_value:
				print('Restricting', variable, 'variable to', max_value)
				result = max_value
		except:
			pass
		return result

	def int_str_to_bool(self, string):
		answer = None
		try:
			answer = bool(int(string))
		except:
			print('String:', string, 'is not convertable to int')
		return answer

	#
	# CONTROLLER API STARTS HERE
	#

	def get_variable(self, variable):
		message = 'Cur ' + str(variable)
		return self.query_message(variable, message)

	def get_current(self):
		return self.get_variable('I')

	def get_temperature(self):
		return self.get_variable('T')


	def set_variable(self, variable, value):
		value = self.restrict_value(variable, value)
		message = 'Set ' + str(variable) + ' ' + self.value_to_str(value)
		return self.query_message(variable, message)

	def set_current(self, value):
		return self.set_variable('I', value)

	def set_temperature(self, value):
		print('set_temperature', 'is not working on controller')
		return None
		#return self.set_variable('T', value)


	def scan_variable(self, variable, value, time):
		value = self.restrict_value(variable, value)
		time = self.restrict_value('t', time)
		message = 'Scan ' + str(variable) + ' ' + self.value_to_str(value) + ' ' + self.value_to_str(time)
		return self.query_message(variable, message)

	def scan_current(self, value, time):
		return self.scan_variable('I', value, time)

	def scan_temperature(self, value, time):
		return self.scan_variable('T', value, time)


	def is_scanning_variable(self, variable):
		message = 'In_Proc? ' + str(variable)
		return self.int_str_to_bool(self.query_message(variable, message))

	def is_scanning_current(self):
		return self.is_scanning_variable('I')

	def is_scanning_temperature(self, value):
		return self.is_scanning_variable('T')


	def set_variable_home(self, variable, value):
		value = self.restrict_value(variable, value)
		message = 'Home ' + str(variable) + ' ' + self.value_to_str(value)
		return self.query_message(variable, message)

	def set_current_home(self, value):
		return self.set_variable_home('I', value)

	def set_temperature_home(self, value):
		print('set_temperature_home', 'is not implemented in controller')
		return None
		#return self.set_variable_home('T', value)


	def go_variable_home(self, variable):
		message = 'GoHome ' + str(variable)
		return self.query_message(variable, message)

	def go_current_home(self):
		return self.go_variable_home('I')

	def go_temperature_home(self):
		print('go_temperature_home', 'is not implemented in controller')
		return None
		#return self.go_variable_home('T')