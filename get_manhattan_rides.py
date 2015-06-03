# get_manhattan_rides.py
# Authored 5/29/15 by Arthur J. Delarue
# Purpose: extract relevant information from taxi database
# and pack it into a new CSV file

from datetime import datetime
from datetime import time
from datetime import timedelta
from point_in_poly import point_in_poly
import os

# Select time interval
INTERVAL_START = time(12, 0, 0)
INTERVAL_END = time(14, 0, 0)

def import_manhattan_polygon():
	# Import manhattan_polygon from file and format it into a list of vertices
	poly_file = open("manhattan_box.txt", "r")
	manhattan_polygon=poly_file.readline().split(";")
	for i in range(len(manhattan_polygon)):
		manhattan_polygon[i] = list(manhattan_polygon[i].replace("(","").replace(")","").split(","))
		for j in range(len(manhattan_polygon[i])):
			manhattan_polygon[i][j] = float(manhattan_polygon[i][j])
		manhattan_polygon[i] = tuple(manhattan_polygon[i])
	poly_file.close()
	return manhattan_polygon


def get_manhattan_rides():
	# Load Manhattan polygon
	manhattan_polygon = import_manhattan_polygon()
	# Set up Boolean variables to check if trip was in Manhattan
	pickup_in_manhattan = False
	dropoff_in_manhattan = False
	# Open output file
	outputFile = open("manhattan_rides_2.csv", "w")
	# Loop through input files
	for i in range(12, 13):
		# This boolean is to make sure the first line is skipped
		firstLine = True
		# Open input file
		fileName = "../Full_data/trip_data_" + str(i) + ".csv"
		inputFile = open(fileName, "r")
		for line in inputFile:
			# Skip first line
			if firstLine:
				firstLine = False
				continue
			# Extract necessary fields from CSV
			row = line.split(",")
			pickup_time = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
			dropoff_time = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
			pickup_longitude = row[10]
			pickup_latitude = row[11]
			dropoff_longitude = row[12]
			dropoff_latitude = row[13]
			# Make sure the coordinates are valid
			try:
				pickup_in_manhattan = point_in_poly(float(pickup_latitude), float(pickup_longitude), manhattan_polygon)
				dropoff_in_manhattan = point_in_poly(float(dropoff_latitude), float(dropoff_longitude), manhattan_polygon)
			except ValueError:
				continue
			# Check if taxi ride is in Manhattan, in the appropriate time interval
			if INTERVAL_START <= pickup_time.time() and pickup_time.time() < INTERVAL_END and INTERVAL_START <= dropoff_time.time() and dropoff_time.time() < INTERVAL_END and pickup_in_manhattan and dropoff_in_manhattan:
				travel_time = dropoff_time - pickup_time
				# Write travel time and coordinates to file
				outputFile.write(str(travel_time.total_seconds()) + ",")
				outputFile.write(",".join(row[10:14]))
		inputFile.close()
	outputFile.close()
	return None

class Square:
	def __init__(self, bottom, top, right, left):
		if top < bottom or right < left:
			raise ValueError("Invalid square parameters")
		self.top = top
		self.bottom = bottom
		self.left = left
		self.right = right

nw_manhattan_sample = Square(bottom=40.8075, top=40.8197, right=-73.9380, left=-73.9465)
ues_sample = Square(bottom=40.7673, top=40.7749, right=-73.9542, left=-73.9619)
ev_sample = Square(bottom=40.7216, top=40.7323, right=-73.9781, left=-73.9878)

def extract_sample(pickup_square, dropoff_square):
	'''
	From large dataset, extract rides that go from one small GPS square
	to another small GPS square
	'''
	inputFile = open("manhattan_rides.csv", "r")
	outputFile = open("manhattan_rides_sample.csv", "w")
	for line in inputFile:
		row = line.split(",")
		xp = float(row[1])
		yp = float(row[2])
		xd = float(row[3])
		yd = float(row[4])
		if pickup_square.left < xp and xp < pickup_square.right and pickup_square.bottom < yp and yp < pickup_square.top and dropoff_square.left < xd and xd < dropoff_square.right and dropoff_square.bottom < yd and yd < dropoff_square.top:
			outputFile.write(line)
	outputFile.close()
	inputFile.close()
	return None

def sort_nodes(fileName):
	'''
	Sort ENU nodes by north coordinate
	'''
	fin = open(fileName, "r")
	fout = open("nodesENU_sorted.csv", "w")
	nodes = []
	for i, line in enumerate(fin):
		if i == 0:
			fout.write(line) # first line has headers, etc.
		else:
			node = line.replace('"', '').split(",")
			nodes.append([float(node[0]), float(node[1])])
	nodes_sorted = sorted(nodes, key=lambda l:l[1])
	for node in nodes_sorted:
		fout.write(str(node[0]) + "," + str(node[1]) + "\n")
	fout.close()
	fin.close()
	return None

if __name__ == "__main__":
	sort_nodes("nodesENU.csv")
	# extract_sample(ues_sample,ev_sample)
	# get_manhattan_rides()