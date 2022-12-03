import config as cfg
from simulate import Clock
from dram import DRAM
from controller import MemoryController
from program import Program

clock = Clock()
memory = MemoryController(cfg, clock)

def p1_read(commandseq, value):
	print(commandseq, value)

# victim program
program1 = Program(clock, memory, 1)
program1.cmd(program1.write, (0x0000001, 255), 10)
program1.cmd(program1.read, (0x0000001, p1_read), 100000000)

#aggressor program
program2 = Program(clock, memory, 2)
program2.cmd(program2.read, (0x0000000, None), 10, period=10, repeat=50000)



# # start events here e.g. rowhammer code execution or row activation by queuing smth in clock
# #clock.schedule(memory.activate, (1,1), run_time=10)
# time = 0
# for j in range(30):
# 	time += cfg.activation_time
# 	#print(time, "activate", j)
# 	clock.schedule(memory.activate, (1,j), run_time=time)
# 	for i in range(30):
# 		time += cfg.write_time
# 		#print(time, "write", i)
# 		clock.schedule(memory.write, (1, i, 1), run_time=time)
# 	time += cfg.precharge_time
# 	#print(time, "precharge", j)
# 	clock.schedule(memory.precharge, (1), run_time=time)

# """
# time += .05 * (10**9)
# for j in range(10):
# 	time+= cfg.activation_time+cfg.precharge_time
# 	clock.schedule(memory.refresh, (j), run_time=time)
# time += .05 * (10**9)
# """
# print("Scheduling rowhammer.")
# for i in range(50000): 
# 	print(i)
# 	for j in range(10,20):
# 		time += cfg.activation_time
# 		#print(time, "activate", j)
# 		clock.schedule(memory.activate, (1,j), run_time=time)
# 		for i in range(30):
# 			time += cfg.write_time
# 			#print(time, "write", i)
# 			clock.schedule(memory.write, (1, i, 1), run_time=time)
# 		time += cfg.precharge_time
# 		#print(time, "precharge", j)
# 		clock.schedule(memory.precharge, (1), run_time=time)

# print("Scheduled rowhammer done.")
# for j in range(30):
# 	time += cfg.activation_time
# 	#print(time, "activate", j)
# 	clock.schedule(memory.activate, (1,j), run_time=time)
# 	for i in range(30):
# 		time += cfg.read_time
# 		#print(time, "read", i)
# 		clock.schedule(memory.read, (1, i), run_time=time)
# 	time += cfg.precharge_time
# 	#print(time, "precharge", j)
# 	clock.schedule(memory.precharge, (1), run_time=time)

# simulation_time = 200000000

# print("Start Clock")
# for i in range(simulation_time):
# 	if i%500:
# 		print(i)
# 	clock.tick_clock()