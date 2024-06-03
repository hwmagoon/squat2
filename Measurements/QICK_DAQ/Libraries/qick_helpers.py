#----------------------------------------------------------------------
#
# qickHelpers.py
# author: Hannah Magoon (+ others)
# Feb 2023
# April 2024 -- HM@SLAC commented out all RF companion board functions
##           -- because we don't have an RF companion board :-)
#
# Library of various functions for assisting measurements. All of these
# should be 100% measurement-agnostic, no exceptions!
#
#----------------------------------------------------------------------
import numpy as np

## ADC and DAC mapping
transmission_ch = 6   ## DAC
chargebias_ch   = 4   ## DAC 
ro_ch           = 1   ## ADC


## This is just Ryan's function, but with a different variable naming convention
def convert_time_vars(soccfg, meas_class, verbose=False):
        print("converting time variables from us to clock ticks")
        if ("adc_trig_offset_us" not in meas_class.meas_cfg):
                if(verbose): print('adc_trig_offset not in meas_cfg')
        else:
                meas_class.meas_cfg["adc_trig_offset"] = soccfg.us2cycles(meas_class.meas_cfg["adc_trig_offset_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["adc_trig_offset_us"]
        #-----------------------------------------------------
        if ("readout_length_us" not in meas_class.meas_cfg):
                if(verbose): print('readout length is not in meas_cfg')
        else:
                meas_class.meas_cfg["readout_length"] = soccfg.us2cycles(meas_class.meas_cfg["readout_length_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["readout_length_us"]        
        #-----------------------------------------------------
        if ("res_length_us" not in meas_class.meas_cfg):
                if(verbose): print('res_length is not in meas_cfg')
        else:
                meas_class.meas_cfg["res_length"] = soccfg.us2cycles(meas_class.meas_cfg["res_length_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["res_length_us"]                
        #-----------------------------------------------------
        if ("qu_length_us" not in meas_class.meas_cfg):
                if(verbose): print('qu_length is not in meas_cfg')
        else:
                meas_class.meas_cfg["qu_length"] = soccfg.us2cycles(meas_class.meas_cfg["qu_length_us"],gen_ch=meas_class.hw_cfg["qu_ch"]) 
                del meas_class.meas_cfg["qu_length_us"]                
        #-----------------------------------------------------
        if ("relax_delay_us" not in meas_class.meas_cfg):
                if(verbose): print('relax delay us is not in meas_cfg')
        else:
                meas_class.meas_cfg["relax_delay"] = soccfg.us2cycles(meas_class.meas_cfg["relax_delay_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["relax_delay_us"]
        #-----------------------------------------------------                
        if ("delay_us" not in meas_class.meas_cfg):
                if(verbose): print('delay us is not in meas_cfg')
        else:
                meas_class.meas_cfg["delay"] = soccfg.us2cycles(meas_class.meas_cfg["delay_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["delay_us"]
        #-----------------------------------------------------                
        if ("qu_sigma_us" not in meas_class.meas_cfg):
                if(verbose): print('qu_sigma_us is not in meas_cfg')
        else:
                meas_class.meas_cfg["qu_sigma"] = soccfg.us2cycles(meas_class.meas_cfg["qu_sigma_us"],gen_ch=meas_class.hw_cfg["qu_ch"])
                del meas_class.meas_cfg["qu_sigma_us"]
        #-----------------------------------------------------                                
        if ("res_sigma_us" not in meas_class.meas_cfg):
                if(verbose): print('res_sigma_us is not in meas_cfg')
        else:
                meas_class.meas_cfg["res_sigma"] = soccfg.us2cycles(meas_class.meas_cfg["res_sigma_us"],gen_ch=meas_class.hw_cfg["res_ch"])
                del meas_class.meas_cfg["res_sigma_us"]
        #-----------------------------------------------------                
        if ("laser_length_us" not in meas_class.meas_cfg):
                if(verbose): print('laser length is not in meas_cfg')
        else:
                meas_class.meas_cfg["laser_length"] = soccfg.us2cycles(meas_class.meas_cfg["laser_length_us"],gen_ch=meas_class.hw_cfg["laser_ch"])
                del meas_class.meas_cfg["laser_length_us"]

        return meas_class

