# speedtests.py
# Test module for testing relative speeds
# Authored by Arthur J Delarue on 6/3/15

import cProfile
import travel_time

list1 = range(100000)
list2 = range(50000,150000)

#cProfile.run('[val for val in list1 if val in list2]')
#cProfile.run('list(set(list1).intersection(list2))')
#cProfile.run('list(set(list1) & set(list2))')

cProfile.run("travel_time.write_travel_times()")