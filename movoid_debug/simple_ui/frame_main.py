#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : frame_main
# Author        : Sun YiFan-Movoid
# Time          : 2024/7/2 0:18
# Description   : 
"""
from PySide6.QtWidgets import QMainWindow


class FrameMainWindow(QMainWindow):

    def __init__(self, flow):
        super().__init__()
        self.flow = flow
        self.testing = False
        self.init_ui()
        self.show()
        self.refresh_ui()

    def init_ui(self):
        pass

    def refresh_ui(self):
        pass
