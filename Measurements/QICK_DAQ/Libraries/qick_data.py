#----------------------------------------------------------------------
#
# qickData.py
# author: Hannah Magoon
# Feb 2023
# Edited April 2024 @ SLAC
#
# Base class for storing data from tests run in the LOUD and QUIET
# detectors. If you don't know what you're doing, DO NOT MODIFY THIS
# CLASS.
#
#----------------------------------------------------------------------
import h5py
import sys, os
import datetime
import numpy as np
import matplotlib.pyplot as plt

class QICKdata:

    ## Metadata to be attached to all measurements
    meta = {
        "series" : "00000000_000000", ## YYYYMMDD_HHMMSS
        "device" : "x",               ## options: {"sil", "sap"}
        "qubits" : [9],               ## options: {1,2,3,4,5,6}
        "meas_type" : "x"             ## options: {"tof", "res_spec"....}
    }
    
    ## Channel mapping from hw_cfg
    hw_cfg = {
        "res_ch"   : None,                 ## DAC options: {0,1,2,3,4,5,6}
        "qu_ch"    : None,                 ## DAC options: {0,1,2,3,4,5,6}
        "ro_ch"    : None,                 ## ADC options: {0,1}
    }

    ## Dictionaries to be populated in measurement subclasses
    rfb_cfg = { }
    meas_cfg = { }
    meas_data = { }

    ## If you are reading in from a file, overwrite the series argument
    ## Otherwise, leave blank and let it self-populate
    def __init__(self, series=None):
        ## HM: don't delete the clear statements! they fix the memory allocation bug
        self.meta.clear()
        self.hw_cfg.clear()
        self.rfb_cfg.clear()
        self.meas_cfg.clear()
        self.meas_data.clear()
        if series is None:
            series = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.meta["series"] = series
        print("Creating dataset with series", series)
        return
    
    def __str__(self):
        print("====---------------------------====")
        print("        ", self.meta["series"])
        print("====---------------------------====")
        print("       Device = ", self.meta["device"])
        print("       Qubits = ", self.meta["qubits"])
        print("    Meas Type = ", self.meta["meas_type"])
        print("====---------------------------====")
        return self.meta["series"]
    

    ## Populates class metadata with device, qubit number(s), and meas_type
    def set_metadata(self, device, qubits, meas_type):
        self.meta["device"] = device
        self.meta["qubits"] = qubits
        self.meta["meas_type"] = meas_type
        return

    ## Populates hw_cfg to record channel mapping
    def set_hw_cfg(self, res_ch, qu_ch, ro_ch):
        self.hw_cfg["res_ch"]   = res_ch
        self.hw_cfg["qu_ch"]    = qu_ch
        self.hw_cfg["ro_ch"]    = ro_ch
        return

    ## Dumps everything in the class into an h5 file
    def write_H5(self, datapath):
        
        ## Follow filepath.  If filpath doesn't exist, make it exist
        if not os.path.exists(datapath):
            print("Datapath doesn't exist yet. Making new datapath")
            os.makedirs(datapath)
        os.chdir(datapath)
        filename = self.meta["series"]+"_"+self.meta["meas_type"]+".h5"
        print("Saving data as:", filename)

        with h5py.File(filename, "w") as f:
            
            ## Make a group for each of the 5 dictionaries
            G_meta      = f.create_group("meta")
            G_hw_cfg    = f.create_group("hw_cfg")
            G_meas_cfg  = f.create_group("meas_cfg")
            G_meas_data = f.create_group("meas_data")

            ## Record down group and dictionary names
            groups_list = [G_meta, G_hw_cfg, G_meas_cfg, G_meas_data]                 ## Groups in the h5  file
            dicts_list = [self.meta, self.hw_cfg, self.meas_cfg, self.meas_data]
            
            ## Iterate through dictionaries, record each variable into the corresponding group
            for i, dict in enumerate(dicts_list):
                for dset in dict:
                    if dict[dset] is None:
                        continue
                    elif (isinstance(dict[dset], str)): 
                        groups_list[i].create_dataset(dset, data=np.array([dict[dset]], dtype='S'))
                    elif (isinstance(dict[dset],int)):
                        groups_list[i].create_dataset(dset, data=np.array([dict[dset]]))
                    else:
                        groups_list[i].create_dataset(dset, data=np.array(dict[dset]).astype(float))       
            f.close()
        return
    

## Reads in an H5, populates class
## Arguments: datapath, filename, class to populate
def read_H5(datapath, filename, dataclass, debug=False):
    if not os.path.exists(datapath):
        exit("Error: invalid datapath")
    os.chdir(datapath)
    print("Reading from filepath", datapath)

    with h5py.File(filename, 'r') as f:
        ## Get series number
        _sers = f["meta"]["series"][0].decode('UTF-8')
        if(debug): print("opening file with series:", _sers)

        ## Make a dataclass output container
        d = dataclass(series=_sers)
        
        ## Get a list of the groups
        groups = [i for i in f.keys()]
        if(debug): print("groups found:", groups)
            
        ## Sanity check of filetype
        expected_groups = ['hw_cfg', 'meas_cfg', 'meas_data', 'meta']
        if not (set(expected_groups).issubset(groups)):
            print("WARNING: missing metadata or unexpected filestructure. Proceed with caution...")
                
        ## Iterate through groups, look at items
        for group in groups:
            items = [i for i in f[group]]
            values = []
            ## Iterate through items, import them
            for item in items:
                if(debug): print(item)
                readin = f[group][item][()]
                ## Fix formatting of scalar quantities
                if (type(readin) != np.float64):
                    if (len(readin)==1 and item!="qubits"):
                        [readin] = readin
                ## Fix formatting of strings
                if (type(readin) == np.bytes_):
                    readin = readin.decode("utf-8")
                values.append(readin)
            ## Save item to dataclass  
            dictionary = dict(zip(items, values))
            if debug: print(dictionary)
            setattr(d, group, dictionary)

        f.close()
    return d