# This file contains various structures that can be imported to add to a chip or wafer
import gdspy
import numpy as np
import math
import structuresLib as structures


def squat_from_center_pt(loc, qpad_x, qpad_y, qpad_angle, qpad_separation, fillet_radius, 
                         jj_gap, jj_finger_width, 
                         pad_layer, pin_layer, under_layer):
      qpad1  = gdspy.Round(
                    center= (loc[0]+qpad_separation/2, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = qpad_angle/2,
                    final_angle = -qpad_angle/2,
                    **pad_layer)
      qpad1.fillet(fillet_radius)
      qpad2  = gdspy.Round(
                    center= (loc[0]-qpad_separation/2, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = math.pi-qpad_angle/2,
                    final_angle = math.pi+qpad_angle/2,
                    **pad_layer)
      qpad2.fillet(fillet_radius)
      

      jpadCenter1 = (loc[0]-qpad_separation/2-fillet_radius/math.sin(qpad_angle/2), loc[1])
      jpadCenter2 = (loc[0]+qpad_separation/2+fillet_radius/math.sin(qpad_angle/2), loc[1])
      jxnpad1 = gdspy.Round(jpadCenter1, fillet_radius, **pin_layer)
      jxnpad2 = gdspy.Round(jpadCenter2, fillet_radius, **pin_layer)

      dolan, dolan_und = structures.dolan(
           start=jpadCenter1,
           end=jpadCenter2,
           fingerWidth=jj_finger_width,
           gap=jj_gap,
           layerMetal=pin_layer['layer'],
           layerShadow=under_layer['layer']
      )
      jpads = gdspy.boolean(jxnpad1, jxnpad2, 'or', layer=pin_layer['layer'])
      dolan = gdspy.boolean(jpads, dolan, 'or', layer=pin_layer['layer'])


      return [qpad1, qpad2], [dolan], [dolan_und]



def squat_from_rhs_pt(loc, qpad_x, qpad_y, qpad_angle, qpad_separation, fillet_radius, 
                         jj_gap, jj_finger_width, 
                         pad_layer, pin_layer, under_layer):
      qpad1  = gdspy.Round(
                    center= (loc[0]-qpad_x, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = qpad_angle/2,
                    final_angle = -qpad_angle/2,
                    **pad_layer)
      qpad1.fillet(fillet_radius)
      qpad2  = gdspy.Round(
                    center= (loc[0]-qpad_x-qpad_separation, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = math.pi-qpad_angle/2,
                    final_angle = math.pi+qpad_angle/2,
                    **pad_layer)
      qpad2.fillet(fillet_radius)
      

      jpadCenter1 = (loc[0]-qpad_separation-fillet_radius/math.sin(qpad_angle/2)-qpad_x, loc[1])
      jpadCenter2 = (loc[0]+fillet_radius/math.sin(qpad_angle/2)-qpad_x, loc[1])
      jxnpad1 = gdspy.Round(jpadCenter1, fillet_radius, **pin_layer)
      jxnpad2 = gdspy.Round(jpadCenter2, fillet_radius, **pin_layer)

      dolan, dolan_und = structures.dolan(
           start=jpadCenter1,
           end=jpadCenter2,
           fingerWidth=jj_finger_width,
           gap=jj_gap,
           layerMetal=pin_layer['layer'],
           layerShadow=under_layer['layer']
      )
      jpads = gdspy.boolean(jxnpad1, jxnpad2, 'or', layer=pin_layer['layer'])
      dolan = gdspy.boolean(jpads, dolan, 'or', layer=pin_layer['layer'])


      return [qpad1, qpad2], [dolan], [dolan_und]



def squat_from_lhs_pt(loc, qpad_x, qpad_y, qpad_angle, qpad_separation, fillet_radius, 
                         jj_gap, jj_finger_width, 
                         pad_layer, pin_layer, under_layer):
      qpad1  = gdspy.Round(
                    center= (loc[0]+qpad_x+qpad_separation, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = qpad_angle/2,
                    final_angle = -qpad_angle/2,
                    **pad_layer)
      qpad1.fillet(fillet_radius)
      qpad2  = gdspy.Round(
                    center= (loc[0]+qpad_x, loc[1]), #(l1[0]-line_xoffset-qpad_x-qpad_gap, qubit_y),
                    radius=(qpad_x, qpad_y),
                    initial_angle = math.pi-qpad_angle/2,
                    final_angle = math.pi+qpad_angle/2,
                    **pad_layer)
      qpad2.fillet(fillet_radius)
      

      jpadCenter1 = (loc[0]-fillet_radius/math.sin(qpad_angle/2)+qpad_x, loc[1])
      jpadCenter2 = (loc[0]+qpad_separation+fillet_radius/math.sin(qpad_angle/2)+qpad_x, loc[1])
      jxnpad1 = gdspy.Round(jpadCenter1, fillet_radius, **pin_layer)
      jxnpad2 = gdspy.Round(jpadCenter2, fillet_radius, **pin_layer)

      dolan, dolan_und = structures.dolan(
           start=jpadCenter1,
           end=jpadCenter2,
           fingerWidth=jj_finger_width,
           gap=jj_gap,
           layerMetal=pin_layer['layer'],
           layerShadow=under_layer['layer']
      )
      jpads = gdspy.boolean(jxnpad1, jxnpad2, 'or', layer=pin_layer['layer'])
      dolan = gdspy.boolean(jpads, dolan, 'or', layer=pin_layer['layer'])


      return [qpad1, qpad2], [dolan], [dolan_und]