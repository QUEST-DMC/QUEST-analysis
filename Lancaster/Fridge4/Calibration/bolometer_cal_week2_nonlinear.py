"""
Week 2 data 
For the calibration of bolometer 1
data from Fri Feb 10 2023 00:54:22 GMT+0000 to Fri Feb 10 2023 01:14:00 GMT+0000
"""
#%%# ------------------------ Load Data
#import required modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#importing data with an irregular number of columns 
# Read the data from the .dat file

# both peaks
# # heater data, w1bh
h_data = pd.read_csv('data/w1bh_get_range_1675990462.000000_1675991640.000000', delimiter=' ', header=None, engine='python', names=range(22))
#thermometer data, w1bt
w1bt = pd.read_csv('data/w1bt_get_range_1675990462.000000_1675991640.000000', delimiter=' ', header=None, engine='python', names=range(22))
#want 13th column, need to use loc as now a pandas df not np array
w1bt_width=w1bt.loc[:,13] #resonance width in Hz
w1bt_time=w1bt.loc[:,0] #time in unix seconds

#drive box of heater
h_dbox=pd.read_csv('data/w1bh_dbox_get_prev_0_1675990462.000000', delimiter=' ', header=None, engine='python')
h_Rbox=h_dbox.loc[0,1] #resistance of drive box of heater
h_att=h_dbox.loc[0,2] #attenuation of drive box of heater

h_time = h_data.loc[:,0]  # time in unix seconds
h_drive = h_data.loc[:,1] # voltage of the generator, V
h_f0= h_data.loc[:,11]   # resonance frequency, Hz
h_df= h_data.loc[:,13]   # resonance width, Hz
h_driveI = h_drive / 10**(h_att/10.0) / np.sqrt(8) / 6.4 / (h_Rbox+400) #drive current
h_amp = np.hypot(h_data.loc[:,7],h_data.loc[:,9])/h_f0/h_df #amplitude of resonance fit of heater
h_pwr = h_amp*h_driveI # heater power, P=IV


#%%# - convert from width to temperature 

#convert from width to temperature 
import functions as fn
w1bt_temp=[]
for width in w1bt_width:
    w1bt_temp.append(fn.Temperature_from_Width(width, 0)[0])

# converting list to array
w1bt_temp = np.array(w1bt_temp)
# convert to uK
w1bt_temp=w1bt_temp*1e6


#%%# - find the baseline fit 

# Flat parts 
# T0 to t0+150
# 511 + t0 to 646 + t0
# 1061 + t0 to tf 

ti1=w1bt_time[0]
tf1=150+ti1
ti2=511 +ti1
tf2=646+ti1
ti3=1061 + ti1
tf3=w1bt_time.iloc[-1]

#Find indices for Tf1 Ti2 Tf2 ti3

# Find indices correlating to the point closest to the time at which width starts to change
# Take the absolute difference of timestamp - t1 and time points - t2
# set loop over times:
diff_tf1=[]
diff_ti2=[]
diff_tf2=[]
diff_ti3=[]

for timestamp in w1bt_time:
    d_tf1=abs(timestamp - tf1)
    diff_tf1.append(d_tf1)
    d_ti2=abs(timestamp - ti2)
    diff_ti2.append(d_ti2)
    d_tf2=abs(timestamp - tf2)
    diff_tf2.append(d_tf2)
    d_ti3=abs(timestamp - ti3)
    diff_ti3.append(d_ti3)

# Use argmin function to find the index of the minimum difference. 
# This will be the index of the point closest to the time, t1 or t2. 
index_tf1=np.argmin(diff_tf1)+1
index_ti2=np.argmin(diff_ti2)+1
index_tf2=np.argmin(diff_tf2)+1
index_ti3=np.argmin(diff_ti3)+1

# actual recorded timestamps in the data for when the width starts changing 
ti1_a=w1bt_time[0]
tf1_a=w1bt_time[index_tf1]
ti2_a=w1bt_time[index_ti2]
tf2_a=w1bt_time[index_tf2]
ti3_a=w1bt_time[index_ti3]
tf3_a=w1bt_time.iloc[-1]

#get a time array for the 3 'flat parts' 
w1bt_flat_time_1=w1bt_time[0:index_tf1]
w1bt_flat_time_2=w1bt_time[index_ti2:index_tf2]
w1bt_flat_time_3=w1bt_time[index_ti3:-1]
w1bt_flat_time=np.concatenate((w1bt_flat_time_1, w1bt_flat_time_2, w1bt_flat_time_3), axis=None)

#get the corresponding temperatures for the indices of the 'flat'
w1bt_flat_temp_1=w1bt_temp[0:index_tf1]
w1bt_flat_temp_2=w1bt_temp[index_ti2:index_tf2]
w1bt_flat_temp_3=w1bt_temp[index_ti3:-1]
w1bt_flat_temp=np.concatenate((w1bt_flat_temp_1, w1bt_flat_temp_2, w1bt_flat_temp_3), axis=None)

#%%# - calculate temp change 

K_T=12e-7 #W/K 
temp_change=h_pwr/K_T
#find temp change in uK
temp_change=temp_change*1e6

#%%# - make a 1d fit for 'flat' width sections 
# polynomial fit of x against y (temp values), 1st order polynomial
z =np.polyfit(w1bt_flat_time-w1bt_time[0], w1bt_flat_temp, 1)
p = np.poly1d(z)
# take away temp_change[0] from the baseline fit 
p0=p-temp_change[0]
p0_slope = p0-p0[0] # this is the slope of the fit i.e. - the +c component
# creates a linspace suitable for the length of the displayed fit line
xp = np.linspace(0, w1bt_time.iloc[-1]-w1bt_time[0], 1031)


#%%# ------------------------ Plot the temperature of w1bt (bolometer 1 thermometer) and temperature change from w1bh (bolometer 1 heater)
plt.figure(1)
#time minus inital time to make plot neater 
plt.plot(w1bt_time-w1bt_time[0], w1bt_temp, label='w1bt temp')
plt.plot(xp, p0(xp), label='Baseline Temp')
plt.plot(h_time-h_time[0], temp_change+p0(xp), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Temperature of bolometer 1 during calibration heating (2023-02-10 00:54:22 to 01:14:00)')
plt.show()

#%%# ------------------------ plot pwr vs temp for the 2 peaks separately 

# need to find the swap over point between the 2 peaks 
# swaps around  1675991045.000000 - 1675990462.000000 = 583 
t_swap=1675991045.000000

diff_swap=[]

for timestamp in w1bt_time:
    d_swap=abs(timestamp - t_swap)
    diff_swap.append(d_swap)

# Use argmin function to find the index of the minimum difference. 
# This will be the index of the point closest to the time, t1 or t2. 
index_swap=np.argmin(diff_swap)+1

# actual recorded timestamps in the data for when the width starts changing 
t_swaps=w1bt_time[index_swap]

xp1 = np.linspace(0, w1bt_time[index_swap]-w1bt_time[0], index_swap)
plt.figure(2)
#time minus inital time to make plot neater 
plt.plot(w1bt_time[0:index_swap]-w1bt_time[0], w1bt_temp[0:index_swap], xp1, p0(xp1), label='w1bt temp')
plt.plot(h_time[0:index_swap]-h_time[0], temp_change[0:index_swap]+p0(xp1), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Peak 1: Temperature of bolometer 1 during calibration heating (2023-02-10 00:54:22 to 01:14:00)')
plt.show()

xp2 = np.linspace(w1bt_time[index_swap]-w1bt_time[0], w1bt_time.iloc[-1]-w1bt_time[0], len(temp_change[index_swap:-1]))
plt.figure(3)
#time minus inital time to make plot neater 
plt.plot(w1bt_time[index_swap:-1]-w1bt_time[0], w1bt_temp[index_swap:-1], xp2, p0(xp2), label='w1bt temp')
plt.plot(h_time[index_swap:-1]-h_time[0], temp_change[index_swap:-1]+p0(xp2), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Peak 2: Temperature of bolometer 1 during calibration heating (2023-02-10 00:54:22 to 01:14:00)')
plt.show()

#%%# - fit to find K 
# temp_change = pwr/ K 
# we have y = mx, temp = 1/K * pwr 
# so linear fit grad = 1/K

#interpolation
# gives interpolated values of the heater power at the timestamps saved in w1bt_time
h_pwr_interp = np.interp(w1bt_time, h_time, h_pwr)

# pwr vs temp for 2 peaks separately 
# polynomial fit of x against y, 1st order polynomial
zp1 =np.polyfit(h_pwr_interp[0:index_swap]*1e12, w1bt_temp[0:index_swap]-p0_slope(xp1), 1)
pp1 = np.poly1d(zp1)
# creates a linspace suitable for the length of the displayed fit line
xpp1 = np.linspace(0, 25, 1715)

# [grad] = uK/pW, e-6/e-12 = e6 
# grad *e6 to get K/W
grad1 = p[1]*1e6
K_Tpeak1=1/grad1 # in W/K
print('K_Tpeak1', K_Tpeak1)

plt.figure(4)
plt.plot(h_pwr_interp[0:index_swap]*1e12, w1bt_temp[0:index_swap]-p0_slope(xp1), '.', xpp1, pp1(xpp1))
plt.xlabel("w1bh [pW]")
plt.ylabel("w1bt [uK] - temperature slope ")
plt.title('Peak 1: Temperature against power of bolometer 1 (2023-02-10 00:54:22 to 01:14:00)')
plt.show()


#%%# - Load data for peak 1 only 
# #peak 1
# # # heater data, w1bh
# h_data = pd.read_csv('data/w1bh_get_range_1675990462.000000_1675991045.000000', delimiter=' ', header=None, engine='python', names=range(22))
# #thermometer data, w1bt
# w1bt = pd.read_csv('data/w1bt_get_range_1675990462.000000_1675991045.000000', delimiter=' ', header=None, engine='python', names=range(22))
# #want 13th column, need to use loc as now a pandas df not np array
# w1bt_width=w1bt.loc[:,13] #resonance width in Hz
# w1bt_time=w1bt.loc[:,0]  #time in unix seconds

# #drive box of heater
# h_dbox=pd.read_csv('data/w1bh_dbox_get_prev_0_1675990462.000000', delimiter=' ', header=None, engine='python')
# h_Rbox=h_dbox.loc[0,1] #resistance of drive box of heater
# h_att=h_dbox.loc[0,2] #attenuation of drive box of heater

# h_time = h_data.loc[:,0]  # time in unix seconds
# h_drive = h_data.loc[:,1] # voltage of the generator, V
# h_f0 = h_data.loc[:,11]   # resonance frequency, Hz
# h_df = h_data.loc[:,13]   # resonance width, Hz
# h_driveI = h_drive / 10**(h_att/10.0) / np.sqrt(8) / 6.4 / (h_Rbox+400) #drive current
# h_amp = np.hypot(h_data.loc[:,7],h_data.loc[:,9])/h_f0/h_df #amplitude of resonance fit of heater
# h_pwr = h_amp*h_driveI # heater power, P=IV

#%%# - Load data for peak 2 only 
# #peak 2 
# # # heater data, w1bh
# h_data = pd.read_csv('data/w1bh_get_range_1675991045.000000_1675991640.000000', delimiter=' ', header=None, engine='python', names=range(22))
# #thermometer data, w1bt
# w1bt = pd.read_csv('data/w1bt_get_range_1675991045.000000_1675991640.000000', delimiter=' ', header=None, engine='python', names=range(22))
# #want 13th column, need to use loc as now a pandas df not np array
# w1bt_width=w1bt.loc[:,13] #resonance width in Hz
# w1bt_time=w1bt.loc[:,0]  #time in unix seconds

# #drive box of heater
# h_dbox=pd.read_csv('data/w1bh_dbox_get_prev_0_1675990462.000000', delimiter=' ', header=None, engine='python')
# h_Rbox=h_dbox.loc[0,1] #resistance of drive box of heater
# h_att=h_dbox.loc[0,2] #attenuation of drive box of heater

# h_time = h_data.loc[:,0]  # time in unix seconds
# h_drive = h_data.loc[:,1] # voltage of the generator, V
# h_f0 = h_data.loc[:,11]   # resonance frequency, Hz
# h_df = h_data.loc[:,13]   # resonance width, Hz
# h_driveI = h_drive / 10**(h_att/10.0) / np.sqrt(8) / 6.4 / (h_Rbox+400) #drive current
# h_amp = np.hypot(h_data.loc[:,7],h_data.loc[:,9])/h_f0/h_df #amplitude of resonance fit of heater
# h_pwr = h_amp*h_driveI # heater power, P=IV
