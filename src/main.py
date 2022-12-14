import config as cfg
from simulate import Clock
from dram import DRAM
from controller import MemoryController
from program import Program

clock = Clock()
memory = MemoryController(cfg, clock)

def p1_read(commandseq, value):
	global clock
	print(clock.get_clock(), "read callback", hex(commandseq.address), bin(value), "time taken (ns):", commandseq.completion_time - commandseq.arrival_time)

def print_row_refreshes():
	global clock, memory
	print("Number of refreshes:", memory.dram.total_refreshes)

# victim address: pick 10th row
# row:001010 bank:00 col:001 = 1401
v_addr = 0x0000140

# aggressor addresses: pick 9th and 11th row
# row:001001 bank:00 col:000 = 121
ag_addr1 = 0x0000120
# row:001011 bank:00 col:000 = 161
ag_addr2 = 0x0000160

ag_addr3 = 0x00001A0
ag_addr4 = 0x00000E0
ag_addr5 = 0x00001E0
ag_addr6 = 0x0000220
ag_addr7 = 0x00000A0

# surrounding addresses: rows 0-20
r_addrs = [0x0000000, 0x0000020, 0x0000040, 0x0000060, 0x0000080, 0x00000A0, 0x00000C0, 0x00000E0, 0x0000100, 0x0000120, 0x0000140, 0x0000160, 0x0000180, 0x00001A0, 0x00001C0, 0x00001E0, 0x0000200, 0x0000220, 0x0000240, 0x0000260, 0x0000280]

# victim program
print("Start")
program1 = Program(clock, memory, 1)
t = 0
for row_addr in r_addrs:
	addr = row_addr
	for column in range(2**(cfg.col_bits)):
		program1.cmd(program1.write, (addr, 255), 10+t*50)
		program1.cmd(program1.read, (addr, p1_read), 50+t*50)
		program1.cmd(program1.read, (addr, p1_read), 19900000+t*50)
		t+=1
		addr = addr + 1
#program1.cmd(program1.write, (v_addr, 255), 10)
#program1.cmd(program1.read, (v_addr, p1_read), 50)
#program1.cmd(program1.read, (v_addr, p1_read), 2999000)

#aggressor program
program2 = Program(clock, memory, 2)
program2.cmd(program2.write, (ag_addr1, 255), 20)
program2.cmd(program2.write, (ag_addr2, 255), 10)
program2.cmd(program2.read, (ag_addr1, None), 20000, period = 80, repeat = 50000)
program2.cmd(program2.read, (ag_addr2, None), 20050, period = 80, repeat = 50000)
#program2.cmd(program2.read, (ag_addr3, None), 60, period = 80, repeat = 20000)
#program2.cmd(program2.read, (ag_addr4, None), 65, period = 80, repeat = 20000)
#program2.cmd(program2.read, (ag_addr5, None), 70, period = 80, repeat = 20000)
#program2.cmd(program2.read, (ag_addr6, None), 75, period = 80, repeat = 20000)
#program2.cmd(program2.read, (ag_addr7, None), 80, period = 80, repeat = 20000)

clock.schedule(print_row_refreshes, None, run_time=19000000)

clock.simulate(20000000)


"""

# victim address: pick 3rd row
# row:00000011 bank:000 col:000001 = 601
v_addr = 0x000060

# aggressor addresses: pick 2nd and 4th row
# row:00000010 bank:000 col:000001 = 401
ag_addr1 = 0x000040
# row:00000100 bank:000 col:000001 = 801
ag_addr2 = 0x000080
# victim program
print("Start")
program1 = Program(clock, memory, 1)
for column in range(2**(cfg.col_bits)):
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

"""

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