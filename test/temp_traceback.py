#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/17
Description:    
"""


class Test:
    diss = True

    def test_f1(self, b):
        print(1 + b)

    def f2(self, a=666):
        print(self, a)

    @property
    def like(self):
        return True

    @like.setter
    def like(self, value):
        print('nonono')

    @classmethod
    def test_class(cls, doit):
        print(cls, doit)


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


def getter_like(self):
    return False


def setter_like(self, value):
    print(value)


@staticmethod
def replace_f2(value=1):
    print('replace', value)


Test.f2 = replace_f2

test_1 = Test()
test_2 = Test()
Test.setter_like = setter_like
Test.like = Test.like.setter(setter_like)

print(Test.like.getter, Test.like.setter, Test.like.deleter)

# setattr(Test, 'like', test_class)
# Test.f2(333)
index = [0, 1]
test_1.like = True
test_1.f2('happy')
Test.f2('sad')
