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

	def get_clock(self):
		return self.tick

	def tick_clock(self):
		for e in self.events:
			if e.scheduled_time == self.tick:
				print(self.tick, end=": ")
				if e.function_args == None:
					e.target_function()
				else:
					try: 
						if len(e.function_args) > 1:
							e.target_function(*e.function_args)
						else:
							e.target_function(e.function_args)
					except:
						e.target_function(e.function_args)
				self.events.remove(e)
			if e.scheduled_time > self.tick:
				break
		self.tick += 1