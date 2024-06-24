#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/21
Description:    
"""
import inspect
import pathlib
import re
from types import CodeType


class Code:
    FUNCTION = 'function'
    CLASS_FUNCTION = 'class_function'
    GETTER = 'getter'
    SETTER = 'setter'
    DELETER = 'deleter'

    def __init__(self, code: CodeType):
        self._code: CodeType = code
        self._style = self.FUNCTION
        self._change_list = []
        self.init()

    @property
    def id(self):
        return id(self._code)

    @property
    def code(self):
        return self._code

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        value = value.lowert()
        if value in (self.FUNCTION, self.CLASS_FUNCTION, self.GETTER, self.SETTER, self.DELETER):
            self._style = value
        else:
            self._style = self.FUNCTION

    def init(self):
        pass

    def analyse_ori_source_file(self):
        source_lines = inspect.getsourcelines(self._code)
        first_line = source_lines[0][0]
        if first_line.startswith(' ') or first_line.startswith('\t'):
            start_blank = ''
            for i in first_line:
                if i in (' ', '\t'):
                    start_blank += i
                else:
                    break
            ori_path = pathlib.Path(self._code.co_filename)
            with ori_path.open(mode='r') as f:
                file_lines = f.readlines()
            lineno = source_lines[1]
            for i in range(lineno - 1, -1, -1):
                line_text = file_lines[i]
                if len(line_text) > len(start_blank) and line_text.startswith(start_blank):
                    if line_text[len(start_blank):].startswith('class'):
                        self._style = self.
                    else:
                        self._style = self.FUNCTION
                        self._change_list = [self.id, self.code, inspect.getsource(self._code)]
                    break
            else:
                self._style = self.FUNCTION
                self._change_list = [self.id, self.code, inspect.getsource(self._code)]
        else:
            self._style = self.FUNCTION
            self._change_list = [self.id, self.code, inspect.getsource(self._code)]


class CodeHistory:
    def __init__(self):
        self.code_dict = {}
