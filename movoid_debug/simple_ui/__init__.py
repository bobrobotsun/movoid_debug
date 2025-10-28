#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:45
# Description   : 
"""
from typing import List

from PySide6.QtWidgets import QApplication, QWidget

from .main_window import MainWindow
from .frame_main import FrameMainWindow


class MainApp:
    def __init__(self, flow):
        self.app = QApplication()
        self.flow = flow
        self.main = None
        self.windows: List[QWidget] = []

    def init(self):
        self.main = MainWindow(self.flow, self)
        self.main.signal_close.connect(self.action_close_main_window)
        self.windows: List[QWidget] = []

    def exec(self):
        re_value = self.app.exec()
        return re_value

    def quit(self):
        return self.app.quit()

    def action_close_main_window(self, sender):
        for window in self.windows[:]:
            window.close()

    def add_frame_window(self):
        frame = FrameMainWindow(self.flow, 3)
        self.windows.append(frame)
        frame.signal_close.connect(self.action_close_frame_window)

    def action_close_frame_window(self, sender):
        if sender in self.windows:
            self.windows.remove(sender)
