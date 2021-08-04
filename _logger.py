# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 02:09:04 2018

logging handler

@author: Jullian G. Damasceno
"""

import os
import logging

def logger_path(lpath=None):
    """[Get and/or set path for the .log file rw]

    Args:
        lpath ([string], optional): [Custom path for .log file]. Defaults to None which will get a default path]

    Returns:
        [string]: [.log file path]
    """
    path = os.path.dirname(os.path.realpath(__file__))
    if not lpath:
        log_file = path + "\\logs\\GDAPP_info.log"
    else:
        log_file = lpath + "\\GDAPP_info.log"
    return log_file

def formatter():
    """[Format strings into expected output]

    Returns:
        [string]: [Formatted string]
    """
    return '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def logger_define(log_file):
    """[Define the instance of logger that'll be responsible for logging activity]

    Args:
        log_file ([string]): [.log path]

    Returns:
        [logger]: [logger instance]
    """

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
