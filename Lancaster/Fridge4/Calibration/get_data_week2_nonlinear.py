import numpy
import math
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '/Users/tinekesalmon/Documents/fridge4_bolometer_calibration/scripts/graphene')
import graphene
graphene.set_source('xyz_f4')
graphene.set_cache('data')

#set time to collect data for non-linear peaks 
# 2 peaks
t1=1675990462
t2=1675991640
t0=1675990462

# #peak 1
# t1=1675990462
# t2=1675991045
# t0=1675990462

# #peak 2 
# t1=1675991045
# t2=1675991640
# t0=1675991045

n=0
for cell in (1, 2):
  # heater wire name 
  nnh = 'w%dbh'%(cell)
  # thermometer wire name 
  nnt = 'w%dbt'%(cell)

  # heater data

  # + '_sweeps' gives raw data. just wire name (i.e. nnh) gives fitting results
  h_data = graphene.get_range(nnh, t1,t2)
  #_dbox:f1 gives the filter 1 of dbox which is the conversion factor between the drive generator voltage (V) and drive current (A)
  h_Rbox, h_att = graphene.get_prev(nnh + '_dbox', t1, unpack=1, usecols=(1,2))

  # thermometer
  t_data= graphene.get_range(nnt, t1, t2)
  (t_time, t_temp) = graphene.get_range(nnt+':f1', t1,t2, usecols=(0,1), unpack=1)
  t_Rbox, t_att = graphene.get_prev(nnt + '_dbox', t1, unpack=1, usecols=(1,2))
