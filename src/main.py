import config as cfg
from simulate import Clock
from dram import DRAM

clock = Clock()
memory = DRAM(clock, 2, 20, 20)

# start events here e.g. rowhammer code execution or row activation by queuing smth in clock
#clock.schedule(memory.activate, (1,1), run_time=10)
time = 0
for j in range(10):
	time += cfg.activation_time
	print(time, "activate", j)
	clock.schedule(memory.activate, (1,j), run_time=time)
	for i in range(10):
		time += cfg.write_time
		print(time, "write", i)
		clock.schedule(memory.write, (1, i, 1), run_time=time)
	time += cfg.precharge_time
	print(time, "precharge", j)
	clock.schedule(memory.precharge, (1), run_time=time)

for j in range(10):
	time += cfg.activation_time
	print(time, "activate", j)
	clock.schedule(memory.activate, (1,j), run_time=time)
	for i in range(10):
		time += cfg.read_time
		print(time, "write", i)
		clock.schedule(memory.read, (1, i), run_time=time)
	time += cfg.precharge_time
	print(time, "precharge", j)
	clock.schedule(memory.precharge, (1), run_time=time)

simulation_time = 1000000

print("Start Clock")
for _ in range(simulation_time):
	clock.tick_clock()