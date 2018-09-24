class EmptyVirtualController():
	def __init__(self):
		self.default_value = 4.0

	def get_current(self):
		return self.default_value

	def scan_current(self, value, time):
		pass

	def is_scanning_current(self):
		return False