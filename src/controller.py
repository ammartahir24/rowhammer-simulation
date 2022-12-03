'''
memory controller operations
'''
import config
from dram import DRAM
from simulate import Clock

def bitExtracted(number, k, p):
	return ( ((1 << k) - 1)  &  (number >> (p-1) ) )

class MemoryBus():
	"""Bus between memory controller and Dram"""
	def __init__(self, size, dram, clock):
		self.size = size
		self.occupancy = 0
		self.dram = dram
		self.clock = clock

	def start_op(self, commandseq):
		if self.occupancy < self.size:
			self.occupancy += 1
			return 1
		return 0

	def fetch(self, commandseq, callback):
		self.occupancy -= 1
		value = 0
		for i in range(8):
			value += (2*self.dram.read(commandseq.bank, 8*commandseq.column+i))**i
		commandseq.completion_time = self.clock.get_clock()
		callback(commandseq, value)

	def write(self, commandseq, callback):
		self.occupancy -= 1
		value = commandseq.value
		for i in range(8):
			val = bitExtracted(value, 1, i+1)
			self.dram.write(commandseq.bank, 8*commandseq.column+i, val)
		commandseq.completion_time = self.clock.get_clock()
		callback(commandseq)

	def open_row(self, commandseq, callback):
		self.dram.activate(commandseq.bank, commandseq.row)
		callback(commandseq)

	def close_row(self, commandseq, callback):
		self.dram.precharge(commandseq.bank)
		callback(commandseq)


class CommandSequence():
	def __init__(self, timestamp, callback=None):
		self.commandseq = []
		self.callback_function = callback
		self.arrival_time = timestamp
		self.completion_time = -1
		self.op_running = False

	def read_sequence(self, bank, row, column):
		self.commandseq.append(("activate", bank, row))
		self.commandseq.append(("read", bank, row, column))
		self.commandseq.append(("precharge", bank))
		self.bank, self.row, self.column = bank, row, column

	def write_sequence(self, bank, row, column, value):
		self.commandseq.append(("activate", bank, row))
		self.commandseq.append(("write", bank, row, column, value))
		self.commandseq.append(("precharge", bank))
		self.bank, self.row, self.column, self.value = bank, row, column, value

class MemoryController():
	"""memory controller to implement different policies and operate DRAM"""
	def __init__(self, configs, clock):
		self.configs = configs
		self.clock = clock
		self.dram = DRAM(self.clock, config.banks, config.rows, config.columns)
		self.memory_mapping = {}
		self.used_memory = []
		self.memory_size = self.dram.size_bytes()
		self.commands_queue = []
		self.scheduled_requests = []
		self.bus = MemoryBus(self.configs.bus_size, self.dram, self.clock)
		self.opened_rows = [0 for _ in size(self.configs.banks)]
		self.bank_status = [0 for _ in size(self.configs.banks)]
		self.clock.schedule(self.operate, None, run_time=1)

	def fcfs(self):
		# first come first serve scheduler
			# serve requests in the order they come
			# keep the row open after an operation
		if len(self.commands_queue) == 0 and len(self.scheduled_requests) == 0:
			return None

		for req in self.scheduled_requests:
			if len(req.commandseq) == 0:
				self.bank_status[req.bank] -= 1
				self.scheduled_requests.remove(req)

		if len(self.scheduled_requests) > 0:
			for req in self.scheduled_requests:
				if req.op_running == False:
					if req.commandseq[0][0] == "read" and self.bus.start_op(req):
						return self.bus.fetch, (req, req.read_callback), self.configs.read_time
					elif req.commandseq[0][0] == "write" and self.bus.start_op(req):
						return self.bus.write, (req, req.read_callback), self.configs.write_time
					elif req.commandseq[0][0] == "activate":
						return self.bus.open_row, (req, req.activate_callback), self.configs.activation_time

		if len(self.commands_queue) > 0:
			req = self.commands_queue[0]
			if req.row == self.opened_rows[req.bank] and self.bus.start_op(req):
				del req.commandseq[0]
				self.scheduled_requests.append(req)
				self.commands_queue.remove(req)
				self.bank_status[req.bank] += 1
				return self.bus.fetch, (req, req.read_callback), self.configs.read_time
			elif self.bank_status[req.bank] < 1:
				self.scheduled_requests.append(req)
				self.commands_queue.remove(req)
				self.bank_status[req.bank] += 1
				return self.bus.close_row, (req, req.precharge_callback), self.configs.precharge_time
		return None


	def operate(self):
		# refreshing done here

		# schedule commands
		task = self.fcfs()
		while task != None:
			command, args, runtime = task
			self.clock.schedule(command, args, run_time=runtime)
			task = self.fcfs()
		self.clock.schedule(self.operate, None, run_time=1)

	def malloc(self, user, size):
		# allocate memory
		address = 0x00000000
		return address

	def translate_address(self, address):
		# 16 bits for row, 3 bits for bank, 12 bits for column
		column = bitExtracted(address, 12, 1)
		bank = bitExtracted(address, 3, 13)
		row = bitExtracted(address, 16, 16)
		return bank, row, column

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
		
		