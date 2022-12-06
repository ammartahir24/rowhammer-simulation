import config
from dram import DRAM
from simulate import Clock
from controller import MemoryController


class Event():
	def __init__(self, func, args, start_time, period, repeat):
		self.func = func
		self.args = args
		self.start = start_time
		self.repeat = repeat
		self.period = period
		self.i = 0

	def next(self, tick):
		if self.start + self.i*self.period <= tick:
			self.i += 1
			return self.func, self.args
		return None, None
		

class Program():
	def __init__(self, clock, memory, user):
		self.clock = clock
		self.memory = memory
		self.user = user
		self.events = []
		self.clock.schedule(self.operate, None, run_time=1)

	def cmd(self, func, args, start_time, period = 0, repeat = 1):
		event = Event(func, args, start_time, period, repeat)
		self.events.append(event)

	def operate(self):
		for e in self.events:
			func, args = e.next(self.clock.get_clock())
			if func != None:
				if self.user == 1:
					print("Program for", self.user, ":", func, args)
				self.clock.schedule(func, args, run_time=1)
			if e.i >= e.repeat:
				self.events.remove(e)
		self.clock.schedule(self.operate, None, run_time=1)

	def read(self, address, callback):
		self.memory.read(self.user, address, callback)

	def write(self, address, value):
		self.memory.write(self.user, address, value)

		