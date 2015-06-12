from fetch_data import fetch_data
from point_in_poly import point_in_poly
from datetime import datetime
from datetime import timedelta

MANHATTAN_BOX=(40.6780, 40.8860, -74.0382, -73.9030)

# Import manhattan_polygon from file and format it into a list of vertices
poly_file = open("manhattan_box.txt", "r")
manhattan_polygon=poly_file.readline().split(";")
for i in range(len(manhattan_polygon)):
	manhattan_polygon[i] = list(manhattan_polygon[i].replace("(","").replace(")","").split(","))
	for j in range(len(manhattan_polygon[i])):
		manhattan_polygon[i][j] = float(manhattan_polygon[i][j])
	manhattan_polygon[i] = tuple(manhattan_polygon[i])
poly_file.close()

# Set time window for SQL query
DELTA = timedelta(seconds=30)

# Had to use a dummy date so that I could add and subtract timedeltas from times
INTERVAL_START = datetime(2013,01,01,12,00,00)
INTERVAL_END = datetime(2013,01,01,13,59,59)

start_datetime = datetime(2013,01,01,12,00,00)
end_datetime = datetime(2013,01,01,12,00,01)
i = 0

# Open CSV file to which taxi travel times will be written
outputFile = open("manhattan_rides.csv", "w")
while end_datetime <= INTERVAL_END and i < 1:
	queryString = "SELECT pickup_datetime,dropoff_datetime,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude FROM [833682135931:nyctaxi.trip_data] WHERE (FLOAT(pickup_longitude) BETWEEN -74.0382 AND -73.9030) AND (FLOAT(dropoff_longitude) BETWEEN -74.0382 AND -73.9030) AND (FLOAT(pickup_latitude) BETWEEN 40.6780 AND 40.8860) AND (FLOAT(dropoff_latitude) BETWEEN 40.6780 AND 40.8860) AND (TIME(dropoff_datetime) BETWEEN TIME(\'" + str(start_datetime) + "\') AND TIME(\'" + str(INTERVAL_END) + "\')) AND (TIME(pickup_datetime) BETWEEN TIME(\'" + str(start_datetime) + "\') AND TIME(\'" + str(end_datetime) + "\'))"
	results = fetch_data(queryString)
	for row in results:
		if point_in_poly(float(row[3]), float(row[2]), manhattan_polygon) and point_in_poly(float(row[5]), float(row[4]), manhattan_polygon):
			travel_time = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")-datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
			outputFile.write(str(travel_time.total_seconds()) + ",")
			outputFile.write(",".join(row[2:6]))
			outputFile.write('\n')
	start_datetime += DELTA
	end_datetime += DELTA
	i += 1
outputFile.close()