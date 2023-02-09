"""
Useful
For the calibration of bolometer 1
Finds thermal conductance, K_T, where delta T = 1/K_T * P
"""
#%%# ------------------------ Load Data
#import required modules
import numpy as np
import matplotlib.pyplot as plt

#thermometer data, w1bt
w1bt=np.loadtxt('data/w1bt_get_range_2023-01-18 17:25_2023-01-18 18:10')
w1bt_time=w1bt[:,0] #time in unix seconds
w1bt_width=w1bt[:,13] #resonance width in Hz

# heater data, w1bh
h_data=np.loadtxt('data/w1bh_get_range_2023-01-18 17:25_2023-01-18 18:10')

h_dbox=np.loadtxt('data/w1bh_dbox_get_prev_0_2023-01-18 17:25') #drive box of heater
h_Rbox=h_dbox[1] #resistance of drive box of heater
h_att=h_dbox[2] #attenuation of drive box of heater

h_time = h_data[:,0]  # time in unix seconds
h_drive = h_data[:,1] # voltage of the generator, V
h_f0 = h_data[:,11]   # resonance frequency, Hz
h_df = h_data[:,13]   # resonance width, Hz
h_driveI = h_drive / 10**(h_att/10.0) / np.sqrt(8) / 6.4 / (h_Rbox+400) #drive current
h_amp = np.hypot(h_data[:,7],h_data[:,9])/h_f0/h_df #amplitude of resonance fit of heater
h_pwr = h_amp*h_driveI # heater power, P=IV

#convert from width to temperature 
import functions as fn
w1bt_temp=[]
for width in w1bt_width:
    w1bt_temp.append(fn.Temperature_from_Width(width, 0)[0])

# converting list to array
w1bt_temp = np.array(w1bt_temp)
# convert to uK
w1bt_temp=w1bt_temp*1e6

#calculate temp change 
K_T=10.5e-7 #W/K , Slava's value 9.09e-10 W/mK for cell 1 
temp_change=h_pwr/K_T
#find temp change in uK
temp_change=temp_change*1e6

#make a 1d fit for the width vs time for the parasitic heating - find the 'flat' parts of the plot, 3 parts 
# just inital time value 
ti1=0+w1bt_time[0] 
# need to find indices in the recorded times that correlate closely to these times
tf1=892+w1bt_time[0]
ti2=1486+w1bt_time[0]
tf2=1981+w1bt_time[0]
ti3=2568+w1bt_time[0]
# just the final time value 
tf3=w1bt_time[-1] 

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
tf3_a=w1bt_time[-1]

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

#make a 1d fit for 'flat' width sections 
# polynomial fit of x against y (temp values), 1st order polynomial
z =np.polyfit(w1bt_flat_time-w1bt_time[0], w1bt_flat_temp, 1)
p = np.poly1d(z)
# take away temp_change[0] from the baseline fit 
p0=p-temp_change[0]
# creates a linspace suitable for the length of the displayed fit line
xp = np.linspace(0, w1bt_time[-1]-w1bt_time[0], 2220)
xp1 = np.linspace(0, w1bt_time[-1]-w1bt_time[0], 2496)
xp2 = np.linspace(0, w1bt_time[-1]-w1bt_time[0], 1715)

#%%# ------------------------ Plot the temperature of w1bt (bolometer 1 thermometer) and temperature change from w1bh (bolometer 1 heater)
plt.figure(1)
#time minus inital time to make plot neater 
plt.plot(w1bt_time-w1bt_time[0], w1bt_temp, xp, p0(xp), label='w1bt temp')
plt.plot(h_time-h_time[0], temp_change+p0(xp), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Temperature of bolometer 1 during calibration heating (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

#%%# ------------------------ Plot time dependence of (w1bt [K] - baseline temperature slope) and temperature change from w1bh 
plt.figure(2)
p0_slope = p0-p0[0] # this is the slope of the fit i.e. - the +c component
#time minus inital time to make plot neater 
# (w1bt [K] - baseline temperature slope) = w1bt_temp-p0_slope(xp1) want to remove temperature slope 
plt.plot(w1bt_time-w1bt_time[0], w1bt_temp-p0_slope(xp1),  label='w1bt temp')
# temp_change is a small value so plus the +c component of the baseline temperature fit
plt.plot(h_time-h_time[0], temp_change+p0[0],  label='temperature change from w1bh power', color='g')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Temperature of bolometer 1 during calibration heating, background subtracted (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

#Plot (w1bt [K] - temperature slope) vs w1bh [W]
#interpolation
# gives interpolated values of the heater power at the timestamps saved in w1bt_time
h_pwr_interp = np.interp(w1bt_time, h_time, h_pwr)

# now fit to find K 
# temp_change = pwr/ K 
# we have y = mx, temp = 1/K * pwr 
# so linear fit grad = 1/K

# polynomial fit of x against y, 1st order polynomial
zK =np.polyfit(h_pwr_interp[780:-1]*1e12, w1bt_temp[780:-1]-p0_slope(xp2), 1)
pK = np.poly1d(zK)
# creates a linspace suitable for the length of the displayed fit line
xpK = np.linspace(0.2, 6.7, 1715)

# [grad] = uK/pW, e-6/e-12 = e6 
# grad *e6 to get K/W
print('pk', pK)
print('pk1', pK[1])
grad = pK[1]*1e6
K_Tcalc=1/grad # in W/K
print(K_Tcalc)

plt.figure(3)
plt.plot(h_pwr_interp[780:-1]*1e12, w1bt_temp[780:-1]-p0_slope(xp2), '.', xpK, pK(xpK))
plt.xlabel("w1bh [pW]")
plt.ylabel("w1bt [uK] - temperature slope ")
plt.title('Temperature against power of bolometer 1 (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

# plot pwr vs temp for the 2 peaks separately 
# need to find the swap over point between the 2 peaks 
# swaps around 1520 s 
print(w1bt_time[1374]-w1bt_time[0])

xp3 = np.linspace(0, w1bt_time[1374]-w1bt_time[0], 1374)
plt.figure(4)
#time minus inital time to make plot neater 
plt.plot(w1bt_time[0:1374]-w1bt_time[0], w1bt_temp[0:1374], xp3, p0(xp3), label='w1bt temp')
plt.plot(h_time[0:1374]-h_time[0], temp_change[0:1374]+p0(xp3), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Peak 1: Temperature of bolometer 1 during calibration heating (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

xp4 = np.linspace(w1bt_time[1374]-w1bt_time[0], w1bt_time[-1]-w1bt_time[0], 845)
plt.figure(5)
#time minus inital time to make plot neater 
plt.plot(w1bt_time[1374:-1]-w1bt_time[0], w1bt_temp[1374:-1], xp4, p0(xp4), label='w1bt temp')
plt.plot(h_time[1374:-1]-h_time[0], temp_change[1374:-1]+p0(xp4), label='temperature change from w1bh power')
plt.xlabel("Time (s)")
plt.ylabel("Temperature (uK)")
plt.legend()
plt.title('Peak 2: Temperature of bolometer 1 during calibration heating (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

# now fit to find K 
# temp_change = pwr/ K 
# we have y = mx, temp = 1/K * pwr 
# so linear fit grad = 1/K

# pwr vs temp for 2 peaks separately 
# polynomial fit of x against y, 1st order polynomial
zK1 =np.polyfit(h_pwr_interp[0:1374]*1e12, w1bt_temp[0:1374]-p0_slope(xp3), 1)
pK1= np.poly1d(zK1)
# creates a linspace suitable for the length of the displayed fit line
xpK1 = np.linspace(0.2, 6.7, 1715)

# [grad] = uK/pW, e-6/e-12 = e6 
# grad *e6 to get K/W
grad1 = pK1[1]*1e6
K_Tpeak1=1/grad1 # in W/K
print('K_Tpeak1', K_Tpeak1)

plt.figure(6)
plt.plot(h_pwr_interp[0:1374]*1e12, w1bt_temp[0:1374]-p0_slope(xp3), '.', xpK1, pK1(xpK1))
plt.xlabel("w1bh [pW]")
plt.ylabel("w1bt [uK] - temperature slope ")
plt.title('Peak 1: Temperature against power of bolometer 1 (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

xp5 = np.linspace(w1bt_time[1374]-w1bt_time[0], w1bt_time[-1]-w1bt_time[0], 1121)
# polynomial fit of x against y, 1st order polynomial peak 2
zK2 =np.polyfit(h_pwr_interp[1374:-1]*1e12, w1bt_temp[1374:-1]-p0_slope(xp5), 1)
pK2= np.poly1d(zK2)
# creates a linspace suitable for the length of the displayed fit line
xpK2 = np.linspace(0.2, 6.66, 1715)

# [grad] = uK/pW, e-6/e-12 = e6 
# grad *e6 to get K/W
grad2 = pK2[1]*1e6
K_Tpeak2=1/grad2 # in W/K
print('K_Tpeak2', K_Tpeak2)

plt.figure(7)
plt.plot(h_pwr_interp[1374:-1]*1e12, w1bt_temp[1374:-1]-p0_slope(xp5), '.', xpK2, pK2(xpK2))
plt.xlabel("w1bh [pW]")
plt.ylabel("w1bt [uK] - temperature slope ")
plt.title('Peak 2: Temperature against power of bolometer 1 (2023-01-18 17:25_2023-01-18 18:10)')
plt.show()

# %%
