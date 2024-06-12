#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : main_window
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:48
# Description   : 
"""
import re

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QTreeWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidgetItem

from .value_set_window import ValueSetWindow, KeySetWindow, tree_item_can_expand, expand_tree_item_to_show_dir


def create_new_dict_item(ori_dict, ori_key=None):
    ori_key = ori_key if ori_key in ori_dict else None
    if len(ori_dict) == 0:
        if ori_key is None:
            ori_dict['key'] = None
        else:
            ori_dict[ori_key] = None
    else:
        if ori_key is None:
            tar_key = list(ori_dict.keys())[-1]
        else:
            tar_key = ori_key
        tar_value = ori_dict[tar_key]
        re_key = re.search(r'(.*)_\d*$', tar_key)
        if re_key is None:
            key_head = tar_key
        else:
            key_head = re_key.group(1)
        index = 2
        while True:
            real_key = f'{key_head}_{index}'
            if real_key in ori_dict:
                index += 1
            else:
                break
        ori_dict[real_key] = tar_value


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
        arg_tree.itemClicked.connect(lambda: self.click_arg_tree_item())
        arg_tree.itemDoubleClicked.connect(lambda: self.change_arg_tree_value())

        global_tree = QTreeWidget(main_table)
        global_tree.setObjectName('global_tree')
        main_gird.addWidget(global_tree, 1, 2, 2, 1)
        global_tree.setHeaderLabels(['key', 'type', 'value'])
        global_tree.itemExpanded.connect(self.expand_tree_item_to_show_dir)

        run_widget = QWidget(main_table)
        end_widget = QWidget(main_table)
        main_gird.addWidget(run_widget, 0, 3, 3, 1)
        main_gird.addWidget(end_widget, 4, 0, 1, 3)
        run_grid = QVBoxLayout(run_widget)
        run_widget.setLayout(run_grid)
        end_grid = QHBoxLayout(end_widget)
        end_widget.setLayout(end_grid)

        run_test_button = QPushButton('测试', main_table)
        run_test_button.setObjectName('run_test_button')
        run_grid.addWidget(run_test_button)
        run_test_button.clicked.connect(lambda: self.run_test())
        run_test_button.setEnabled(False)
        run_grid.addStretch(1)

        add_args_button = QPushButton('新增args', main_table)
        add_args_button.setObjectName('add_args_button')
        run_grid.addWidget(add_args_button)
        add_args_button.clicked.connect(lambda: self.action_add_args())
        add_args_button.setEnabled(False)
        delete_args_button = QPushButton('删除args', main_table)
        delete_args_button.setObjectName('delete_args_button')
        run_grid.addWidget(delete_args_button)
        delete_args_button.clicked.connect(lambda: self.action_delete_args())
        delete_args_button.setEnabled(False)
        run_grid.addStretch(1)

        change_kwargs_key_button = QPushButton('修改kwargs的key', main_table)
        change_kwargs_key_button.setObjectName('change_kwargs_key_button')
        run_grid.addWidget(change_kwargs_key_button)
        change_kwargs_key_button.clicked.connect(lambda: self.action_change_kwargs_key())
        change_kwargs_key_button.setEnabled(False)

        add_kwargs_button = QPushButton('新增kwargs', main_table)
        add_kwargs_button.setObjectName('add_kwargs_button')
        run_grid.addWidget(add_kwargs_button)
        add_kwargs_button.clicked.connect(lambda: self.action_add_kwargs())
        add_kwargs_button.setEnabled(False)
        delete_kwargs_button = QPushButton('删除kwargs', main_table)
        delete_kwargs_button.setObjectName('delete_kwargs_button')
        run_grid.addWidget(delete_kwargs_button)
        delete_kwargs_button.clicked.connect(lambda: self.action_delete_kwargs())
        delete_kwargs_button.setEnabled(False)

        run_grid.addStretch(3)

        run_continue_button = QPushButton('忽略错误并continue', main_table)
        run_continue_button.setObjectName('run_continue_button')
        run_grid.addWidget(run_continue_button)
        run_continue_button.clicked.connect(lambda: self.run_continue())
        run_grid.addStretch(1)

        run_raise_button = QPushButton('raise错误', main_table)
        run_raise_button.setObjectName('run_raise_button')
        run_grid.addWidget(run_raise_button)
        run_raise_button.clicked.connect(lambda: self.run_raise())

        run_raise_one_button = QPushButton('raise错误至上一层', main_table)
        run_raise_one_button.setObjectName('run_raise_one_button')
        run_grid.addWidget(run_raise_one_button)
        run_raise_one_button.clicked.connect(lambda: self.run_raise_one())

        run_grid.addStretch(6)

    def refresh_ui(self):
        self.refresh_flow_tree()
        self.refresh_global_tree()

    def refresh_flow_tree(self):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')  # noqa
        print_text: QTextEdit = self.findChild(QTextEdit, 'print_text')  # noqa
        flow_tree.clear()
        self.refresh_flow_tree_item(flow_tree, self.flow.main)
        current_function = self.flow.current_function
        print_text.setText(str(current_function.result(tostring=True)))
        flow_tree.expandAll()

    def refresh_flow_tree_item(self, top_item, flow):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        select_flow = getattr(arg_tree, '__func', None)
        for i in flow.son:
            if i[1] == 'function':
                child = QTreeWidgetItem(top_item)
                child.setText(0, i[0].func_type)
                child.setText(1, i[0].func.__name__)
                child.setText(2, str(i[0].args))
                child.setText(3, str(i[0].kwargs))
                child.setText(4, str(i[0].result(True, tostring=True)))
                setattr(child, '__func', i[0])
                self.refresh_flow_tree_item(child, i[0])
                if i[0] == select_flow:
                    self.findChild(QTreeWidget, 'flow_tree').setCurrentItem(child)  # noqa
            else:
                child = QTreeWidgetItem(top_item)
                child.setText(0, 'log')
                child.setText(1, str(i[0]))

    def click_flow_refresh_ui(self, q):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')  # noqa
        current_text: QTextEdit = self.findChild(QTextEdit, 'current_text')  # noqa
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        arg_tree.clear()
        current_item = flow_tree.currentItem()
        current_func = getattr(current_item, '__func')
        current_text.setText(str(current_func.result(tostring=True)))
        self.refresh_arg_tree(current_func)

    def refresh_arg_tree(self, func, kwarg_value=None):
        kwarg_value = func.kwarg_value if kwarg_value is None else kwarg_value
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        run_test_button: QPushButton = self.findChild(QPushButton, 'run_test_button')  # noqa
        add_args_button: QPushButton = self.findChild(QPushButton, 'add_args_button')  # noqa
        add_kwargs_button: QPushButton = self.findChild(QPushButton, 'add_kwargs_button')  # noqa
        run_test_button.setEnabled(True)

        setattr(arg_tree, '__func', func)
        setattr(arg_tree, '__kwarg_value', kwarg_value)
        arg_tree.clear()
        current_item = getattr(arg_tree, '__current_value', [None, None])
        for k, v in kwarg_value['arg'].items():
            temp = QTreeWidgetItem(arg_tree)
            temp.setText(0, 'arg')
            temp.setText(1, str(k))
            temp.setText(2, type(v).__name__)
            temp.setText(3, str(v))
            setattr(temp, '__value', ['arg', k, v])
            if current_item[0] == 'arg' and current_item[1] == k:
                arg_tree.setCurrentItem(temp)
        add_args_button.setEnabled('args' in kwarg_value)
        if 'args' in kwarg_value:
            args_name = list(kwarg_value['args'].keys())[0]
            args_list = kwarg_value['args'][args_name]
            for k, v in enumerate(args_list):
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(0, 'args')
                temp.setText(1, f'{args_name}[{k}]')
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, '__value', ['args', args_name, k, v])
                if current_item[0] == 'args' and current_item[1] == k:
                    arg_tree.setCurrentItem(temp)
        for k, v in kwarg_value['kwarg'].items():
            temp = QTreeWidgetItem(arg_tree)
            temp.setText(0, 'kwarg')
            temp.setText(1, str(k))
            temp.setText(2, type(v).__name__)
            temp.setText(3, str(v))
            setattr(temp, '__value', ['kwarg', k, v])
            if current_item[0] == 'kwarg' and current_item[1] == k:
                arg_tree.setCurrentItem(temp)
        add_kwargs_button.setEnabled('kwargs' in kwarg_value)
        if 'kwargs' in kwarg_value:
            kwargs_name = list(kwarg_value['kwargs'].keys())[0]
            kwargs_dict = kwarg_value['kwargs'][kwargs_name]
            for k, v in kwargs_dict.items():
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(0, 'kwargs')
                temp.setText(1, f'{kwargs_name}[{k}]')
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, '__value', ['kwargs', kwargs_name, k, v])
                if current_item[0] == 'kwargs' and current_item[1] == k:
                    arg_tree.setCurrentItem(temp)

    def click_arg_tree_item(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        delete_args_button: QPushButton = self.findChild(QPushButton, 'delete_args_button')  # noqa
        delete_kwargs_button: QPushButton = self.findChild(QPushButton, 'delete_kwargs_button')  # noqa
        change_kwargs_key_button: QPushButton = self.findChild(QPushButton, 'change_kwargs_key_button')  # noqa
        current_item = arg_tree.currentItem()
        current_value = getattr(current_item, '__value')
        delete_args_button.setEnabled(current_value[0] == 'args')
        delete_kwargs_button.setEnabled(current_value[0] == 'kwargs')
        change_kwargs_key_button.setEnabled(current_value[0] == 'kwargs')
        setattr(arg_tree, '__current_value', [current_value[0], current_value[-2]])

    def refresh_global_tree(self):
        global_value = globals()
        global_tree: QTreeWidget = self.findChild(QTreeWidget, 'global_tree')  # noqa
        global_tree.clear()
        for k, v in global_value.items():
            if not k.startswith('__'):
                temp = QTreeWidgetItem(global_tree)
                temp.setText(0, k)
                temp.setText(1, type(v).__name__)
                temp.setText(2, str(v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)

    def run_test(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        if hasattr(arg_tree, '__func'):
            func = getattr(arg_tree, '__func')
            kwarg_value = getattr(arg_tree, '__kwarg_value')
            args = [_v for _k, _v in kwarg_value['arg'].items()]
            if 'args' in kwarg_value:
                args += [*list(kwarg_value['args'].values())[0]]
            kwargs = {_k: _v for _k, _v in kwarg_value['kwarg'].items()}
            if 'kwargs' in kwarg_value:
                for k, v in list(kwarg_value['kwargs'].values())[0].items():
                    kwargs[k] = v
            func(*args, **kwargs)
            self.refresh_ui()

    def run_continue(self):
        self.close()

    def run_raise(self):
        self.flow.raise_error = -1
        self.close()

    def run_raise_one(self):
        self.flow.raise_error = 1
        self.close()

    def change_arg_tree_value(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        current_value = getattr(current_item, '__value')
        new_value = ValueSetWindow.get_value(current_value[-1])
        if new_value != current_value[-1]:
            temp = kwarg_value
            for i in current_value[:-2]:
                temp = temp[i]
            temp[current_value[-2]] = new_value
            self.refresh_arg_tree(func, kwarg_value)

    @staticmethod
    def expand_tree_item_to_show_dir(item: QTreeWidgetItem):
        expand_tree_item_to_show_dir(item, {
            0: lambda k, v: str(k),
            1: lambda k, v: type(v).__name__,
            2: lambda k, v: str(v),
        })

    def action_add_args(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        args_list = list(kwarg_value['args'].values())[0]
        if current_item is None:
            if len(args_list) == 0:
                args_list.append(None)
            else:
                args_list.append(args_list[-1])
        else:
            current_value = getattr(current_item, '__value')
            if current_value[0] == 'arg':
                if len(args_list) == 0:
                    args_list.insert(0, None)
                else:
                    args_list.insert(0, args_list[0])
            elif current_value[0] == 'args':
                index = current_value[2]
                args_list.insert(index + 1, args_list[index])
            else:
                if len(args_list) == 0:
                    args_list.append(None)
                else:
                    args_list.append(args_list[-1])
        self.refresh_arg_tree(func, kwarg_value)

    def action_delete_args(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        args_list: list = list(kwarg_value['args'].values())[0]
        if current_item is not None:
            current_value = getattr(current_item, '__value')
            if current_value[0] == 'args':
                index = current_value[2]
                args_list.pop(index)
                self.refresh_arg_tree(func, kwarg_value)

    def action_change_kwargs_key(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        kwargs_dict = list(kwarg_value['kwargs'].values())[0]
        if current_item is not None:
            current_value = getattr(current_item, '__value')
            if current_value[0] == 'kwargs':
                if KeySetWindow.get_value(kwargs_dict, current_value[2]):
                    self.refresh_arg_tree(func, kwarg_value)

    def action_add_kwargs(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        kwargs_dict = list(kwarg_value['kwargs'].values())[0]
        if current_item is None:
            create_new_dict_item(kwargs_dict, None)
        else:
            current_value = getattr(current_item, '__value')
            if current_value[0] == 'kwargs':
                create_new_dict_item(kwargs_dict, current_value[2])
            else:
                create_new_dict_item(kwargs_dict, None)
        self.refresh_arg_tree(func, kwarg_value)

    def action_delete_kwargs(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_item = arg_tree.currentItem()
        kwargs_dict = list(kwarg_value['kwargs'].values())[0]
        if current_item is not None:
            current_value = getattr(current_item, '__value')
            if current_value[0] == 'kwargs':
                key = current_value[2]
                kwargs_dict.pop(key)
                self.refresh_arg_tree(func, kwarg_value)
