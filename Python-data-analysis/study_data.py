# study_data.py
# Python module to extract properties of dataset obtained from travel_time.py
# Authored by Arthur J Delarue on 6/5/15

import numpy as np
import matplotlib.pyplot as plt

def get_histogram(inputFileName, bins):
	inputFile = open(inputFileName, "r")
	data = []
	for i, line in enumerate(inputFile):
		row = line.split(",")
		data.append(int(row[4]))
	bins = max(data) - min(data)
	return np.histogram(data, bins)

def plot_histogram(inputFileName, bins):
	plt.figure(1)
	hist, bin_edges = get_histogram(inputFileName, bins)
	center = (bin_edges[:-1] + bin_edges[1:]) / 2
	plt.bar(center, hist)
	plt.gca().set_xlim(right = 30)
	plt.show()

if __name__ == "__main__":
	#plot_histogram("travel_times_r100_wd_1214.csv", 1000)
	#plot_histogram("travel_times_r80_wd_1214.csv", 1000)
	plot_histogram("travel_times_r60_wd_1214.csv", 1000)