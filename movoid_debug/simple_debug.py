#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : simple_debug
# Author        : Sun YiFan-Movoid
# Time          : 2024/5/20 1:52
# Description   : 
"""
import traceback
from movoid_function import wraps, Function


class ErrorFunction:
    def __init__(self, func, args, kwargs, error):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.error = error
        self.traceback = traceback.format_exc()


class SimpleDebug:
    def __init__(self):
        self._error_list = []

    def when_error(self, _continue=True, error_teardown=None, error_teardown_args=None, error_teardown_kwargs=None):
        if isinstance(_continue, bool):
            error_teardown_function = Function(error_teardown, error_teardown_args, error_teardown_kwargs)

            def dec(func):
                @wraps(func)
                def wrapping(*args, **kwargs):
                    try:
                        re_value = func(*args, **kwargs)
                    except Exception as err:
                        if _continue:
                            self._error_list.append(ErrorFunction(func, args, kwargs, err))
                            try:
                                error_teardown_function()
                            except:
                                print(f'fail to teardown:\n{traceback.format_exc()}')
                        else:
                            raise err
                    else:
                        return re_value

                return wrapping

            return dec
        else:
            return self.when_error()(_continue)

    def raise_all(self):
        if self._error_list:
            temp = self._error_list
            self._error_list = []
            raise DebugError(temp)


class DebugError(Exception):
    def __init__(self, error_list: list, *args):
        all_info = ''
        for error in error_list:
            all_info += f'{error.func.__name__}{error.args}{error.kwargs}:{error.error}\n{error.traceback}\n'
        super().__init__(all_info, *args)


DEBUG = SimpleDebug()
