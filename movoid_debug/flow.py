#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : flow
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/14 16:15
# Description   : 
"""

from movoid_function import Function


class FlowFunction:
    def __init__(self, func, args, kwargs, flow, ignore_exception):
        self._func = Function(func, args, kwargs)
        self._flow = flow
        self._ignore_exception = ignore_exception
        self._init = True
        self._exception = None

    def __call__(self):
        while True:
            try:
                self.ask_call()
                break
            except:
                break

    def ask_call(self):
        if self._init:
            self._init = False
            return self._func()
        else:
            ask_str = input('请输入操作方案（1）重新执行（2）返回None跳过执行（3）输入返回值后跳过执行（4）重新输入参数后执行（其他）认可失败，退出：')
            if ask_str == '1':
                return self._func()
            elif ask_str == '2':
                return None
            elif ask_str == '3':
                ask_return = input('请输入返回值：')
                return eval(ask_return)
            elif ask_str == '4':
                ask_args = input('请输入参数值：')
                return eval(f'self._func({ask_args})')
            else:
                raise self._exception


class Flow:
    def __init__(self):
        self._function_list = []
