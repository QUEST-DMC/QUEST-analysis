import numpy
import math
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '/Users/tinekesalmon/Documents/fridge4_bolometer_calibration/scripts/graphene')
import graphene
graphene.set_source('xyz_f4')
graphene.set_cache('data')

#f,ax = plt.subplots(2,1)

t1='2023-01-18 17:25'
t2='2023-01-18 18:10'
t0=1674062700

n=0
for cell in (1, 2):
  nnh = 'w%dta2'%(cell)
  #nnt = 'w%dbt'%(cell)

  # heater data
  h_data = graphene.get_range(nnh, t1,t2)
  h_Rbox, h_att = graphene.get_prev(nnh + '_dbox', t1, unpack=1, usecols=(1,2))

  # h_time = h_data[:,0]  # time in unix seconds
  # h_drive = h_data[:,1] # voltage of the generator, V
  # h_f0 = h_data[:,11]   # resonance frequency, Hz
  # h_df = h_data[:,13]   # resonance width, Hz
  # h_driveI = h_drive / 10**(h_att/10.0) / numpy.sqrt(8) / 6.4 / (h_Rbox+400)
  # h_amp = numpy.hypot(h_data[:,7],h_data[:,9])/h_f0/h_df
  # h_pwr = h_amp*h_driveI
  # ax[0].plot(h_time - t0, 1e12*h_pwr, '-', label=nnh)

#   # thermometer
#   (t_time, t_temp) = graphene.get_range(nnt+':f1', t1,t2, usecols=(0,1), unpack=1)
#   ax[1].plot(t_time - t0, t_temp, '-', label=nnt)

#   temp1 = numpy.mean(t_temp[0:30])
#   temp2 = numpy.mean(t_temp[-30:])
#   temp_sh = temp1 + (t_time-t_time[0])*(temp2-temp1)/(t_time[-1]-t_time[0])
#   pwr = numpy.interp(t_time-t0, h_time-t0, h_pwr);
#   pwr0 = numpy.mean(pwr[0:30])

#   if cell==1:
#     K = 9.09e-10  # W/mK
#   else:
#     K = 7.17e-10  # W/mK

#   ax[1].plot(t_time - t0, temp_sh - pwr0/K, 'k-')
#   ax[1].plot(t_time - t0, temp_sh + (pwr-pwr0)/K, 'k-')


# ax[0].set_title('2023-01-18, heating bolometers')
# ax[0].set_xlabel('time, s')
# ax[0].set_ylabel('power, pW')
# ax[1].set_xlabel('time, s')
# ax[1].set_ylabel('temperature, mK')

# #plt.xlim([4100,4300])
# ax[0].legend()
# ax[1].legend()
# fig = plt.gcf()
# fig.set_size_inches(9, 12)
# plt.savefig("data.png", dpi=100)
# #plt.show()
