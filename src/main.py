import config as cfg
from simulate import Clock
from dram import DRAM
from controller import MemoryController
from program import Program

clock = Clock()
memory = MemoryController(cfg, clock)

def p1_read(commandseq, value):
	global clock
	print(clock.get_clock(), "read callback", commandseq, bin(value))

"""
# victim address: pick 10th row
# row:00001010 bank:000 col:000001 = 1401
v_addr = 0x0001400

# aggressor addresses: pick 9th and 11th row
# row:00001001 bank:000 col:000001 = 1201
ag_addr1 = 0x0001200
# row:00001011 bank:000 col:000001 = 1601
ag_addr2 = 0x0001600

# surrounding addresses: rows 0-20
r_addrs = [0x0000000, 0x0000200, 0x0000400, 0x0000600, 0x0000800, 0x0000A00, 0x0000C00, 0x0000E00, 0x0001000, 0x0001200, 0x0001400, 0x0001600, 0x0001800, 0x0001A00, 0x0001C00, 0x0001E00, 0x0002000, 0x0002200, 0x0002400, 0x0002600, 0x0002800]

# victim program
print("Start")
program1 = Program(clock, memory, 1)
for row_addr in r_addrs:
	addr = row_addr
	for column in range(2**(cfg.col_bits-3)):
		program1.cmd(program1.write, (addr, 255), 10)
		program1.cmd(program1.read, (addr, p1_read), 50)
		program1.cmd(program1.read, (addr, p1_read), 19900000)
		addr = addr + 1
#program1.cmd(program1.write, (v_addr, 255), 10)
#program1.cmd(program1.read, (v_addr, p1_read), 50)
#program1.cmd(program1.read, (v_addr, p1_read), 2999000)

#aggressor program
program2 = Program(clock, memory, 2)
program2.cmd(program2.write, (ag_addr1, 255), 20)
program2.cmd(program2.write, (ag_addr2, 128), 10)
program2.cmd(program2.read, (ag_addr1, None), 55, period = 80, repeat = 50000)
program2.cmd(program2.read, (ag_addr2, None), 50, period = 80, repeat = 50000)


clock.simulate(20000000)
"""

# victim address: pick 3rd row
# row:00000011 bank:000 col:000001 = 601
v_addr = 0x0000600

# aggressor addresses: pick 2nd and 4th row
# row:00000010 bank:000 col:000001 = 401
ag_addr1 = 0x0000400
# row:00000100 bank:000 col:000001 = 801
ag_addr2 = 0x0000800
# victim program
print("Start")
program1 = Program(clock, memory, 1)
for column in range(2**(cfg.col_bits-3)):
	program1.cmd(program1.write, (v_addr, 255), 10)
	program1.cmd(program1.read, (v_addr, p1_read), 50)
	program1.cmd(program1.read, (v_addr, p1_read), 9900000)
	v_addr = v_addr + 1

#aggressor program
program2 = Program(clock, memory, 2)
program2.cmd(program2.write, (ag_addr1, 255), 20)
program2.cmd(program2.write, (ag_addr2, 128), 10)
program2.cmd(program2.read, (ag_addr1, None), 55, period = 80, repeat = 50000)
program2.cmd(program2.read, (ag_addr2, None), 50, period = 80, repeat = 50000)


clock.simulate(10000000)


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