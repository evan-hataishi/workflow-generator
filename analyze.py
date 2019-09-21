import re
import sys
import statistics


def calculate_sequential_runtime(file):
	res = open(file, 'r').read()
	runtimes = re.findall('runtime=\"([-+]?\d*\.\d+|\d+)\"', res)
	# raw = [float(x) for x in runtimes]
	s = sum([float(x) for x in runtimes])
	target = int(file.split('_')[-1][:-4])
	print("tasks: %f, runtime: %f, difference: %f" % (len(runtimes), s, (abs(target-s))))
	# print("AVG: %f, Standard Deviation of sample is %s" % ((s / len(runtimes)), statistics.stdev(raw)))

def main(file):
	calculate_sequential_runtime(file)

if __name__ == '__main__':
	file = sys.argv[1]
	main(file)