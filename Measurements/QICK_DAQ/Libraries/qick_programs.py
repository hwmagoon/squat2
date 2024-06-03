import numpy as np
from qick import *
from qick_data import *
from qick_helpers import *

#----------------------------------------------------------------------
#
# qick_programs.py
# author: Hannah Magoon
# June 2023 [edited May 2024]
#
# Pulse sequences for SQUAT datataking
#
#
#----------------------------------------------------------------------


class oneTonePulse(AveragerProgram):
    def initialize(self):
        cfg=self.cfg  
        ## Declare generators 
        self.declare_gen(ch=cfg["res_ch"], nqz=1) 

        ## Declare readout
        self.declare_readout(ch=cfg["ro_ch"], length=cfg["readout_length"],
                                freq=cfg["res_freq"], gen_ch=cfg["res_ch"])
        
        resphase = self.deg2reg(cfg["res_phase"], gen_ch=cfg["res_ch"])
        resfreq=self.freq2reg(cfg["res_freq"], gen_ch=cfg["res_ch"], ro_ch=self.cfg["ro_ch"])  # convert frequency to dac frequency (ensuring it is an available adc frequency)
        style=self.cfg["res_style"]
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
             syncdelay=cfg["relax_delay"])




## Sends a pulse in two tones
class twoTonePulse(AveragerProgram):
    def initialize(self,verbose=False):
        cfg=self.cfg

        ## set up DACs
        self.declare_gen(ch=cfg["res_ch"], nqz=1)
        self.declare_gen(ch=cfg["qu_ch"],nqz=1)

        ## Set up ADCs
        self.declare_readout(ch=cfg["ro_ch"], length=self.cfg["readout_length"],freq=self.cfg["res_freq"], gen_ch=cfg["res_ch"])

        ## Convert quantities to boardspeak
        resfreq  = self.freq2reg(cfg["res_freq"], gen_ch=cfg["res_ch"], ro_ch=cfg["ro_ch"])
        qufreq   = self.freq2reg(cfg["qu_freq"],gen_ch=cfg["qu_ch"],ro_ch=cfg["ro_ch"])
        resphase = self.deg2reg(cfg["res_phase"], gen_ch=cfg["res_ch"])
        quphase  = self.deg2reg(cfg["qu_phase"], gen_ch=cfg["qu_ch"])
        #print(resfreq, qufreq)
        
        ## Pull parameters for convenience
        resgain  = cfg["res_gain"]
        qugain   = cfg["qu_gain"]
        resstyle = cfg["res_style"]
        qustyle  = cfg["qu_style"]

        ## Set the qubit pulse registers
        if qustyle == "const":
            self.set_pulse_registers(ch=cfg["qu_ch"], style="const", freq=qufreq, phase=quphase, gain=qugain, length=cfg["qu_length"])
        elif qustyle == "gauss":
            self.add_gauss(ch=cfg["qu_ch"], name="probe", sigma=cfg["qu_sigma"], length=cfg["qu_length"])
            self.set_pulse_registers(ch=cfg["qu_ch"], style="arb", freq=qufreq, phase=quphase, gain=qugain,waveform="probe")
        else:
            print("oh no! pulse type not yet supported")
            return

        ## Set the resonator pulse registers
        if resstyle == "const":
            self.set_pulse_registers(ch=cfg["res_ch"], style="const", freq=resfreq, phase=resphase, gain=resgain, length=cfg["res_length"])
        elif resstyle == "gauss":
            self.add_gauss(ch=cfg["res_ch"], name="measure", sigma=cfg["res_sigma"], length=cfg["res_length"])
            self.set_pulse_registers(ch=cfg["res_ch"], style="arb", freq=resfreq, phase=resphase, gain=resgain, waveform="measure")
        

        self.synci(200)  ## give processor some time to configure pulses
        
    def body(self):        
        #Need to send in a probe pulse (qubit pulse) and then wait a bit of time
        self.pulse(ch=self.cfg["qu_ch"])
        self.sync_all(self.cfg["delay"])
        
        self.measure(pulse_ch=[self.cfg["res_ch"]],
             adcs=[self.cfg["ro_ch"]],
             adc_trig_offset=self.cfg["adc_trig_offset"],
             wait=True,
             syncdelay=self.cfg["relax_delay"])