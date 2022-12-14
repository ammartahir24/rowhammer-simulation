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
		if (self.V_s >= (cfg.VDD/2) + cfg.VDD*0.1):
			return 1
		elif (self.V_s <= (cfg.VDD/2) - cfg.VDD*0.1):
			return 0
		else: 
			return random.randrange(0,2)
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
		self.trr_samples = [[0, 0, 0, 0] for k in range(cfg.trr_samples)] # [bank, row, activations, last accessed]
		self.cm_table = [[[0 for k in range(cfg.count_min_size[1])] for j in range(cfg.count_min_size[0])] for i in range(self.num_banks)]
		#for analysis
		self.total_refreshes = 0
		print("DRAM __init__")

	def activate(self, bank, row):
		''' opens a row: transfers a row from bank to its row buffer'''
		# update row buffer for bank
		self.row_buffers[bank][0] = row
		#print("Activating bank, row: " + str(bank) + ", " + str(row))
		# update activation time as current time
		#print("DRAM Activate", bank, row)
		self.row_buffers[bank][1] = self.Clock.get_clock()
		#TODO switch updates to here instead of reads/writes
		for column in range(self.num_columns):
			#self.cells[bank][row][column].update_t_N()
			#if bank == 0 and row != 9 and row != 11 and row >=0 and row <= 21:
			#	print("Current charge for bank ", bank, " row ", row, "column ", column, " = ", self.cells[bank][row][column].V_s)
			self.cells[bank][row][column].update_V_s_leakage()
			#if bank == 0 and row != 9 and row != 11 and row >=0 and row <= 21:
			#	print("Later charge for bank ", bank, " row ", row, "column ", column, " = ", self.cells[bank][row][column].V_s)
			self.cells[bank][row][column].refresh()

		#if in-dram trr enabled, sample for aggressor activations
		if cfg.in_dram_trr == True:
			self.trr_check(bank, row)
		return

	def trr_hash_read(self, bank, row):
		min_count = 999999999
		for i in range(cfg.count_min_size[0]):
			index = (row + (2*i)) % cfg.count_min_size[1]
			if self.cm_table[bank][i][index] < min_count:
				min_count = self.cm_table[bank][i][index]
		return min_count

	def trr_hash_write(self, bank, row, incr):
		for i in range(cfg.count_min_size[0]):
			index = (row + (2*i)) % cfg.count_min_size[1]
			if incr:
				self.cm_table[bank][i][index] += 1
			else: 
				self.cm_table[bank][i][index] = 0

	def trr_check(self, bank, row):
		found = False
		found_ind = -1
		evict = 0
		min_count = 999999999
		for i in range(cfg.trr_samples):
			if self.trr_samples[i][0] == bank and self.trr_samples[i][1] == row:
				#print("Found activation count for bank ", bank, " row ", row, " value = ", self.trr_samples[i][2])
				self.trr_samples[i][2] = self.trr_samples[i][2]+1
				self.trr_samples[i][3] = self.Clock.get_clock()
				self.trr_hash_write(bank, row, True)
				found_ind = i
				found = True
			hash_count = self.trr_hash_read(self.trr_samples[i][0], self.trr_samples[i][1])
			#print("count ", hash_count, " row ", self.trr_samples[i][1])
			if hash_count < min_count:
				min_count = hash_count
				evict = i
		if found == False:
			#print("Starting sample for bank ", bank, " row ", row, " at ind ", evict, " old row was ", self.trr_samples[i][1])
			self.trr_samples[evict] = [bank, row, 1, self.Clock.get_clock()]
			#print(self.trr_samples)
			self.trr_hash_write(bank, row, True)
		
		return


	def size_bytes(self):
		return self.num_banks*self.num_columns*self.num_rows / 8

	def read(self, bank, column):
		''' read column from bank's row buffer'''
		row = self.row_buffers[bank][0]
		# read cell
		#print("DRAM READ", bank, row, column)
		value = self.cells[bank][row][column].read()
		# if (bank == 0 and row == 3 and column >=8 and column <= 15):
		# 	print("Reading cell " + str(bank) + " " + str(column) + " = " + str(self.cells[bank][row][column].V_s))
		return value

	def write(self, bank, column, value):
		''' write value to column of row bank'''
		row = self.row_buffers[bank][0]
		# print("Write cell bank ", bank, " row ", row, " column ", column, " = ", value)
		# write cell
		#print("DRAM WRITE", bank, row, column)
		self.cells[bank][row][column].write(value)
		
		return

	def precharge(self, bank):
		''' write back row buffer to appropriate row of the bank'''
		
		# restore cells in row buffer to full charge for current state (refresh cells)
		row = self.row_buffers[bank][0]
		# print("Precharging bank " + str(bank) + ", row " + str(row))
		#print(self.row_buffers[bank][0])
		#print("DRAM Precharge", bank, row)
		# update activation time as current time for current row buffer
		self.row_buffers[bank][2] = self.Clock.get_clock() - self.row_buffers[bank][1]
		activation_time = self.row_buffers[bank][2]
		# update aggressor activation time + aggressor activation toggle for n adjacent cells with some probability
		for i in range(-7, 7):
			row_vict = row + i
			if (i!=0 and row_vict >= 0 and row_vict < self.num_rows):
				
				row_dist = row_vict - row
				if (row_dist%2 == 1):
					probability_toggle = cfg.a*(cfg.b**(-(abs(row_dist))))
				else: 
					probability_toggle = 0
				#print("Toggle prob: " + str(probability_toggle), " row: " + str(row_vict))
				for column in range(self.num_columns):
					random_num = random.randrange(0, 100000) 
					if (random_num < (probability_toggle*100000/self.num_columns)):
						#print("Toggled cell ", row_vict, " ", column)
						#self.cells[bank][row_vict][column].N_att += 1
						#self.cells[bank][row_vict][column].B_tot = self.cells[bank][row_vict][column].B_tot + self.row_buffers[bank][2] 
						#print("before agg toggle: V_s = ", self.cells[bank][row_vict][column].V_s)
						#if (bank == 0 and row_vict < 22 and row_vict >= 0):
						#	print ("Before V_s for row", row_vict, " column ", column, " after toggle from row ", row, " with probability ", random_num, " out of ", (probability_toggle*100000/self.num_columns), " = ", self.cells[bank][row_vict][column].V_s)
						self.cells[bank][row_vict][column].update_V_s_agg(activation_time)
						#if (bank == 0 and row_vict < 22 and row_vict >= 0):
						#	print ("After V_s activation time ", activation_time, " for row ", row_vict, " column ", column, " after toggle from row ", row, " with probability ", random_num, " out of ", (probability_toggle*100000/self.num_columns), " = ", self.cells[bank][row_vict][column].V_s)
						#print("after agg toggle: V_s = ", self.cells[bank][row_vict][column].V_s)
						pass
		# remove row buffer from bank
		self.row_buffers[bank] = [None, 0, 0]
		
		return

	def refresh(self, bank, row):
		''' refresh all bank's row by activating and precharging it'''
		# activate and precharge row in all banks
		#print("Refreshing row", row, "of", bank, "bank")
		# for bank in range(self.num_banks):
		self.activate(bank, row)
		self.total_refreshes += 1
		if cfg.in_dram_trr:
			aggr = -1
			for i in range(cfg.trr_samples):
				if self.trr_samples[i][2] > cfg.maximum_activate_count:
					#print("Max ", max_count, " comparing ", self.trr_samples[i][2] )
					aggr = i
			#print(self.trr_samples)
			#print(aggr)
			if aggr != -1:		
				aggr_bank = self.trr_samples[aggr][0]
				aggr_row = self.trr_samples[aggr][1]
				self.target_row_refresh(aggr_bank, aggr_row)
				self.trr_hash_write(aggr_bank, aggr_row, False)
				self.trr_samples[aggr] = [0, 0, 0, 0]
			# self.precharge(bank)
		return

	def target_row_refresh(self, bank, row):
		''' refresh target row's neighbors by activating it'''
		# print("Target Refreshing row", row, "of", bank, "bank")
		#print("Target Refreshing row", row, "of", bank, "bank")
		#print(self.trr_samples)
		# for bank in range(self.num_banks):
		"""
		random_num = random.randrange(0, 1)
		if random_num == 1:
			if row-1 >= 0:
				self.activate(bank, row-1)
			else:
				self.activate(bank, row+1) 
		else:
			if row+1 < self.num_rows:
				self.activate(bank, row+1)
			else:
				self.activate(bank, row-1)
			# self.precharge(bank)
		"""
		if row-1 >= 0:
			self.activate(bank, row-1)
			self.total_refreshes += 1
		if row+1 < self.num_rows:
			self.activate(bank, row+1)
			self.total_refreshes += 1
		return