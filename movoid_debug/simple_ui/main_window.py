#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : main_window
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/2 21:48
# Description   : 
"""
import inspect
import re

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow, QApplication, QTreeWidget, QTextEdit, QVBoxLayout, QPushButton, QTreeWidgetItem, QHeaderView, QSplitter, QWidget, QDialog, QLabel, QHBoxLayout, QSystemTrayIcon

from .flow_thread import FlowThread
from .value_set_window import ValueSetWindow, KeySetWindow
from .basic import BasicMainWindow, tree_item_can_expand, expand_tree_item_to_show_dir, PixmapWindow, TextWindow


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


class MainWindow(BasicMainWindow):

    def __init__(self, flow, app):
        super().__init__()
        self.flow = flow
        self.app = app
        self.clipboard = QApplication.instance().clipboard()
        self.testing = False
        self.children_dialog = []
        self.init_ui()
        self.show()
        self.refresh_ui()

    def init_ui(self):
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_rect.width() * 0.1), int(screen_rect.height() * 0.2), int(screen_rect.width() * 0.8), int(screen_rect.height() * 0.6))
        main_splitter = QSplitter(self)
        self.setCentralWidget(main_splitter)

        flow_tree = QTreeWidget(main_splitter)
        flow_tree.setObjectName('flow_tree')
        main_splitter.addWidget(flow_tree)
        main_splitter.setStretchFactor(0, 12)
        flow_tree.setHeaderLabels(['type', 'func', 'status', 'last time', 'start time', 'end time'])
        flow_tree_header = flow_tree.header()
        flow_tree_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        flow_tree_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        flow_tree.itemClicked.connect(self.action_click_flow_tree_item)
        flow_tree.itemDoubleClicked.connect(self.action_double_click_flow_tree_item)

        error_text_splitter = QSplitter(Qt.Vertical, main_splitter)
        main_splitter.addWidget(error_text_splitter)
        main_splitter.setStretchFactor(1, 4)

        print_text = QTextEdit(main_splitter)
        print_text.setObjectName('print_text')
        error_text_splitter.addWidget(print_text)
        current_text = QTextEdit(main_splitter)
        current_text.setObjectName('current_text')
        error_text_splitter.addWidget(current_text)

        variable_tree_splitter = QSplitter(Qt.Vertical, main_splitter)
        main_splitter.addWidget(variable_tree_splitter)
        main_splitter.setStretchFactor(2, 6)

        arg_tree = QTreeWidget(variable_tree_splitter)
        arg_tree.setObjectName('arg_tree')
        variable_tree_splitter.addWidget(arg_tree)
        arg_tree.setHeaderLabels(['arg', 'name', 'type', 'value'])
        arg_tree.itemClicked.connect(self.click_arg_tree_item)
        arg_tree.itemDoubleClicked.connect(self.change_arg_tree_value)
        variable_tree_splitter.setStretchFactor(0, 6)

        return_tree = QTreeWidget(variable_tree_splitter)
        return_tree.setObjectName('return_tree')
        variable_tree_splitter.addWidget(return_tree)
        return_tree.setHeaderLabels(['return', 'type', 'value'])
        return_tree.itemDoubleClicked.connect(self.change_return_tree_value)
        variable_tree_splitter.setStretchFactor(1, 1)

        global_tree = QTreeWidget(variable_tree_splitter)
        global_tree.setObjectName('global_tree')
        variable_tree_splitter.addWidget(global_tree)
        global_tree.setHeaderLabels(['key', 'type', 'value'])
        global_tree.itemExpanded.connect(self.expand_tree_item_to_show_dir)
        variable_tree_splitter.setStretchFactor(2, 5)

        step_tree_splitter = QSplitter(Qt.Vertical, main_splitter)
        main_splitter.addWidget(step_tree_splitter)
        main_splitter.setStretchFactor(3, 6)

        step_tree = QTreeWidget(main_splitter)
        step_tree.setObjectName('step_tree')
        step_tree_splitter.addWidget(step_tree)
        step_tree.setHeaderLabels(['complete', 'code', 'error'])

        function_code = QTextEdit(main_splitter)
        function_code.setObjectName('function_code')
        step_tree_splitter.addWidget(function_code)

        run_widget = QWidget(main_splitter)
        run_grid = QVBoxLayout(run_widget)
        run_widget.setLayout(run_grid)
        main_splitter.addWidget(run_widget)
        main_splitter.setStretchFactor(4, 1)

        run_test_button = QPushButton('测试', run_widget)
        run_test_button.setObjectName('run_test_button')
        run_grid.addWidget(run_test_button)
        run_test_button.clicked.connect(lambda: self.run_test())
        run_test_button.setEnabled(False)
        run_grid.addStretch(1)

        add_args_button = QPushButton('新增args', run_widget)
        add_args_button.setObjectName('add_args_button')
        run_grid.addWidget(add_args_button)
        add_args_button.clicked.connect(lambda: self.action_add_args())
        add_args_button.setEnabled(False)
        delete_args_button = QPushButton('删除args', run_widget)
        delete_args_button.setObjectName('delete_args_button')
        run_grid.addWidget(delete_args_button)
        delete_args_button.clicked.connect(lambda: self.action_delete_args())
        delete_args_button.setEnabled(False)
        run_grid.addStretch(1)

        change_kwargs_key_button = QPushButton('修改kwargs的key', run_widget)
        change_kwargs_key_button.setObjectName('change_kwargs_key_button')
        run_grid.addWidget(change_kwargs_key_button)
        change_kwargs_key_button.clicked.connect(lambda: self.action_change_kwargs_key())
        change_kwargs_key_button.setEnabled(False)

        add_kwargs_button = QPushButton('新增kwargs', run_widget)
        add_kwargs_button.setObjectName('add_kwargs_button')
        run_grid.addWidget(add_kwargs_button)
        add_kwargs_button.clicked.connect(lambda: self.action_add_kwargs())
        add_kwargs_button.setEnabled(False)
        delete_kwargs_button = QPushButton('删除kwargs', run_widget)
        delete_kwargs_button.setObjectName('delete_kwargs_button')
        run_grid.addWidget(delete_kwargs_button)
        delete_kwargs_button.clicked.connect(lambda: self.action_delete_kwargs())
        delete_kwargs_button.setEnabled(False)

        copy_return_button = QPushButton('使用这个return值', run_widget)
        copy_return_button.setObjectName('copy_return_button')
        run_grid.addWidget(copy_return_button)
        copy_return_button.clicked.connect(lambda: self.action_copy_return())
        copy_return_button.setEnabled(False)

        run_grid.addStretch(1)

        frame_window_button = QPushButton('打开调试台', run_widget)
        frame_window_button.setObjectName('frame_window_button')
        run_grid.addWidget(frame_window_button)
        frame_window_button.clicked.connect(lambda: self.action_frame_window())
        frame_window_button.setEnabled(True)

        run_grid.addStretch(1)

        run_continue_button = QPushButton('忽略错误并return', run_widget)
        run_continue_button.setObjectName('run_continue_button')
        run_grid.addWidget(run_continue_button)
        run_continue_button.clicked.connect(lambda: self.run_continue())
        run_grid.addStretch(1)

        run_raise_exit_button = QPushButton('raise错误直到退出', run_widget)
        run_raise_exit_button.setObjectName('run_raise_exit_button')
        run_grid.addWidget(run_raise_exit_button)
        run_raise_exit_button.clicked.connect(lambda: self.run_raise_until_exit())

        run_raise_one_button = QPushButton('raise错误至上一层', run_widget)
        run_raise_one_button.setObjectName('run_raise_one_button')
        run_grid.addWidget(run_raise_one_button)
        run_raise_one_button.clicked.connect(lambda: self.run_raise_one())

        run_grid.addStretch(6)

    def refresh_ui(self):
        self.refresh_arg_tree(self.flow.current_function)
        self.refresh_return_tree(self.flow.current_function)
        self.refresh_flow_tree()
        self.refresh_global_tree()
        self.refresh_current_text()
        self.refresh_function_code()

    def refresh_flow_tree(self):
        flow_tree: QTreeWidget = self.findChild(QTreeWidget, 'flow_tree')  # noqa
        print_text: QTextEdit = self.findChild(QTextEdit, 'print_text')  # noqa
        flow_tree.clear()
        self.refresh_flow_tree_item(flow_tree, self.flow.main)
        current_function = self.flow.current_function
        print_text.setText(str(current_function.result(tostring=True)))

    def refresh_flow_tree_item(self, top_item, flow):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        select_func = getattr(arg_tree, '__func', None)
        for i in flow.son:
            child = QTreeWidgetItem(top_item)
            if i[1] == 'function':
                child.setText(0, i[0].func_type)
                child.setText(1, i[0].func.__name__)
                child.setText(2, str(i[0].result(True, tostring=True)))
                child.setText(3, i[0].time_str_all_last)
                child.setText(4, i[0].time_str_start)
                child.setText(5, i[0].time_str_all_end)
                self.refresh_flow_tree_item(child, i[0])
                if i[0] == select_func:
                    self.findChild(QTreeWidget, 'flow_tree').setCurrentItem(child)  # noqa
                    child.setExpanded(True)
                    self.refresh_arg_tree(i[0])
                setattr(child, '__type', 'function')
                setattr(child, '__value', i[0])
            elif i[1] == 'web_pic':
                child.setText(0, 'web picture')
                child.setText(1, self.flow.return_str_in_size(i[0]))
                setattr(child, '__type', 'web_pic')
                setattr(child, '__value', str(i[0]))
            elif i[1] == 'local_pic':
                child.setText(0, 'local picture')
                child.setText(1, self.flow.return_str_in_size(i[0]))
                setattr(child, '__type', 'local_pic')
                setattr(child, '__value', str(i[0]))
            elif isinstance(i[1], tuple):
                if i[1][0] == 'print':
                    child.setText(0, f'{i[1][1].str} {i[1][1].int}')
                    child.setText(1, self.flow.return_str_in_size(i[0]))
                    setattr(child, '__type', i[1])
                    setattr(child, '__value', i[0])

    def action_click_flow_tree_item(self, current_item, column):
        flow_item_type = getattr(current_item, '__type', None)
        flow_item_value = getattr(current_item, '__value', None)
        if flow_item_type == 'function':
            current_func = flow_item_value
            self.refresh_arg_tree(current_func)
            self.refresh_return_tree(current_func)
            self.refresh_current_text()
            if column <= 1:
                self.clipboard.setText(current_func.func.__name__)
            elif column == 2:
                self.clipboard.setText(str(current_func.result(tostring=True)))
            elif column == 3:
                self.clipboard.setText(current_func.time_str_all_last)
            elif column == 4:
                self.clipboard.setText(current_func.time_str_start)
            elif column == 5:
                self.clipboard.setText(current_func.time_str_all_end)
        else:
            self.clipboard.setText(str(flow_item_value))

    def action_double_click_flow_tree_item(self, current_item, column):
        flow_item_type = getattr(current_item, '__type', None)
        flow_item_value = getattr(current_item, '__value', None)
        if flow_item_type == 'web_pic':
            PixmapWindow.show_web_pixmap(getattr(current_item, '__value'))
        elif flow_item_type == 'local_pic':
            PixmapWindow.show_local_pixmap(getattr(current_item, '__value'))
        elif flow_item_type == 'function':
            if column <= 1:
                text = flow_item_value.func.__name__
            elif column == 2:
                text = str(flow_item_value.result(tostring=True))
            elif column == 3:
                text = flow_item_value.time_str_all_last
            elif column == 4:
                text = flow_item_value.time_str_start
            elif column == 5:
                text = flow_item_value.time_str_all_end
            else:
                text = str(flow_item_value.result(tostring=True))
            TextWindow.show_text(text, parent=self)
        elif isinstance(flow_item_type, tuple):
            if flow_item_type[0] == 'print':
                text = flow_item_value
                TextWindow.show_text(text, parent=self)

    def refresh_current_text(self):
        current_text: QTextEdit = self.findChild(QTextEdit, 'current_text')  # noqa
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        current_func = getattr(arg_tree, '__func', None)
        if current_func is not None:
            current_text.setText(str(current_func.result(tostring=True)))

    def refresh_arg_tree(self, func, kwarg_value=None):
        if func is not None:
            kwarg_value = func.kwarg_value if kwarg_value is None else kwarg_value
            arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
            run_test_button: QPushButton = self.findChild(QPushButton, 'run_test_button')  # noqa
            add_args_button: QPushButton = self.findChild(QPushButton, 'add_args_button')  # noqa
            add_kwargs_button: QPushButton = self.findChild(QPushButton, 'add_kwargs_button')  # noqa
            run_test_button.setEnabled(not self.testing)

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

    def refresh_return_tree(self, func):
        if func is not None:
            return_tree: QTreeWidget = self.findChild(QTreeWidget, 'return_tree')  # noqa
            copy_return_button: QPushButton = self.findChild(QPushButton, 'copy_return_button')  # noqa
            copy_return_button.setEnabled(type(func).__name__ == 'TestFunction' and func.ori == self.flow.current_function and func.has_return)

            setattr(return_tree, '__func', func)
            return_tree.clear()

            temp = QTreeWidgetItem(return_tree)
            temp.setText(0, 'select')
            temp.setText(1, type(func.re_value).__name__)
            temp.setText(2, str(func.re_value))

            temp = QTreeWidgetItem(return_tree)
            temp.setText(0, 'current')
            temp.setText(1, type(self.flow.current_function.re_value).__name__)
            temp.setText(2, str(self.flow.current_function.re_value))

    def click_arg_tree_item(self, current_item):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        delete_args_button: QPushButton = self.findChild(QPushButton, 'delete_args_button')  # noqa
        delete_kwargs_button: QPushButton = self.findChild(QPushButton, 'delete_kwargs_button')  # noqa
        change_kwargs_key_button: QPushButton = self.findChild(QPushButton, 'change_kwargs_key_button')  # noqa
        current_value = getattr(current_item, '__value')
        delete_args_button.setEnabled(current_value[0] == 'args')
        delete_kwargs_button.setEnabled(current_value[0] == 'kwargs')
        change_kwargs_key_button.setEnabled(current_value[0] == 'kwargs')
        setattr(arg_tree, '__current_value', [current_value[0], current_value[-2]])

    def refresh_global_tree(self):
        global_value = self.flow.error_frame.frame.f_globals
        local_value = self.flow.error_frame.frame.f_locals
        global_tree: QTreeWidget = self.findChild(QTreeWidget, 'global_tree')  # noqa
        global_tree.clear()
        for k, v in {**global_value, **local_value}.items():
            if not k.startswith('__'):
                temp = QTreeWidgetItem(global_tree)
                temp.setText(0, k)
                temp.setText(1, type(v).__name__)
                temp.setText(2, str(v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)

    def refresh_function_code(self):
        function_code: QTextEdit = self.findChild(QTextEdit, 'function_code')  # noqa
        try:
            lines, first_line = inspect.getsourcelines(self.flow.error_frame.frame.f_code)
            code_str = ''.join(lines)
        except:
            code_str = ''
        function_code.setText(code_str)

    def run_test(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        if hasattr(arg_tree, '__func') and not self.testing:
            func = getattr(arg_tree, '__func')
            kwarg_value = getattr(arg_tree, '__kwarg_value')
            args = [_v for _k, _v in kwarg_value['arg'].items()]
            if 'args' in kwarg_value:
                args += [*list(kwarg_value['args'].values())[0]]
            kwargs = {_k: _v for _k, _v in kwarg_value['kwarg'].items()}
            if 'kwargs' in kwarg_value:
                for k, v in list(kwarg_value['kwargs'].values())[0].items():
                    kwargs[k] = v
            self.thread = FlowThread(func, args=args, kwargs=kwargs)
            self.thread.signal_test.connect(self.slot_test)
            self.thread.start()

    def run_continue(self):
        self.flow.raise_error = 0
        self.close()

    def run_raise_until_exit(self):
        self.flow.raise_until_exit = True
        self.close()

    def run_raise_one(self):
        self.flow.raise_error = 1
        self.close()

    def change_arg_tree_value(self, current_item):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        func = getattr(arg_tree, '__func')
        kwarg_value = getattr(arg_tree, '__kwarg_value')
        current_value = getattr(current_item, '__value')
        new_value = ValueSetWindow.get_value(current_value[-1], parent=self)
        if new_value != current_value[-1]:
            temp = kwarg_value
            for i in current_value[:-2]:
                temp = temp[i]
            temp[current_value[-2]] = new_value
            self.refresh_arg_tree(func, kwarg_value)

    def change_return_tree_value(self, current_item: QTreeWidgetItem):
        if current_item.text(0) == 'current':
            return_tree: QTreeWidget = self.findChild(QTreeWidget, 'return_tree')  # noqa
            func = getattr(return_tree, '__func')
            new_value = ValueSetWindow.get_value(self.flow.current_function.re_value, parent=self)
            if new_value != self.flow.current_function.re_value:
                self.flow.current_function.re_value = new_value
                self.refresh_return_tree(func)

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

    def action_copy_return(self):
        return_tree: QTreeWidget = self.findChild(QTreeWidget, 'return_tree')  # noqa
        func = getattr(return_tree, '__func')
        self.flow.current_function.re_value = func.re_value
        self.refresh_return_tree(func)

    def action_frame_window(self):
        self.app.add_frame_window()

    @Slot(bool)
    def slot_test(self, start: bool):
        self.testing = start
        self.refresh_ui()
