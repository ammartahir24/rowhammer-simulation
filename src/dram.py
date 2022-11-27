'''
dram operations
'''

class DRAM():
	"""DRAM simulation based on DDR4"""
	def __init__(self, arg):
		self.arg = arg

	def activate(bank, row):
		''' opens a row: transfers a row from bank to its row buffer'''
		return

	def read(bank, column):
		''' read column from bank's row buffer'''
		value = None
		return value

	def write(bank, column, value):
		''' write value to column of row bank'''
		return

	def precharge(bank):
		''' wrtie back row buffer to appropriate row of the bank'''
		return

	def refresh(row):
		''' refresh all bank's row by activating and precharging it'''
