# This file contains various structures that can be imported to add to a chip or wafer
import gdspy
import numpy as np

###########################################
# TEST STRUCTURES
###########################################

"""
Cloverleaf for conductivity probing
Reference DOI: 10.1088/0957-0233/26/11/115004
Where applicable, parameters match parameters in reference paper fig 3b
Inputs:
  D       cloverleaf outer diameter
  w       width of slits
  r       radius of slit inner corner curve
  l       length of slits
  center  [x,y] position of cloverleaf center
  layer   object layer
Output:
  cloverleaf polygon
  boundingCircle polygon of circle hole around clover
"""
## [HM] -- adding circle layer as an argument and renaming variables accordingly
def cloverleaf(D = 300, w = 30, r = 15, l = 100, center = (0,0), clover_layer = 0, circ_layer = 0):
    cloverleaf = gdspy.Round(center, D/2.)
    cutout_up = gdspy.Rectangle([center[0]+w/2., center[1]+D/2.-l], [center[0]-w/2., center[1]+D])
    cutout_down = gdspy.Rectangle([center[0]+w/2., center[1]-D/2.+l], [center[0]-w/2., center[1]-D])
    cutout_right = gdspy.Rectangle([center[0]+D/2.-l, center[1]-w/2.], [center[0]+D, center[1]+w/2.])
    cutout_left = gdspy.Rectangle([center[0]-D/2.+l, center[1]-w/2.], [center[0]-D, center[1]+w/2.])

    cutout_up.fillet(r)
    cutout_down.fillet(r)
    cutout_right.fillet(r)
    cutout_left.fillet(r)

    cloverleaf = gdspy.boolean(cloverleaf, [cutout_up,cutout_down,cutout_right,cutout_left], 'not', layer = clover_layer)

    boundingCircle = gdspy.Round(center, D/2.+2.*w, layer = circ_layer)

    return cloverleaf, boundingCircle

###########################################
# ALIGNMENT MARKS
###########################################

"""
"Plus" alignment mark for dicing
Inputs:
  l       length of plus lines
  w       width of plus lines
  center  center of plus
  layer   object layer
Output:
  Plus polygon
"""
def plus(l = 80, w = 7, center = [0,0], layer = 0):
    vertical = gdspy.Rectangle([center[0]+w/2.,center[1]+l/2.], [center[0]-w/2.,center[1]-l/2.])
    horizontal = gdspy.Rectangle([center[0]+l/2.,center[1]+w/2.], [center[0]-l/2.,center[1]-w/2.])

    plus = gdspy.boolean(vertical, horizontal, 'or', layer = layer)

    return plus

"""
Quarter "plus" alignment mark for dicing
Inputs:
  l       length of full plus lines (once joined to other three quarters)
  w       width of full plus lines
  center  center of full plus
  corner  options for which direction to point, labeled by chip corner: 'tl' 'tr' 'bl' 'br'
  layer   object layer
Output:
  Plus polygon
"""
def partplus(l = 80, w = 7, center = [0,0], corner = 'bl', layer = 0):
    if corner == 'bl' or corner == 'tl':
        hDir = 1
    else:
        hDir = -1
    if corner == 'tl' or corner == 'tr':
        vDir = -1
    else:
        vDir = 1
    vertical = gdspy.Rectangle([center[0], center[1]], [center[0]+hDir*w/2., center[1]+vDir*l/2.])
    horizontal = gdspy.Rectangle([center[0],center[1]], [center[0]+hDir*l/2., center[1]+vDir*w/2.])

    partplus = gdspy.boolean(vertical, horizontal, 'or', layer = layer)

    return partplus


###########################################
# JUNCTIONS
###########################################

"""
Junction circular pads
These are the small pads that either Manhattan or Dolan junctions connect to
Inputs:
  center1, center2    coordinates of pad centers
  r                   radius of pads
  layer               object layer
Output:
  pads polygon
"""
def jxnCircPads(center1 = [0,0], center2 = [10,10], r = 2, layer = 0):
    jxnpad1 = gdspy.Round(center1, r)
    jxnpad2 = gdspy.Round(center2, r)
    jxnPads = gdspy.boolean(jxnpad1, jxnpad2, 'or', layer = layer)

    return jxnPads

"""
Dolan junction
Makes a horizontal junction (but can be rotated later).  All units are um
Inputs:
    start, end                  coordinates of L/R limits of jxn area
    fingerWidth                 width of jxn finger
    gap                         gap between finger tip and line
    lineWidth                   width of lines approaching jxn
    taperLength                 length of triangle that tapers to jxn finger
    fingerLength                length of jxn finger
    shadowWidth                 thickness of shadow offset from metal
    shadowRegionLength          length along each line shadow region extends
    layerMetal                  metal layer
    layerShadow                 shadow layer
Output:
    (dolan, shadow)             (polygon with junction layer,
                                polygon of shadow layer)
"""
def dolan(start = (0,0), end = (10,0), fingerWidth = 0.15, gap = 0.22, lineWidth = 2., taperLength = 2., fingerLength = 0.5, shadowWidth = 0.2, shadowRegionLength = 3, layerMetal = 0, layerShadow = 1):
    # a few definitions
    d = np.abs(end[0] - start[0]) # total width of junction region
    taperStartX = end[0]-d/2.-taperLength/2.+gap+fingerLength+taperLength # x location where rectangle starts taper

    # make lines
    rect1 = gdspy.Rectangle([start[0], start[1]-lineWidth/2.], [start[0]+d/2.-taperLength/2., start[1]+lineWidth/2.])
    rect2 = gdspy.Rectangle([end[0], end[1]-lineWidth/2.], [taperStartX, end[1]+lineWidth/2.])
    dolan = gdspy.boolean(rect1, rect2, 'or')

    # add taper
    taper = gdspy.Polygon([[taperStartX, end[1]-lineWidth/2.], [taperStartX, end[1]+lineWidth/2.], [taperStartX-taperLength, end[1]+fingerWidth/2.], [taperStartX-taperLength, end[1]-fingerWidth/2.]])
    dolan = gdspy.boolean(dolan, taper, 'or')

    # add finger
    finger = gdspy.Rectangle([taperStartX-taperLength, end[1]-fingerWidth/2.], [taperStartX-taperLength-fingerLength, end[1]+fingerWidth/2.])
    dolan = gdspy.boolean(dolan, finger, 'or', layer = layerMetal)

    # make shadow
    shadow = gdspy.offset(dolan, shadowWidth)

    # extend shadow for gap
    # note that if shadowWidth > gap, the shadow at the gap will be larger than the gap
    gapShadow = gdspy.Rectangle([start[0]+d/2.-taperLength/2., start[1]+lineWidth/2.+shadowWidth], [start[0]+d/2.-taperLength/2.+gap, start[1]-lineWidth/2.-shadowWidth])
    shadow = gdspy.boolean(shadow, gapShadow, 'or')

    # remove shadow away from junction
    removeRect = gdspy.Rectangle([start[0]+d/2.-taperLength/2.-shadowRegionLength, start[1]-lineWidth], [taperStartX+shadowRegionLength, end[1]+lineWidth])
    shadow = gdspy.boolean(shadow, removeRect, 'and', layer = layerShadow)

    ## [HM] removing overlap of junction and undercut layers area to avoid double-exposure in ebeam
    shadow = gdspy.boolean(shadow, dolan, 'not', layer=layerShadow)
    return dolan, shadow


"""
Manhattan junction and undercut
This code is copied from qubitDet_05b but has not been updated to work as a callable function with input variables.  Just for reference to turn into a function later.
"""
## junction
#qpad_realgap = qpad_gap + 2*(bend_r_small/math.sin(qpad_angle/2)-bend_r_small) # the real gap between the qubit pads taking into account the filleting
#jline_x2 = qpad_realgap/2 + bend_r_small
#jline2 = gdspy.Rectangle(
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2-qpad_realgap/2-bend_r_small, qubit_y-3*jline_y/2),
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2-qpad_realgap/2-bend_r_small+jline_x2, qubit_y-jline_y/2),
#        **metal3)
#qubitRowCell.add(jline2)
#
#jxn_l1 = bend_r_small+3*qpad_realgap/4
#jxn1 = gdspy.Rectangle(
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2+qpad_realgap/2+bend_r_small, qubit_y+jline_y/2),
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2+qpad_realgap/2+bend_r_small-jxn_l1, qubit_y+jline_y/2+jxn_w),
#        **metal3)
#qubitRowCell.add(jxn1)
#
#jxn2 = gdspy.Rectangle(
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2, qubit_y-3*jline_y/2),
#        (l1[0]-line_xoffset-qpad_x-qpad_gap/2+jxn_w, qubit_y-3*jline_y/2+jxn_l),
#        **metal3)
#qubitRowCell.add(jxn2)
#
#jxnpad1 = gdspy.Round((l1[0]-line_xoffset-qpad_x+bend_r_small/math.sin(qpad_angle/2), qubit_y), bend_r_small, **metal3)
#qubitRowCell.add(jxnpad1)
#
#jxnpad2 = gdspy.Round((l1[0]-line_xoffset-qpad_x-qpad_gap-bend_r_small/math.sin(qpad_angle/2), qubit_y), bend_r_small, **metal3)
#qubitRowCell.add(jxnpad2)
#
## junction undercut
#
#undercut = gdspy.offset([jline2, jxn1, jxn2, jxnpad1, jxnpad2], undercut_w_small, join_first=True, layer=4)
#qubitRowCell.add(undercut)

###########################################
# FLUX TRAPS
###########################################

"""
Add flux trap holes
"""

###########################################
# OTHER FUNCTIONS
###########################################

"""
Invert Nb optical layer
Inputs:
    lib         gdspy library
    chip        object, cell containing layers to invert
    posLayer    int, layer to substract from
    negLayer    int, layer to subtract
    resLayer    int, layer of result
"""
def invert_layer(chip, posLayer = 0, negLayer = 1, resLayer = 1):
    # layerPos - layerNeg gives the area that should not be Nb (the "inversion")
    layerNeg = chip.copy(chip.name+'_neg')
    layerPos = chip.copy(chip.name+'_pos')
    layerNeg.remove_polygons(lambda pts, layer, datatype: layer != negLayer)
    layerPos.remove_polygons(lambda pts, layer, datatype: layer != posLayer)
    inversion = gdspy.boolean(layerPos, layerNeg, 'not', layer = resLayer)
    chip.remove_polygons(lambda pts, layer, datatype: layer == resLayer)
    chip.add(inversion)

