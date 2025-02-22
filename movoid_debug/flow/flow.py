#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : flow
# Author        : Sun YiFan-Movoid
# Time          : 2024/4/14 16:15
# Description   : 
"""
import inspect
import sys
import traceback

from movoid_config import Config
from movoid_function import wraps, analyse_args_value_from_function, wraps_ori, adapt_call

from enum import Enum

TYPE_NO_UI = 0  # 强制不使用UI相关的内容
TYPE_UI = 1  # 可以使用UI进行过程排查

FLAG_UI = 0  # 当报错时，弹到UI上进行报错
FLAG_RAISE = 1  # 当报错时，将error raise出去
FLAG_PASS = 2  # 当报错时，将error储存起来，在适当时机再抛出


class Flow:
    def __init__(self):
        self.main = MainFunction(self)
        self.current_function = self.main
        self.error_function = None
        self.test = False
        self._raise_error = 0
        self.raise_until_exit = False  # 这个参数不要开启，一旦修改为True，那么flow将尝试一直raise Error直到软件结束为止
        self.config = Config({
            'debug': {
                "type": "int",
                "default": TYPE_NO_UI,
                "full": "debug",
                "key": "debug",
            },
            'flag': {
                "type": "int",
                "default": FLAG_UI,
                "key": "debug_flag",
            },
        }, 'movoid_debug.ini', False)
        self.debug_type = self.config.debug
        self.debug_flag = self.config.flag
        self.app = None
        self.continue_error_list = []

    @property
    def raise_error(self):
        return self._raise_error

    @raise_error.setter
    def raise_error(self, value):
        if value < 0:
            self._raise_error = 0
        self._raise_error = value

    def set_current_function(self, func):
        self.current_function.add_son(func)
        self.current_function = func

    def print(self, *args, sep=' ', end='\n'):
        """
        打印内容
        """
        text_list = [str(_) for _ in args]
        sep = str(sep)
        end = str(end)
        print_text = sep.join(text_list) + end
        self.current_function.add_son(print_text, '')

    def current_function_end(self):
        """
        包内的函数，如果某个函数执行完毕后，需要调用这个函数，来告知flow退出当前函数
        """
        if self.current_function is None:
            raise Exception('已经退出了所有的结算函数，并且额外执行了一次current_function_end')
        else:
            self.current_function = self.current_function.parent

    def when_error(self, *debug_flag, err=None, trace_back=None):
        """
        这是供FlowFunction反调的函数，保证当前的处理模式是预选模式
        :param debug_flag: 这是个传入的参数，就是把自己的参数传进去
        :param err: 把故障传上来
        :param trace_back: 把traceback信息传上来
        :return: 如果return 2 则是需要continue。如果return 1 则是需要 raise Error
        """
        self.test = True
        self.error_function = self.current_function
        flag = self.analyse_target_debug_flag(*debug_flag)
        if flag == FLAG_UI:  # 如果需要调用UI，那么要根据UI的结果决定最后的flag结论
            self.get_error_step()
            re_value = self.when_error_window()
        else:  # 非UI情况下，不需要修改flag逻辑
            re_value = flag
            if flag == FLAG_PASS:
                self.continue_error_list.append([err, trace_back])
        self.error_function = None
        self.test = False
        return re_value

    def when_test_error(self, *debug_flag, err=None, trace_back=None):
        """
        这是供TestFunction反调的函数，保证当前的处理模式是预选模式
        :param debug_flag: 这是个传入的参数，就是把自己的参数传进去
        :param err: 把故障传上来
        :param trace_back: 把traceback信息传上来
        :return: 如果return 2 则是需要continue。如果return 1 则是需要 raise Error
        """
        flag = self.analyse_target_debug_flag(*debug_flag)
        flag = max(FLAG_RAISE, flag)  # 在test function的时候，不可以重复调用UI
        re_value = flag
        if flag == FLAG_PASS:
            self.continue_error_list.append([err, trace_back])
        return re_value

    def when_error_window(self):
        """
        调出一个debug窗口来进行debug，编辑请前往main_window.py进行
        """
        from ..simple_ui import MainApp, MainWindow
        if self.app is None:
            self.app = MainApp()
        self.app.main = MainWindow(self)
        self.app.exec()
        if self.raise_until_exit:
            return 1
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
        if self.debug_type == 0:  # 如果是标准运行逻辑，那么不可以调用UI
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

    def get_error_step(self):
        temp_traceback = sys.exc_info()[2]
        while temp_traceback.tb_next is not None:
            temp_traceback = temp_traceback.tb_next
        # temp_traceback.with_traceback()
        temp_frame = temp_traceback.tb_frame
        temp_code = temp_frame.f_code
        self.final_frame = temp_frame
        self.final_code = temp_code
        self.final_lines, self.final_first_lineno = inspect.getsourcelines(temp_code)

        # traceback.print_exc()
        # temp_frame = inspect.currentframe()
        # last_file = pathlib.Path(temp_frame.f_code.co_filename)
        # temp_frame = temp_frame.f_back
        # while temp_frame is not None:
        #     temp_code = temp_frame.f_code
        #     print(temp_frame.f_trace_lines, temp_frame.f_trace_opcodes, temp_frame.f_trace, temp_frame, temp_code)
        #     # print('line table', temp_code.co_linetable)
        #     file_path_text = temp_frame.f_code.co_filename
        #     file_path = pathlib.Path(file_path_text)
        #     with file_path.open(mode='r', encoding='utf8') as f:
        #         file_lines = f.readlines()
        #     lineno = temp_code.co_firstlineno
        #     print(file_lines[lineno - 2:lineno + 3])
        #     with last_file.open(mode='r', encoding='utf8') as f:
        #         last_file_lines = f.readlines()
        #     lineno = temp_frame.f_lineno
        #     print(last_file_lines[lineno - 2:lineno + 3])
        #     last_file = pathlib.Path(temp_frame.f_code.co_filename)
        #     temp_frame = temp_frame.f_back


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
        """
        获取当前函数的运行状态，分为已有返回值、处于error状态、正在运行中（正在处理的函数是本函数的子步骤）
        :param simple: error信息是否需要简化
        :param tostring: 如果是return的话，返回字符串还是实际值
        :return: 函数的运行状态
        """
        if self.has_return:
            re_value = f'return({type(self.re_value).__name__}): {self.re_value}' if tostring else self.re_value
        elif self.traceback:
            if simple:
                re_value = f'{type(self.error).__name__}:{self.error}' if tostring else self.error
            else:
                re_value = self.traceback
        else:
            re_value = 'running'
        return re_value

    def add_son(self, son, son_type='function'):
        """
        当函数没有运行完毕时，如果执行了其他函数，那么需要把这些函数归类为自己的子函数
        son：目标元素
        son_type：目标类型，默认function，也可以是log（纯文字日志）
        """
        self.son.append([son, son_type])


class MainFunction(BasicFunction):
    def __init__(self, flow):
        super().__init__()
        self.flow = flow
        self.parent = flow


class FlowFunction(BasicFunction):
    func_type = 'function'

    def __init__(self, func, flow: Flow, include=None, exclude=None, teardown_function=None, debug_default: int = None, debug_debug: int = None):
        """

        """
        super().__init__()
        self.func = func
        self.teardown_function = (lambda function, args, kwargs, re_value, error, trace_back, has_return: re_value) if teardown_function is None else debug(debug_default, debug_debug, include, exclude, teardown_function=None)(teardown_function)
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
        self.debug_default = debug_default
        self.debug_debug = debug_debug

    def __call__(self, *args, **kwargs):
        debug_default = kwargs.pop('__debug_default', None)
        debug_debug = kwargs.pop('__debug_debug', None)
        debug_default = self.debug_default if debug_default is None else debug_default
        debug_debug = self.debug_debug if debug_debug is None else debug_debug
        if self.flow.test:
            test = TestFunction(func=self.func, flow=self.flow, ori=self, debug_default=debug_default, debug_debug=debug_debug)
            return test(*args, **kwargs, __debug_default=debug_default, __debug_debug=debug_debug)
        else:
            try:
                self.args = args
                self.kwargs = kwargs
                self.kwarg_value = analyse_args_value_from_function(self.func, *args, **kwargs)
                self.flow.set_current_function(self)
                re_value = self.func(*self.args, **self.kwargs)
            except self.exclude_error as err:
                raise err
            except self.include_error as err:
                if self.flow.raise_until_exit:
                    raise err
                if self.flow.raise_error > 0:
                    self.flow.raise_error -= 1
                    raise err
                self.error = err
                self.traceback = traceback.format_exc()
                error_flag = self.flow.when_error(debug_default, debug_debug, err=self.error, trace_back=self.traceback)
                if error_flag == FLAG_RAISE:
                    self.flow.raise_error -= 1
                    raise err
                elif error_flag == FLAG_PASS:
                    self.has_return = True
            except Exception as err:
                raise err
            else:
                self.has_return = True
                self.re_value = re_value
            finally:
                teardown_args = dict(function=self.func, args=self.args, kwargs=self.kwargs, re_value=self.re_value, error=self.error, trace_back=self.traceback, has_return=self.has_return)
                self.re_value = adapt_call(self.teardown_function, [], teardown_args, self.func, self.args, self.kwargs)
                self.end = True
                self.flow.current_function_end()
                if self.has_return:
                    return self.re_value


class TestFunction(BasicFunction):
    func_type = 'test'

    def __init__(self, func, flow, ori, debug_default=None, debug_debug=None):
        super().__init__()
        self.func = func
        self.flow = flow
        self.ori = ori
        self.debug_default = debug_default
        self.debug_debug = debug_debug
        self.parent = self.flow.current_function

    def __call__(self, *args, **kwargs):
        debug_default = kwargs.pop('__debug_default', None)
        debug_debug = kwargs.pop('__debug_debug', None)
        debug_default = self.debug_default if debug_default is None else debug_default
        debug_debug = self.debug_debug if debug_debug is None else debug_debug
        if self.end:
            self.ori(*args, __debug_default=debug_default, __debug_debug=debug_debug, **kwargs)
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
            except self.ori.exclude_error as err:
                raise err
            except self.ori.include_error as err:
                if self.flow.raise_until_exit:
                    raise err
                self.error = err
                self.traceback = traceback.format_exc()
                error_flag = self.flow.when_test_error(debug_default, debug_debug, err=self.error, trace_back=self.traceback)
                if error_flag == FLAG_RAISE:
                    raise err
                elif error_flag == FLAG_PASS:
                    self.has_return = True
            except Exception as err:
                self.error = err
                self.traceback = traceback.format_exc()
                if isinstance(self.parent, TestFunction):
                    raise TestError
            else:
                self.has_return = True
                self.re_value = re_value
                if self.ori == self.flow.error_function:
                    self.ori.re_value = self.re_value
            finally:
                teardown_args = dict(function=self.func, args=self.args, kwargs=self.kwargs, re_value=self.re_value, error=self.error, trace_back=self.traceback, has_return=self.has_return)
                self.re_value = adapt_call(self.ori.teardown_function, [], teardown_args, self.func, self.args, self.kwargs)
                self.end = True
                self.flow.current_function_end()
                if self.has_return:
                    return self.re_value


class TestError(Exception):
    pass


FLOW = Flow()


def debug(debug_default: int = None, debug_debug: int = None, include_error=None, exclude_error=None, teardown_function=None, force=False):
    """
    作为装饰器使用，使该函数会被debug覆盖
    :param debug_default: 默认情况下的处理方法，0→1
    :param debug_debug: debug状态下的处理方法，0
    :param include_error: 仅抓取这些bug
    :param exclude_error: 不抓取这些bug
    :param teardown_function: 统一的teardown函数，需要传入参数、返回值、错误信息
    :param force: 强制将debug 逻辑转换为当前逻辑
    """
    if callable(debug_default):
        return debug()(debug_default)

    def dec(func):
        if getattr(func, '__debug', False):
            if force:
                func = getattr(func, '__function')
            else:
                return func

        @wraps(func)
        def wrapper(*args, __debug_default=debug_default, __debug_debug=debug_debug, **kwargs):
            temp = FlowFunction(func, FLOW, include=include_error, exclude=exclude_error, teardown_function=teardown_function, debug_default=__debug_default, debug_debug=__debug_debug)
            re_value = temp(*args, **kwargs)
            return re_value

        setattr(wrapper, '__debug', True)
        setattr(wrapper, '__function', func)
        return wrapper

    return dec


def debug_include(*name_list, debug_default=None, debug_debug=None, include_error=None, exclude_error=None, teardown_function=None, force=False):
    """
    作为装饰器使用，传入的若干名称，都会搜索相应的函数，让后对这些名字的函数进行debug
    :param name_list:
    :param debug_default: 默认情况下的处理方法，0→1
    :param debug_debug: debug状态下的处理方法，0
    :param include_error: 仅抓取这些bug
    :param exclude_error: 不抓取这些bug
    :param teardown_function: 统一的teardown函数，需要传入参数、返回值、错误信息
    :param force: 满足规则的强制转换为当前的debug逻辑
    """

    def dec(cls):
        for name in name_list:
            if hasattr(cls, name):
                func = getattr(cls, name)
                if callable(func):
                    setattr(cls, name, debug(debug_default=debug_default, debug_debug=debug_debug, include_error=include_error, exclude_error=exclude_error, teardown_function=teardown_function, force=force)(func))
        return cls

    return dec


def debug_include_regex(*name_list, debug_default=None, debug_debug=None, include_error=None, exclude_error=None, teardown_function=None, force=False):
    """
    作为装饰器使用，传入的若干名称，都会搜索相应的函数，让后对这些名字的函数进行debug
    :param name_list:
    :param debug_default: 默认情况下的处理方法，0→1
    :param debug_debug: debug状态下的处理方法，0
    :param include_error: 仅抓取这些bug
    :param exclude_error: 不抓取这些bug
    :param teardown_function: 统一的teardown函数，需要传入参数、返回值、错误信息
    :param force: 满足规则的强制转换为当前的debug逻辑
    """

    def dec(cls):
        for name in name_list:
            if hasattr(cls, name):
                func = getattr(cls, name)
                if callable(func):
                    setattr(cls, name, debug(debug_default=debug_default, debug_debug=debug_debug, include_error=include_error, exclude_error=exclude_error, teardown_function=teardown_function, force=force)(func))
        return cls

    return dec


def debug_exclude(*name_list, debug_default=None, debug_debug=None, include_error=None, exclude_error=None, teardown_function=None, force=False):
    """
    作为装饰器使用，除了__开头和列表里的名称，所有的函数均会被增加debug
    不输入的情况下，会包含所有的函数
    :param name_list:
    :param debug_default: 默认情况下的处理方法，0→1
    :param debug_debug: debug状态下的处理方法，0
    :param include_error: 仅抓取这些bug
    :param exclude_error: 不抓取这些bug
    :param teardown_function: 统一的teardown函数，需要传入参数、返回值、错误信息
    :param force: 满足规则的强制转换为当前的debug逻辑
    """

    def dec(cls):
        for name in dir(cls):
            if not name.startswith('__') and name not in name_list:
                func = getattr(cls, name)
                if callable(func):
                    setattr(cls, name, debug(debug_default=debug_default, debug_debug=debug_debug, include_error=include_error, exclude_error=exclude_error, teardown_function=teardown_function, force=force)(func))
        return cls

    return dec


class DebugError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        re_str = ''
        for err, trace in self.args:
            re_str += f'{type(err).__name__}:{err}\n'
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
    想要规范teardown函数，请务必保证该函数拥有一个返回值，以防止运行过程中，没有返回值导致的错误
    """

    @wraps_ori(func)
    def wrapper(function=None, args=None, kwargs=None, re_value=None, error=None, trace_back=None, has_return=None) -> object:  # noqa
        pass

    return wrapper
