import config as cfg
from simulate import Clock
from dram import DRAM
from controller import MemoryController
from program import Program

clock = Clock()
memory = MemoryController(cfg, clock)

def p1_read(commandseq, value):
	global clock
	print(clock.get_clock(), "read callback", commandseq, value)


# victim address: pick 3rd row
# row:00000011 bank:000 col:000001 = 601
v_addr = 0x0000601

# aggressor addresses: pick 2nd and 4th row
# row:00000010 bank:000 col:000001 = 401
ag_addr1 = 0x0000401
# row:00000100 bank:000 col:000001 = 801
ag_addr2 = 0x0000801
# victim program
print("Start")
program1 = Program(clock, memory, 1)
program1.cmd(program1.write, (v_addr, 25), 10)
program1.cmd(program1.read, (v_addr, p1_read), 50)
program1.cmd(program1.read, (v_addr, p1_read), 2999000)

#aggressor program
program2 = Program(clock, memory, 2)
program2.cmd(program2.write, (ag_addr1, 255), 20)
program2.cmd(program2.write, (ag_addr2, 128), 10)
program2.cmd(program2.read, (ag_addr1, None), 55, period = 80, repeat = 500)
program2.cmd(program2.read, (ag_addr2, None), 50, period = 80, repeat = 500)


clock.simulate(3000000)


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