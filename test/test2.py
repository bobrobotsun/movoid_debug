#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/3
Description:    
"""
import traceback

from movoid_debug.flow.flow import debug, debug_exclude


@debug
def test1():
    test2()
    test3()
    test2()


@debug
def test2():
    test3(a=11)


@debug
def test3(*, a=12):
    raise Exception


@debug
def test4():
    test3()
    test2()


@debug
def test5():
    for i in range(100):
        test4()
    test6()


@debug
def test6(a=1, b=2):
    raise Exception


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
test = Test()
# test.test1()
# test1()