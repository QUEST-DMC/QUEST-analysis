import numpy
import math
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '/Users/tinekesalmon/exp_py/py')
import graphene002 as graphene
graphene.set_source('xyz_f4')
import f4wire001 as f4wire

#set time to collect data for non-linear peaks 
# 00:24 - 00:32 10022023
t1=1675988640
t2=1675989120

n=0
for cell in (1, 2):
  # wire name 
  nnh = 'w%dbh'%(cell)
  nnt = 'w%dbt'%(cell)
  
  # f4wire (drive current and conv voltage) data
  h_wire_data = f4wire.get_data(nnh, t1,t2, use_bg=1, cnv_drive=1, cnv_volt=1, cache='data/' + '%s' %nnh + '_f4wire_get_data_' + '%d' %t1 + '_%d' %t2 )
  t_wire_data = f4wire.get_data(nnt, t1,t2, use_bg=1, cnv_drive=1, cnv_volt=1, cache='data/' + '%s' %nnt + '_f4wire_get_data_' + '%d' %t1 + '_%d' %t2 )

  # get_range fitting database for width and fitting parameters 

  # heater data
  # + '_sweeps' gives raw data. just wire name (i.e. nnh) gives fitting results
  h_data = graphene.get_range(nnh, t1,t2,  cache='data/' + '%s' %nnh + '_get_range_' + '%d' %t1 + '_%d' %t2)
  #_dbox:f1 gives the filter 1 of dbox which is the conversion factor between the drive generator voltage (V) and drive current (A)
  h_Rbox, h_att = graphene.get_prev(nnh + '_dbox', t1, unpack=1, usecols=(1,2), cache='data/' + '%s' %nnh + '_dbox_get_prev_' + '%d' %t1 + '_%d' %t2)

  # thermometer
  t_data= graphene.get_range(nnt, t1, t2, cache='data/' + '%s' %nnt + '_get_range_' + '%d' %t1 + '_%d' %t2)
  t_Rbox, t_att = graphene.get_prev(nnt + '_dbox', t1, unpack=1, usecols=(1,2), cache='data/' + '%s' %nnt + '_dbox_get_prev_' + '%d' %t1 + '_%d' %t2)
