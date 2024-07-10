#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : flow_thread
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/14 0:47
# Description   : 
"""
from PySide6.QtCore import QThread, Signal


class FlowThread(QThread):
    signal_test = Signal(bool)

    def __init__(self, func, parent=None, args=None, kwargs=None):
        super().__init__(parent)
        self.func = func
        self.args = [] if args is None else args
        self.kwargs = {} if kwargs is None else kwargs

    def run(self):
        self.signal_test.emit(True)
        try:
            self.func(*self.args, **self.kwargs)
        except:
            pass
        finally:
            self.signal_test.emit(False)
