# travel_time.py
# Some functions to extract travel times between nodes from taxi data
# Assumes taxi data has been preprocessed by get_manhattan_rides()
# Created 6/1/15 by Arthur J Delarue

from scipy.spatial import KDTree
import math
import numpy as np

def point_within_radius(point, center, radius):
	x,y = point
	x0,y0 = center
	return (math.sqrt((x-x0) ** 2 + (y-y0) ** 2) < radius)

def extract_sample(bottom=40.80750782222972, top=40.81972031701224, right=-73.9380, left=-73.9465):
	# From large dataset, extract small GPS square (where all pickups/dropoffs occur)
	inputFile = open("manhattan_rides.csv", "r")
	outputFile = open("manhattan_rides_sample.csv", "w")
	for line in inputFile:
		row = line.split(",")
		x = float(row[1])
		y = float(row[2])
		if left < x and x < right and bottom < y and y < top:
			outputFile.write(line)
	outputFile.close()
	inputFile.close()
	return None

test_point = (-73.9422, 40.8121)

def get_rides(point):
	# Loops through CSV file to find all pickups/dropoffs within radius R of the target point
	R = 80.0 # meters
	f = open("manhattan_rides_sample.csv")
	pickups = []
	dropoffs = []
	# Loop through file
	for i, line in enumerate(f):
		row = line.split(",")
		pickup = (float(row[1]), float(row[2]))
		dropoff = (float(row[3]), float(row[4]))
		if point_within_radius(pickup, test_point, R * 180/(math.pi * 6400000)):
			pickups.append(i)
		if point_within_radius(dropoff, test_point, R * 180/(math.pi * 6400000)):
			dropoffs.append(i)
	f.close()
	# print "Number of pickups: " + str(len(pickups))
	# print "Number of dropoffs: " + str(len(dropoffs))
	# print pickups
	# print dropoffs
	return pickups, dropoffs

def find_all_rides(pickups, dropoffs, nodes, radius=0):
	if radius == 0:
		R = 80.0 # meters
		real_R = R * 180/(math.pi * 6400000)
	else:
		real_R = radius
	# Build KDTrees
	pTree = KDTree(pickups)
	dTree = KDTree(dropoffs)
	nTree = KDTree(nodes)
	# Find pickups and dropoffs close to each node
	pickups = nTree.query_ball_tree(pTree, real_R)
	dropoffs = nTree.query_ball_tree(dTree, real_R)
	# Initialize dictionary where we store rides between each pair of nodes
	nodePairs = {}
	for i in range(len(nodes)):
		for j in range(len(nodes)):
			if i != j:
				# Rides from i to j are the intersection of pickups[i] and dropoffs[j]
				nodePairs[(i, j)] = [val for val in pickups[i] if val in dropoffs[j]]
	return nodePairs

def get_rides_fast():
	# Toy example
	if False:
		nodes = np.array([[2,2],[4,0],[4,4]])
		pickups = np.array([[2,3],[2,3],[2,2.5],[1.5,2],[2,1.5]])
		dropoffs = np.array([[4,3],[4,1],[4,0.5],[4.5,0],[4., 3.5]])
		result = find_all_rides(pickups, dropoffs, nodes, 1.25)
	else: # Actual code
		f = open("manhattan_rides_sample.csv")
		pickup_list = []
		dropoff_list = []
		for line in f:
			row = line.split(",")
			pickup_list.append([float(row[1]), float(row[2])])
			dropoff_list.append([float(row[3]), float(row[4])])
		f.close()
		pickups = np.array(pickup_list)
		dropoffs = np.array(dropoff_list)
		nodes = [[-73.9422, 40.8121],[-73.9475, 40.8103]]
		result = find_all_rides(pickups, dropoffs, nodes)
	print result
	return None

if __name__ == "__main__":
	get_rides_fast()