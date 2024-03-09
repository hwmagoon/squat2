#!/usr/bin/env python3

import gdspy
import math
import structuresLib as structures
from squatHelperLib import *



## To do
## -- do i want a material test clover for junction layer?

####------------------------------------------------------####
####                   Parameters                         ####
####------------------------------------------------------####

filepath = "../GDS/V4_masks/20240309_ebeam_only_junction_array.gds"

## GDS Layers
layer_chip     = {"layer": 0, "datatype": 0}
layer_opt_nb   = {"layer": 1, "datatype": 0}
layer_opt_al   = {"layer": 2, "datatype": 0}
layer_eb_pin   = {"layer": 3, "datatype": 0}
layer_eb_under = {"layer": 4, "datatype": 0}


## Chip setup
chip_x = 10000     ## [float] chip x-dimension
chip_y = 10000     ## [float] chip y-dimension
border = 10        ## [float] min distannce from any feature to edge of chip
dice_width = 300   ## [float] width of dicing saw lanes
gnd_plane = True   ## [bool]  indicates whether there should be a gnd plane
clover_size = 300  #450
fillet_r_small = 2


## Ebeam Features
eb_align_dim    = 40   ## [float] side length of ebeam alignment squares
eb_align_offset = 480  ## [float] distance between ebeam marker and side of the chip


## Witness junctions
witness_jj_gaps = [0, 0.22, 0.22, 0.22, 0.23, 0.24]
witness_pad_layers = [layer_opt_al, layer_opt_nb]    ## [list of layers] Each material gets its own column of test JJs
witness_pad_mult = 1.25                              ## [float] Make test pads bigger so that probing is easier
witness_separation = eb_align_offset                 ## [float] Vertical separation of witness jjs


## Parameters for individual SQUATs
qpad_x = 110
qpad_y = 110
qpad_angle = 7*math.pi/8
qpad_separation = 800
qpad_gnd_cutout_mult = [1.2, 3]


## Array parameters
qpad_array_spacing_mult = 0.7 ## Times the width of each array feature

jj_gaps = np.array([
    [0.10, 0.15, 0.20, 0.25],
    [0.10, 0.15, 0.20, 0.25],
    [0.10, 0.15, 0.20, 0.25],
    [0.10, 0.15, 0.20, 0.25]
])

jj_finger_widths = np.array([
    [0.08, 0.08, 0.08, 0.08],
    [0.10, 0.10, 0.10, 0.10],
    [0.12, 0.12, 0.12, 0.12],
    [0.14, 0.14, 0.14, 0.14]
])



####------------------------------------------------------####
####                     Setup                            ####
####------------------------------------------------------####


lib = gdspy.GdsLibrary()

## Make cells
cell_chip     = lib.new_cell('chip')
cell_gnd_neg  = lib.new_cell('gnd_neg')
cell_fins     = lib.new_cell('fins')
cell_junc     = lib.new_cell('junctions')


## Make chip outline as a reference
full_rect = gdspy.Rectangle((-dice_width/2., -dice_width/2.), (chip_x+dice_width/2., chip_y+dice_width/2.), **layer_chip)
chip_rect = gdspy.Rectangle((0,0), (chip_x,chip_y), **layer_chip)
cell_chip.add(full_rect)
cell_chip.add(chip_rect)


## Make ebeam alignment boxes
## -- Subtract ebeam align boxes from the ground plane
## -- Add ebeam align boxes to the ebeam pin layer (so that they appear in the cjob file)
align_locs = [[chip_x-eb_align_offset-eb_align_dim, chip_y-eb_align_offset-eb_align_dim], 
                [chip_x-eb_align_offset-eb_align_dim, eb_align_offset],
                [eb_align_offset, eb_align_offset],
                [eb_align_offset, chip_y-eb_align_offset-eb_align_dim]]
for idx, loc in enumerate(align_locs):
    align_box_opt = gdspy.Rectangle([loc[0],loc[1]], [loc[0]+eb_align_dim,loc[1]+eb_align_dim], **layer_opt_nb)
    align_box_eb  = gdspy.Rectangle([loc[0],loc[1]], [loc[0]+eb_align_dim,loc[1]+eb_align_dim], **layer_eb_pin)
    cell_gnd_neg.add(align_box_opt)
    cell_chip.add(align_box_eb)



####------------------------------------------------------####
####                Calibration Features                  ####
####------------------------------------------------------####


## Make material test clovers
clover1, cloverCirc1 = structures.cloverleaf(center = (chip_x-eb_align_offset, chip_y-2*eb_align_offset), D=clover_size, clover_layer=layer_opt_nb['layer'], circ_layer=layer_opt_nb['layer'])
clover2, cloverCirc2 = structures.cloverleaf(center = (chip_x-eb_align_offset-1.5*eb_align_offset, chip_y-2*eb_align_offset), D=clover_size, clover_layer=layer_opt_al['layer'], circ_layer=layer_opt_nb['layer'])
cell_chip.add([clover1, clover2])

## Make gnd plane cutouts for clovers
if gnd_plane:
    cell_gnd_neg.add([cloverCirc1, cloverCirc2])


## Make witness SQUATs
#for gap in witness_jj_gaps:
#    for layer in witness_pad_layers:
#        print(gap, layer)


####------------------------------------------------------####
####               Chip design: jj array                  ####
####------------------------------------------------------####


## Sanity check inputs
if len(jj_gaps) != len(jj_finger_widths):
    print("Error: inconsistent array dimensions")
elif len(jj_gaps[0]) != len(jj_finger_widths[0]):
    print("Error: inconsistent array dimensions")


## Calculate feature spacing
chip_center = [chip_x/2, chip_y/2]
qpad_gnd_cutout_radius = np.array([qpad_gnd_cutout_mult[0]*(qpad_x+qpad_separation/2), qpad_gnd_cutout_mult[1]*(qpad_y)])
feature_array_space = 2*qpad_gnd_cutout_radius*qpad_array_spacing_mult


## Figure out placement on chip
ncols = len(jj_gaps[0])
nrows = len(jj_gaps)
if ncols%2 == 0:
    print("Number of columns is even")
    ypos = chip_center[1] + feature_array_space[1]*(ncols+2)/2
else:
    print("Number of columns is odd")
    ypos = chip_center[1] + feature_array_space[1]*(ncols+1)/2
if nrows%2 == 0:
    print("Number of rows is even")
    xpos_start = chip_center[0] - feature_array_space[0]*(nrows+2)/2
else:
    print("Number of rows is odd")
    xpos_start = chip_center[1] - feature_array_space[0]*(nrows+1)/2
xpos = xpos_start 



## Make a junction at each array location
for col in range(0, ncols):
    for row in range(0, nrows):
        loc = [xpos, ypos]
        ## Make junction
        qpads, jpads, und = squat_from_center_pt(loc=loc, 
                                            qpad_x=qpad_x, qpad_y=qpad_y, 
                                            qpad_angle=qpad_angle, qpad_separation=qpad_separation, 
                                            fillet_radius=fillet_r_small, 
                                            jj_gap=jj_gaps[row][col], jj_finger_width=jj_finger_widths[row][col], 
                                            pad_layer=layer_opt_al, pin_layer=layer_eb_pin, under_layer=layer_eb_under)
        cell_fins.add(qpads) #, jpads, und])
        cell_junc.add(jpads)
        cell_junc.add(und)
        ## Mae cutout for junction in ground plane
        qpad_gnd_cutout = gdspy.Round(center=loc, radius=(qpad_gnd_cutout_radius), **layer_opt_nb)
        cell_gnd_neg.add(qpad_gnd_cutout)
        ## Update x location
        xpos += 2*feature_array_space[0]
    xpos = xpos_start
    ypos -= 2*feature_array_space[1]


####------------------------------------------------------####
####              Tag bottom with text                    ####
####------------------------------------------------------####



####------------------------------------------------------####
####                  Save file                           ####
####------------------------------------------------------####

## If there is a ground plane, make a ground plane and subtract the contents of the 'ground plane' layer
## -- otherwise, add the contents of the ground plane layer
if gnd_plane:
    gnd_plane = gdspy.Rectangle((0,0), (chip_x, chip_y), **layer_opt_nb)
    gnd_plane = gdspy.boolean(gnd_plane, cell_gnd_neg, 'not', **layer_opt_nb, max_points=0)
    cell_chip.add(gnd_plane)


cell_chip.add(cell_junc)
cell_chip.add(cell_fins)


lib.write_gds(filepath)







