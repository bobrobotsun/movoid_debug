#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/18
Description:    
"""
from movoid_debug.flow.traceback import Traceback
from test_traceback import test_1, test_2, index

index += [1, 2]
tb = Traceback()
try:
    test_1.test_f1(1)
    test_2.test_f1('1')
except:
    tb.init()
    tb.test()
    tb.test2()
try:
    test_1.wrapper('123')
except:
    tb.init()
    tb.test()
