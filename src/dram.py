'''
dram operations
'''

class DRAM():
	"""DRAM simulation based on DDR4"""
	def __init__(self, clock):
		self.clock = clock

	def activate(self, bank, row):
		''' opens a row: transfers a row from bank to its row buffer'''
		print(bank, row)
		self.clock.schedule(self.read, (bank, 2), run_time=1)
		return

	def read(self, bank, column):
		''' read column from bank's row buffer'''
		value = None
		return value

	def write(self, bank, column, value):
		''' write value to column of row bank'''
		return

	def precharge(self, bank):
		''' wrtie back row buffer to appropriate row of the bank'''
		return

	def refresh(self, row):
		''' refresh all bank's row by activating and precharging it'''
