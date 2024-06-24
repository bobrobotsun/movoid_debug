#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/24
Description:    
"""

from movoid_debug.flow.code import Code
from movoid_debug.flow.traceback import Traceback


class Test:
    def __init__(self):
        self._prop = 0

    @property
    def prop(self):
        return self._prop

    @prop.setter
    def prop(self, value):
        self._prop = value

    @prop.deleter
    def prop(self):
        self._prop = 0

    def do1(self):
        raise Exception
        print('do1', self._prop)

    def do2(self, value='stop'):
        print('do2', self._prop, value)


def func_test(func_a):
    from test.test2 import test
    print('func_test', test.test1())


def func_error(a):
    raise Exception(a)


#
# for i in [func_test.__code__, Test.prop.fget.__code__, Test.prop.fset.__code__, Test.prop.fdel.__code__, Test.do1.__code__]:
#     code = Code(i,__frame__)
#     print(code.style, code._style_info)
tb = Traceback()
try:
    test = Test()
    test.do1()
except:
    tb.init()
    # print(tb.frame.f_globals.get('Test'))
    code = Code(tb.code, tb.frame)
    code.replace_by_new_text("""def temp_func(self, a):
    print(a)
    print('down')
""")
    test.do1(123)