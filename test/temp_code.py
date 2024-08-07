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
        raise Exception
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


def func_error(a=1):
    # var_a2 = '2'
    # var_b = a + var_a
    # raise Exception(a)
    b = func_error2()
    c = a + b
    print(c)


def func_error2():
    a = 1 + '1'
    return a


#
# for i in [func_test.__code__, Test.prop.fget.__code__, Test.prop.fset.__code__, Test.prop.fdel.__code__, Test.do1.__code__]:
#     code = Code(i,__frame__)
#     print(code.style, code._style_info)
tb = Traceback()
var_a = '1'
try:
    # b = 1 + var_a
    func_error(1)
    # test = Test()
    # test.prop
except:
    tb.init()
    print(tb.frame, tb.code)
    code = Code(tb.code, tb.frame)
    # print(code._style_info)
    # code = Code(tb.code, tb.frame)
    # print(tb.frame.f_globals.get('Test'))
    # a = tb.frame
    # b = tb.code
    # print(func_error.__code__)
    # print(tb.frame.f_globals.get('var_a'))
    # print(tb.frame.f_locals.get('var_a'))
    exec("print(222)", tb.frame.f_globals, tb.frame.f_locals)

try:
    func_error(1)
    test = Test()
    test.prop
except:
    tb.init()
    # print(tb.frame.f_globals.get('Test'))
    c = tb.frame
    d = tb.code
    code.replace_by_new_text("""def func_error2(b=1):
    print(b)
    """)
    print(func_error.__code__)
func_error(1)
