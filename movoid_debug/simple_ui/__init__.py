#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:45
# Description   : 
"""
from typing import List

import movoid_function
from PySide6.QtWidgets import QApplication, QWidget
from movoid_function import STACK

from .main_window import MainWindow
from .frame_main import FrameMainWindow


class MainApp:
    def __init__(self, flow):
        self.app = QApplication()
        self.flow = flow
        self.main = None
        self.windows: List[QWidget] = []

    def when_error(self):
        self.main = MainWindow(self.flow, self)
        self.main.signal_close.connect(self.action_close_main_window)
        self.windows: List[QWidget] = []

    def when_error_end(self):
        self.app.exec()

    def quit(self):
        return self.app.quit()

    def action_close_main_window(self, sender):
        for window in self.windows[:]:
            window.close()

    def add_frame_window(self):
        frame = FrameMainWindow(self.flow, 0)
        self.windows.append(frame)
        frame.signal_close.connect(self.action_close_frame_window)

    def action_close_frame_window(self, sender):
        if sender in self.windows:
            self.windows.remove(sender)


STACK.this_file_lineno_should_ignore(None, ignore_level=movoid_function.stack.UI)
