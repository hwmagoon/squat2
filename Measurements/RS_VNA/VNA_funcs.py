import numpy as np
import matplotlib.pyplot as plt


import os
import glob
import datetime
from time import *

#from ZNB import ZNB20


## ------------------
## Import Functions
## ------------------
def write_file(data, filepath, filename=None):
    filename = data["series"] + "_" + filename
    print("Storing data to filepath: ", filepath)
    print("Storing data to filename: ", filename)
    if not os.path.isdir(filepath):
        os.makedirs(filepath)
    np.savez(os.path.join(filepath, filename), data=data)
    return filepath, filename

def read_file(filepath, filename):
    readin = np.load(os.path.join(filepath, filename), allow_pickle=True)
    return readin['data'].item()

## ------------------
## Plotting Functions
## ------------------
def plot_amp(data, filepath=None, filename=None, save_fig=True):
    plt.plot(data["freqs"], data["amps"])
    plt.title(f"{data['series']}, device power={data['power_at_device']} dBm \n IFBW={data['bandwidth']} Hz, avgs={data['averages']}")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel(f"Amplitude (dB), relative to {data['vna_power']} dBm at VNA")
    if save_fig:
        if filepath is None:
            print("Error: no filepath specified.  Either specify a filepath in the arguments or set save_fig=False")
            return
        if filename is None:
            filename = data["series"] + "_amp.pdf"
        else:
            filename = data["series"] + "_amp_" + filename + ".pdf"
        plt.savefig(os.path.join(filepath, filename))
    plt.show()
    return


def plot_phase(data, filepath=None, filename=None, save_fig=True):
    plt.plot(data["freqs"], data["phases"])
    plt.title(f"{data['series']}, device power={data['power_at_device']} dBm \n IFBW={data['bandwidth']} Hz, avgs={data['averages']}")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (rad)")
    if save_fig:
        if filepath is None:
            print("Error: no filepath specified.  Either specify a filepath in the arguments or set save_fig=False")
            return
        if filename is None:
            filename = data["series"] + "_phase.pdf"
        else:
            filename = data["series"] + "_phase_" + filename + ".pdf"
        plt.savefig(os.path.join(filepath, filename))
    plt.show()
    return

## ------------------
## Correcting phase for line delay  
## ------------------
def unwrap_phases(data, force_line_delay_val=None):
    ## Set up output containers, unwrap phases (i.e. remove 2pi jumps)
    corrected_phases = np.zeros(len(data["phases"]-1))
    unwrapped = np.unwrap(data["phases"])
    ## Give user the option to manually set a line delay
    ## If no value is supplied, calculate the line delay from the data
    if force_line_delay_val is None:
        line_delay = np.mean(unwrapped[1:]-unwrapped[:-1])/(data["freqs"][1:]-data["freqs"][:-1])
        line_delay = np.mean(line_delay)
        print("Calculated line delay:", line_delay)
    else:
         print("Manually set line delay:", force_line_delay_val)
         line_delay = force_line_delay_val
    for n, phase in enumerate(unwrapped):
            corrected_phases[n] = phase - (data["freqs"][n] - data["freqs"][0])*line_delay
    return corrected_phases, line_delay

def plot_unwrapped_phase(data, filepath=None, filename=None, save_fig=True, force_line_delay_val=None):
    ## Unwrap phases
    corrected_phases, line_delay = unwrap_phases(data, force_line_delay_val)
    ## Plot unwrapped phases
    plt.plot(data["freqs"], corrected_phases)
    plt.title(f"{data['series']}, device power={data['power_at_device']} dBm \n IFBW={data['bandwidth']} Hz, avgs={data['averages']}")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Corrected phase (rad)")
    if save_fig:
        if filepath is None:
            print("Error: no filepath specified.  Either specify a filepath in the arguments or set save_fig=False")
            return
        if filename is None:
            filename = data["series"] + "_phase.pdf"
        else:
            filename = data["series"] + "_phase_" + filename + ".pdf"
        plt.savefig(os.path.join(filepath, filename))
    plt.show()
    return


## Handle power conversion
def dBm_to_mW(dBm):
    return 10**(dBm/10)

def mW_to_dBm(mW):
    return 10*np.log10(mW)

def add_powers_dbm(a, b):
    return mW_to_dBm(dBm_to_mW(a) + dBm_to_mW(b))


## ------------------
## Average multiple scans
## ------------------

def average_folder_of_scans(fp):
    flist = glob.glob(fp + '/*')
    nscans = 0
    series_list = []
    for i, fn in enumerate(flist):
        ## Read file
        f = read_file(fp, fn)

        ## Set up using first file
        if i==0:
            freqs = f['freqs']
            amps = f['averages'] * f['amps']
            phases = f['averages'] * f['phases']
            vna_power = f['vna_power']
            power_at_device = f['power_at_device']
            ifbw = f['bandwidth']
            amps = np.zeros(len(f['amps']))
            phases = np.zeros(len(f['phases']))
        else:
            if f['freqs'][0] != freqs[0] or f['freqs'][-1] != freqs[-1] or len(f['freqs']) != len(freqs):
                print('Error: frequency mismatch! in file:', fn)
                #return
            if f['vna_power'] != vna_power:
                print('Error: VNA power mismatch! in file:', fn)
                #return
            if f['power_at_device'] != power_at_device:
                print('Error: power at device mismatch! in file:', fn)
                #return
            if f['bandwidth'] != ifbw:
                print('Error: IF bandwidth mismatch! in file:', fn)
                #return
        series_list.append(f['series'])
        amps += f['averages'] * f['amps']
        phases += f['averages'] * f['phases']
        nscans += f['averages']
        
    ## Take average of amplitude and phase
    amps = amps / nscans
    phases = phases / nscans
    print(f"Folder contains {nscans} scans taken from {min(series_list)} to {max(series_list)}")

    ## Return a dictionary of the average values
    avg_vals = {
        'freqs': freqs,
        'amps': amps,
        'phases': phases,
        'vna_power': vna_power,
        'power_at_device': power_at_device,
        'bandwidth': ifbw,
        'nscans': nscans,
        'series': str(min(series_list)) + '-' + str(max(series_list))
    }
    return avg_vals