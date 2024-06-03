#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : main_window
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:48
# Description   : 
"""
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QTreeWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidgetItem


class MainWindow(QMainWindow):
    def __init__(self, flow):
        super().__init__()
        self.flow = flow
        self.init_ui()
        self.show()
        self.refresh_ui()

    def init_ui(self):
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_rect.width() * 0.2), int(screen_rect.height() * 0.2), int(screen_rect.width() * 0.6), int(screen_rect.height() * 0.6))
        main_table = QWidget(self)
        self.setCentralWidget(main_table)
        main_gird = QGridLayout(main_table)
        main_table.setLayout(main_gird)
        main_gird.setColumnStretch(0, 4)
        main_gird.setColumnStretch(1, 2)
        main_gird.setColumnStretch(2, 1)

        flow_tree = QTreeWidget(main_table)
        flow_tree.setObjectName('flow_tree')
        main_gird.addWidget(flow_tree, 0, 0, 2, 1)
        flow_tree.setHeaderLabels(['type', 'func', 'args', 'kwargs', 'status'])
        flow_tree.itemClicked.connect(self.refresh_current_text)

        print_text = QTextEdit(main_table)
        print_text.setObjectName('print_text')
        main_gird.addWidget(print_text, 0, 1)

        current_text = QTextEdit(main_table)
        current_text.setObjectName('current_text')
        main_gird.addWidget(current_text, 1, 1)

        run_widget = QWidget(main_table)
        end_widget = QWidget(main_table)
        main_gird.addWidget(run_widget, 0, 3)
        main_gird.addWidget(end_widget, 4, 0, 1, 3)
        run_grid = QVBoxLayout(run_widget)
        run_widget.setLayout(run_grid)
        end_grid = QHBoxLayout(end_widget)
        end_widget.setLayout(end_grid)

        run_test_button = QPushButton('测试', main_table)
        run_test_button.setObjectName('run_test_button')
        run_grid.addWidget(run_test_button)
        run_test_button.clicked.connect(self.run_test)
        run_grid.addStretch(1)

        run_continue_button = QPushButton('忽略错误并continue', main_table)
        run_continue_button.setObjectName('run_continue_button')
        run_grid.addWidget(run_continue_button)
        run_continue_button.clicked.connect(self.run_continue)
        run_grid.addStretch(1)

        run_raise_button = QPushButton('忽略错误并raise error', main_table)
        run_raise_button.setObjectName('run_raise_button')
        run_grid.addWidget(run_raise_button)
        run_raise_button.clicked.connect(self.run_raise)

        run_grid.addStretch(10)

    def refresh_ui(self):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')
        print_text: QTextEdit = self.findChild(QTextEdit, 'print_text')
        flow_tree.clear()
        main = self.flow.main
        for i in main.son:
            if i[1] == 'function':
                child = QTreeWidgetItem(flow_tree)
                child.setText(0, 'function')
                child.setText(1, i[0].func.__name__)
                child.setText(2, str(i[0].args))
                child.setText(3, str(i[0].kwargs))
                child.setText(4, str(i[0].result(True, tostring=True)))
                setattr(child, '__flow', i[0])
                flow_tree.addTopLevelItem(child)
                self.refresh_flow_tree(child, i[0])
            else:
                child = QTreeWidgetItem(flow_tree)
                child.setText(0, 'log')
                child.setText(1, str(i[0]))
                flow_tree.addTopLevelItem(child)
        current_function = self.flow.current_function
        print_text.setText(str(current_function.result(tostring=True)))
        flow_tree.expandAll()

    def refresh_flow_tree(self, top_item, flow):
        for i in flow.son:
            if i[1] == 'function':
                child = QTreeWidgetItem(top_item)
                child.setText(0, i[0].func_type)
                child.setText(1, i[0].func.__name__)
                child.setText(2, str(i[0].args))
                child.setText(3, str(i[0].kwargs))
                child.setText(4, str(i[0].result(True, tostring=True)))
                setattr(child, '__flow', i[0])
                top_item.addChild(child)
                self.refresh_flow_tree(child, i[0])
            else:
                child = QTreeWidgetItem(top_item)
                child.setText(0, 'log')
                child.setText(1, str(i[0]))
                top_item.addChild(child)

    def refresh_current_text(self, q):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')
        current_text: QTextEdit = self.findChild(QTextEdit, 'current_text')
        current_item = flow_tree.currentItem()
        current_flow = getattr(current_item, '__flow')
        current_text.setText(str(current_flow.result(tostring=True)))

    def run_test(self, q):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')
        current_item = flow_tree.currentItem()
        current_flow = getattr(current_item, '__flow')
        current_flow(*current_flow.args, **current_flow.kwargs)
        self.refresh_ui()

    def run_continue(self, q):
        self.close()

    def run_raise(self, q):
        self.flow.raise_error = -1
        self.close()
