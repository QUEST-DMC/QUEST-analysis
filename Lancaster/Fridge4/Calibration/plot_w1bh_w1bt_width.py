"""
Useful
Produces plots for bolometer 1. Time dependence of heater power, width of bolometer thermometer and corresponding temperature.
"""
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

# produce a subplot of time dependence of width of bolometer thermometer
# and time dependence of bolometer heater power  
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Bolometer 1 2023-01-18 17:25_2023-01-18 18:10')
ax1.plot(w1bt_time, w1bt_width)
ax1.set_title('w1bt')
ax1.set_ylabel('resonance width (Hz)')
ax1.set_xlabel('time (s)')
ax2.plot(h_time, h_pwr)
ax2.set_xlabel('time (s)')
ax2.set_ylabel('heater power')
ax2.set_title('w1bh')
plt.show()

#convert from width to temperature 
import functions as fn
w1bt_temp=[]
for width in w1bt_width:
    w1bt_temp.append(fn.Temperature_from_Width(width, 0)[0])

# plots time dependence of bolometer thermometer width 
plt.figure(2)
plt.plot(w1bt_time, w1bt_width)
# calculate the relative temperature level from which to find the temp change 
# take average of last 10 points of width 
# this is a straight line from start time, mean of first 10 widths to end time, mean of last ten widths 
plt.plot([w1bt_time[0], w1bt_time[-1]], [np.mean(w1bt_width[0:9]), np.mean(w1bt_width[-11:-1])])
plt.title('w1bt 2023-01-18 17:25_2023-01-18 18:10')
plt.ylabel('resonance width (Hz)')
plt.xlabel('time (s)')
plt.show()

#calculate temp change 
thermal_conductance=9.09e-7 #W/K , 9.09e-10 W/mK for cell 1 
temp_change=h_pwr/thermal_conductance

# plot the time dependence of temperature change recorded by bolometer thermometer on same axes as temp change line
fig,ax = plt.subplots()
ax.plot(w1bt_time, w1bt_temp, color='blue')
ax.plot([w1bt_time[0], w1bt_time[-1]], [np.mean(w1bt_temp[0:9]), np.mean(w1bt_temp[-11:-1])])
ax.set_title('w1bt temp and temp change from w1bh power 2023-01-18 17:25_2023-01-18 18:10')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (K)", color='blue')
# twin object for two different y-axis
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(h_time, temp_change, color='red')
# ax2.plot([w1bt_time[0], w1bt_time[-1]], [grad*np.mean(w1bt_temp[0:9]), grad*np.mean(w1bt_temp[-11:-1])])
ax2.set_ylabel("temperature change (K)", color='red')
plt.show()

# # calculate the relative temperature level from which to find the temp change 
# # take average of last 10 points of width 
# # this is a straight line from start time, mean of first 10 widths to end time, mean of last ten widths 
# plt.plot([w1bt_time[0], w1bt_time[-1]], [np.mean(w1bt_width[0:9]), np.mean(w1bt_width[-11:-1])])


#     n_time=n[:,0]
#     print('hi')
#     print(n_time)

#make a 1d fit for the width vs time for the parasitic heating
# find the 'flat' parts of the plot 
# 3 parts 
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
# Take the absolute difference of time points - t1 and time points - t2
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

#get the corresponding widths for the indices of the 'flat'
w1bt_flat_width_1=w1bt_width[0:index_tf1]
w1bt_flat_width_2=w1bt_width[index_ti2:index_tf2]
w1bt_flat_width_3=w1bt_width[index_ti3:-1]
w1bt_flat_width=np.concatenate((w1bt_flat_width_1, w1bt_flat_width_2, w1bt_flat_width_3), axis=None)

#make a 1d fit for 'flat' width sections 
# polynomial fit of x against y (temp values), 1st order polynomial
z =np.polyfit(w1bt_flat_time-w1bt_time[0], w1bt_flat_width, 1)
p = np.poly1d(z)
print("p =",p)
# creates a linspace suitable for the length of the displayed fit line
xp = np.linspace(0, w1bt_time[-1]-w1bt_time[0], 2220)

p1=p-12.53676
print('p1 fudged', p1)

#plot width vs time for w1bt as width changes by a greater percentage 
# plot the time dependence of width recorded by bolometer thermometer on same axes as temp change line
fig,ax = plt.subplots()
ax.plot(w1bt_time-w1bt_time[0], w1bt_width, '.', xp, p(xp), color='g', markerfacecolor='blue', markeredgecolor='blue')
#ax.plot(w1bt_flat_time-w1bt_time[0], w1bt_flat_width, '.', xp, p(xp))
ax.set_title('w1bt width and w1bh temp change 2023-01-18 17:25_2023-01-18 18:10')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Resonance width (Hz)", color='blue')
#twin object for two different y-axis
ax2=ax.twinx()
# make a plot with different y-axis for temp change 
#ax2.plot(h_time-h_time[0], temp_change*1e6,  xp, p1(xp), color='red' )
ax2.plot(h_time-h_time[0], temp_change*1e6 + p1(xp), color='red' )
ax2.set_ylabel("temperature change (uK)", color='red')
plt.show()

# # make the fit in temperature 
# #get the corresponding temperatures for the indices of the 'flat'
# w1bt_flat_temp_1=w1bt_temp[0:index_tf1] 
# w1bt_flat_temp_2=w1bt_temp[index_ti2:index_tf2]
# w1bt_flat_temp_3=w1bt_temp[index_ti3:-1]
# w1bt_flat_temp=np.concatenate((w1bt_flat_temp_1, w1bt_flat_temp_2, w1bt_flat_temp_3), axis=None)

# #make a 1d fit for 'flat' width sections 
# # polynomial fit of x against y (temp values), 1st order polynomial
# z2 =np.polyfit(w1bt_flat_time-w1bt_time[0], w1bt_flat_temp*1e6, 1)
# p2 = np.poly1d(z2)
# print("p2 =",p2)
# # creates a linspace suitable for the length of the displayed fit line
# xp = np.linspace(0, w1bt_time[-1]-w1bt_time[0], 100)


