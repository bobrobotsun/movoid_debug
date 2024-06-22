#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/21
Description:    
"""


class Code:
    FUNCTION = 'function'
    CLASS_FUNCTION = 'class_function'
    GETTER = 'getter'
    SETTER

    def __init__(self, code):
        self.code = code
        self.style = 'function'

    @property
    def id(self):
        return id(self.code)


class CodeHistory:
    def __init__(self):
        self.code_dict = {}
