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

# Import manhattan_polygon from file and format it into a list of vertices
poly_file = open("manhattan_box.txt", "r")
manhattan_polygon=poly_file.readline().split(";")
for i in range(len(manhattan_polygon)):
	manhattan_polygon[i] = list(manhattan_polygon[i].replace("(","").replace(")","").split(","))
	for j in range(len(manhattan_polygon[i])):
		manhattan_polygon[i][j] = float(manhattan_polygon[i][j])
	manhattan_polygon[i] = tuple(manhattan_polygon[i])
poly_file.close()

# Set up Boolean variables to check if trip was in Manhattan
pickup_in_manhattan = False
dropoff_in_manhattan = False

# Open output file
outputFile = open("manhattan_rides_2.csv", "w")
# Loop through input files
for i in range(1, 13):
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