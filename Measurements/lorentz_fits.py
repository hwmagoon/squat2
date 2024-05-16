
## --------------------------------------
## Fit functions for SQUAT data
## [HM] May 2024
## If you are reading this, I'm sorry
## --------------------------------------

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def lorentzian(x, f0, amp, gamma, offset):
    lorentz = amp * (gamma/2/np.pi) / ((gamma/2)**2 + (x-f0)**2)
    return lorentz + offset

## Add two lorentzians together!
def double_lorentzian(x, L_f0, R_f0, amp, gamma, offset):
    return lorentzian(x, L_f0, amp, gamma, 0) + lorentzian(x, R_f0, amp, gamma, 0) + offset


## Curve function needs rough guess of the parameters
## This function isn't great, but it's a start
def guessfit_lorentz(freqs, xi, xq):
    amps = np.sqrt(xi**2 + xq**2)
    nvals = len(freqs)
    if nvals < 16:
        print("Error: not enough data")
        return None
    
    ## Guess offset
    initial_offset = np.mean(amps[:8])
    final_offset = np.mean(amps[-8:])
    offset = 0.5*(initial_offset + final_offset)
    
    ## Guess amplitude and center freq
    dist = amps - offset
    argsort_dist = np.argsort(dist)
    f0  = np.mean(freqs)
    if (np.mean(amps) < offset):     ## negative amplitude
        print(np.mean(amps), offset, "negative")
        amp = np.mean(dist[argsort_dist[:8]])
    elif (np.mean(amps) > offset):   ## positive amplitude
        print(np.mean(amps), offset, "positive")
        print(dist[argsort_dist[-8:]])
        amp = np.mean(dist[argsort_dist[-8:]])
    else:
        print("Error: curve is poorly centered or something")
        print(np.mean(amps))
        print(offset)
        return None
    return {"g_f0": f0, "g_amp": amp, "g_gamma": 0.1, "g_offset": offset}

## uses scipy curve_fit to fit a lorentzian to the data
def curvefit_lorentz(freqs, xi, xq, fit_params, plot=True, plot_title=None):
    amps = np.sqrt(xi**2 + xq**2)
    g_f0 = fit_params["g_f0"]
    g_amp = fit_params["g_amp"]
    g_gamma = fit_params["g_gamma"]
    g_offset = fit_params["g_offset"]
    
    popt, pcov = curve_fit(lorentzian, freqs, amps, p0=(g_f0, g_amp, g_gamma, g_offset))
    
    ## save fits to parameter dict
    fit_params["f_f0"]     = popt[0]
    fit_params["f_amp"]    = popt[1]
    fit_params["f_gamma"]  = popt[2]
    fit_params["f_offset"] = popt[3]
    fit_params["f_err"] = np.sqrt(np.diag(pcov))
    
    if(plot):
        plt.plot(freqs, amps, '.', label='Data')
        #plt.plot(freqs, lorentzian(freqs, fit_params["g_f0"], fit_params["g_amp"], fit_params["g_gamma"], fit_params["g_offset"] ), label='Guess', linewidth=2.5, ls="--")
        plt.plot(freqs, lorentzian(freqs, fit_params["f_f0"], fit_params["f_amp"], fit_params["f_gamma"], fit_params["f_offset"] ), label='Fit', linewidth=2.5, color='indigo')
        plt.axvline(fit_params["f_f0"], label=f"{round(fit_params['f_f0'],2)} MHz", ls="--", color="black")
        plt.legend()
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("Magnitude [a.u.]")
        plt.title(plot_title + f" ; Q = {fit_params['f_f0']/fit_params['f_gamma']}")
        plt.show()
    
    return fit_params

## same thing but for double lorentzian
def curvefit_double_lorentz(freqs, xi, xq, fit_params, plot=True, plot_title=" "):
    amps = np.sqrt(xi**2 + xq**2)
    g_L_f0 = fit_params["g_f0"]+4
    g_R_f0 = fit_params["g_f0"]-4
    g_amp = fit_params["g_amp"]
    g_gamma = fit_params["g_gamma"]
    g_offset = fit_params["g_offset"]

    popt, pcov = curve_fit(double_lorentzian, freqs, amps, p0=(g_L_f0, g_R_f0, g_amp, g_gamma, g_offset))
        
    ## save fits to parameter dict
    fit_params["f_L_f0"]     = popt[0]
    fit_params["f_R_f0"]     = popt[1]
    fit_params["f_amp"]    = popt[2]
    fit_params["f_gamma"]  = popt[3]
    fit_params["f_offset"] = popt[4]

    
    if(plot):
        plt.plot(freqs, amps, '.', label='Data')
        #plt.plot(freqs, lorentzian(freqs, fit_params["g_f0"], fit_params["g_amp"], fit_params["g_gamma"], fit_params["g_offset"] ), label='Guess', linewidth=2.5, ls="--")
        plt.plot(freqs, double_lorentzian(freqs, fit_params["f_L_f0"], fit_params["f_R_f0"], fit_params["f_amp"], fit_params["f_gamma"], fit_params["f_offset"] ), label='Fit', linewidth=2.5, color='indigo')
        plt.axvline(fit_params["f_L_f0"], label=f"{round(fit_params['f_L_f0'],2)} MHz", ls="--", color="black")
        plt.axvline(fit_params["f_R_f0"], label=f"{round(fit_params['f_R_f0'],2)} MHz", ls="--", color="grey")
        plt.legend()
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("Magnitude [a.u.]")
        plt.title(plot_title + f" ; Q = {fit_params['f_L_f0']/fit_params['f_gamma']}")
        plt.show()
    
    return fit_params


## Calls the guess function then scipy fit function
def fit_lorentz(freqs, xi, xq, plot=True, plot_title=None):
    guess_fits = guessfit_lorentz(freqs, xi, xq)
    fit_params = curvefit_lorentz(freqs, xi, xq, guess_fits, plot=plot, plot_title=plot_title)
    return(fit_params)

def fit_double_lorentz(freqs, xi, xq, plot=True, plot_title=" "):
    guess_fits = guessfit_lorentz(freqs, xi, xq)
    fit_params = curvefit_double_lorentz(freqs, xi, xq, guess_fits, plot=plot, plot_title=plot_title)
    return(fit_params)