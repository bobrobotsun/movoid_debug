#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : __init__.py
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:45
# Description   : 
"""
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


class MainApp:
    def __init__(self):
        self.app = QApplication()

    def exec(self):
        return self.app.exec()

    def quit(self):
        return self.app.quit()
