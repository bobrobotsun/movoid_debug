#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : traceback
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/18 1:19
# Description   : 
"""
import sys


class Traceback:
    def __init__(self):
        temp_traceback = sys.exc_info()[2]
        self.traceback_list = [temp_traceback]
        while True:
            temp_traceback = temp_traceback.tb_next
            if temp_traceback is None:
                break
            else:
                self.traceback_list.append(temp_traceback)
