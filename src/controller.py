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
		print(commandseq)
		self.occupancy -= 1
		value = 0
		for i in range(8):
			if i==0:
				value += self.dram.read(commandseq.bank, 8*commandseq.column+i)
			else:
				value += (2*self.dram.read(commandseq.bank, 8*commandseq.column+i))**i
		commandseq.completion_time = self.clock.get_clock()
		commandseq.op_running = False
		if callback != None:
			callback(commandseq, value)

	def write(self, commandseq, callback):
		self.occupancy -= 1
		value = commandseq.value
		for i in range(8):
			val = bitExtracted(value, 1, i+1)
			self.dram.write(commandseq.bank, 8*commandseq.column+i, val)
		commandseq.completion_time = self.clock.get_clock()
		commandseq.op_running = False
		if callback != None:
			callback(commandseq, value)

	def open_row(self, commandseq, callback):
		self.dram.activate(commandseq.bank, commandseq.row)
		commandseq.op_running = False
		if callback != None:
			callback(commandseq, value)

	def close_row(self, commandseq, callback):
		self.dram.precharge(commandseq.bank)
		commandseq.op_running = False
		if callback != None:
			callback(commandseq, value)


class CommandSequence():
	def __init__(self, timestamp, callback=None):
		self.commandseq = []
		self.callback = callback
		self.arrival_time = timestamp
		self.next_op_time = 0
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
		self.opened_rows = [0 for _ in range(self.configs.banks)]
		for i in range(self.configs.banks):
			self.dram.activate(i,0)
		self.bank_status = [0 for _ in range(self.configs.banks)]
		self.clock.schedule(self.operate, None, run_time=1)
		print("MemoryController __init__")

	def fcfs(self):
		# first come first serve scheduler
			# serve requests in the order they come
			# keep the row open after an operation
		if len(self.commands_queue) == 0 and len(self.scheduled_requests) == 0:
			return None

		# for req in self.scheduled_requests:
		# 	if len(req.commandseq) == 0:
		# 		self.bank_status[req.bank] -= 1
		# 		self.scheduled_requests.remove(req)

		if len(self.scheduled_requests) > 0:
			for req in self.scheduled_requests:
				if req.op_running == False:
					if req.commandseq[0][0] == "read" and self.bus.start_op(req):
						req.next_op_time = self.configs.read_time
						req.op_running = True
						del req.commandseq[0]
						return self.bus.fetch, (req, req.callback), req.next_op_time 
					elif req.commandseq[0][0] == "write" and self.bus.start_op(req):
						req.next_op_time = self.configs.write_time
						req.op_running = True
						del req.commandseq[0]
						return self.bus.write, (req, None), req.next_op_time
					elif req.commandseq[0][0] == "activate":
						req.next_op_time = self.configs.activation_time
						req.op_running = True
						del req.commandseq[0]
						return self.bus.open_row, (req, None), req.next_op_time
					elif req.commandseq[0][0] == "precharge":
						del req.commandseq[0]
						self.bank_status[req.bank] -= 1
						self.scheduled_requests.remove(req)

		if len(self.commands_queue) > 0:
			req = self.commands_queue[0]
			# print(req.commandseq)
			if req.row == self.opened_rows[req.bank] and self.bus.start_op(req):
				print("row is open", req.commandseq)
				if req.commandseq[0][0] == "activate":
					del req.commandseq[0]
				if req.commandseq[0][0] == "read":
					del req.commandseq[0]
					self.scheduled_requests.append(req)
					self.commands_queue.remove(req)
					self.bank_status[req.bank] += 1
					req.next_op_time = self.configs.read_time
					req.op_running = True
					return self.bus.fetch, (req, req.callback), req.next_op_time
				elif req.commandseq[0][0] == "write":
					del req.commandseq[0]
					self.scheduled_requests.append(req)
					self.commands_queue.remove(req)
					self.bank_status[req.bank] += 1
					req.next_op_time = self.configs.write_time
					req.op_running = True
					return self.bus.write, (req, None), req.next_op_time
			elif self.bank_status[req.bank] < 1:
				print("row is closed", req.commandseq, self.bank_status[req.bank])
				self.scheduled_requests.append(req)
				self.commands_queue.remove(req)
				self.bank_status[req.bank] += 1
				req.next_op_time = self.configs.precharge_time
				req.op_running = True
				return self.bus.close_row, (req, None), req.next_op_time
		return None


	def operate(self):
		# refreshing done here

		# schedule commands
		task = self.fcfs()
		while task != None:
			command, args, runtime = task
			print("MemoryController: ", self.clock.get_clock(), command, args, runtime)
			self.clock.schedule(command, args, run_time=runtime)
			task = self.fcfs()
		self.clock.schedule(self.operate, None, run_time=1)

	def malloc(self, user, size):
		# allocate memory
		address = 0x00000000
		return address

	def translate_address(self, address):
		# self.config.row_bits bits for row, self.config.bank_bits bits for bank, self.config.col_bits bits for column
		column = bitExtracted(address, self.configs.col_bits, 1)
		bank = bitExtracted(address, self.configs.bank_bits, 1+self.configs.col_bits)
		row = bitExtracted(address, self.configs.row_bits, 1+self.configs.col_bits+self.configs.bank_bits)
		return bank, row, column

	def read(self, user, address, callback):
		# address translation to physical address to bank, row tuple
		# checks about security etc.
		bank, row, column = self.translate_address(address)
		print("read", user, bank, row, column)
		commands = CommandSequence(self.clock.get_clock(), callback=callback)
		commands.read_sequence(bank, row, column)
		self.commands_queue.append(commands)

	def write(self, user, address, value):
		# address translation to physical address to bank, row tuple
		# checks about security etc.
		bank, row, column = self.translate_address(address)
		print("write", user, bank, row, column)
		commands = CommandSequence(self.clock.get_clock())
		commands.write_sequence(bank, row, column, value)
		self.commands_queue.append(commands) 
		
		