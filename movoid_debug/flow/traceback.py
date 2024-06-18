#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : traceback
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/18 1:19
# Description   : 
"""
import inspect
import sys
from types import TracebackType, FrameType, CodeType
from typing import List, Tuple


class Traceback:
    def __init__(self):
        self._index: int = -1
        self.traceback_list: List[TracebackType] = []
        self.self_frame: FrameType = inspect.currentframe()
        self.init()

    def init(self):
        temp_traceback = sys.exc_info()[2]
        self.traceback_list = [temp_traceback]
        while True:
            temp_traceback = temp_traceback.tb_next
            if temp_traceback is None:
                break
            else:
                self.traceback_list.append(temp_traceback)
        self.index = -1

    @property
    def traceback(self) -> TracebackType:
        return self.traceback_list[self._index]

    @property
    def frame(self) -> FrameType:
        return self.traceback_list[self._index].tb_frame

    @property
    def code(self) -> CodeType:
        return self.traceback_list[self._index].tb_frame.f_code

    @property
    def tracebacks(self) -> List[TracebackType]:
        return self.traceback_list

    @property
    def frames(self) -> List[FrameType]:
        return [_.tb_frame for _ in self.traceback_list]

    @property
    def codes(self) -> List[CodeType]:
        return [_.tb_frame.f_code for _ in self.traceback_list]

    @property
    def source_lines(self) -> Tuple[List[str], int]:
        return inspect.getsourcelines(self.code)

    def temporary_environment(self, index=None):
        self.index = index

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        try:
            value = int(value)
        except ValueError:
            pass
        else:
            loop = value // len(self.traceback_list)
            self._index = value + (loop + 1 if loop < 0 else loop) * len(self.traceback_list)

    def __iter__(self):
        self._last_index = self._index
        self._index = -1
        return self

    def __next__(self):
        self._index += 1
        if self._index >= len(self.traceback_list):
            self.index = self._last_index
            raise StopIteration()
        return self._index

    def test(self):
        temp = None
        for i in self:
            print(i, self.frame.f_globals.get('Test'))
            temp = self.frame.f_globals.get('Test', temp)
        self.self_frame.f_globals.setdefault('Test', temp)
        # print(self.self_frame.f_builtins)
        # print(self.self_frame.f_globals)
        exec_text = """
print('asdf')
def wrapper(self, do):
    print(do)
Test.wrapper=wrapper
        """
        self.index = 1
        exec(exec_text, self.frame.f_globals, self.frame.f_locals)
        Test.wrapper(888)
        print(self.self_frame.f_globals.get('wrapper'))
        for i in self:
            print(i, self.frame.f_globals.get('wrapper', 'no wrap'))
