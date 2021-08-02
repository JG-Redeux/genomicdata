# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 02:09:04 2018

logging handler

@author: Jullian GD.
"""

import os
import logging

def logger_path(lpath=None):
    path = os.path.dirname(os.path.realpath(__file__))
    if not lpath:
        log_file = path + "\\logs\\GDAPP_info.log"
    else:
        log_file = lpath + "\\GDAPP_info.log"
    return (log_file)

def formatter():
    return '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def logger_define(log_file):

    log_file = logger_path(log_file)
    form = formatter()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    dhandler = logging.FileHandler(log_file, "a")
    dhandler.setLevel(logging.DEBUG)
    dhandler.setFormatter(logging.Formatter(form))
    logger.addHandler(dhandler)

    ihandler = logging.FileHandler(log_file, "a")
    ihandler.setLevel(logging.INFO)
    ihandler.setFormatter(logging.Formatter(form))
    # logger.addHandler(ihandler)

    return logger
