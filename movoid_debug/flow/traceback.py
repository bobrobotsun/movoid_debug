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
    temp_code = {}

    def __init__(self):
        self._index: int = -1
        self.traceback_list: List[TracebackType] = []
        self.self_frame: FrameType = inspect.currentframe()
        self.init()

    def init(self):
        temp_traceback = sys.exc_info()[2]
        self.traceback_list.clear()
        if temp_traceback is not None:
            while True:
                if temp_traceback is None:
                    break
                else:
                    self.traceback_list.append(temp_traceback)
                    temp_traceback = temp_traceback.tb_next
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
        code_id = id(self.code)
        print('source\n', inspect.getsource(self.code))
        print('source_file', inspect.getsourcefile(self.code))
        return (self.temp_code[code_id], 0) if code_id in self.temp_code else inspect.getsourcelines(self.code)

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
            loop = 0 if len(self.traceback_list) == 0 else value // len(self.traceback_list)
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
        print(self.traceback)
        print(self.frame)
        print(self.code)
        print(self.source_lines)

    def test2(self):
        # print(self.self_frame.f_builtins)
        # print(self.self_frame.f_globals)
        func_text = """def wrapper(self, do):
    print(do+123)
"""
        exec_text = f"""
{func_text}
Test.wrapper=wrapper
        """
        # self.index = 1
        exec(exec_text, self.frame.f_globals, self.frame.f_locals)
        print(self.frame.f_globals.get('wrapper'))
        print(self.frame.f_locals.get('wrapper'))

        # print('Test.wrapper', Test.wrapper.__code__)
        # print('Test.wrapper', id(Test.wrapper.__code__))
        # self.temp_code[id(Test.wrapper.__code__)] = func_text.strip('\n').split('\n')
        # print(self.temp_code)
        # Test.wrapper(888)
        # print(self.self_frame.f_globals.get('wrapper'))
        # for i in self:
        #     print(i, self.frame.f_globals.get('wrapper', 'no wrap'))
