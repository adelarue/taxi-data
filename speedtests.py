# speedtests.py
# Test module for testing relative speeds
# Authored by Arthur J Delarue on 6/3/15

import cProfile
import travel_time
import numpy as np
from scipy.spatial import cKDTree
from conversions import Ellipsoid

list1 = range(100000)
list2 = range(50000,150000)

def createTrees(array1, array2):
	tree1 = cKDTree(array1)
	tree2 = cKDTree(array2)
	return (tree1, tree2)

def treeTest():
	a = np.random.rand(1000000,2)
	b = np.random.rand(1000000,2)
	at,bt = createTrees(a,b)
	bt.query_ball_tree(at, 0.001)
	return None

def AccessTest():
	WGS84 = Ellipsoid(6378137.0, 6356752.3142)
	for i in xrange(100000):
		a1 = access1(WGS84)
		a2 = access2(WGS84)
	return None

def access1(ellipsoid):
	return ellipsoid.a

def access2(ellipsoid):
	return ellipsoid.getSemiMajorAxis()

#cProfile.run("treeTest()")

#cProfile.run('AccessTest()')

cProfile.run("travel_time.write_travel_times('output2.csv')")