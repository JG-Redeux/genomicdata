# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 12:30:25 2018

auxiliary functions

@author: Usagi
"""

from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np

def image_divider(image):
    pil_img = Image.open(image)
    arr_img = np.array(pil_img)
    custom_height = arr_img.shape[0] // 3
    pix_group = []

    for i in range(0, arr_img.shape[0], custom_height):
        j = i + custom_height
        if len(pix_group) < 3:
            pix_group.append(arr_img[i:j])
    return pix_group

def print_img(img_list):
    for item in img_list:
        imgpix = Image.fromarray(item)
        imgpix.show()

def pil_to_qt(img_list):
    qt_pix_list = []
    for item in img_list:
        imgpix = Image.fromarray(item)
        qt_img = ImageQt(imgpix)
        qt_pix_list.append(qt_img)
    return qt_pix_list

def str_to_hex(string, factor):
    hex_list = []
    for char in string:
        hex_list.append(hex(ord(char) * int(factor)))
    return " ".join(hex_list)

def hex_to_str(hexa, factor):
    hex_list = hexa.split(" ")
    str_list = []
    for hex_ind in hex_list:
        h = int(int(hex_ind, 0) / int(factor))
        str_list.append(chr(h))
    return "".join(str_list)

def barcode_gen():
    pass
