
files = ["baseline.log", "dramtrr.log", "ptrr.log", "refresh2x.log", "refresh3x.log", "para.log"]


def parse_file(filename):
	file = open(filename, "r")
	contents = file.read().split("\n")
	contents = [c for c in contents if "read callback" in c]
	latencies = [int(c.split(" ")[-1]) for c in contents]
	return latencies


for f in files:
	latencies = parse_file(f)
	latencies_sum = sum(latencies)
	size = len(latencies)
	average = latencies_sum / size
	latencies = sorted(latencies)
	print(f) 
	print ("Average: ", average)
	print ("Avg. 95th percentile onward: ",sum(latencies[int(len(latencies)*0.95):]), sum(latencies[int(len(latencies)*0.95):]) / (size*0.05))
	print ("Avg. 99th percentile onward: ", sum(latencies[int(len(latencies)*0.99):]), sum(latencies[int(len(latencies)*0.99):]) / (size*0.01))
	print ("Avg. 99.9th percentile onward: ", sum(latencies[int(len(latencies)*0.999):]), sum(latencies[int(len(latencies)*0.999):]) / (size*0.001))