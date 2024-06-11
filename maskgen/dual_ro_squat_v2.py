'''
Last Updated: 2024-06-11
Description: SQUAT qubit with two parallel transmission lines
'''

import gdspy
import structuresLib as structures
from squatHelperLib import *
from skimage import io, color, measure, morphology
import numpy as np
pi = np.pi


####------------------------------------------------------####
####                   Parameters                         ####
####------------------------------------------------------####

filepath = "../GDS/V4_masks/dualro_squat.gds"
image_path = 'C:\\Users\\Hannah\\Desktop\\SLAC\\squat2\\GDS\\logos\\DMQIS.gds'

## GDS Layers
layer_chip     = {"layer": 0, "datatype": 0}
layer_opt_nb   = {"layer": 1, "datatype": 0}
layer_opt_al   = {"layer": 2, "datatype": 0}
layer_eb_pin   = {"layer": 3, "datatype": 0}
layer_eb_under = {"layer": 4, "datatype": 0}

## Chip setup
chip_x = 10000      ## chip x-dimension
chip_y = 10000      ## chip y-dimension
border = 10         ## min distannce from any feature to edge of chip
dice_width = 300    ## width of dicing saw lanes
gnd_plane = True    ## indicates whether there should be a gnd plane
clover_size = 300   ## material test clover
fillet_r = 70       ## round corners of large features
fillet_r_small = 2  ## round corners of small features
fillet_r_jj = 2     ## junction circle overlap pads

## RF Launch Positions: just a spot on perimeter- border will be added later
launch_bot1 = (2*chip_x/3, 0)
launch_bot2 = (chip_x/3, 0)
launch_top1 = (2*chip_x/3, chip_y)
launch_top2 = (chip_x/3, chip_y)

## Connection pads (taper width for wirebonds)
pad_taper_l = 400
pad_w_in = 200
pad_l_in = 200

## Offset connection pads from edge of chip
pad_gnd_edgethickness = 665 ## thickness of gnd along edge of chip
pad_gap_edgethickness = 50  ## thickness of gap along edge of chip
pad_gap_thickness = 90

## CPW and launch sizes
cpw_s = 20        ## width of central conductor
cpw_w = 9         ## width of gaps
cpw_gnd = 100     ## width of ground lines
cpw_bend_r = 100  ## bend radius of CPW
cpw_tail = 80     ## straight section of CPW coming out of bond pad

## True false indicating whether the transmission lines should curve
left_curve = True
right_curve = True

## Ebeam Features
eb_align_dim    = 40   ## side length of ebeam alignment squares
eb_align_offset = 480  ## distance between ebeam marker and side of the chip

## SQUAT placement
n_qubits = 5                ## number of SQUAT qubits
q_spacing = 7800/n_qubits   ## vertical spacing between SQUATs
q_left_tl_offset = 60       ## coupling distance from edge of SQUAT fin to left TL
q_right_tl_offset = 60      ## coupling distance from edge of SQUAT fin to right TL
q_gnd_height = 60           ## vertical distance between SQUAT fin and ground plane

## Parameters for SQUAT fins --- provide arrays of length n_qubits
qpad_x = np.full(n_qubits, 110)            ##  x radius of SQUAT fins (i.e. x direction fin length)
qpad_y = np.full(n_qubits, 110)            ##  y radius of SQUAT fins
qpad_angle = np.full(n_qubits, 7*pi/8)     ## angle of sector carved out by SQUAT fin
qpad_separation = np.full(n_qubits, 13)    ## distance in center between fins (i.e. length of junction structure)

## Paramers for SQUAT junctions --- provide arrays of length n_qubits
jj_gap = np.full(n_qubits, 0.22)            ## dolan bridge length
jj_finger_width = np.full(n_qubits, 0.12)   ## dolan bridge width


## Misc
logo_loc = (chip_x-2.5*eb_align_offset, eb_align_offset) ## location of logo


####------------------------------------------------------####
####                     Setup                            ####
####------------------------------------------------------####

lib = gdspy.GdsLibrary()

## Make cells
cell_chip     = lib.new_cell('chip')
cell_gnd_neg  = lib.new_cell('gnd_neg')
cell_gnd_pos  = lib.new_cell('gnd_pos')
cell_fins     = lib.new_cell('fins')
cell_junc     = lib.new_cell('junctions')
cell_logo     = lib.new_cell('logo')

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
####         Make N SQUATs between the lines              ####
####------------------------------------------------------####

q_locs = [[chip_x/2, (chip_y-q_spacing*(n_qubits-1))/2 + i*q_spacing] for i in range(n_qubits)]

## array holding cutouts for ground plane
cutouts = [None]*n_qubits

## Loop over the qubits
for i in range(n_qubits):
    ## Make SQUAT
    qubit = squat_from_center_pt(loc=q_locs[i], qpad_x=qpad_x[i], qpad_y=qpad_y[i], 
                                 qpad_angle=qpad_angle[i], qpad_separation=qpad_separation[i], 
                                 fillet_radius=fillet_r_jj, jj_gap=jj_gap[i], jj_finger_width=jj_finger_width[i], 
                                 pad_layer=layer_opt_al, pin_layer=layer_eb_pin, under_layer=layer_eb_under)
    cell_fins.add(qubit[0])
    cell_junc.add(qubit[1])
    cell_junc.add(qubit[2])

    ## Ground plane cutout
    cutout_x_start = chip_x/2 - qpad_separation[i]/2 - qpad_x[i] - q_left_tl_offset
    cutout_x_end = chip_x/2 + qpad_separation[i]/2 + qpad_x[i] + q_right_tl_offset
    cutout_y_start = q_locs[i][1] - qpad_y[i] - q_gnd_height
    cutout_y_end = q_locs[i][1] + qpad_y[i] + q_gnd_height
    cutouts[i] = gdspy.Rectangle((cutout_x_start, cutout_y_start), (cutout_x_end, cutout_y_end), **layer_opt_nb)

## Combine ground cutouts
gnd_cutout = gdspy.boolean(cutouts[0], cutouts[1], 'or', **layer_opt_nb)
for i in range(2,n_qubits):
    gnd_cutout = gdspy.boolean(gnd_cutout, cutouts[i], 'or', **layer_opt_nb)


####------------------------------------------------------####
####           Parallel Transmission Lines                ####
####------------------------------------------------------####


## Connection pad for input line
pad_w_gap = pad_w_in + 2*pad_gap_thickness
pad_l_gap = pad_l_in + pad_gap_edgethickness

## Start by drawing right TL
curve = right_curve
which_line = "right"

## Hold features in arrays
inner_features = []
outer_features = []

## Loop over the two transmission lines
for tl_loc in [[launch_bot1, launch_top1], [launch_bot2, launch_top2]]:
    ## inner wirebond pad bottom
    pad_inner_l = gdspy.Path(pad_w_in, (tl_loc[0][0], pad_gnd_edgethickness+pad_gap_edgethickness+tl_loc[0][1]))
    pad_inner_l.segment(pad_l_in, "+y")
    pad_inner_l.segment(pad_taper_l, "+y", final_width=cpw_s)

    ## inner wirebond pad top
    pad_inner_r = gdspy.Path(pad_w_in, (tl_loc[1][0], -pad_gnd_edgethickness-pad_gap_edgethickness+tl_loc[1][1]))
    pad_inner_r.segment(pad_l_in, "-y")
    pad_inner_r.segment(pad_taper_l, "-y", final_width=cpw_s)

    ## outer wirebond pad bottom
    pad_outer_l = gdspy.Path(pad_w_gap, (tl_loc[0][0], pad_gnd_edgethickness+tl_loc[0][1]))
    pad_outer_l.segment(pad_l_gap, "+y")
    pad_outer_l.segment(pad_taper_l, "+y", final_width=cpw_s+2*cpw_w)

    ## outer wirebond pad top
    pad_outer_r = gdspy.Path(pad_w_gap, (tl_loc[1][0], -pad_gnd_edgethickness+tl_loc[1][1]))
    pad_outer_r.segment(pad_l_gap, "-y")
    pad_outer_r.segment(pad_taper_l, "-y", final_width=cpw_s+2*cpw_w)

    ## combine two pads
    pad_inner = gdspy.boolean(pad_inner_l, pad_inner_r, 'or', **layer_opt_nb)
    pad_outer = gdspy.boolean(pad_outer_l, pad_outer_r, 'or', **layer_opt_nb)

    ## Find vertical length, accounting for bends
    tl_len = tl_loc[1][1]-tl_loc[0][1]-2*pad_gnd_edgethickness-2*pad_gap_edgethickness-2*pad_l_in-2*pad_taper_l
    tl_inner = gdspy.Path(cpw_s, (tl_loc[0][0], pad_gnd_edgethickness+pad_gap_edgethickness+pad_l_in+pad_taper_l+tl_loc[0][1]))
    tl_outer = gdspy.Path(cpw_s+2*cpw_w, (tl_loc[0][0], pad_gnd_edgethickness+pad_gap_edgethickness+pad_l_in+pad_taper_l+tl_loc[0][1]))
    if curve:
        ## account for bump in y-direction
        tl_len = tl_len - 4*cpw_bend_r - 2*cpw_tail

        ## figure out direction of meander bump
        if which_line == "left":
            x_target = chip_x/2 - 2*cpw_bend_r - cpw_s/2 - qpad_separation[0]/2 - qpad_x[0] - q_left_tl_offset
        else:
            x_target = chip_x/2 + 2*cpw_bend_r + cpw_s/2 + qpad_separation[0]/2 + qpad_x[0] + q_right_tl_offset
        if x_target < tl_loc[0][0]:
            bump = "left"
        else: bump = "right"

        ## Make tail with quarter bend
        tl_inner.segment(cpw_tail, "+y")
        tl_outer.segment(cpw_tail, "+y")
        if bump == "left":
            tl_inner.turn(cpw_bend_r, angle="l")
            tl_outer.turn(cpw_bend_r, angle="l")
        else: 
            tl_inner.turn(cpw_bend_r, angle="r")
            tl_outer.turn(cpw_bend_r, angle="r")
            
        ## travel horizontal distance to meet coupling target dimension
        if bump == "left":                
            tl_inner.segment(tl_loc[0][0] - x_target, "-x")
            tl_outer.segment(tl_loc[0][0] - x_target, "-x")
        else: 
            tl_inner.segment(x_target - tl_loc[0][0], "+x")
            tl_outer.segment(x_target - tl_loc[0][0], "+x")

        ## quarter bend for center portion (nearest to qubit)
        if bump == "left":
            tl_inner.turn(cpw_bend_r, angle="r")
            tl_outer.turn(cpw_bend_r, angle="r")
        else:
            tl_inner.turn(cpw_bend_r, angle="l")
            tl_outer.turn(cpw_bend_r, angle="l")

        ## straight vertical portion
        tl_inner.segment(tl_len, "+y")
        tl_outer.segment(tl_len, "+y")

        ## opposite of the horizontal section to return to launches
        if bump == "left":
            tl_inner.turn(cpw_bend_r, angle="r")
            tl_outer.turn(cpw_bend_r, angle="r")
            tl_inner.segment(tl_loc[0][0] - x_target, "+x")
            tl_outer.segment(tl_loc[0][0] - x_target, "+x")
        else: 
            tl_inner.turn(cpw_bend_r, angle="l")
            tl_outer.turn(cpw_bend_r, angle="l")
            tl_inner.segment(x_target-tl_loc[0][0], "-x")
            tl_outer.segment(x_target-tl_loc[0][0], "-x")
        if bump == "left":
            tl_inner.turn(cpw_bend_r, angle="l")
            tl_outer.turn(cpw_bend_r, angle="l")
        else:
            tl_inner.turn(cpw_bend_r, angle="r")
            tl_outer.turn(cpw_bend_r, angle="r")

        ## hit final bond pad
        tl_inner.segment(cpw_tail, "+y")
        tl_outer.segment(cpw_tail, "+y")

        ## prep for next line
        bump = "right"
        curve = left_curve
        which_line = "left"

    ## If no curve, just draw straight line
    else:
        tl_len = tl_loc[1][1]-tl_loc[0][1]-2*pad_gnd_edgethickness-2*pad_gap_edgethickness-2*pad_l_in-2*pad_taper_l
        tl_inner = gdspy.Path(cpw_s, (tl_loc[0][0], pad_gnd_edgethickness+pad_gap_edgethickness+pad_l_in+pad_taper_l+tl_loc[0][1]))
        tl_inner.segment(tl_len, "+y")
        tl_outer = gdspy.Path(cpw_s+2*cpw_w, (tl_loc[0][0], pad_gnd_edgethickness+pad_gap_edgethickness+pad_l_in+pad_taper_l+tl_loc[0][1]))
        tl_outer.segment(tl_len, "+y")

    ## combine pads with line
    inner_features.append(gdspy.boolean(tl_inner, pad_inner, 'or', **layer_opt_nb))
    outer_features.append(gdspy.boolean(tl_outer, pad_outer, 'or', **layer_opt_nb))

## Combine the two transmission lines
inner = gdspy.boolean(inner_features[0], inner_features[1], 'or', **layer_opt_nb) 
inner.fillet(fillet_r)


## combine outer with qubit cutouts
## this is a dumb way to do it but the fillets cause issues otherwise
outer_left = gdspy.boolean(outer_features[0], cutouts[0], 'or', **layer_opt_nb)
for cutout in cutouts[1:]:
    outer_left = gdspy.boolean(outer_left, cutout, 'or', **layer_opt_nb)
outer_left.fillet(fillet_r)
outer_right = gdspy.boolean(outer_features[1], cutouts[0], 'or', **layer_opt_nb)
for cutout in cutouts[1:]:
    outer_right = gdspy.boolean(outer_right, cutout, 'or', **layer_opt_nb)
outer_right.fillet(fillet_r)
outer = gdspy.boolean(outer_left, outer_right, 'or', **layer_opt_nb)

## boolean subtraction to make the transmission line
tl = gdspy.boolean(outer, inner, 'not', **layer_opt_nb)
cell_gnd_neg.add(tl)




####------------------------------------------------------####
####                  Exporting                           ####
####------------------------------------------------------####

## Add DMQIS logo
cell_logo = import_cell_from_gds(image_path, 'dmqis_logo', cell_logo, logo_loc)
cell_gnd_neg.add(cell_logo)

## If there is a ground plane, make a ground plane and subtract the contents of the 'ground plane' layer
if gnd_plane:
    gnd_plane = gdspy.Rectangle((0,0), (chip_x, chip_y), **layer_opt_nb)
    gnd_plane = gdspy.boolean(gnd_plane, cell_gnd_neg, 'not', **layer_opt_nb, max_points=0)
    cell_chip.add(gnd_plane)

## Add cells to top cell
cell_chip.add(cell_gnd_pos)
cell_chip.add(cell_junc)
cell_chip.add(cell_fins)

## Save the file
lib.write_gds(filepath)

