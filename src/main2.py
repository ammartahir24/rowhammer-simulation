import config as cfg
from simulate import Clock
from dram import DRAM
from controller import MemoryController
from program import Program

clock = Clock()
memory = MemoryController(cfg, clock)
log = open("read.log", "w")
def p1_read(commandseq, value):
	global clock, log
	log.write("%d read callback %x %b time taken (ns): %d", %(clock.get_clock(), hex(commandseq.address), bin(value), commandseq.completion_time - commandseq.arrival_time))
	print(clock.get_clock(), "read callback", hex(commandseq.address), bin(value), "time taken (ns):", commandseq.completion_time - commandseq.arrival_time)

def print_row_refreshes():
	global clock, memory, log
	print("Number of refreshes:", memory.dram.total_refreshes)
	log.close()

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

# program
print("Start")
program1 = Program(clock, memory, 1)
t = 0
for row_addr in r_addrs:
	addr = row_addr
	for column in range(2**(cfg.col_bits)):
		program1.cmd(program1.write, (addr, 255), 10+t*50)
		program1.cmd(program1.read, (addr, p1_read), 50+t*50, period = 8000, repeat=1000)
		t+=1
		addr = addr + 1

clock.schedule(print_row_refreshes, None, run_time=19999999)

clock.simulate(20000000)


