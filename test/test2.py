#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/3
Description:    
"""
import traceback

from movoid_debug.flow.flow import debug, debug_exclude, teardown


@debug
def test1():
    test2()
    test3()
    test2()


@debug
def test2(a=8):
    temp = test3(a=a)
    if temp < 10:
        raise Exception(temp)
    return temp


@debug
def test3(*, a=12):
    return a


@debug
def test4():
    test3()
    re2 = test2()
    raise Exception(re2)


@debug
def test5():
    for i in range(100):
        test4()
    test6()


do_value = True


@debug
@teardown
def test6_teardown(args, kwargs, re_value, error, trace_back):
    global do_value
    do_value = 100
    print('teardown', do_value)
    if error:
        print('final error', error)
        return error
    else:
        print('final return', re_value)
        return re_value


@debug(teardown_function=test6_teardown)
def test6(a=1, b=2):
    global do_value
    do_value = a + b
    raise Exception(123321)


@debug_exclude()
class Test:
    __a = 1
    __b = 2

    @debug
    def test1(self):
        self.__a = 1
        if self.__a == 1:
            raise Exception
        self.__b = 2
        if self.__b == 1:
            raise ValueError


# test5()
# test6()
# test = Test()
# test.test1()
# test1()
print('test6', test6())
print(do_value)
