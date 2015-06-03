# conversions.py
# Provides methods to convert between LLA -> ECEF -> ENU coordinates
# LLA = latitude, longitude, altitude
# ENU = east, north, up

import math

class Ellipsoid:
	def __init__(self, a, b):
		'''
		Initializes an Ellipsoid object
		Parameters:
		a: semimajor axis, in meters
		b: semiminor axis, in meters
		
		Attributes:
		e: eccentricity
		f: ellipsoid flatness
		'''
		self.a = a
		self.b = b
		self.f = (a-b)/a
		self.e = math.sqrt(self.f * (2 - self.f))

	def getSemiMajorAxis(self):
		return self.a

	def getSemiMinorAxis(self):
		return self.b

	def getFlatness(self):
		return self.f

	def getEccentricity(self):
		return self.e

WGS84 = Ellipsoid(6378137.0, 6356752.3142)
MANHATTAN_CENTER = (40.782, -73.9706) # Coordinates of center used for node ENU coordinates

def LL0_to_ECEF(ll_coords, ellipsoid=WGS84):
	'''
	Just pass in a latitude and longitude, as a tuple in that order.
	All altitudes are 0 in our case.
	'''
	psi_deg, lambda_deg = ll_coords

	sin_psi = math.sin(math.radians(psi_deg))
	cos_psi = math.cos(math.radians(psi_deg))
	sin_lambda = math.sin(math.radians(lambda_deg))
	cos_lambda = math.cos(math.radians(lambda_deg))

	# Extract ellipsoid parameters
	a = ellipsoid.getSemiMajorAxis()
	e = ellipsoid.getEccentricity()
	N = a / math.sqrt(1 - e ** 2 * sin_psi ** 2)	# Radius of curvature (meters)

	# Do the calculation
	x = N * cos_psi * cos_lambda
	y = N * cos_psi * sin_lambda
	z = N * (1 - e ** 2) * sin_psi

	return (x, y, z)

def ECEF_to_ENU(ecef_coords, ll_center_coords, ellipsoid=WGS84):
	'''
	Coordinates of point must be passed as ECEF, but coordinates of reference must be passed
	as (latitude, longitude)
	'''
	# Get reference parameters from center
	psi_deg, lambda_deg = ll_center_coords

	sin_psi = math.sin(math.radians(psi_deg))
	cos_psi = math.cos(math.radians(psi_deg))
	sin_lambda = math.sin(math.radians(lambda_deg))
	cos_lambda = math.cos(math.radians(lambda_deg))
	
	ecef_center = LL0_to_ECEF(ll_center_coords, ellipsoid)

	dx = ecef_coords[0] - ecef_center[0]
	dy = ecef_coords[1] - ecef_center[1]
	dz = ecef_coords[2] - ecef_center[2]

	# Matrix multiplication
	east  = dx * (- sin_lambda) + dy * cos_lambda + dz * 0.0
	north = dx * (- cos_lambda * sin_psi) + dy * (- sin_lambda * sin_psi) + dz * cos_psi
	up    = dx * cos_lambda * cos_psi + dy * sin_lambda * cos_psi + dz * sin_psi

	return (east, north)

def LL0_to_ENUm(ll_coords, ll_center_coords=MANHATTAN_CENTER, ellipsoid=WGS84):
	'''
	Shortcut for the Manhattan problem. Easier to import and run in travel_time.py
	'''
	return ECEF_to_ENU(LL0_to_ECEF(ll_coords, ellipsoid), ll_center_coords, ellipsoid)
	
if __name__ == "__main__":
	pass







