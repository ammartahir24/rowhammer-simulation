'''
memory controller operations
'''
import config
from dram import DRAM
from simulate import Clock

class MemoryBus():
	"""Bus between memory controller and Dram"""
	def __init__(self, arg):
		self.arg = arg

class CommandSequence():
	def __init__(self, timestamp, callback=None):
		self.commandseq = []
		self.callback_function = callback
		self.arrival_time = timestamp

	def read_sequence(self, bank, row, column):
		self.commandseq.append(("activate", bank, row))
		self.commandseq.append(("read", bank, row, column))
		self.commandseq.append(("precharge", bank))
		self.bank, self.row, self.column = bank, row, column

	def write_sequence(self, bank, row, column, value):
		self.commandseq.append(("activate", bank, row))
		self.commandseq.append(("write", bank, row, column, value))
		self.commandseq.append(("precharge", bank))
		self.bank, self.row, self.column = bank, row, column

class MemoryController():
	"""memory controller to implement different policies and operate DRAM"""
	def __init__(self, configs, clock):
		self.configs = configs
		self.clock = clock
		self.dram = DRAM(self.clock)
		self.commands_queue = []

	def operate(self):
		# schedule commands
		self.clock.schedule(self.operate, None, run_time=1)

	def malloc(self, user, size):
		# allocate memory

	def read(self, user, address, callback):
		# address translation to physical address to bank, row tuple
		# checks about security etc.
		bank, row, column = self.translate_address(address)
		commands = CommandSequence(self.clock.get_clock(), callback=callback)
		commands.read_sequence(bank, row, column)
		self.commands_queue.append(commands)

	def write(self, user, address, value):
		# address translation to physical address to bank, row tuple
		# checks about security etc.
		bank, row, column = self.translate_address(address)
		commands = CommandSequence(self.clock.get_clock())
		commands.write_sequence(bank, row, column, value)
		self.commands_queue.append(commands) 
		
		