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
		self.N_att = 0 # activations from adjacent aggressor row
		self.t_N = 0   # Interval between the successive accessing
		self.B_tot = 0     # aggressive activation interval
		self.A_tot = 0     # normal activation interval
		self.last_refresh = 0 # time of last refresh or activation
	def update_V_s(self):
		"""update voltage of storage capacitor, includes normal leakage and leakage due to aggressor activations"""
		B = self.B_tot / self.N_att
		self.A_tot = self.t_i - self.B_tot
		A = self.A_tot / (self.N_att+1)
		D = self.B_tot / (self.A_tot + self.B_tot)
		t_i = self.t_N / N_att
		self.V_s = cfg.VDD * math.exp(-(self.N_att/cfg.C_S)*((1/cfg.R_L)+(D/cfg.R_SW))*self.t_i) + ((cfg.VDD*cfg.R_L)/(2*(cfg.R_L+cfg.R_SW)) * (1 - math.exp(-(self.N_att/cfg.C_S)*((1/cfg.R_L)+(1/cfg.R_SW))*D*self.t_i)))
		# TODO might need to change to update voltage on every access instead of all at once
		return
	def update_t_N(self):
		""" update t_N which is total time since refresh or activation """
		self.t_N = self.Clock.get_clock() - self.last_refresh
		return
	def refresh(self):
		""" restore capacitor voltage """
		# reset aggressor activations
		self.N_att = 0
		# reset time intervals
		self.t_N = 0
		self.B_tot = 0
		self.A_tot = 0
		# reset voltage
		self.set_value(self.get_value)
		# update last refresh
		self.last_refresh = self.Clock.get_clock()
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
		return
	def get_value(self):
		""" return value interpreted by SA """
		if (self.V_s >= VDD/2 * C_S):
			return 1
		else:
			return 0
	def set_value(self, value):
		if (value == 1):
			self.V_s = VDD
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

	def activate(self, bank, row):
		''' opens a row: transfers a row from bank to its row buffer'''
		# update row buffer for bank
		self.row_buffers[bank][0] = row
		print("Activating bank, row: " + str(bank) + ", " + str(row))
		# update activation time as current time
		self.row_buffers[bank][1] = self.Clock.get_clock()
		#TODO switch updates to here instead of reads/writes
		for column in self.num_columns:
			self.cells[bank][row][column].update_t_N()
			self.cells[bank][row][column].update_V_s()
		return

	def read(self, bank, column):
		''' read column from bank's row buffer'''
		row = self.row_buffers[bank][0]
		# read cell
		value = self.cells[bank][row][column].read()
		print("Cell " + str(bank) + " " + str(column) + " = " + str(value))
		return value

	def write(self, bank, column, value):
		''' write value to column of row bank'''
		row = self.row_buffers[bank][0]
		# write cell
		self.cells[bank][row][column].write(value)
		return

	def precharge(self, bank, dummy):
		''' write back row buffer to appropriate row of the bank'''
		# restore cells in row buffer to full charge for current state (refresh cells)
		row = self.row_buffers[bank][0]
		#print(self.row_buffers[bank][0])
		for column in range(self.num_columns):
			#print(str(bank)+str(row)+str(column))
			self.cells[bank][row][column].refresh()
		# update activation time as current time for current row buffer
		self.row_buffers[bank][2] = self.Clock.get_clock() - self.row_buffers[bank][1]
		# update aggressor activation time + aggressor activation toggle for n adjacent cells with some probability
		for i in range(-7, 7):
			row_vict = row + i
			if (i!=0 and row_vict >= 0):
				random_num = random.randrange(0, 100) 
				row_dist = row_vict - row
				if (row_dist%2 == 1):
					probability_toggle = cfg.a*math.exp(-(row_dist))
				else: 
					probability_toggle = 0
				if (random_num < probability_toggle*100):
					for column in range(self.num_columns):
						self.cells[bank][row_vict][column].N_att += 1
						self.cells[bank][row_vict][column].B_tot = self.cells[bank][row_vict][column].B_tot + self.row_buffers[bank][2] 
		# remove row buffer from bank
		self.row_buffers[bank] = (None, 0, 0)
		return

	def refresh(self, row):
		''' refresh all bank's row by activating and precharging it'''
		# activate and precharge row in all banks
		for bank in range(num_banks):
			self.activate(bank, row)
			self.precharge(bank)
		return