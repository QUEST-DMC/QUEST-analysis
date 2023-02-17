import numpy
import math
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '/Users/tinekesalmon/Documents/fridge4_bolometer_calibration/scripts/py')
import graphene002 as graphene
graphene.set_source('xyz_f4')
import f4wire001 as f4wire

#set time to collect data for non-linear peaks 
# 00:24 - 00:32 10022023
t1=1675988640
t2=1675989120
t0=1675988640

n=0
for cell in (1, 2):
  # wire name 
  nnh = 'w%dbh'%(cell)
  nnt = 'w%dbt'%(cell)
  
  # data
  h_wire_data = f4wire.get_data(nnh, t1,t2, use_bg=1, cnv_drive=1, cnv_volt=1, cache='data/' + '%s' %nnh + '_f4wire_get_data_' + '%d' %t1 + '_%d' %t2 )
  t_wire_data = f4wire.get_data(nnt, t1,t2, use_bg=1, cnv_drive=1, cnv_volt=1, cache='data/' + '%s' %nnt + '_f4wire_get_data_' + '%d' %t1 + '_%d' %t2 )