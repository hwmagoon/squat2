#!/usr/bin/env python3

import gdspy
import math
import structuresLib as structures
from squatHelperLib import *

def oxide_ion_mill_from_lhs_pt(loc, qpad_x, qpad_y, qpad_angle, oxide_overlap, N_island, len_island, width_island, sep_island,  fillet_radius,
                         pad_layer, oxide_layer):
    # first probe pad
    qpad2  = gdspy.Round(
                center=(loc[0]+qpad_x, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                radius=(qpad_x, qpad_y),
                initial_angle = math.pi-qpad_angle/2,
                final_angle = math.pi+qpad_angle/2,
                **pad_layer)
    qpad2.fillet(fillet_radius)

    # probe to island
    probe_to_island = gdspy.Rectangle(
                (loc[0]+qpad_x-oxide_overlap, loc[1]-oxide_overlap/2),
                (loc[0]+qpad_x+sep_island+oxide_overlap, loc[1]+oxide_overlap/2),
                **pad_layer)
    
    # combine probe to island with qpad2
    qpad2 = gdspy.boolean(qpad2, probe_to_island, 'or', **pad_layer)

    qpad_separation = sep_island+oxide_overlap

    islands_list = []
    between_islands_list = []
    for N in range(N_island):
        island = gdspy.Rectangle(
                (loc[0]+qpad_x+qpad_separation-oxide_overlap, loc[1]-width_island/2),
                (loc[0]+qpad_x+qpad_separation+len_island+oxide_overlap, loc[1]+width_island/2),
                **oxide_layer)
        islands_list.append(island)
        qpad_separation += len_island

        if N == N_island-1:
            break

        between_islands = gdspy.Rectangle(
                (loc[0]+qpad_x+qpad_separation, loc[1]-oxide_overlap/2),
                (loc[0]+qpad_x+qpad_separation+sep_island+2*oxide_overlap, loc[1]+oxide_overlap/2),
                **pad_layer)
        between_islands_list.append(between_islands)
        qpad_separation += sep_island+2*oxide_overlap

    # probe to island
    probe_to_island2 = gdspy.Rectangle(
                (loc[0]+qpad_x+qpad_separation, loc[1]-oxide_overlap/2),
                (loc[0]+qpad_x+qpad_separation+sep_island+oxide_overlap+oxide_overlap, loc[1]+oxide_overlap/2),
                **pad_layer)
    
    # second probe pad
    qpad1  = gdspy.Round(
                center=(loc[0]+qpad_x+qpad_separation+sep_island+oxide_overlap, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                radius=(qpad_x, qpad_y),
                initial_angle = qpad_angle/2,
                final_angle = -qpad_angle/2,
                **pad_layer)
    qpad1.fillet(fillet_radius)

    # combine probe to island with qpad1    
    qpad1 = gdspy.boolean(qpad1, probe_to_island2, 'or', **pad_layer)


    text_size = 80
    # add text of N_island below center of islands
    text = gdspy.Text(f"{N_island}", size=text_size, position=(loc[0]+qpad_x+(qpad_separation+sep_island+oxide_overlap-text_size)/2, loc[1]-width_island/2-20-text_size), layer=oxide_layer['layer'])

    # add text of overlap above center of islands
    horizontal = True
    if N_island == 1:
        horizontal = False
    text2 = gdspy.Text(f"{round(oxide_overlap)}", size=text_size, position=(loc[0]+qpad_x+(qpad_separation+oxide_overlap-text_size+(not horizontal)*text_size)/2, loc[1]+width_island/2+20+(not horizontal)*text_size), horizontal=horizontal, layer=oxide_layer['layer'])

    # combine text with islands
    islands_list.append(text)
    islands_list.append(text2)

    return [qpad1, qpad2], islands_list, between_islands_list


def checkerboard(loc, width, num, layer):
    squares = []
    for i in range(num):
        for j in range(num):
            if (i+j)%2 == 0:
                square = gdspy.Rectangle(
                    (loc[0]+i*width, loc[1]+j*width),
                    (loc[0]+(i+1)*width, loc[1]+(j+1)*width),
                    **layer)
                squares.append(square)
    return squares

## To do
## -- do i want a material test clover for junction layer?

####------------------------------------------------------####
####                   Parameters                         ####
####------------------------------------------------------####

# get current time for file naming
import datetime
now = datetime.datetime.now()

name = "ion_mill_mask_v1_time"
name = name.replace("time", now.strftime("%Y%m%d-%H%M%S"))
filepath = f"./GDS/ion_mill/{name}.gds"

## GDS Layers
layer_chip     = {"layer": 0, "datatype": 0}
layer_al_oxide   = {"layer": 1, "datatype": 0}
layer_al_pad   = {"layer": 2, "datatype": 0}
# layer_eb_pin   = {"layer": 3, "datatype": 0}
# layer_eb_under = {"layer": 4, "datatype": 0}


## Chip setup
chip_x = 10000     ## [float] chip x-dimension
chip_y = 10000     ## [float] chip y-dimension
border = 10        ## [float] min distannce from any feature to edge of chip
dice_width = 300   ## [float] width of dicing saw lanes
gnd_plane = False   ## [bool]  indicates whether there should be a gnd plane
clover_size = 300  #450
fillet_r_small = 2


## Ebeam Features
eb_align_dim    = 40   ## [float] side length of ebeam alignment squares
eb_align_offset = 480  ## [float] distance between ebeam marker and side of the chip


## Parameters for individual SQUATs
qpad_x = 110                 ## [float]  x radius of SQUAT fins (i.e. x direction fin length)
qpad_y = 110                 ## [float]  y radius of SQUAT fins
qpad_angle = 7*math.pi/8     ## [float]  angle of sector carved out by SQUAT fin
qpad_separation = 200        ## [float]  distance in center between fins (i.e. length of junction structure)
qpad_spacing_mult = [0.5, 0.8]    ## [2 item list] multipliers for feature spacing in x and y directions


## Parameters for oxide ion mill
oxide_overlap = 4
N_island = 8
len_island = 10
width_island = 25
sep_island = 20
redundancy = 5      ## [int] number of redundant junctions to make 

## Array parameters
# qpad_array_spacing_mult = 0.7 ## [float] Spacing between elements = (this multiplier) * (the width of each array feature)

jj_gaps = np.array([
    [0.10, 0.15, 0.20, 0.25],
    [0.10, 0.15, 0.20, 0.25],
    [0.10, 0.15, 0.20, 0.00],
    [0.10, 0.15, 0.20, 0.00]
])

jj_finger_widths = np.array([
    [0.08, 0.08, 0.08, 0.08],
    [0.10, 0.10, 0.10, 0.10],
    [0.12, 0.12, 0.12, 0.12],
    [0.14, 0.14, 0.14, 0.14]
])

overlaps = np.linspace(4.0, 22.0, 7)
N_vals = np.array([1, 2, 3, 6, 10])


## Row of dose test SQUATS at bottom.  Will do different ebeam doses to each set of probe pads
##   each jj will be the same (using the following finger width and gap)
##   but I'll use this as a dose test for probe pads
cal_jj_finger_width = 0.18
cal_jj_gap = 0.15
ndoses = 5
cal_qpad_separation = 100


####------------------------------------------------------####
####                     Setup                            ####
####------------------------------------------------------####


lib = gdspy.GdsLibrary()

## Make cells
cell_chip     = lib.new_cell('chip')
# cell_gnd_neg  = lib.new_cell('gnd_neg')
cell_probes    = lib.new_cell('probes')
cell_islands     = lib.new_cell('islands')


## Make chip outline as a reference
full_rect = gdspy.Rectangle((-dice_width/2., -dice_width/2.), (chip_x+dice_width/2., chip_y+dice_width/2.), **layer_chip)
chip_rect = gdspy.Rectangle((0,0), (chip_x,chip_y), **layer_chip)
cell_chip.add(full_rect)
cell_chip.add(chip_rect)


# ## Make ebeam alignment boxes
# ## -- Subtract ebeam align boxes from the ground plane
# ## -- Add ebeam align boxes to the ebeam pin layer (so that they appear in the cjob file)
# align_locs = [[chip_x-eb_align_offset-eb_align_dim, chip_y-eb_align_offset-eb_align_dim], 
#                 [chip_x-eb_align_offset-eb_align_dim, eb_align_offset],
#                 [eb_align_offset, eb_align_offset],
#                 [eb_align_offset, chip_y-eb_align_offset-eb_align_dim]]
# for idx, loc in enumerate(align_locs):
#     align_box_opt = gdspy.Rectangle([loc[0],loc[1]], [loc[0]+eb_align_dim,loc[1]+eb_align_dim], **layer_al_oxide)
#     cell_gnd_neg.add(align_box_opt)



####------------------------------------------------------####
####                Calibration Features                  ####
####------------------------------------------------------####


# add aligment pluses to the corners of the chip
plus_size = 300
plus_width = 40

# top right to both layers
plus_tr = structures.plus(plus_size, plus_width, (chip_x+dice_width/2, chip_y+dice_width/2), layer_al_oxide['layer'])
plus_tr_2 = structures.plus(plus_size, plus_width, (chip_x+dice_width/2, chip_y+dice_width/2), layer_al_pad['layer'])

# top left
plus_tl = structures.plus(plus_size, plus_width, (-dice_width/2, chip_y+dice_width/2), layer_al_oxide['layer'])
plus_tl_2 = structures.plus(plus_size, plus_width, (-dice_width/2, chip_y+dice_width/2), layer_al_pad['layer'])

# bottom right
plus_br = structures.plus(plus_size, plus_width, (chip_x+dice_width/2, -dice_width/2), layer_al_oxide['layer'])
plus_br_2 = structures.plus(plus_size, plus_width, (chip_x+dice_width/2, -dice_width/2), layer_al_pad['layer'])

# bottom left
plus_bl = structures.plus(plus_size, plus_width, (-dice_width/2, -dice_width/2), layer_al_oxide['layer'])
plus_bl_2 = structures.plus(plus_size, plus_width, (-dice_width/2, -dice_width/2), layer_al_pad['layer'])

cell_islands.add([plus_tr, plus_tl, plus_br, plus_bl])
cell_probes.add([plus_tr_2, plus_tl_2, plus_br_2, plus_bl_2])


# add smaller alignment pluses to corners of the chip
plus_size = 80
plus_width = 10

# top right to both layers
plus_tr = structures.plus(plus_size, plus_width, (chip_x, chip_y), layer_al_oxide['layer'])
plus_tr_2 = structures.plus(plus_size, plus_width, (chip_x, chip_y), layer_al_pad['layer'])

# top left
plus_tl = structures.plus(plus_size, plus_width, (0, chip_y), layer_al_oxide['layer'])
plus_tl_2 = structures.plus(plus_size, plus_width, (0, chip_y), layer_al_pad['layer'])

# bottom right
plus_br = structures.plus(plus_size, plus_width, (chip_x, 0), layer_al_oxide['layer'])
plus_br_2 = structures.plus(plus_size, plus_width, (chip_x, 0), layer_al_pad['layer'])

# bottom left
plus_bl = structures.plus(plus_size, plus_width, (0, 0), layer_al_oxide['layer'])
plus_bl_2 = structures.plus(plus_size, plus_width, (0, 0), layer_al_pad['layer'])

cell_islands.add([plus_tr, plus_tl, plus_br, plus_bl])
cell_probes.add([plus_tr_2, plus_tl_2, plus_br_2, plus_bl_2])


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
# qpad_gnd_cutout_radius = np.array([qpad_spacing_mult[0]*(qpad_x+qpad_separation/2), qpad_spacing_mult[1]*(qpad_y)])
# feature_array_space = 2*qpad_gnd_cutout_radius*qpad_array_spacing_mult
center_vals = np.array([(chip_x/8, 11*chip_y/32),
                        (7*chip_x/16, 11*chip_y/32),
                        (3*chip_x/4, 11*chip_y/32),
                        (2*chip_x/16, 11*chip_y/16),
                        (10*chip_x/16, 11*chip_y/16),
                        (5*chip_x/16, 7*chip_y/8)])


# ## Figure out placement on chip
# ncols = len(jj_gaps[0])
# nrows = len(jj_gaps)
# if ncols%2 == 0:
#     print("Number of columns is even")
#     ypos = chip_center[1] + feature_array_space[1]*(ncols+2)/2
# else:
#     print("Number of columns is odd")
#     ypos = chip_center[1] + feature_array_space[1]*(ncols+1)/2
# if nrows%2 == 0:
#     print("Number of rows is even")
#     xpos_start = chip_center[0] - feature_array_space[0]*(nrows+2)/2
# else:
#     print("Number of rows is odd")
#     xpos_start = chip_center[0] - feature_array_space[0]*(nrows+1)/2
# xpos = xpos_start 



## Make a junction at each array location
# for col in range(0, ncols):
#     for row in range(0, nrows):
#         loc = [xpos, ypos]
#         ## Make junction
#         qpads, islands, between = oxide_ion_mill_from_lhs_pt(loc=loc, 
#                                 qpad_x=qpad_x, qpad_y=qpad_y, 
#                                 qpad_angle=qpad_angle, oxide_overlap=oxide_overlap,
#                                 N_island=N_island, len_island=len_island, width_island=width_island,
#                                 sep_island=sep_island, fillet_radius=fillet_r_small,
#                                 pad_layer=layer_al_pad, oxide_layer=layer_al_oxide)
#         cell_probes.add(qpads)
#         cell_probes.add(between)

#         cell_islands.add(islands)

#         ## Update x location
#         xpos += 2*feature_array_space[0]
#     xpos = xpos_start
#     ypos -= 2*feature_array_space[1]


# add text in center of chip
text = gdspy.Text(name, size=100, position=(0.40*chip_x, 0.45*chip_y), layer=layer_al_oxide['layer'])
cell_islands.add(text)

## Make material test clovers
clover1, cloverCirc1 = structures.cloverleaf(center = [0.320*chip_x, 0.46*chip_y], D=clover_size, clover_layer=layer_al_oxide['layer'], circ_layer=layer_al_oxide['layer'])
cell_chip.add([clover1])

# add checkerboard pattern
num_squares = 10
width_square = 20 # width of each square (in um)
checkerboard_1 = checkerboard([0.355*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_oxide)
cell_islands.add(checkerboard_1)

# add checkerboard pattern
num_squares = 10
width_square = 10 # width of each square (in um)
checkerboard_1 = checkerboard([0.380*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_oxide)
cell_islands.add(checkerboard_1)

# add smaller checkerboard pattern
num_squares = 10
width_square = 4 # width of each square (in um)
checkerboard_2 = checkerboard([0.392*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_oxide)
cell_islands.add(checkerboard_2)

# add tiny checkerboard pattern
num_squares = 10
width_square = 1 # width of each square (in um)
checkerboard_3 = checkerboard([0.398*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_oxide)
cell_islands.add(checkerboard_3)


# add same checkerboard patterns to the right of the clover on layer_al_pad
num_squares = 10
width_square = 1 # width of each square (in um)
checkerboard_1 = checkerboard([0.69*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_pad)
cell_probes.add(checkerboard_1)

# add checkerboard pattern
num_squares = 10
width_square = 4 # width of each square (in um)
checkerboard_1 = checkerboard([0.696*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_pad)
cell_probes.add(checkerboard_1)

# add checkerboard pattern
num_squares = 10
width_square = 10 # width of each square (in um)
checkerboard_1 = checkerboard([0.708*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_pad)
cell_probes.add(checkerboard_1)

# add checkerboard pattern
num_squares = 10
width_square = 20 # width of each square (in um)
checkerboard_1 = checkerboard([0.733*chip_x, 0.45*chip_y], width_square, num_squares, layer_al_pad)
cell_probes.add(checkerboard_1)

# make clover on layer_al_pad
clover1, cloverCirc1 = structures.cloverleaf(center = [0.79*chip_x, 0.46*chip_y], D=clover_size, clover_layer=layer_al_pad['layer'], circ_layer=layer_al_pad['layer'])
cell_probes.add([clover1])







for i, N in enumerate(N_vals):
    ## Figure out placement on chip
    chip_center = center_vals[i]

    if i == len(N_vals)-1:
        Neff = N*1.3
    else:
        Neff = N

    feature_array_space = np.array([2*qpad_x+Neff*(sep_island+width_island+2*oxide_overlap)*qpad_spacing_mult[0], 2*qpad_y*qpad_spacing_mult[1]])

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
        xpos_start = chip_center[0] - feature_array_space[0]*(nrows+1)/2
    xpos = xpos_start 
    
    for overlap in overlaps:
        for _ in range(redundancy):
            loc = [xpos, ypos]
            ## Make junction
            qpads, islands, between = oxide_ion_mill_from_lhs_pt(loc=loc, 
                                    qpad_x=qpad_x, qpad_y=qpad_y, 
                                    qpad_angle=qpad_angle, oxide_overlap=overlap,
                                    N_island=N, len_island=len_island, width_island=width_island,
                                    sep_island=sep_island, fillet_radius=fillet_r_small,
                                    pad_layer=layer_al_pad, oxide_layer=layer_al_oxide)
            cell_probes.add(qpads)
            cell_probes.add(between)

            cell_islands.add(islands)

            ## Update x location
            xpos += 2*feature_array_space[0]
        xpos = xpos_start
        ypos -= 2*feature_array_space[1]


# add shorted row of pads (N=0) for comparison below existing structures
N = 0
overlap = 20
[xpos, ypos] = (0.23*chip_x, 0.425*chip_y)
feature_array_space = (200, 0)
for _ in range(redundancy*3):
    loc = [xpos, ypos]
    ## Make junction
    qpads, _, between = oxide_ion_mill_from_lhs_pt(loc=loc, 
                            qpad_x=qpad_x, qpad_y=qpad_y, 
                            qpad_angle=qpad_angle, oxide_overlap=overlap,
                            N_island=N, len_island=len_island, width_island=width_island,
                            sep_island=sep_island, fillet_radius=fillet_r_small,
                            pad_layer=layer_al_pad, oxide_layer=layer_al_oxide)
    cell_probes.add(qpads)
    cell_probes.add(between)

    # cell_islands.add(islands)

    ## Update x location
    xpos += 2*feature_array_space[0]

####------------------------------------------------------####
####         Calibration Array along bottom               ####
####------------------------------------------------------####
    

# ## Figure out starting position and spacing
# feature_array_space = 2*qpad_x
# if ndoses%2 == 0:
#     print("Number of dose tests is even")
#     xpos_start = chip_center[0] - feature_array_space*(ndoses+2)/2
# else:
#     print("Number of dose tests is odd")
#     xpos_start = chip_center[0] - feature_array_space*(ndoses+1)/2
# xpos = xpos_start
# ypos = 4*eb_align_offset

# ## Make a new layer for each set of pads
# pad_dose_layer = {"layer": 5, "datatype": 0}

# ## Make a row of the same feature, each with pads in a new layer
# for i in range(0, ndoses):
#     loc = [xpos, ypos]
#     qpads, jpads, und = squat_from_center_pt(loc=loc, 
#                                         qpad_x=qpad_x, qpad_y=qpad_y, 
#                                         qpad_angle=qpad_angle, qpad_separation=cal_qpad_separation, 
#                                         fillet_radius=fillet_r_small, 
#                                         jj_gap=cal_jj_gap, jj_finger_width=cal_jj_finger_width, 
#                                         pad_layer=pad_dose_layer, pin_layer=layer_eb_pin, under_layer=layer_eb_under)
#     ## Add junctions to cells
#     cell_fins.add(qpads)
#     cell_junc.add(jpads)
#     cell_junc.add(und)
#     ## Make cutout in ground plane
#     qpad_gnd_cutout = gdspy.Round(center=loc, radius=2*qpad_x, **layer_opt_nb)
#     cell_gnd_neg.add(qpad_gnd_cutout)
#     ## Update position and pad layer
#     xpos += 2*feature_array_space
#     pad_dose_layer['layer'] += 1



####------------------------------------------------------####
####                  Save file                           ####
####------------------------------------------------------####

## If there is a ground plane, make a ground plane and subtract the contents of the 'ground plane' layer
## -- otherwise, add the contents of the ground plane layer
# if gnd_plane:
#     gnd_plane = gdspy.Rectangle((0,0), (chip_x, chip_y), **layer_al_1)
#     gnd_plane = gdspy.boolean(gnd_plane, cell_gnd_neg, 'not', **layer_al_1, max_points=0)
#     cell_chip.add(gnd_plane)


## Add cells to top cell
cell_chip.add(cell_probes)
cell_chip.add(cell_islands)


# move all features -chip_x/2, -chip_y/2 to center the design
cell_chip.translate(-chip_x/2, -chip_y/2)


lib.write_gds(filepath)







