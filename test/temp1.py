#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/5/20
Description:    
"""
import sys
import traceback


def dec1(func):
    def dec_func1(*args, **kwargs):
        print('dec_func1')
        return func(*args, **kwargs)

    return dec_func1


@dec1
def test1():
    print('test1')
    test2()


@dec1
def test2():
    print('test2')
    raise Exception('wrong')


try:
    sys_exc_info = sys.exc_info()
    exc_type, exc_value, exc_traceback = sys_exc_info
    print(exc_type, exc_value, exc_traceback)
    test1()
except:
    sys_exc_info = sys.exc_info()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(type(sys_exc_info), len(sys_exc_info))
    print(exc_type, exc_value, exc_traceback)
    temp_traceback: traceback = exc_traceback
    while temp_traceback is not None:
        print(temp_traceback.tb_frame, temp_traceback.tb_lineno)
        temp_traceback = temp_traceback.tb_next
    # for i in dir(exc_traceback):
    #     v = getattr(exc_traceback, i)
    #     if callable(v):
    #         print(f'{i}(function) {v}')
    #     else:
    #         print(f'{i}({type(v).__name__}) {v}')

    # 提取堆栈跟踪帧
    # tb_list = traceback.extract_tb(exc_traceback)
    # print(tb_list)
