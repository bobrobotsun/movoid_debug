#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/17
Description:    
"""
import sys


def test1():
    a = 1
    print('test1 start')
    raise Exception('test1')
    print('test1 end')


def test2():
    a = 2
    print('test2 start')
    test1()
    print('test2 start')


try:
    test2()
except:
    tb = sys.exc_info()[2]
    while tb.tb_next is not None:
        tb = tb.tb_next
    frame = tb.tb_frame
    code = frame.f_code
    name = code.co_name
    global_dict = frame.f_globals
    func = global_dict.get(name)


    def test_func():
        a = 0
        print('test func start')


    global_dict[name] = test_func
    print(frame.f_globals)
    print(frame.f_locals)
    test1()
    print(frame.f_locals)
