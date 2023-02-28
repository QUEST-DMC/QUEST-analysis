"""
Week 2 data 
For the calibration of bolometer 1
data from Fri Feb 10 2023 00:24:00 to 00:32:00 GMT+0000
find temperature from width at lowest drive to sub into eq 1 
new F(v) using terms from Paolo's note
"""
#%%# ------------------------ Load Data from f4wire database
#import required modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import helium 3 library 
import mod_helium3 as mod

#importing data with an irregular number of columns 
# Read the data from the .dat file

# load data using f4wire_get_data function
# gives corrected voltage and drive current 
# https://github.com/slazav/exp_py/blob/main/py/f4wire.md
wire_data = pd.read_csv('data/w1bt_f4wire_get_data_1675988640_1675989120', delimiter=' ', header=None, engine='python')

time=wire_data.iloc[:,0] # time in unix seconds
freq=wire_data.iloc[:,1] # frequency(Hz)
x=wire_data.iloc[:,2] # X(Vrms) 
y=wire_data.iloc[:,3] # Y(Vrms) 
drive_I=wire_data.iloc[:,-1] # D(Vpp or Arms)

mag_data=pd.read_csv('data/demag_pc_f2_get_prev_0_1675988640.000000', delimiter=' ', header=None, engine='python')

mag=mag_data.iloc[0,1]

length = 0.00115 # in metres 1.15mm 

diameter = 4.5e-6 # in metres 4.5 um 

force=mag*length*drive_I * np.sqrt(2)

#[force] = tesla * metres * Amps rms 
# 1 kg⋅s−2⋅A−1 * m * A 
# kg s-2 m = Newtons 

geo=1

vel=np.hypot(x, y)*((geo)/(mag*length)) * np.sqrt(2)

#%%# - Need width - can get from get_range database

#thermometer data, w1bt
w1bt = pd.read_csv('data/w1bt_get_range_1675988640_1675989120', delimiter=' ', header=None, engine='python', names=range(22))
#want 13th column, need to use loc as now a pandas df not np array
w1bt_width=w1bt.loc[:,13] #resonance width in Hz
w1bt_time=w1bt.loc[:,0] #time in unix seconds

# there are small differences in the timestamps recorded in the databases
# off by a decimal place or two. Interpolate to be safe
# gives interpolated values of the drive current of w1bt (timestamps under time variable) at the timestamps saved in w1bt_time
drive_I_interp = np.interp(w1bt_time, time, drive_I)
drive_I_interp=pd.Series(drive_I_interp)

#plot drive current vs width for w1bt to find width at min drive 
plt.figure(1)
plt.plot(drive_I_interp, w1bt_width, '.')
plt.xlabel('Drive Current (Arms)')
plt.ylabel('Width (Hz)')
plt.title('W1BT: Drive Current vs. Width Fri Feb 10 2023 00:24:00 to 00:32:00')
plt.show()

# width at min drive found from plot 
width_smalldrive=14.95

# find temp from width 
import functions

temp_smalldrive=functions.Temperature_from_Width(width_smalldrive,0)
print(temp_smalldrive)
print(type(temp_smalldrive))

#%%# - find velocities less than pair breaking velocity
# function will not fit after pair breaking up tick
# pair breaking at 8.5 mm/s = 0.0085 m/s
vel_85=vel[vel < 0.0085]

# find indices of the velocities below pair breaking 
vel_85_indices=[]

# for index, value in vel_85.items():
#     print(f"Index : {index}, Value : {value}")
for index , value in vel_85.items():
    vel_85_indices.append(index)

# get forces corresponding to indices of velocities below pair breaking 
# make an empty list
force_85=[]

# append the values of force that correspond with the indices of the velocities below pair breaking 
for index in vel_85_indices:
    force_85.append(force.loc[index])

# convert forces below 8.5 mm/s from list into pandas series
force_85 = pd.Series(data=force_85, index=vel_85_indices) 

# for index, value in force_85.items():
#     print(f"Index : {index}, Value : {value}")

#%%# - Eq 1 

# constants 
# gap = gap in low temp limit = 2.25834805e-26 ie 1.76KT
gap = mod.energy_gap_in_low_temp_limit(0) 

k_B = mod.Boltzmann_const #[J/K]
p_F = mod.Fermi_momentum(0) #[kg m s-1]
v_F = 59.03 #[m/s]
N0 = 5.01e37*1e6*1e7 # in SI units

# Use temperature as constant 
T = temp_smalldrive

# variables

# vel =np.hypot(x, y)*((geo)/(mag*length)) * np.sqrt(2)
# amplitude of voltage * (1/mag*length) * peak to peak conversion 
# length, mag and peak to peak conversion are cons
# timestamps of velocity depend on amplitude of voltage timestamps i.e. timestamps of x,y 
# i.e. uses 'time' values from f4wire database 
# force comes from drive_I which also has 'time' timestamps from f4wire database

# plot force=y vs. vel=x
plt.figure(2)
plt.plot(vel, force, '.')
plt.xlabel('Velocity (m/s)')
plt.ylabel('Force (N)')
plt.title('Force Velocity Fri Feb 10 2023 00:24:00 to 00:32:00')
plt.show()

# using fitting function

from scipy.optimize import curve_fit

def fit_function(vel_85,C,lambda_1):
    # Eq 1 from Paolo's note 
    force_func_v = length * C * diameter * np.pi * 0.25 * p_F * v_F * N0 * np.exp(-gap/(k_B*T)) * (1-np.exp((-lambda_1*p_F*vel_85)/(k_B*T)))*k_B*T
    return force_func_v
    
popt, pcov = curve_fit(fit_function, vel_85, force_85)

C,lambda_1 = popt

plt.figure(3)
plt.plot(vel,force, '.', label='Data')
plt.plot(vel_85, fit_function(vel_85,*popt), label='Fitting function')
plt.xlabel('Velocity (m/s)')
plt.ylabel('Force (N)')
plt.title('Force Velocity Eq Fri Feb 10 2023 00:24:00 to 00:32:00')
plt.legend()
plt.show()

# # fitting parameters to manually adjust
# C = 3e9
# lambda_1 = 0.05