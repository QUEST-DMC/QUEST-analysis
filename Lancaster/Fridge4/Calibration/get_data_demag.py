import numpy
import math
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '/Users/tinekesalmon/Documents/fridge4_bolometer_calibration/scripts/graphene')
import graphene
graphene.set_source('xyz_f4')
graphene.set_cache('data')

#set time to collect data for non-linear peaks 
# 00:24 - 00:32 10022023
t1=1675988640
t2=1675989120
t0=1675988640

# demag_pc:f2 # magnetic field 
# demag_pc:f1 # current of solenoid 

#mag = graphene.get_wrange('demag_pc:f2',t1,t2)
graphene.get_prev('demag_pc:f2',t1)


