import sys

file = open(sys.argv[1], "r")
contents = file.read().split("\n")
contents = [l.split(" ") for l in contents]
contents = [(int(l[3],0), int(l[4],0)) for l in contents]

contents = sorted(contents, key=lambda x:x[0])

def bitExtracted(number, k, p):
	return ( ((1 << k) - 1)  &  (number >> (p-1) ) )

# for c in contents:
# 	print(c)
total = 0
for i in range(int(len(contents)/8)):
	bitflips = 0
	for j in range(8):
		for k in range(8):
			if bitExtracted(contents[i*8+j][1], 1, k+1) == 0:
				bitflips += 1
	print(bitflips)
	total+=bitflips

print("Total", total-7)