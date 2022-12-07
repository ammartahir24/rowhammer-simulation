'''
For all configurations e.g. refresh rate, scheduling algorithms, dram configs
'''

""" Cell parameters as defined in "Quantifying Rowhammer Vulnerability for DRAM Security" """

R_SW = 40000000            # Equivalent resistance of coupling leakage
R_L = 4000000000000           # Equivalent resistance of intrinsic leakage
VDD = 1.2                   # Power supply voltage
C_S = .00000000000003      # Capacitance of the storage capacitor, could not find in any datasheets but some sources say 25-30 fF. units?

""" 
Activation probability params 

Cell aggressor activation toggled with probabilty 
y = a(e^-x),
where a is parameter used to adjust probability, x is the number of rows away from aggressor

y = 0 if x is even

"""

a = .3
b = 3

""" DRAM timing parameters (ns) """

activation_time = 37.5
read_time = 15
write_time = 11.25
precharge_time = 15

""" DRAM Parameters """

bank_bits = 3
row_bits = 8
col_bits = 6

banks = 2**bank_bits
rows = 2**row_bits
columns = 2**col_bits
cells = 8 #bits

""" Memory controller params"""
bus_size = 8 #bytes
refresh_freq = 6400000
