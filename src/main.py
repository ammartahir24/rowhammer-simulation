from simulate import Clock
from dram import DRAM


clock = Clock()
memory = DRAM(clock)

# start events here e.g. rowhammer code execution or row activation by queuing smth in clock
clock.schedule(memory.activate, (1,11), run_time=10)

simulation_time = 1000000

for _ in range(simulation_time):
	clock.tick_clock()