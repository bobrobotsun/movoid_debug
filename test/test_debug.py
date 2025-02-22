#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : test_debug
# Author        : Sun YiFan-Movoid
# Time          : 2025/2/22 21:38
# Description   : 
"""

from movoid_debug import debug


@debug(2)
def func1():
    raise Exception()


class TestDebug:
    def test_debug_pass(self):
        func1()
