#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : main_window
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:48
# Description   : 
"""
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QTreeWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidgetItem

from .value_set_window import ValueSetWindow, tree_item_can_expand, expand_tree_item_to_show_dir


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
        main_gird.setColumnStretch(2, 3)
        main_gird.setColumnStretch(3, 1)
        main_gird.setRowStretch(0, 1)
        main_gird.setRowStretch(1, 2)

        flow_tree = QTreeWidget(main_table)
        flow_tree.setObjectName('flow_tree')
        main_gird.addWidget(flow_tree, 0, 0, 2, 1)
        flow_tree.setHeaderLabels(['type', 'func', 'args', 'kwargs', 'status'])
        flow_tree.itemClicked.connect(self.click_flow_refresh_ui)

        print_text = QTextEdit(main_table)
        print_text.setObjectName('print_text')
        main_gird.addWidget(print_text, 0, 1)

        current_text = QTextEdit(main_table)
        current_text.setObjectName('current_text')
        main_gird.addWidget(current_text, 1, 1, 2, 1)

        arg_tree = QTreeWidget(main_table)
        arg_tree.setObjectName('arg_tree')
        main_gird.addWidget(arg_tree, 0, 2, 1, 1)
        arg_tree.setHeaderLabels(['arg', 'name', 'type', 'value'])
        arg_tree.itemDoubleClicked.connect(lambda: self.change_arg_tree_value())

        global_tree = QTreeWidget(main_table)
        global_tree.setObjectName('global_tree')
        main_gird.addWidget(global_tree, 1, 2, 2, 1)
        global_tree.setHeaderLabels(['key', 'type', 'value'])
        global_tree.itemExpanded.connect(self.expand_tree_item_to_show_dir)

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

        run_raise_button = QPushButton('raise错误', main_table)
        run_raise_button.setObjectName('run_raise_button')
        run_grid.addWidget(run_raise_button)
        run_raise_button.clicked.connect(self.run_raise)

        run_raise_one_button = QPushButton('raise错误至上一层', main_table)
        run_raise_one_button.setObjectName('run_raise_one_button')
        run_grid.addWidget(run_raise_one_button)
        run_raise_one_button.clicked.connect(self.run_raise_one)

        run_grid.addStretch(10)

    def refresh_ui(self):
        self.refresh_flow_tree()
        self.refresh_global_tree()

    def refresh_flow_tree(self):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')
        print_text: QTextEdit = self.findChild(QTextEdit, 'print_text')
        flow_tree.clear()
        self.refresh_flow_tree_item(flow_tree, self.flow.main)
        current_function = self.flow.current_function
        print_text.setText(str(current_function.result(tostring=True)))
        flow_tree.expandAll()

    def refresh_flow_tree_item(self, top_item, flow):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')
        select_flow = getattr(arg_tree, 'flow', None)
        for i in flow.son:
            if i[1] == 'function':
                child = QTreeWidgetItem(top_item)
                child.setText(0, i[0].func_type)
                child.setText(1, i[0].func.__name__)
                child.setText(2, str(i[0].args))
                child.setText(3, str(i[0].kwargs))
                child.setText(4, str(i[0].result(True, tostring=True)))
                setattr(child, '__flow', i[0])
                self.refresh_flow_tree_item(child, i[0])
                if i[0] == select_flow:
                    self.findChild(QTreeWidget, 'flow_tree').setCurrentItem(child)
            else:
                child = QTreeWidgetItem(top_item)
                child.setText(0, 'log')
                child.setText(1, str(i[0]))

    def click_flow_refresh_ui(self, q):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')
        current_text: QTextEdit = self.findChild(QTextEdit, 'current_text')
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')
        arg_tree.clear()
        current_item = flow_tree.currentItem()
        current_flow = getattr(current_item, '__flow')
        current_text.setText(str(current_flow.result(tostring=True)))
        self.refresh_arg_tree(current_flow)

    def refresh_arg_tree(self, flow, kwarg_value=None):
        kwarg_value = flow.kwarg_value if kwarg_value is None else kwarg_value
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')
        setattr(arg_tree, 'flow', flow)
        setattr(arg_tree, 'kwarg_value', kwarg_value)
        arg_tree.clear()
        for k, v in kwarg_value['arg'].items():
            temp = QTreeWidgetItem(arg_tree)
            temp.setText(0, 'arg')
            temp.setText(1, str(k))
            temp.setText(2, type(v).__name__)
            temp.setText(3, str(v))
            setattr(temp, 'kwarg_value', ['arg', k, v])
            temp.setExpanded(True)
        if 'args' in kwarg_value:
            args_name = list(kwarg_value['args'].keys())[0]
            args_list = kwarg_value['args'][args_name]
            for k, v in enumerate(args_list):
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(0, 'args')
                temp.setText(1, f'{args_name}[{k}]')
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, 'kwarg_value', ['args', args_name, k, v])
        for k, v in kwarg_value['kwarg'].items():
            temp = QTreeWidgetItem(arg_tree)
            temp.setText(0, 'kwarg')
            temp.setText(1, str(k))
            temp.setText(2, type(v).__name__)
            temp.setText(3, str(v))
            setattr(temp, 'kwarg_value', ['kwarg', k, v])
        if 'kwargs' in kwarg_value:
            kwargs_name = list(kwarg_value['kwargs'].keys())[0]
            kwargs_dict = kwarg_value['kwargs'][kwargs_name]
            for k, v in kwargs_dict.items():
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(0, 'kwargs')
                temp.setText(1, f'{kwargs_name}[{k}]')
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, 'kwarg_value', ['kwargs', kwargs_name, k, v])

    def refresh_global_tree(self):
        global_value = globals()
        global_tree: QTreeWidget = self.findChild(QTreeWidget, 'global_tree')
        global_tree.clear()
        for k, v in global_value.items():
            if not k.startswith('__'):
                temp = QTreeWidgetItem(global_tree)
                temp.setText(0, k)
                temp.setText(1, type(v).__name__)
                temp.setText(2, str(v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)

    def run_test(self, q):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')
        if hasattr(arg_tree, 'flow'):
            flow = getattr(arg_tree, 'flow')
            kwarg_value = getattr(arg_tree, 'kwarg_value')
            args = [_v for _k, _v in kwarg_value['arg'].items()]
            if 'args' in kwarg_value:
                args += [*list(kwarg_value['args'].values())[0]]
            kwargs = {_k: _v for _k, _v in kwarg_value['kwarg'].items()}
            if 'kwargs' in kwarg_value:
                for k, v in list(kwarg_value['kwargs'].values())[0].items():
                    kwargs[k] = v
            flow(*args, **kwargs)
            self.refresh_ui()

    def run_continue(self, q):
        self.close()

    def run_raise(self, q):
        self.flow.raise_error = -1
        self.close()

    def run_raise_one(self, q):
        self.flow.raise_error = 1
        self.close()

    def change_arg_tree_value(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')
        flow = getattr(arg_tree, 'flow')
        kwarg_value = getattr(arg_tree, 'kwarg_value')
        current_item = arg_tree.currentItem()
        current_value = getattr(current_item, 'kwarg_value')
        new_value = ValueSetWindow.get_value(current_value[-1])
        if new_value != current_value[-1]:
            temp = kwarg_value
            for i in current_value[:-2]:
                temp = temp[i]
            temp[current_value[-2]] = new_value
            self.refresh_arg_tree(flow, kwarg_value)

    @staticmethod
    def expand_tree_item_to_show_dir(item: QTreeWidgetItem):
        expand_tree_item_to_show_dir(item, {
            0: lambda k, v: str(k),
            1: lambda k, v: type(v).__name__,
            2: lambda k, v: str(v),
        })
