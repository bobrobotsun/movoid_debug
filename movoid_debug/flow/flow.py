#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : flow
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/14 16:15
# Description   : 
"""
import sys
import traceback

from movoid_function import Function, wraps

from ..simple_ui import MainApp


class Flow:
    def __init__(self):
        self.main = MainFunction(self)
        self.current_function = self.main
        self.test = False
        self.raise_error = 0
        self.error_type = 0
        self.check_error_type()

    def check_error_type(self):
        for i in sys.argv:
            if i.startswith('_debug='):
                temp = i[7:]
                if temp == '1':
                    self.error_type = 1

    @property
    def text(self):
        return self.main.total_text()

    def set_current_function(self, func):
        self.current_function.add_son(func)
        self.current_function = func

    def current_function_end(self):
        if self.current_function is None:
            raise Exception('已经退出了所有的结算函数，并且额外执行了一次current_function_end')
        else:
            self.current_function = self.current_function.parent

    def when_error(self):
        self.test = True
        if self.error_type == -1:
            self.when_error_cmd()
        elif self.error_type == 1:
            self.when_error_debug()
        self.test = False

    def when_error_debug(self):
        debug_app = MainApp(self)
        debug_app.exec()

    def when_error_cmd(self):
        print('错误发生：')
        while True:
            print('以下是当前流程')
            print(self.text)
            input_str = input('请问如何处理？1、重新测试；2、弹出错误到上一级；3、弹出错误直至退出；其他、以当前的返回值返回：')
            if input_str == '1':
                self.current_function(*self.args, **self.kwargs)
            elif input_str == '2':
                self.raise_error = 1
                break
            elif input_str == '3':
                self.raise_error = -1
                break
            else:
                self.raise_error = False
                break


class BasicFunction:
    func_type = '--'

    def __init__(self):
        self.flow = None
        self.parent = None
        self.son = []
        self.error = None
        self.traceback = ''
        self.error_mode = {}

    def add_son(self, son, son_type='function'):
        """
        当函数没有运行完毕时，如果执行了其他函数，那么需要把这些函数归类为自己的子函数
        son：目标元素
        son_type：目标类型，默认function，也可以是log（纯文字日志）
        """
        self.son.append([son, son_type])

    def self_text(self, indent=0):
        return '\t' * indent + '--'

    def total_text(self, indent=0):
        re_str = self.self_text(indent)
        for son, son_type in self.son:
            if son_type == 'function':
                re_str += '\n' + son.total_text(indent=indent + 1)
            elif son_type == 'test':
                re_str += '\n' + self.son_test_text(son, indent + 1)
            else:
                re_str += '\n' + '\t' * (indent + 1) + str(son)
        return re_str

    def join_func_args_kwargs(self, func, args, kwargs):
        func_str = f'{func.__module__}:{func.__name__}'
        args_str = f'{args}'
        kwargs_str = f'{kwargs}'
        arg_total_str = f'{args_str}{kwargs_str}'
        return f'{func_str}({arg_total_str})'

    def son_test_text(self, son, indent=0):
        bool_str = f'测试{"成功" if son[0] else "失败"}'
        func_str = self.join_func_args_kwargs(*son[1:4])
        if son[0]:
            tail_str = f'->{son[4]}'
        else:
            tail_str = '\n' + '\t' * (indent + 1) + son[5]
        return '\t' * indent + f'{bool_str}{func_str}{tail_str}'


class MainFunction(BasicFunction):
    def __init__(self, flow):
        super().__init__()
        self.flow = flow
        self.parent = flow

    def self_text(self, indent=0):
        return '\t' * indent + 'main'


class FlowFunction(BasicFunction):
    func_type = 'function'

    def __init__(self, func, flow, include=None, exclude=None, error_function=None, error_args=None, error_kwargs=None):
        """

        """
        super().__init__()
        self.func = func
        self.error_func = Function(error_function, error_args, error_kwargs)
        if include is None:
            self.include_error = Exception
            if exclude is None:
                self.exclude_error = ()
            else:
                self.exclude_error = exclude
        else:
            self.exclude_error = ()
            self.include_error = include
        self.args = []
        self.kwargs = {}
        self.has_return = False
        self.re_value = None
        self.flow = flow
        self.parent = flow.current_function
        self.raise_error = False
        self.end = False
        self.debug_mode = {
            0: True,
            1: True
        }

    def __call__(self, *args, **kwargs):
        if self.flow.test:
            test = TestFunction(self.func, self.flow)
            self.son.append([test, 'function'])
            test(*args, **kwargs)
        else:
            try:
                self.args = args
                self.kwargs = kwargs
                self.flow.set_current_function(self)
                re_value = self.func(*self.args, **self.kwargs)
            except self.exclude_error as err:
                raise err
            except self.include_error as err:
                if self.flow.raise_error != 0:
                    self.flow.raise_error -= 1
                    raise err
                self.error = err
                self.traceback = traceback.format_exc()
                if self.debug_mode.get(self.flow.error_type, False):
                    if self.flow.error_type in (-1, 1):
                        self.flow.when_error()
                        if self.flow.raise_error != 0:
                            self.flow.raise_error -= 1
                            raise err
                        else:
                            self.has_return = True
                            return self.re_value
                    else:
                        self.error_func()
                else:
                    raise err
            except Exception as err:
                raise err
            else:
                self.has_return = True
                self.re_value = re_value
                return self.re_value
            finally:
                self.flow.current_function_end()

    def self_text(self, indent=0):
        indent_str = '\t' * indent
        func_str = self.join_func_args_kwargs(self.func, self.args, self.kwargs)
        if self.end:
            if self.has_return:
                return_str = f' -> {self.re_value}'
            else:
                return_str = self.traceback
        else:
            return_str = '...'
        return f'{indent_str}{func_str}{return_str}'


class TestFunction(BasicFunction):
    func_type = 'test'

    def __init__(self, func, flow):
        super().__init__()
        self.func = func
        self.flow = flow
        self.parent = self.flow.current_function
        self.has_return = False
        self.re_value = None
        self.end = False

    def __call__(self, *args, **kwargs):
        try:
            self.args = args
            self.kwargs = kwargs
            re_value = self.func(*args, **kwargs)
        except TestError as err:
            if isinstance(self.parent, TestFunction):
                raise err
        except Exception as err:
            self.err = err
            self.traceback = traceback.format_exc()
            if isinstance(self.parent, TestFunction):
                raise TestError
        else:
            self.has_return = True
            self.re_value = re_value
            return self.re_value
        finally:
            self.end = True

    def self_text(self, indent=0):
        indent_str = '\t' * indent
        func_str = self.join_func_args_kwargs(self.func, self.args, self.kwargs)
        if self.end:
            if self.has_return:
                pass_str = '通过：'
                return_str = f' -> {self.re_value}'
            else:
                pass_str = '失败：'
                return_str = self.traceback
        else:
            pass_str = '进行中：'
            return_str = '...'
        return f'{indent_str}{pass_str}{func_str}{return_str}'


class TestError(Exception):
    pass


FLOW = Flow()
