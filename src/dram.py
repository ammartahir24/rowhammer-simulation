'''
dram operations
'''
import math
import random
import config as cfg

class Cell():
	"""Cell based on cell params"""
	def __init__(self, clock):
		self.Clock = clock
		self.V_s = 0
		#self.N_att = 1 # activations from adjacent aggressor row
		#self.t_N = 0   # Interval between the successive accessing
		#self.B_tot = 0     # aggressive activation interval
		#self.A_tot = 0     # normal activation interval
		self.last_refresh = 0 # time of last refresh or activation
		self.last_leakage_update = 0
	def update_V_s_leakage(self):
		"""update voltage of storage capacitor, includes normal leakage"""
		
		normal_time = self.update_t_N()
		#print("Leakage time: ", normal_time)
		#print("V_s = ", self.V_s, "coeff = ", math.exp(-normal_time*(10**-9)/(cfg.R_L*cfg.C_S)))
		self.V_s = self.V_s * math.exp(-normal_time*(10**-9)/(cfg.R_L*cfg.C_S))
		#print("V_s = ", self.V_s, "coeff = ", math.exp(-normal_time*(10**-9)/(cfg.R_L*cfg.C_S)))
		#self.V_s = cfg.VDD * math.exp(-(self.N_att/cfg.C_S)*((1/cfg.R_L)+(D/cfg.R_SW))*t_i) + ((cfg.VDD*cfg.R_L)/(2*(cfg.R_L+cfg.R_SW)) * (1 - math.exp(-(self.N_att/cfg.C_S)*((1/cfg.R_L)+(1/cfg.R_SW))*D*t_i)))
		# TODO might need to change to update voltage on every access instead of all at once
		return
	def update_V_s_agg(self, activation_time):
		"""update voltage of storage capacitor, includes normal leakage and aggressor toggle leakage"""
		#print("V_s before agg: ", self.V_s)
		self.update_V_s_leakage()
		multiplier = math.exp(-((1/cfg.C_S)*((1/cfg.R_L)+(1/cfg.R_SW)))*activation_time*(10**-9))
		adder = ((cfg.VDD*cfg.R_L)/(2*(cfg.R_L+cfg.R_SW)))*(1-math.exp(-((1/cfg.C_S)*((1/cfg.R_L)+(1/cfg.R_SW)))*activation_time*(10**-9)))
		self.V_s = self.V_s*multiplier + adder
		#print("V_s after agg: ", self.V_s)
		return
	def update_t_N(self):
		""" update t_N which is total time since refresh or activation """
		time = self.Clock.get_clock() - self.last_leakage_update
		self.last_leakage_update = self.Clock.get_clock()
		return time
	def refresh(self):
		""" restore capacitor voltage """
		# reset aggressor activations
		#self.N_att = 1
		# reset time intervals
		#self.t_N = 0
		#self.B_tot = 0
		#self.A_tot = 0
		# reset voltage
		current_val = self.get_value()
		self.set_value(current_val)
		# update last refresh
		self.last_refresh = self.Clock.get_clock()
		self.last_leakage_update = self.Clock.get_clock()
		return
	def read(self):
		""" return value based on stored voltage """
		# update cell's leakage  
		value = self.get_value()
		return value
	def write(self, value):
		""" write voltage to cell """
		# update cell's leakage
		self.set_value(value)
		# print("V_s = ", self.V_s)
		return
	def get_value(self):
		""" return value interpreted by SA """
		if (self.V_s >= cfg.VDD/2):
			return 1
		else:
			return 0
	def set_value(self, value):
		if (value == 1):
			self.V_s = cfg.VDD
		else: 
			self.V_s = 0


class DRAM():
	"""DRAM simulation based on DDR4"""
	def __init__(self, clock, num_banks, num_columns, num_rows):
		self.Clock = clock
		self.num_banks = num_banks
		self.num_columns = num_columns
		self.num_rows = num_rows
		self.num_cells = num_banks*num_columns*num_rows
		self.cells = [[[Cell(self.Clock) for k in range(num_columns)] for j in range(num_rows)] for i in range(num_banks)]
		self.row_buffers = [[None, 0, 0] for k in range(num_banks)] # (Row number, activation time, activation time interval)
		print("DRAM __init__")

	def activate(self, bank, row):
		''' opens a row: transfers a row from bank to its row buffer'''
		# update row buffer for bank
		self.row_buffers[bank][0] = row
		# print("Activating bank, row: " + str(bank) + ", " + str(row))
		# update activation time as current time
		print("DRAM Activate", bank, row)
		self.row_buffers[bank][1] = self.Clock.get_clock()
		#TODO switch updates to here instead of reads/writes
		for column in range(self.num_columns):
			#self.cells[bank][row][column].update_t_N()
			#print("Current charge for bank ", bank, " row ", row, " = ", self.cells[bank][row][column].V_s)
			self.cells[bank][row][column].update_V_s_leakage()
		return

	def size_bytes(self):
		return self.num_banks*self.num_columns*self.num_rows / 8

	def read(self, bank, column):
		''' read column from bank's row buffer'''
		row = self.row_buffers[bank][0]
		# read cell
		print("DRAM READ", bank, row, column)
		value = self.cells[bank][row][column].read()
		# print("Reading cell " + str(bank) + " " + str(column) + " = " + str(value))
		return value

	def write(self, bank, column, value):
		''' write value to column of row bank'''
		row = self.row_buffers[bank][0]
		# write cell
		print("DRAM WRITE", bank, row, column)
		self.cells[bank][row][column].write(value)
		# print("Write cell " + str(bank) + " " + str(column) + " = " + str(value))
		return

	def precharge(self, bank):
		''' write back row buffer to appropriate row of the bank'''
		
		# restore cells in row buffer to full charge for current state (refresh cells)
		row = self.row_buffers[bank][0]
		# print("Precharging bank " + str(bank) + ", row " + str(row))
		#print(self.row_buffers[bank][0])
		print("DRAM Precharge", bank, row)
		for column in range(self.num_columns):
			#print(str(bank)+str(row)+str(column))
			#print("1Current charge for bank ", bank, " row ", row, " = ", self.cells[bank][row][column].V_s)
			self.cells[bank][row][column].refresh()
			#print("2Current charge for bank ", bank, " row ", row, " = ", self.cells[bank][row][column].V_s)
		# update activation time as current time for current row buffer
		self.row_buffers[bank][2] = self.Clock.get_clock() - self.row_buffers[bank][1]
		activation_time = self.row_buffers[bank][2]
		# update aggressor activation time + aggressor activation toggle for n adjacent cells with some probability
		for i in range(-7, 7):
			row_vict = row + i
			if (i!=0 and row_vict >= 0 and row_vict < self.num_rows):
				
				row_dist = row_vict - row
				if (row_dist%2 == 1):
					probability_toggle = cfg.a*math.exp(-(abs(row_dist)))
				else: 
					probability_toggle = 0
				#print("Toggle prob: " + str(probability_toggle), " row: " + str(row_vict))
				for column in range(self.num_columns):
					random_num = random.randrange(0, 100) 
					if (random_num < probability_toggle*100):
						#print("Toggled cell ", row_vict, " ", column)
						#self.cells[bank][row_vict][column].N_att += 1
						#self.cells[bank][row_vict][column].B_tot = self.cells[bank][row_vict][column].B_tot + self.row_buffers[bank][2] 
						#print("before agg toggle: V_s = ", self.cells[bank][row_vict][column].V_s)
						self.cells[bank][row_vict][column].update_V_s_agg(activation_time)
						#print("after agg toggle: V_s = ", self.cells[bank][row_vict][column].V_s)
						pass
		# remove row buffer from bank
		self.row_buffers[bank] = [None, 0, 0]
		
		return

	def refresh(self, row):
		''' refresh all bank's row by activating and precharging it'''
		# activate and precharge row in all banks
		print("Refreshing row " + str(row))
		for bank in range(self.num_banks):
			self.activate(bank, row)
			self.precharge(bank)
		return