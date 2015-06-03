# stats.py
# Some basic statistical functions
# Authored 6/2/15 by Arthur J Delarue

import math

def avg(input_list):
	if len(input_list) > 0:
		return sum(input_list)/len(input_list)
	else:
		return 0.0

def var(input_list):
	if len(input_list) < 2:
		return 0.0
	mean = avg(input_list)
	var = 0
	for element in input_list:
		var += (element - mean) ** 2
	var = float(var) / (len(input_list) - 1)
	return var

def stddev(input_list):
	return math.sqrt(var(input_list))

def stderr(input_list):
	if len(input_list) > 0:
		return stddev(input_list)/math.sqrt(len(input_list))
	else:
		return 0.0