import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import csv
import datetime

# import Tsepelin code
exec(open("/home/franchini/Dropbox/QUEST/code/mod_helium3.py").read())

###########################################################

pressure = 0 # [bar]
density = 6.05e3 # [kg/m^3] Niobium-Titanium (NbTi)   
volume = 0.315e-6  # [m^3] # Bolometer boxes with 0.5mm hole in 100um PET wall. Estimated time constant 1.0s (https://github.com/slazav/cryo_data/blob/main/f4_data.md)

verbose=False
plot=True

###########################################################                                                                                                                

def arguments(argv):

    global filename
    global diameter
    arg_help = "{0} -f <file> -d <diameter [m]>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hf:d:", ["help", "file=", "diameter="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-f", "--file"):
            filename = arg
        elif opt in ("-d", "--diameter"):
            diameter = float(arg)


## More routines: ###########################################

def Width_from_Temperature(Temperature,PressureBar):
    
    gap = energy_gap_in_low_temp_limit(PressureBar)
    width=np.power(Fermi_momentum(PressureBar),2)*Fermi_velocity(PressureBar)*density_of_states(PressureBar)/(2*density*np.pi*diameter)*np.exp(-gap/(Boltzmann_const*Temperature))
    return width

def Temperature_from_Width(Width,PressureBar):
    
    gap = energy_gap_in_low_temp_limit(PressureBar)
    temperature=-gap/(Boltzmann_const*np.log( Width*2*density*np.pi*diameter/(np.power(Fermi_momentum(PressureBar),2)*Fermi_velocity(PressureBar)*density_of_states(PressureBar))))
    return temperature

def DeltaWidth_from_Energy(E,PressureBar,BaseTemperature):
    # Find delta width from the input energy deposition for a certain base temperature

    # find fit line for the Width variation vs Deposited energy for the base temperature
    W0=Width_from_Temperature(BaseTemperature,PressureBar)
        
    DQ = np.array([])  # delta energy [eV]
    DW = np.array([])  # delta width [Hz]    
    
    #for dw in np.arange(0,2.5,0.001):  # Delta(Deltaf)
    for dw in np.arange(0,2.5,0.01):  # Delta(Deltaf)  FASTER
        T2= Temperature_from_Width(W0+dw,PressureBar)
        T1= Temperature_from_Width(W0,PressureBar)
        DQ = np.append(DQ,(heat_capacity_Cv_B_phase_intergral_from_0(T2, PressureBar) - heat_capacity_Cv_B_phase_intergral_from_0(T1, PressureBar)) * volume * 6.242e+18)
        # [eV]
        DW = np.append(DW,dw)
        
    # Draw the plot 
    if verbose:
        plt.plot(DQ/1e3,DW*1e3,label='DQvsDW')
        plt.title('Width variation vs Deposited energy')
        plt.xlim([0, 100])
        plt.ylim([0, 200])
        plt.xlabel('$\Delta$Q [KeV]')
        plt.ylabel('$\Delta(\Delta f)$ [mHz]')
        plt.show()
    
    
    # Fit line to extract the slope alpha: DQ = alpha * DW
    global alpha
    alpha, _ = np.polyfit(DW, DQ, 1)
    
    # Input delta width from input energy
    deltawidth = E/alpha
       
    return deltawidth, alpha

###########################################################                                                                                                                 
if __name__ == "__main__":

    arguments(sys.argv)
    print('File: ', filename)
    print('Diameter: ', diameter)
    
    # Read the file
    f=open(filename,'r')
    lines=f.readlines()
    time=[]
    width_=[]
    for line in lines:
        if line.strip():
            time.append(float(line.split(' ')[0]))
            width_.append(float(line.split(' ')[13]))
            f.close()

    width = np.array([])
    for x in width_:
        width = np.append(width,float(x))

            
    # Fit the width slope and subtract it
    slope=np.polyfit(time, width, 6)
    signal=width-np.polyval(slope, time)

    width_mean = np.nanmean(width)
    print("Mean width:       ", width_mean, " Hz")
    t_base = Temperature_from_Width(width_mean,pressure)
    print("Mean temperature: ", t_base*1e6, " uK")
   
    #Find peaks above 2*rms
    rms = np.sqrt(np.mean(signal**2))
    print('rms:              ',rms)
    print("Find peaks...")
    peaks, _ = find_peaks(signal, height = 2*rms)

    rate=len(peaks)/(max(time)-min(time))

    print("Number of peaks: ", len(peaks))
    print("Start time:      ", datetime.datetime.fromtimestamp(min(time)))
    print("Stop time:       ", datetime.datetime.fromtimestamp(max(time)))
    print("Total time:      ", max(time)-min(time), " s")
    print("Rate:            ", rate, " Hz")
    print("Events/minute:   ", rate*60)

    # Plot the subtraction
    plt.title(filename.split("Data/")[1])
    plt.plot(time,width, label='Width')
    plt.plot(time, np.polyval(slope, time), label='fit')
    plt.plot(time, signal,label='Signal')
    plt.plot(time, np.zeros_like(time)+2*rms, "--", color="gray")
    plt.xlabel('time [s]')     
    plt.ylabel('resonance width [Hz]')
    plt.legend()   
    plt.show()


    ##############################################################

    # Rough estimate of the energy threshold at 2rms:
    print('Threshold:       ',rms*2*DeltaWidth_from_Energy(1000,pressure,Temperature_from_Width(width_mean,pressure))[1]*1e-3, " keV")

    # Energy from the model calibration
    alphas=np.full_like(time,0)
    for i in peaks:
        _, alphas[i] = DeltaWidth_from_Energy(1000,pressure,Temperature_from_Width(width[i],pressure))

    energy = signal[peaks]*alphas[peaks]
    
    if plot:
        # Energy vs time
        plt.plot(time,signal*alpha/1e3)
        plt.xlabel('time [s]')
        plt.ylabel('energy [keV]')
        plt.show()
        
        # Energy distribution
        plt.hist(energy/1e3, 100, range=[0, 1000])
        plt.yscale('log')
        #plt.xlim([0, 5000])    
        plt.xlabel('Energy [keV]')
        plt.axvline(x=1311, linestyle="--", color="gray")  # K-40: beta
        plt.axvline(x=728.8, linestyle="--", color="gray") # Pb-214: beta
        plt.show()
