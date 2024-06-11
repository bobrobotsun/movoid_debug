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

from movoid_function import Function, wraps, analyse_args_value_from_function, wraps_ori

from ..simple_ui import MainApp, MainWindow


class Flow:
    def __init__(self):
        self.main = MainFunction(self)
        self.current_function = self.main
        self.test = False
        self.raise_error = 0
        self.debug_type = 0
        self.debug_flag = 0
        self.init_debug_param()
        self.app = None
        self.continue_error_list = []

    def init_debug_param(self):
        for i in sys.argv:
            if i.startswith('__debug='):
                if i[8:] in ('1', 'debug'):
                    self.debug_type = 1
                else:
                    self.debug_type = 0
            elif i.startswith('__debug_flag='):
                if i[13:] in ('0', 'debug'):
                    self.debug_flag = 0
                elif i[13:] in ('2',):
                    self.debug_flag = 2
                else:
                    self.debug_flag = 1

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

    def when_error(self, *debug_flag, err=None, traceback_str=None):
        """
        这是供FlowFunction反调的函数，保证当前的处理模式是预选模式
        :param debug_flag: 这是个传入的参数，就是把自己的参数传进去
        :param err: 把故障传上来
        :param traceback_str: 把traceback信息传上来
        :return: 如果return 1 则是需要continue。如果return 2 则是需要 raise Error
        """
        self.test = True
        flag = self.analyse_target_debug_flag(*debug_flag)
        if flag == 0:
            re_value = self.when_error_debug()
        else:
            re_value = flag
            if flag == 2:
                self.continue_error_list.append([err, traceback_str])
        self.test = False
        return re_value

    def when_error_debug(self):
        """
        调出一个debug窗口来进行debug，编辑请前往main_window.py进行
        """
        if self.app is None:
            self.app = MainApp()
        self.app.main = MainWindow(self)
        self.app.exec()
        return 2 if self.raise_error == 0 else 1

    def analyse_target_debug_flag(self, default_flag=None, *debug_flag):
        """
        解析当前的函数对应的debug flag是多少
        优先看是否设置，没有设置就按照debug_type==0时的设置，如果也没有设置，那就继承flow的设置
        当debug_type为0时，flag 0会被强制转换为1
        :param default_flag: 保证在无设置时，可以继承flow的设置
        :param debug_flag: 其他debug_type时的设置
        :return: 返回具体的flag
        """
        debug_flag = [default_flag, *debug_flag]
        ind = self.debug_type
        tar_ind_flag = debug_flag[ind] if len(debug_flag) > ind else None
        tar_flag = debug_flag[0] if tar_ind_flag is None else tar_ind_flag
        flag = self.debug_flag if tar_flag is None else tar_flag
        flag = max(0, min(2, flag))
        if self.debug_type == 0:
            flag = max(1, flag)
        return flag

    def release_all_pass_error(self, raise_it=True):
        """
        如果之前曾经continue掉一部分error，那么可以通过调用这个函数，来将所有的error释放出来。
        :param raise_it: 是否把这些Error统一在一起raise 一个Error出来
        """
        if raise_it and self.continue_error_list:
            temp = self.continue_error_list
            self.continue_error_list = []
            raise DebugError(*temp)


class BasicFunction:
    func_type = '--'

    def __init__(self):
        self.flow = None
        self.parent = None
        self.son = []
        self.error = None
        self.traceback = ''
        self.error_mode = {}
        self.end = False
        self.has_return = False
        self.re_value = None

    def result(self, simple=False, tostring=False):
        if self.has_return:
            re_value = str(self.re_value) if tostring else self.re_value
        elif self.traceback:
            if simple:
                re_value = f'{type(self.error).__name__}:{self.error}' if tostring else self.error
            else:
                re_value = self.traceback
        else:
            re_value = 'not done yet'
        return re_value

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

    def __init__(self, func, flow, include=None, exclude=None, teardown_function=None):
        """

        """
        super().__init__()
        self.func = func
        self.teardown_function = Function() if teardown_function is None else FlowFunction(Function(teardown_function), flow, include=include, exclude=exclude, teardown_function=None)
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
        self.kwarg_value = {}
        self.flow = flow
        self.parent = flow.current_function
        self.raise_error = False
        self.debug_mode = {
            0: True,
            1: True
        }

    def __call__(self, *args, **kwargs):
        if self.flow.test:
            test = TestFunction(self.func, self.flow, self)
            test(*args, **kwargs)
        else:
            debug_default = kwargs.pop('__debug_default', None)
            debug_debug = kwargs.pop('__debug_debug', None)
            try:
                self.args = args
                self.kwargs = kwargs
                self.kwarg_value = analyse_args_value_from_function(self.func, *args, **kwargs)
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
                error_flag = self.flow.when_error(debug_default, debug_debug, err=self.error, traceback_str=self.traceback)
                if error_flag == 1:
                    self.flow.raise_error -= 1
                    raise err
            except Exception as err:
                raise err
            else:
                self.has_return = True
                self.re_value = re_value
                return self.re_value
            finally:
                self.teardown_function(args=self.args, kwargs=self.kwargs, re_value=self.re_value, error=self.error, traceback_str=self.traceback)
                self.end = True
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

    def __init__(self, func, flow, ori):
        super().__init__()
        self.func = func
        self.flow = flow
        self.ori = ori
        self.parent = self.flow.current_function

    def __call__(self, *args, **kwargs):
        if self.end:
            self.ori(*args, **kwargs)
        else:
            try:
                self.args = args
                self.kwargs = kwargs
                self.kwarg_value = analyse_args_value_from_function(self.func, *args, **kwargs)
                self.flow.set_current_function(self)
                re_value = self.func(*args, **kwargs)
            except TestError as err:
                if isinstance(self.parent, TestFunction):
                    raise err
            except Exception as err:
                self.error = err
                self.traceback = traceback.format_exc()
                if isinstance(self.parent, TestFunction):
                    raise TestError
            else:
                self.has_return = True
                self.re_value = re_value
                return self.re_value
            finally:
                self.end = True
                self.flow.current_function_end()

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


def debug_function(debug_default=None, debug_debug=None):
    if callable(debug_default):
        return debug_function()(debug_default)

    def dec(func):
        if getattr(func, '__debug', False):
            return func
        else:
            @wraps(func)
            def wrapper(*args, __debug_default=debug_default, __debug_debug=debug_debug, **kwargs):
                temp = FlowFunction(func, FLOW)
                re_value = temp(*args, __debug_default=debug_default, __debug_debug=debug_debug, **kwargs)
                return re_value

            setattr(wrapper, '__debug', True)
            return wrapper

    return dec


def debug_class_include(name_list):
    """
    作为装饰器使用，传入一个列表，列表内所有函数的名称均会被增加debug
    """

    def dec(cls):
        for name in name_list:
            if hasattr(cls, name):
                func = getattr(cls, name)
                if callable(func):
                    setattr(cls, name, debug_function(func))
        return cls

    return dec


def debug_class_exclude(name_list=None):
    """
    作为装饰器使用，传入一个列表，除了__开头和列表里的名称，所有的函数均会被增加debug
    不输入的情况下，会包含所有的函数
    """

    name_list = [] if name_list is None else list(name_list)

    def dec(cls):
        for name in dir(cls):
            if not name.startswith('__') and name not in name_list:
                func = getattr(cls, name)
                if callable(func):
                    setattr(cls, name, debug_function(func))
        return cls

    return dec


class DebugError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        re_str = ''
        for err, trace in self.args:
            re_str += f'{type(err).__name__}\n'
        re_str.strip('\n')
        return re_str

    def traceback(self):
        re_str = ''
        for err, trace in self.args:
            re_str += f'{trace}\n'
        re_str.strip('\n')
        return re_str


def teardown(func):
    """
    这个函数可以规范teardown函数，保证无论怎么写，都不会因为参数的传递而报错
    """

    @wraps_ori(func)
    def wrapper(args=None, kwargs=None, re_value=None, error=None, traceback_str=None):
        pass

    return wrapper
