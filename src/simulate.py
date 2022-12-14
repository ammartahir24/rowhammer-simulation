''' 
simulates the clock 
'''

class Event():
	def __init__(self, time, func, args):
		self.scheduled_time = time
		self.target_function = func
		self.function_args = args

class Clock():
	"""simulates the clock, read current clock value and schedule events"""
	def __init__(self):
		# clock value in nanoseconds
		self.tick = 0
		# list of all scheduled events, each event is a tuple of clock value for when event completes, function, and args
		self.events = []
		print("Clock __init__")

	def schedule(self, func, args, run_time=0, end_time=None):
		time = run_time + self.tick
		if end_time != None:
			time = end_time
		index = 0
		while (index < len(self.events)):
			if self.events[index].scheduled_time > time:
				break
			index += 1
		self.events.insert(index, Event(time, func, args))
		# print("New events now", self.tick, [(e.scheduled_time, e.target_function) for e in self.events])

	def get_clock(self):
		return self.tick

	def get_seconds(self):
		return self.tick * (10**-9)

	def tick_clock(self):
		# print("Scheduled events now", self.tick, [(e.scheduled_time, e.target_function) for e in self.events])
		if self.tick % 100000 == 0:
			print(self.tick, ": events in queue", len([(e.scheduled_time, e.target_function) for e in self.events]))
		temp_events = [e for e in self.events]
		for e in temp_events:
			if e.scheduled_time <= self.tick:
				# print(self.tick, end=": ")
				# print(e.target_function, e.function_args)
				if e.function_args == None:
					e.target_function()
				else:
					if len(e.function_args) > 1:
						e.target_function(*e.function_args)
					else:
						e.target_function(e.function_args)
				self.events.remove(e)
			else:
				# print(self.tick, end=": Stopping tick: ")
				# print(e.target_function, e.function_args, e.scheduled_time)
				break
		# print("Unscheduled events now", self.tick, [(e.scheduled_time, e.target_function) for e in self.events])
		self.tick += 1

	def simulate(self, simul_time):
		for i in range(simul_time):
			self.tick_clock()