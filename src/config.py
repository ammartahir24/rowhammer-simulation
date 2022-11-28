'''
For all configurations e.g. refresh rate, scheduling algorithms, dram configs
'''

""" Cell parameters as defined in "Quantifying Rowhammer Vulnerability for DRAM Security" """

R_SW = 820000000            # Equivalent resistance of coupling leakage
R_L = 4800000000000000      # Equivalent resistance of intrinsic leakage
VDD = 1.2                   # Power supply voltage
C_S = .000000000000003      # Capacitance of the storage capacitor, could not find in any datasheets but some sources say 25-30 fF. units?

""" 
Activation probability params 

Cell aggressor activation toggled with probabilty 
y = a(e^-x),
where a is parameter used to adjust probability, x is the number of rows away from aggressor

y = 0 if x is even

"""

a = 0.45