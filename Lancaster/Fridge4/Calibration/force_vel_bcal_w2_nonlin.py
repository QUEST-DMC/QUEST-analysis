"""
Week 2 data 
For the calibration of bolometer 1
data from Fri Feb 10 2023 00:24:00 to 00:32:00 GMT+0000
plot force velocity graph 
"""
#%%# ------------------------ Load Data
#import required modules
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
print(mag)
print(x)

length = 0.00115 # in metres 1.15mm 

force=mag*length*drive_I * np.sqrt(2)

#[force] = tesla * metres * Amps rms 
# 1 kg⋅s−2⋅A−1 * m * A 
# kg s-2 m = Newtons 

# is amps rms okay???

geo=1

vel=np.hypot(x, y)*((geo)/(mag*length)) * np.sqrt(2)

# V rms * (1/tesla 1/m)
# V 1 kg-1 ⋅s+2⋅A+1 m-1
# 1 kg m2 s-3 A -1 kg-1 ⋅s+2⋅A+1 m-1
# m1 s-1

# print(drive_I.argmin())

plt.figure(1)
plt.plot(force, vel)
plt.title('Force Velocity W1BT Feb 10 2023 00:24:00 to 00:32:00')
plt.xlabel('Force (N)')
plt.ylabel('Velocity (m/s)')
plt.show()
