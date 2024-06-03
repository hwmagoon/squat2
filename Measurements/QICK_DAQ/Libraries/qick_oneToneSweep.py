import numpy as np
from qick import *
from qick_data import *
from qick_helpers import *

#----------------------------------------------------------------------
#
# qick_oneToneSweep.py
# author: Hannah Magoon
# Jun 2023
# Edited April 2024 @ SLAC
#
# Generalized dataclass for one tone sweeps 
#
#
#----------------------------------------------------------------------

## Make one of these classes for each measurement notebook
class oneToneSweep(QICKdata):
    
    ## Meas_cfg file specific to your measurement
    meas_cfg = { }

    ## This holds everything that isn't in a config file
    ## This includes sweep variables and data
    ## Super important note: don't save as complex values.  Separate into I and Q!!!
    meas_data = { }

    ## Sets software sweep variables
    ## Input sweep_num=None or 1 for 1D sweep or x-axis of 2D sweep
    ## Input sweep_num=2 for y-axis of 2D sweep
    def set_soft_sweep_vals(self, npts, valStart, valStop, sweepVarName, sweep_num=None):
        if(sweepVarName=="qu_pulse_freq"):
            print("Error:  This is a one-tone dataclass and you are trying to take a 2-tone acquisition")
            print("try again")
            return
        if (sweep_num is not None) and (sweep_num > 2):
            print("Error: Only 1D and 2D sweeps are currently supported")
            print("Set 'sweep_num' to either 1 or 2 and rerun")
            return
        if (sweep_num==1) or ((sweep_num is None) and (self.meas_data.get('x_sweepVarName') is None)):
            print("Writing x-axis sweep values")
            self.meas_data["x_sweepVals"] = np.linspace(valStart,valStop,npts,endpoint=True)
            self.meas_data["x_sweepVarName"] = sweepVarName
        else:
            print("Writing y-axis sweep values")
            self.meas_data["y_sweepVals"] = np.linspace(valStart,valStop,npts,endpoint=True)
            self.meas_data["y_sweepVarName"] = sweepVarName
        return
      

    ## Prepares to run a measurement
    def setup_meas(self, soc,soccfg):   
        self.check_time_params()
        self.convert_sweep_time_vars(soccfg)
        convert_time_vars(soccfg, self, verbose=False)
        config = {**self.hw_cfg,**self.meas_cfg,**self.rfb_cfg}   ## Make one huge config dict
        return config
    
    
    ## Calls the acquisition function to sweep across 1 value in software
    def do_soft_1D_measurement(self, soc, soccfg, datapath=None, forceInt=False, overwrite_existing_data=False, save_data=True, do_decimated=True):   
        ## Sanity check inputs
        if save_data and datapath==None:
            print("Error: no datapath provided.  Either provide a datapath argument, or rerun the function with save_data=False")
            return
        elif datapath is not None:
            if datapath[0:1] == "./":
                print("Error: you provided a relative datapath.  Rerun with a total datapath")
                return        
        if "x_sweepVals" not in self.meas_data.keys():
            print("Error: x sweep values not found")
            return
        elif "y_sweepVals" in self.meas_data.keys():
            print("Error: y sweep values were provided, but you are running a 1D sweep")
            print("measurement cancelled to prevent future confusion")
            return
        elif "xi" in self.meas_data.keys() and not overwrite_existing_data:
            print("Error: data already exists in this measurement object.")
            print("to run acquisition, either initialize a new object")
            print("or rerun this function with argument overwrite_existing_data=True")
            return
        elif (self.check_for_qubit_params())== True:
            print("Error: you are setting qubit parameters for a one tone sweep")
            print("Measurement cancelled")
            return
        elif (self.meas_data["x_sweepVarName"][0:1] == "qu"):
            print("Error: This is a single tone sweep.  You are trying to sweep over a qubit pulse variable")
            return
        
        ## Prepare for measurement
        print("Starting measurement setup")
        config = self.setup_meas(soc,soccfg)

        ## Actually do the measurement
        print("Starting measurement")
        [xi, xq, output_decimated] = oneTone_oneSoftSweep(soc, soccfg, config, sweepVarName=self.meas_data["x_sweepVarName"],sweepVals=self.meas_data["x_sweepVals"], forceInt=forceInt, progress=False, do_decimated=do_decimated)
        print("Measurement complete")
        
        ## Store data in class
        self.meta["sweep_type"] = "1D"
        self.meas_data["xi"]    = xi
        self.meas_data["xq"]    = xq
        self.meas_data["output_decimated"] = output_decimated[0]
        
        ## Save data
        if save_data:
            self.write_H5(datapath)        
        return
    
    
    ## Sweeps any two variables in software
    def do_soft_2D_measurement(self, soc, soccfg, datapath=None, x_forceInt=False, y_forceInt=False, overwrite_existing_data=False, save_data=True, do_decimated=True):        
        ## Sanity check inputs
        if save_data and datapath==None:
            print("Error: no datapath provided.  Either provide a datapath argument, or rerun the function with save_data=False")
            return
        elif datapath is not None:
            if datapath[0:1] == "./":
                print("Error: you provided a relative datapath.  Rerun with a total datapath")
                return        
        if "x_sweepVals" not in self.meas_data.keys():
            print("Error: x sweep values not found")
            return
        elif "y_sweepVals" not in self.meas_data.keys():
            print("Error: y sweep values not found")
            return
        elif "xi" in self.meas_data.keys() and not overwrite_existing_data:
            print("Error: data already exists in this measurement object.")
            print("to run acquisition, either initialize a new object")
            print("or rerun this function with argument overwrite_existing_data=True")
            return
        elif (self.check_for_qubit_params())== True:
            print("Error: you are setting qubit parameters for a one tone sweep")
            print("Measurement cancelled")
            return
        elif (self.meas_data["x_sweepVarName"][0:1] == "qu") or (self.meas_data["y_sweepVarName"][0:1] == "qu"):
            print("Error: This is a single tone sweep.  You are trying to sweep over a qubit pulse variable")
            return
        
        ## Prepare for measurement
        print("Starting measurement setup")
        config = self.setup_meas(soc,soccfg)

        ## Actually do the measurement
        print("Starting measurement")
        [xi, xq, output_decimated] = oneTone_twoSoftSweep(soc, soccfg, config, x_sweepVarName=self.meas_data["x_sweepVarName"], x_sweepVals=self.meas_data["x_sweepVals"], y_sweepVarName=self.meas_data["y_sweepVarName"], y_sweepVals=self.meas_data["y_sweepVals"], x_forceInt=x_forceInt, y_forceInt=y_forceInt, do_decimated=do_decimated)
        print("Measurement complete")
    
        ## Store data in class
        self.meta["sweep_type"] = "2D"
        self.meas_data["xi"] = xi
        self.meas_data["xq"] = xq
        self.meas_data["output_decimated"] = output_decimated[0]
        
        ## Save data
        if save_data:
            self.write_H5(datapath)        
        return
    
    
    ## Plots a 1D sweep
    def plot_1D_measurement(self, title=None):
        x_in_us = False
        if title is not None:
            title_string = title + "\n" + self.meta["series"]
        else:
            title_string = self.meta["series"]
        if "x_sweepVals" not in self.meas_data.keys():
            print("Error: data not found")
            return
        elif "xi" not in self.meas_data.keys():
            print("Error: data not found")
            return        
        elif "y_sweepVals" in self.meas_data.keys():
            print("Error: data is 2D, not 1D")
            return
        elif "is_x_sweep_in_us" in self.meas_data.keys():
            print("Plotting time variable in us, not clock ticks")
            x_in_us = True
            
        if x_in_us:
            values = self.meas_data["x_sweepVals_us"]
            var    = self.meas_data["x_sweepVarName_us"]
        else:
            values = self.meas_data["x_sweepVals"]
            var    = self.meas_data["x_sweepVarName"]
        x      = self.meas_data["xi"] + 1j*self.meas_data["xq"]
        amps = np.abs(x)
        plt.plot(values, amps, label="Amplitude")
        plt.plot(values, x.real, label="I")
        plt.plot(values, x.imag, label="Q")
        if title is not None:
            title_string = title + "\n" + self.meta["series"]
        else:
            title_string = self.meta["meas_type"] + "\n" + self.meta["series"]        
        plt.ylabel("adc units")
        plt.xlabel(var)
        plt.title(title_string)
        plt.legend()
        plt.show()
        return  
    
    ## Plots a 2D sweep
    def plot_2D_heatmap(self, title=None, plot_amp=True, plot_phase=True):
        x_in_us = False
        y_in_us = False
        if title is not None:
            title_string = title + "\n" + self.meta["series"]
        else:
            title_string = self.meta["series"]
        if "xi" not in self.meas_data.keys():
            print("Error: data not found")
            return            
        elif "x_sweepVals" not in self.meas_data.keys():
            print("Error: data not found")
            return
        elif "y_sweepVals" not in self.meas_data.keys():
            print("Error: data is not 2D")
            return
        elif "is_x_sweep_in_us" in self.meas_data.keys():
            if(self.meas_data["is_x_sweep_in_us"]) == 1:
                print("Plotting x axis variable in us, not clock ticks")
                x_in_us = True
        elif "is_y_sweep_in_us" in self.meas_data.keys():
            if(self.meas_data["is_y_sweep_in_us"]) == 1:
                print("Plotting y axis variable in us, not clock ticks")
                y_in_us = True
                
        ## Pull data from dict        
        if x_in_us:
            x_sweepVarName = self.meas_data["x_sweepVarName_us"]
            x_sweepVals = self.meas_data["x_sweepVals_us"]
        else:
            x_sweepVarName = self.meas_data["x_sweepVarName"]
            x_sweepVals = self.meas_data["x_sweepVals"]            
        if y_in_us:
            y_sweepVarName = self.meas_data["y_sweepVarName_us"]
            y_sweepVals = self.meas_data["y_sweepVals_us"]  
        else:
            y_sweepVarName = self.meas_data["y_sweepVarName"]
            y_sweepVals = self.meas_data["y_sweepVals"]                
        xi = self.meas_data["xi"]
        xq = self.meas_data["xq"]
        amps = (np.abs(xi + 1j*xq))
        phases = (np.angle(xi + 1j*xq))
        
        ## Do plots
        if(plot_amp):
            a_title_string = "AMPLITUDE\n" + title_string
            plt.subplot(111,title=title, xlabel=x_sweepVarName, ylabel=y_sweepVarName)
            bounds = [min(x_sweepVals),max(x_sweepVals), min(y_sweepVals), max(y_sweepVals)]
            im = plt.imshow((amps),origin='lower',extent=bounds,aspect='auto')  
            plt.colorbar(im,label="Amplitude")
            plt.title(a_title_string)
            plt.show()
        if(plot_phase):
            p_title_string = "PHASE\n" + title_string
            plt.subplot(111,title=title, xlabel=x_sweepVarName, ylabel=y_sweepVarName)
            bounds = [min(x_sweepVals),max(x_sweepVals), min(y_sweepVals), max(y_sweepVals)]
            im = plt.imshow((phases),origin='lower',extent=bounds,aspect='auto')  
            plt.colorbar(im,label="Phase")
            plt.title(p_title_string)
            plt.show()
        return
    
    ## Plots a series of nTraces as stacked 1D sweeps
    def plot_2D_stacked(self, nTraces=10, title=None, plot_amp=True, plot_phase=True):
        x_in_us = False
        y_in_us = False        
        if "xi" not in self.meas_data.keys():
            print("Error: data not found")
            return            
        elif "x_sweepVals" not in self.meas_data.keys():
            print("Error: data not found")
            return
        elif "y_sweepVals" not in self.meas_data.keys():
            print("Error: data is not 2D")
            return
        total_y_traces = len(self.meas_data["y_sweepVals"])
        if nTraces > total_y_traces:
            print("Warning: you requested", nTraces, "traces but only", total_y_traces, "were found in the dataset")
            nTraces = total_y_traces
        elif "is_x_sweep_in_us" in self.meas_data.keys():
            if(self.meas_data["is_x_sweep_in_us"]) == 1:
                print("Plotting x axis variable in us, not clock ticks")
                x_in_us = True
        elif "is_y_sweep_in_us" in self.meas_data.keys():
            if(self.meas_data["is_y_sweep_in_us"]) == 1:
                print("Plotting y axis variable in us, not clock ticks")
                y_in_us = True        
        ## Pull data from dict        
        if x_in_us:
            x_sweepVarName = self.meas_data["x_sweepVarName_us"]
            x_sweepVals = self.meas_data["x_sweepVals_us"]
        else:
            x_sweepVarName = self.meas_data["x_sweepVarName"]
            x_sweepVals = self.meas_data["x_sweepVals"]            
        if y_in_us:
            y_sweepVarName = self.meas_data["y_sweepVarName_us"]
            y_sweepVals = self.meas_data["y_sweepVals_us"]  
        else:
            y_sweepVarName = self.meas_data["y_sweepVarName"]
            y_sweepVals = self.meas_data["y_sweepVals"]
        if title is not None:
            title_string = title + "\n" + self.meta["series"]
        else:
            title_string = "Stacked Sweeps, varying " + y_sweepVarName + "\n" + self.meta["series"]
        x = self.meas_data["xi"] + 1j*self.meas_data["xq"]
        amps = np.abs(x)
        phase = np.angle(x)
        
        ## do plot
        skip_n_traces = int((total_y_traces-nTraces)/(total_y_traces)) + 1
        if(plot_amp):
            curr_trace = 0
            while curr_trace < total_y_traces:
                plt.plot(x_sweepVals, amps[:][curr_trace], label=y_sweepVals[curr_trace])
                curr_trace += skip_n_traces
            plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
            plt.title(title_string)
            plt.xlabel(x_sweepVarName)
            plt.ylabel("Amplitude [a.u.]")
            plt.show()
        if(plot_phase):
            curr_trace = 0
            while curr_trace < total_y_traces:
                plt.plot(x_sweepVals, phase[:][curr_trace], label=y_sweepVals[curr_trace])
                curr_trace += skip_n_traces
            plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
            plt.title(title_string)
            plt.xlabel(x_sweepVarName)
            plt.ylabel("Phase")
            plt.show()
        return
    
    ## Plots a decimated sweep
    def plot_decimated(self):
        title_string = "Decimated Output" + "\n" + self.meta["series"]
        plt.plot(np.abs(self.meas_data["output_decimated"][0]+1j*self.meas_data["output_decimated"][1]), label="amps")
        plt.plot(self.meas_data["output_decimated"][0], label="I")
        plt.plot(self.meas_data["output_decimated"][1], label="Q")

        plt.legend()
        plt.ylabel("adc units")
        plt.xlabel("clock ticks")
        plt.title(title_string)
        plt.show()
        return
    
    ## Returns 'true' if qubit params are being set
    def check_for_qubit_params(self):
        keys = self.meas_cfg.keys()
        keys = list(keys)
        data_dict_keys =  self.meas_data.keys()
        if "x_sweepVarName" in data_dict_keys:
            keys = keys + [self.meas_data["x_sweepVarName"]]
        if "y_sweepVarName" in data_dict_keys:
            keys = keys + [self.meas_data["y_sweepVarName"]]
        if self.hw_cfg["qu_ch"] != None:
            print("Error: qubit channel is not set to None in hw_cfg dict")
            return True
        if "qu_pulse_style" in keys:
            print("Error: qu_pulse_style is set, but you are running a oneTone measurement")
            return True
        if "qu_gain" in keys:
            print("Error: qu_gain is set, but you are running a oneTone measurement")
            return True
        if "qu_length_us" in keys:
            print("Error: qu_length_us is set, but you are running a oneTone measurement")
            return True
        if "qu_length" in keys:
            print("Error: qu_length is set, but you are running a oneTone measurement")
            return True
        if "qu_phase" in keys:
            print("Error: qu_phase is set, but you are running a oneTone measurement")
            return True
        if "qu_sigma_us" in keys:
            print("Error: qu_sigma_us is set, but you are running a oneTone measurement")
            return True
        if "qu_sigma" in keys:
            print("Error: qu_sigma is set, but you are running a oneTone measurement")
            return True
        if "qu_pulse_freqF" in keys:
            print("Error: qu_pulse_freq is set, but you are running a oneTone measurement")
            return True
        return False
    
    
    ## Returns 'true' if you set a value in clock ticks
    def check_time_params(self):
        keys = self.meas_cfg.keys()
        if "relax_delay" in keys and "relax_delay_us" not in keys:
            print("Warning: you are setting relax_delay in clock ticks, not us. This makes Ryan sad.")
            print("next time, set parameter relax_delay_us instead")
            return False
        if "adc_trig_offset" in keys and "adc_trig_offset_us" not in keys:
            print("Warning: you are setting adc_trig_offset in clock ticks, not us. This makes Ryan sad.")
            print("next time, set parameter adc_trig_offset_us instead")
            return False
        if "readout_length" in keys and "readout_length_us" not in keys:
            print("Warning: you are setting readout_length in clock ticks, not us. This makes Ryan sad.")
            print("next time, set parameter readout_length_us instead")
            return False
        if "sync_all" in keys and "sync_all_us" not in keys:
            print("Warning: you are setting sync_all in clock ticks, not us. This makes Ryan sad.")
            print("next time, set parameter sync_all_us instead")
            return False
        if "res_length" in keys and "res_length_us" not in keys:
            print("Warning: you are setting res_length in clock ticks, not us. This makes Ryan sad.")
            print("next time, set parameter res_length_us instead")
            return False
        return True
    
    ## Rotates x and y axes of a 2D scan
    def swap_x_and_y_data(self):
        contains_data = True
        ## Sanity check
        if "xi" not in self.meas_data.keys():
            print("Warning: data not found reorienting axes only")
            contains_data = False
        elif "x_sweepVals" not in self.meas_data.keys():
            print("Error: x-sweep not found")
            return
        elif "y_sweepVals" not in self.meas_data.keys():
            print("Error: data is not 2D")
            return
        print("Swapping x and y data")
        ## Do the swappy thing
        temp_sweepVals = self.meas_data["x_sweepVals"]
        self.meas_data["x_sweepVals"] = self.meas_data["y_sweepVals"]
        self.meas_data["y_sweepVals"] = temp_sweepVals
        temp_sweep_var_name = self.meas_data["x_sweepVarName"]
        self.meas_data["x_sweepVarName"] = self.meas_data["y_sweepVarName"]
        self.meas_data["y_sweepVarName"] = temp_sweep_var_name
        ## rename us stored data if applicable
        x_to_temp_to_y = False
        if "is_x_sweep_in_us" in self.meas_data.keys():
            print("Noting that x data is in us")
            self.meas_data["is_temp_sweep_in_us"] = self.meas_data.pop("is_x_sweep_in_us")
            self.meas_data["temp_sweepVals_us"] = self.meas_data.pop("x_sweepVals_us")
            self.meas_data["temp_sweepVarName_us"] = self.meas_data.pop("x_sweepVarName_us")
            x_to_temp_to_y = True
        ## rename y variables as x variables
        if "is_y_sweep_in_us" in self.meas_data.keys():
            print("Noting that y data is in us")
            self.meas_data["is_x_sweep_in_us"] = self.meas_data.pop("is_y_sweep_in_us")
            self.meas_data["x_sweepVals_us"] = self.meas_data.pop("y_sweepVals_us")
            self.meas_data["x_sweepVarName_us"] = self.meas_data.pop("y_sweepVarName_us")  
        if x_to_temp_to_y:
            self.meas_data["is_y_sweep_in_us"] = self.meas_data.pop("is_temp_sweep_in_us")  
            self.meas_data["y_sweepVals_us"] = self.meas_data.pop("temp_sweepVals_us")  
            self.meas_data["y_sweepVarName_us"] = self.meas_data.pop("temp_sweepVarName_us")         
        ## Flip the data, if applicable
        if contains_data:
            self.meas_data["xi"] = np.transpose(self.meas_data["xi"])
            self.meas_data["xq"] = np.transpose(self.meas_data["xq"])
        return
    
    
    ## Converts a sweep from us to clock ticks
    def convert_sweep_time_vars(self, soccfg):   
        ## Pull names of items in measurement config dict
        keys = self.meas_data.keys()

        ## Check if x sweep is set
        if "x_sweepVarName" in keys:
            x_sweepVarName = self.meas_data["x_sweepVarName"]

            ## If it ends in "_us", then this needs to be converted
            if(x_sweepVarName[-3:] == "_us"):
                print("Converting x sweep from us to clock ticks")

                ## Make an array to hold converted sweep vals
                converted_sweep_vals = np.zeros(len(self.meas_data["x_sweepVals"]))

                ## Iterate through, convert from us to clock ticks
                for i, val in enumerate(self.meas_data["x_sweepVals"]):
                    if (x_sweepVarName[:1] == "qu"):
                        converted_sweep_vals[i] = soccfg.us2cycles(val,gen_ch=self.hw_cfg["qu_ch"])
                    else:
                        converted_sweep_vals[i] = soccfg.us2cycles(val,gen_ch=self.hw_cfg["res_ch"])

                ## Overwrite sweep values with us version
                print("Saving unconverted sweep as x_sweepVals_us")
                self.meas_data["is_x_sweep_in_us"] = 1
                self.meas_data["x_sweepVarName_us"] = x_sweepVarName
                self.meas_data["x_sweepVals_us"] = self.meas_data["x_sweepVals"]
                self.meas_data["x_sweepVarName"] = x_sweepVarName[:-3]
                self.meas_data["x_sweepVals"] = converted_sweep_vals            

        ## Check if y sweep is set
        if "y_sweepVarName" in keys:
            y_sweepVarName = self.meas_data["y_sweepVarName"]

            ## If it ends in "_us", then this needs to be converted
            if(y_sweepVarName[-3:] == "_us"):
                print("Converting y sweep from us to clock ticks")

                ## Make an array to hold converted sweep vals
                converted_sweep_vals = np.zeros(len(self.meas_data["y_sweepVals"]))

                ## Iterate through, convert from us to clock ticks
                for i, val in enumerate(self.meas_data["y_sweepVals"]):
                    if (y_sweepVarName[:1] == "qu"):
                        converted_sweep_vals[i] = soccfg.us2cycles(val,gen_ch=self.hw_cfg["qu_ch"])
                    else:
                        converted_sweep_vals[i] = soccfg.us2cycles(val,gen_ch=self.hw_cfg["res_ch"])

                ## Overwrite sweep values with us version
                print("Saving unconverted sweep as y_sweepVals_us")
                self.meas_data["is_y_sweep_in_us"] = 1
                self.meas_data["y_sweepVarName_us"] = y_sweepVarName
                self.meas_data["y_sweepVals_us"] = self.meas_data["y_sweepVals"]
                self.meas_data["y_sweepVarName"] = y_sweepVarName[:-3]
                self.meas_data["y_sweepVals"] = converted_sweep_vals 
        return True


#----------------------------------------------------------------------------------------------------------------------
# Helper Functions
#----------------------------------------------------------------------------------------------------------------------

## Arguments:
## sweepVarName    = dictionary key for the variable
## sweepVals       = array of values to sweep over
## forceInt        = true/false indicating whether your sweep var needs to be an int
## Sweeps a variable in software by updating the program config file.  Returns accumulated output
def oneTone_oneSoftSweep(soc, soccfg, config, sweepVarName, sweepVals, forceInt=False, progress=True, do_decimated=True):
    ## Make an output container
    xi = np.zeros(len(sweepVals))
    xq = np.zeros(len(sweepVals))

    ## Iterate over list of sweep values
    output = np.zeros(len(sweepVals)).astype(complex)
    for i, val in enumerate(sweepVals):
            ## Convert to int if needed
            if(forceInt):
                val = int(val)                
            config[sweepVarName] = val      ## update val
            prog = oneTonePulse(soccfg, config)   ## remake program
            [[I]], [[Q]] = prog.acquire(soc, progress=progress)
            xi[i] = I
            xq[i] = Q

    #Get the decimated output for the last run, just for a sample
    if(do_decimated):
        config["reps"] = 1
        config["soft_avgs"] = 2000
        prog = oneTonePulse(soccfg, config)
        output_decimated = prog.acquire_decimated(soc, progress=False)
    else:
        output_decimated = np.zeros((2,2))
    fullOutput = [xi, xq, output_decimated]
    return fullOutput

    
## Sweeps any two variables in software
def oneTone_twoSoftSweep(soc, soccfg, config, x_sweepVarName, x_sweepVals, y_sweepVarName, y_sweepVals, x_forceInt=False, y_forceInt=False, do_decimated=True):    
    npts_x = len(x_sweepVals)
    npts_y = len(y_sweepVals)
    
    ## Make an output container
    xi   = np.zeros((npts_x, npts_y))
    xq   = np.zeros((npts_x, npts_y))

    ## Iterate through first variable
    for i, val in enumerate(x_sweepVals):
        ## Print status text
        print("Sweep", (i+1), "of", npts_x, end="\r")
        sys.stdout.flush()
        
        ## Convert to int if needed
        if(x_forceInt):
            val = int(val)
            
        ## Set the variable   
        config[x_sweepVarName] = val  
        
        ## Iterate through second variable, repeating same process
        for j, val2 in enumerate(y_sweepVals):                
            ## Set value
            if(y_forceInt):
                val2 = int(val2)    
            config[y_sweepVarName] = val2
            
            ## Remake the program, do the measurement
            prog = oneTonePulse(soccfg, config)
            [[I]], [[Q]] = prog.acquire(soc, load_pulses=True, progress=False)
            xi[i][j] = I
            xq[i][j] = Q
        
    #Get the decimated output for the last run, just for a sample
    if(do_decimated):
        config["reps"] = 1
        config["soft_avgs"] = 2000
        prog = oneTonePulse(soccfg, config)
        output_decimated = prog.acquire_decimated(soc, load_pulses=True, progress=False)
    else:
        output_decimated = np.zeros((2,2))
    fullOutput = [np.transpose(xi), np.transpose(xq), output_decimated]
    return fullOutput



#----------------------------------------------------------------------------------------------------------------------
# QICK Programs (Averager, RAverager)
#----------------------------------------------------------------------------------------------------------------------

## Sends & measures a pulse @ a given frequency
class oneTonePulse(AveragerProgram):
    def initialize(self):
        cfg=self.cfg  
        ## Declare generators 
        self.declare_gen(ch=cfg["res_ch"], nqz=1) #Readout

        ## Declare readout
        self.declare_readout(ch=cfg["ro_ch"], length=cfg["readout_length"],
                                freq=cfg["res_freq"], gen_ch=cfg["res_ch"])
        
        resphase = self.deg2reg(cfg["res_phase"], gen_ch=cfg["res_ch"])
        resfreq=self.freq2reg(cfg["res_freq"], gen_ch=cfg["res_ch"], ro_ch=self.cfg["ro_ch"])  # convert frequency to dac frequency (ensuring it is an available adc frequency)
        style=self.cfg["res_pulse_style"]
        if style == "const":    
            self.set_pulse_registers(ch=cfg["res_ch"], style="const", freq=resfreq, phase=resphase, gain=cfg["res_gain"],
                                length=cfg["res_length"])
        elif style == "gauss":
                self.add_gauss(ch=cfg["res_ch"], name="measure", sigma=(cfg['res_length'])/5, length=cfg['res_length'])
                self.set_pulse_registers(ch=cfg["res_ch"], style="arb", freq=resfreq, phase=resphase, gain=cfg["res_gain"], waveform="measure")
                                
        
        self.synci(200)  # give processor some time to configure pulses
    
    def body(self):
        cfg=self.cfg   
        self.measure(pulse_ch=cfg["res_ch"], 
             adcs=[self.cfg["ro_ch"]],
             adc_trig_offset=cfg["adc_trig_offset"],
             wait=True,
             syncdelay=self.us2cycles(cfg["relax_delay"]))   









class oneTonePulse_old_and_bad(AveragerProgram):
    def initialize(self):
        cfg=self.cfg

        ## Declare generators
        self.declare_gen(ch=cfg["res_ch"], nqz=1)
        
        ## Declare readout
        self.declare_readout(ch=cfg["ro_ch"], length=cfg["readout_length"],
                               freq=cfg["res_pulse_freq"], gen_ch=cfg["res_ch"])
            
        ## Convert frequency to DAC frequency (ensuring it is an available ADC frequency)
        resfreq  = self.freq2reg(cfg["res_pulse_freq"],gen_ch=cfg["res_ch"], ro_ch=cfg["ro_ch"])
        resphase = self.deg2reg(cfg["res_phase"], gen_ch=cfg["res_ch"])
        resgain  = cfg["res_gain"]        
        
        ## Set pulse registers with correct settings
        res_ch = cfg["res_ch"]
        self.pulse_registers(ch=cfg["res_ch"], freq=resfreq, phase=resphase, gain=resgain)
        
        ## Load pulse shape into registers
        style=self.cfg["res_pulse_style"]
        if style == "const":
                self.set_pulse_registers(ch=cfg["res_ch"], style=style, length=cfg['res_length'])
        elif style == "gauss":
                self.add_gauss(ch=cfg["res_ch"], name="measure", sigma=(cfg['res_length'])/5, length=cfg['res_length'])
                self.set_pulse_registers(ch=cfg["res_ch"], style=style, waveform="measure")
        else:
            print("oh no! pulse type not yet supported")
        ## Give processor some time to configure pulses
        self.synci(200)
    
    def body(self):
        # fire the pulse
        # trigger all declared ADCs
        # pulse PMOD0_0 for a scope trigger
        # pause the tProc until readout is done
        # increment the time counter to give some time before the next measurement
        # (the syncdelay also lets the tProc get back ahead of the clock)
        self.measure(pulse_ch=self.cfg["res_ch"], 
                     adcs=[self.cfg["ro_ch"]],
                     adc_trig_offset=self.cfg["adc_trig_offset"],
                     wait=True,
                     syncdelay=self.us2cycles(self.cfg["relax_delay"])) # should now no longer have the "to-cycles"
        

class LoopbackProgram(AveragerProgram):
    def initialize(self):
        cfg=self.cfg   

        ## Declare generators
        self.declare_gen(ch=cfg["res_ch"], nqz=1) #Readout

#         self.declare_gen(ch=cfg["qubit_ch"], nqz=2) #Qubit
#         self.declare_gen(ch=cfg["storage_ch"], nqz=2) #Storage

        for ch in [0,1]: #configure the readout lengths and downconversion frequencies
            self.declare_readout(ch=ch, length=cfg["readout_length"],
                                 freq=cfg["res_freq"], gen_ch=cfg["res_ch"])

        freq=self.freq2reg(cfg["res_freq"], gen_ch=cfg["res_ch"], ro_ch=self.cfg["ro_ch"])  # convert frequency to dac frequency (ensuring it is an available adc frequency)
        self.set_pulse_registers(ch=cfg["res_ch"], style="const", freq=freq, phase=0, gain=cfg["pulse_gain"],
                                length=cfg["res_length"])
        
        self.synci(200)  # give processor some time to configure pulses
    
    def body(self):
        cfg=self.cfg   
        self.measure(pulse_ch=cfg["res_ch"], 
             adcs=[0,1],
             adc_trig_offset=cfg["adc_trig_offset"],
            #t=0,
             wait=True,
             syncdelay=self.us2cycles(cfg["relax_delay"]))   
