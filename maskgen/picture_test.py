# -*- coding: utf-8 -*-
"""Convert an image file to a GDS file
stolen from:
https://github.com/kadomoto/picture-to-gds/tree/master
"""

import cv2
import numpy as np
import gdspy
from tqdm import tqdm

import argparse

def minmax(v):
    if v > 255:
        v = 255
    if v < 0:
        v = 0
    return v

def img_to_gds(fileName, scale_factor, layer, isDither, scale=1.0, loc=(0, 0)):
    """Convert an image file (fileName) to a GDS file
    returns the GDS object
    """
    print("Converting an image file to a GDS file..")
    # Read an image file
    img = cv2.resize(cv2.imread(fileName), dsize=None, fx=scale, fy=scale)

    width = img.shape[1]
    height = img.shape[0]
    print("width:{0}".format(width))
    print("height:{0}".format(height))

    # Convert an image to grayscale one
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    if(isDither):
        # Floyd–Steinberg dithering
        # https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering
        for y in range(0, height-1):
            for x in range(1, width-1):
                old_p = gray[y, x]
                new_p = np.round(old_p/255.0) * 255
                gray[y, x] = new_p            
                error_p = old_p - new_p
                gray[y, x+1] = minmax(gray[y, x+1] + error_p * 7 / 16.0)
                gray[y+1, x-1] = minmax(gray[y+1, x-1] + error_p * 3 / 16.0)
                gray[y+1, x] = minmax(gray[y+1, x] + error_p * 5 / 16.0)
                gray[y+1, x+1] = minmax(gray[y+1, x+1] + error_p * 1 / 16.0)
        
        ret, binaryImage = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    else:
        ret, binaryImage = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

    # Fill orthological corner
    for x in range(width - 1):
        for y in range(height - 1):
            if binaryImage.item(y, x) == 0 and binaryImage.item(y + 1, x) == 255 \
                    and binaryImage.item(y, x + 1) == 255 and binaryImage.item(y + 1, x + 1) == 0:
                binaryImage.itemset((y + 1, x), 0)
            elif binaryImage.item(y, x) == 255 and binaryImage.item(y + 1, x) == 0 \
                    and binaryImage.item(y, x + 1) == 0 and binaryImage.item(y + 1, x + 1) == 255:
                binaryImage.itemset((y + 1, x + 1), 0)

    # # Output image.bmp
    # cv2.imwrite("image.bmp", binaryImage)
    
    # # The GDSII file is called a library, which contains multiple cells.
    # lib = gdspy.GdsLibrary()
    # gdspy.current_library=gdspy.GdsLibrary()

    # # Geometry must be placed in cells.
    # unitCell = lib.new_cell('CELL')
    # square = gdspy.Rectangle((0.0, 0.0), (1.0, 1.0), layer=(int)(layerNum))
    # unitCell.add(square)

    grid = gdspy.Cell("GRID")

    for x in tqdm(range(width)):
        for y in range(height):
            if binaryImage.item(y, x) == 0:
                # print("({0}, {1}) is black".format(x, y))

                cell = gdspy.Rectangle((scale_factor*x + loc[0], scale_factor*(height - y - 1) + loc[1]), (scale_factor*(x+1) + loc[0], scale_factor*(height -y -2) + loc[1]), **layer)
                grid = gdspy.boolean(grid, cell, "or", layer=layer["layer"])

    # scaledGrid = gdspy.CellReference(
    #     grid, origin=(0, 0), magnification=(float)(sizeOfTheCell))

    # # Add the top-cell to a layout and save
    # top = lib.new_cell("TOP")
    # top.add(scaledGrid)

    return grid

    # lib.write_gds("image.gds")