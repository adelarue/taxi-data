# travel_time.py
# Some functions to extract travel times between nodes from taxi data
# Assumes taxi data has been preprocessed by get_manhattan_rides()
# Created 6/1/15 by Arthur J Delarue

from scipy.spatial import cKDTree
import math
import numpy as np
from conversions import LL0_to_ENUm
import sys
from stats import avg, stddev, stderr

def point_within_radius(point, center, radius): # deprecated
	x,y = point
	x0,y0 = center
	return (math.sqrt((x-x0) ** 2 + (y-y0) ** 2) < radius)

test_point = (-73.9422, 40.8121)

def get_rides(point): # deprecated
	# Loops through CSV file to find all pickups/dropoffs within radius R of the target point
	R = 80.0 # meters
	f = open("manhattan_rides_sample.csv")
	pickups = []
	dropoffs = []
	# Loop through file (brute-force)
	for i, line in enumerate(f):
		row = line.split(",")
		pickup = (float(row[1]), float(row[2]))
		dropoff = (float(row[3]), float(row[4]))
		if point_within_radius(pickup, test_point, R * 180/(math.pi * 6400000)):
			pickups.append(i)
		if point_within_radius(dropoff, test_point, R * 180/(math.pi * 6400000)):
			dropoffs.append(i)
	f.close()
	return pickups, dropoffs

def test():
	nodes = np.array([[2,2],[4,0],[4,4]])
	pickups = np.array([[2,3],[2,3],[2,2.5],[1.5,2],[2,1.5]])
	dropoffs = np.array([[4,3],[4,1],[4,0.5],[4.5,0],[4, 3.5]])
	times = [0,1,2,3,4]
	result = find_all_times_faster(pickups, dropoffs, times, nodes, 1.25)
	print result

def find_all_times(pickups, dropoffs, time_list, nodes, radius=0):
	'''
	For each pair of nodes, finds the travel times of all rides with a pickup within
	radius R of the first node, and a dropoff within radius R of the second node.
	Uses KDTrees for speed (hopefully fast).
	'''
	MIN_RIDES = 4
	if radius == 0:
		real_R = 100.0 # meters
	else:
		real_R = radius
	# Build KDTrees
	print "**** Building KDTrees ****"
	pTree = cKDTree(pickups)
	dTree = cKDTree(dropoffs)
	nTree = cKDTree(np.array(nodes))
	print "**** Querying KDTrees ****"
	# Find pickups and dropoffs close to each node
	pickups = nTree.query_ball_tree(pTree, real_R)
	dropoffs = nTree.query_ball_tree(dTree, real_R)
	print "**** Finding travel times ****"
	# Initialize dictionary where we store rides between each pair of nodes
	nodePairs = {}
	# First loop
	length = len(nodes)
	for i in xrange(length):
		# progress bar code
		if i % 100 == 0:
			progress = 100.0*i/len(nodes)
			if i > 0:
				sys.stdout.write('\r')
			sys.stdout.write("Progress: " + "%.02f" % progress + "%" + " completed.")
			sys.stdout.flush()
		tmp_pickups = set(pickups[i])
		tmp_length = len(pickups[i])
		# Second loop
		for j in xrange(length):
			if i != j and tmp_length >= MIN_RIDES and len(dropoffs[j]) >= MIN_RIDES:
				# Rides from i to j are the intersection of pickups[i] and dropoffs[j]
				intersection = tmp_pickups.intersection(set(dropoffs[j]))
				if len(intersection) >= MIN_RIDES:
					nodePairs[(i, j)] = [time_list[val] for val in intersection]
	sys.stdout.write("\rProgress: " + "%.01f" % 100.0 + "%" + " completed.\n")
	sys.stdout.flush()
	return nodePairs

def get_rides_fast():
	'''
	Extracts rides and nodes from appropriate files
	'''
	# Open input file with rides
	fileName = "manhattan_rides.csv"
	rideFile = open(fileName, "r")
	print "**** Reading ride file ****"
	pickup_list = []
	dropoff_list = []
	travel_time_list = []
	# Extract all rides, put them in appropriate lists
	for i, line in enumerate(rideFile):
		row = line.split(",")
		pickup_list.append( list( LL0_to_ENUm( (float(row[2]), float(row[1])))))
		dropoff_list.append( list( LL0_to_ENUm( (float(row[4]), float(row[3])))))
		travel_time_list.append(float(row[0]))
		# Progress bar code
		if fileName == "manhattan_rides.csv":
			if i % 100000 == 0:
				progress = 100.0*i/13296074
				if progress > 1:
					break
				if i > 0:
					sys.stdout.write('\r')
				sys.stdout.write("Progress: " + "%.02f" % progress + "%" + " completed.")
				sys.stdout.flush()
	sys.stdout.write('\n')
	rideFile.close()
	pickups = np.array(pickup_list)
	dropoffs = np.array(dropoff_list)
	nodeFile = open("nodesENU.csv", "r")
	print "**** Reading node file ****"
	nodes = []
	for i, line in enumerate(nodeFile):
		if i == 0:
			continue # skip first line
		node = line.replace('"', '').split(",")
		nodes.append([float(node[0]), float(node[1])])
	nodeFile.close()
	return find_all_times(pickups, dropoffs, travel_time_list, nodes)

def write_travel_times(fileName="output.csv"):
	outputFile = open(fileName, "w")
	result = get_rides_fastest()
	for key in result.keys():
		outputFile.write(str(key[0]) + ";" + str(key[1]) + ",")
		outputFile.write("%.02f" % avg(result[key]) + "," + "%.02f" % stddev(result[key]) + "," + "%.02f" % stderr(result[key]) + "," + str(len(result[key])))
		# outputFile.write(",")
		# outputFile.write(",".join([str(element) for element in result[key]]))
		outputFile.write("\n")
	outputFile.close()
	return None

def find_all_times_faster(pickups, dropoffs, time_list, nodes, radius=0):
	'''
	Same as get_rides_fast, except designed to work on large inputs. Will split rides based on pickup location
	and call find_all_times several times. 
	'''
	if radius == 0:
		R = 100.0 # meters
	else:
		R = radius
	print "**** Building KDTrees ****"
	pTree = cKDTree(pickups)
	dTree = cKDTree(dropoffs)
	nTree = cKDTree(np.array(nodes))
	print "**** Querying KDTrees ****"
	# Find pickups and dropoffs close to each node
	node_p = pTree.query_ball_tree(nTree, R)
	node_d = dTree.query_ball_tree(nTree, R)
	print "**** Finding travel times ****"
	nodePairs = {}
	length = len(node_p)
	for i in xrange(length):
		if i % 1000 == 0:
			progress = 100.0*i/length
			if i > 0:
				sys.stdout.write('\r')
			sys.stdout.write("Progress: " + "%.02f" % progress + "%" + " completed.")
			sys.stdout.flush()
		for pickup in node_p[i]:
			for dropoff in node_d[i]:
				if (pickup, dropoff) in nodePairs.keys():
					nodePairs[(pickup,dropoff)].append(time_list[i])
				else:
					nodePairs[(pickup, dropoff)] = [time_list[i]]
	sys.stdout.write("\rProgress: " + "%.01f" % 100.0 + "%" + " completed.\n")
	sys.stdout.flush()
	return nodePairs

def get_rides_fastest():
	'''
	Extracts rides and nodes from appropriate files
	'''
	MIN_RIDES = 4
	R = 100.0
	nodeFile = open("nodesENU.csv", "r")
	print "**** Reading node file ****"
	nodes = []
	for i, line in enumerate(nodeFile):
		if i == 0:
			continue # skip first line
		node = line.replace('"', '').split(",")
		nodes.append([float(node[0]), float(node[1])])
	nodeFile.close()
	nTree = cKDTree(nodes)
	# Open input file with rides
	fileName = "manhattan_rides_2.csv"
	rideFile = open(fileName, "r")
	print "**** Reading ride file ****"
	tmpNodePairs = {}
	nodePairs = {}
	keys = set()
	tmpkeys = set()
	# Extract all rides, put them in appropriate lists
	for i, line in enumerate(rideFile):
		row = line.split(",")
		pickups = nTree.query_ball_point(LL0_to_ENUm((float(row[2]), float(row[1]))), R)
		dropoffs = nTree.query_ball_point(LL0_to_ENUm((float(row[4]), float(row[3]))), R)
		for pickup in pickups:
			for dropoff in dropoffs:
				if (pickup, dropoff) in keys:
					nodePairs[(pickup,dropoff)].append(float(row[0]))
				elif (pickup, dropoff) in tmpkeys:
					if len(tmpNodePairs[(pickup, dropoff)]) >= MIN_RIDES - 1:
						tmpkeys.remove((pickup,dropoff))
						keys.add((pickup, dropoff))
						nodePairs[(pickup, dropoff)] = tmpNodePairs[(pickup, dropoff)]
						nodePairs[(pickup, dropoff)].append(float(row[0]))
						del tmpNodePairs[(pickup, dropoff)]
					else:
						tmpNodePairs[(pickup, dropoff)].append(float(row[0]))
				else:
					tmpkeys.add((pickup, dropoff))
					tmpNodePairs[(pickup, dropoff)] = [float(row[0])]
		# Progress bar code
		if fileName == "manhattan_rides_2.csv":
			if i % 1000 == 0:
				progress = 100.0*i/1000000#9072075
				if progress > 100:
					break
				if i > 0:
					sys.stdout.write('\r')
				sys.stdout.write("Progress: " + "%.02f" % progress + "%" + " completed.")
				sys.stdout.flush()
	sys.stdout.write('\n')
	rideFile.close()
	return nodePairs

if __name__ == "__main__":
	write_travel_times()