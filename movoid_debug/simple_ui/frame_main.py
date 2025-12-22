#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : frame_main
# Author        : Sun YiFan-Movoid
# Time          : 2024/7/2 0:18
# Description   : 
"""
import builtins
import inspect
import pathlib
import sys
import traceback
from datetime import datetime
from types import FrameType
from typing import List, Union, Tuple

from PySide6.QtCore import Qt, Signal, QObject

from PySide6.QtWidgets import QApplication, QSplitter, QTreeWidget, QTextEdit, QWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QCheckBox, QGroupBox
from movoid_function import ReplaceFunction, STACK, stack, StackFrame

from .basic import tree_item_can_expand, expand_tree_item_to_show_dir, BasicMainWindow, change_time_float_to_str, CodeTextEdit


class FrameStdout(QObject):
    style = 'out'
    signal_write = Signal(datetime, str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.temp_text = ''
        self.temp_time = datetime.now()

    def write(self, text):
        if self.temp_text:
            text_list = text.split('\n', 1)
            self.temp_text += text_list[0]
            if len(text_list) > 1:
                self.signal_write.emit(self.temp_time, self.style, self.temp_text)
                self.temp_time = datetime.now()
                self.temp_text = text_list[1]
        else:
            self.temp_text = text
            self.temp_time = datetime.now()


class FrameStderr(FrameStdout):
    style = 'error'


class FrameExecute(QObject):
    signal_terminal_start = Signal()
    signal_terminal_end = Signal()
    signal_text_new = Signal(datetime, str, str)

    def __init__(self, script, frame, index, parent=None):
        super().__init__(parent=parent)
        self.script = script
        self.frame = frame
        self.index = index
        self.re_value = None
        self.error = None
        self.traceback = None
        self.start_time = datetime(1970, 1, 1)
        self.end_time = datetime(1970, 1, 1)
        self.history = []  # [time(datetime),style(in,out,error),str]
        self.ori_stdout = sys.stdout
        self.ori_stderr = sys.stderr
        self.stdout = FrameStdout(self)
        self.stderr = FrameStderr(self)
        self.stdout.signal_write.connect(self.action_write_stdout)
        self.stderr.signal_write.connect(self.action_write_stdout)

    def start(self):
        self.signal_terminal_start.emit()
        self.start_time = datetime.now()
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        if isinstance(builtins.print, ReplaceFunction):
            builtins.print.multi_use_ori()
        self.signal_text_new.emit(self.start_time, 'script', self.script)
        try:
            re_value = eval(self.script, self.frame.f_globals, self.frame.f_locals)
        except SyntaxError:
            try:
                exec(self.script, self.frame.f_globals, self.frame.f_locals)
            except Exception as e:
                self.error = e
                self.traceback = traceback.format_exc()
            else:
                pass
        except Exception as e:
            self.error = e
            self.traceback = traceback.format_exc()
        else:
            self.re_value = re_value
        if isinstance(builtins.print, ReplaceFunction):
            builtins.print.multi_use_last()
        sys.stdout = self.ori_stdout
        sys.stderr = self.ori_stderr
        self.end_time = datetime.now()
        if self.error is None:
            self.signal_text_new.emit(self.end_time, 'end out', str(self.re_value))
        else:
            self.signal_text_new.emit(self.end_time, 'end error', str(self.traceback))
        self.signal_terminal_end.emit()

    def action_write_stdout(self, write_time, style, text):
        self.history.append((write_time, style, text))
        self.signal_text_new.emit(write_time, style, text)


class FrameMainWindow(BasicMainWindow):

    def __init__(self, flow, _stack_level=None, parent=None):
        super().__init__(parent=parent)
        self.flow = flow
        _stack_level = (0 if _stack_level is None else int(_stack_level))
        _frame: FrameType = inspect.currentframe()
        self._frame_list_ignore: List[Tuple[StackFrame, int]] = STACK.get_frame_list(
            stacklevel=_stack_level,
            init_ignore_level=stack.DEBUG,
            skip_ignore_level=stack.DECORATOR,
            with_stack_level=True)
        self._frame_list_all: List[Tuple[StackFrame, int]] = STACK.get_frame_list(
            stacklevel=_stack_level,
            init_ignore_level=stack.DEBUG,
            skip_ignore_level=stack.NO_SKIP,
            with_stack_level=True)
        self._frame_list: List[Tuple[StackFrame, int]] = self._frame_list_all
        self._index = 0
        self._execute_list: List[FrameExecute] = []
        self._current_execute = False
        self.init_ui()
        self.show()
        self.refresh_ui()

    @property
    def frame(self) -> FrameType:
        return self._frame_list[self._index][0].frame

    @property
    def frame_index(self) -> int:
        return self._frame_list[self._index][1]

    def init_ui(self):
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_rect.width() * 0), int(screen_rect.height() * 0), int(screen_rect.width() * 0.8), int(screen_rect.height() * 0.6))
        main_splitter = QSplitter(self)
        self.setCentralWidget(main_splitter)
        # main_splitter = self

        # frame area 放frame区域的
        frame_area = QWidget(main_splitter)
        main_splitter.addWidget(frame_area)
        main_splitter.setStretchFactor(0, 1)
        frame_layout = QVBoxLayout(frame_area)
        frame_area.setLayout(frame_layout)
        # 切换frame是否全部显示
        frame_wrap_switch = QCheckBox('show wrap frame')
        frame_wrap_switch.setObjectName('frame_wrap_switch')
        frame_layout.addWidget(frame_wrap_switch)
        frame_wrap_switch.setChecked(False)
        frame_wrap_switch.setToolTip('关闭后会隐藏因为装饰器而产生的frame')
        frame_wrap_switch.stateChanged.connect(self.refresh_frame_tree)

        frame_tree = QTreeWidget(frame_area)
        frame_tree.setObjectName('frame_tree')
        frame_layout.addWidget(frame_tree)
        frame_tree.itemDoubleClicked.connect(self.action_double_click_frame_tree_item)
        frame_tree.header().setVisible(False)

        history_area = QWidget(main_splitter)
        main_splitter.addWidget(history_area)
        main_splitter.setStretchFactor(1, 1)
        history_layout = QVBoxLayout(history_area)
        history_area.setLayout(history_layout)
        history_tree = QTreeWidget(history_area)
        history_tree.setObjectName('history_tree')
        history_layout.addWidget(history_tree)
        history_tree.header().setVisible(False)
        history_tree.itemDoubleClicked.connect(self.action_double_click_history_tree_item)

        terminal_splitter = QSplitter(Qt.Vertical, main_splitter)
        main_splitter.addWidget(terminal_splitter)
        main_splitter.setStretchFactor(2, 1)

        terminal_info_text = QTextEdit(terminal_splitter)
        terminal_info_text.setReadOnly(True)
        terminal_info_text.setObjectName('terminal_info_text')
        terminal_splitter.addWidget(terminal_info_text)
        terminal_splitter.setStretchFactor(0, 1)

        terminal_input_text = CodeTextEdit(terminal_splitter)
        terminal_input_text.setObjectName('terminal_input_text')
        terminal_splitter.addWidget(terminal_input_text)
        terminal_input_text.signal_shift_enter.connect(self.action_click_terminal_button_enter)
        terminal_splitter.setStretchFactor(1, 1)

        terminal_button_area = QWidget(terminal_splitter)
        terminal_button_area.setObjectName('terminal_button_area')
        terminal_splitter.addWidget(terminal_button_area)
        terminal_splitter.setStretchFactor(2, 0)
        terminal_button_layout = QVBoxLayout(terminal_button_area)
        terminal_button_area.setLayout(terminal_button_layout)
        terminal_button_enter = QPushButton('Enter', terminal_button_area)
        terminal_button_enter.setObjectName('terminal_button_enter')
        terminal_button_layout.addWidget(terminal_button_enter)
        terminal_button_enter.clicked.connect(self.action_click_terminal_button_enter)

        var_splitter = QSplitter(Qt.Vertical, main_splitter)
        global_var_group_box = QGroupBox('global', var_splitter)
        global_var_group_box_layout = QVBoxLayout(global_var_group_box)
        global_var_group_box.setLayout(global_var_group_box_layout)
        global_var_full_switch = QCheckBox('show all variables')
        global_var_full_switch.setObjectName('global_var_full_switch')
        global_var_group_box_layout.addWidget(global_var_full_switch)
        global_var_full_switch.setChecked(False)
        global_var_full_switch.setToolTip('选中后可以选择所有__xxx__类型的变量')
        global_var_full_switch.stateChanged.connect(self.refresh_global_var_tree)
        global_var_tree = QTreeWidget(var_splitter)
        global_var_tree.setObjectName('global_var_tree')
        global_var_group_box_layout.addWidget(global_var_tree)
        var_splitter.setStretchFactor(0, 1)
        global_var_tree.setHeaderLabels(['name', 'type', 'value'])
        global_var_tree.itemExpanded.connect(self.expand_global_var_tree_item_to_show_dir)

        local_var_group_box = QGroupBox('local', var_splitter)
        local_var_group_box_layout = QVBoxLayout(local_var_group_box)
        local_var_group_box.setLayout(local_var_group_box_layout)
        local_var_full_switch = QCheckBox('show all variables')
        local_var_full_switch.setObjectName('local_var_full_switch')
        local_var_group_box_layout.addWidget(local_var_full_switch)
        local_var_full_switch.setChecked(False)
        local_var_full_switch.setToolTip('选中后可以选择所有__xxx__类型的变量')
        local_var_full_switch.stateChanged.connect(self.refresh_local_var_tree)
        local_var_tree = QTreeWidget(var_splitter)
        local_var_tree.setObjectName('local_var_tree')
        local_var_group_box_layout.addWidget(local_var_tree)
        var_splitter.setStretchFactor(1, 1)
        local_var_tree.setHeaderLabels(['name', 'type', 'value'])
        local_var_tree.itemExpanded.connect(self.expand_local_var_tree_item_to_show_dir)
        main_splitter.addWidget(var_splitter)
        main_splitter.setStretchFactor(3, 1)

    def refresh_ui(self):
        self.refresh_frame_tree()
        self.refresh_history_tree()

    def refresh_frame_tree(self):
        frame_tree: QTreeWidget = self.findChild(QTreeWidget, 'frame_tree')
        frame_wrap_switch: QCheckBox = self.findChild(QCheckBox, 'frame_wrap_switch')
        frame_wrap_switch_state = frame_wrap_switch.isChecked()
        frame_index = self.frame_index
        if frame_wrap_switch_state:
            self._frame_list = self._frame_list_all
        else:
            self._frame_list = self._frame_list_ignore
        frame_tree.clear()
        main_file_path = pathlib.Path(sys.argv[0]).parent
        frame_selected = True
        for _list_index, _frame_list in enumerate(self._frame_list):
            _stack_frame, _frame_index = _frame_list
            _frame=_stack_frame.frame
            frame_file_path = pathlib.Path(_frame.f_code.co_filename)
            frame_code_lines, frame_code_lineno = inspect.getsourcelines(_frame.f_code)
            frame_code_text = ''.join(frame_code_lines).strip('\n')
            frame_item = QTreeWidgetItem(frame_tree, [f'{_frame_index} {_stack_frame.info()}'])
            frame_tree.addTopLevelItem(frame_item)
            frame_item.setData(0, Qt.UserRole, _list_index)
            if frame_selected and _frame_index >= frame_index:
                self._index = _list_index
                frame_selected = False
            try:
                frame_file_path_relative = frame_file_path.relative_to(main_file_path)
            except ValueError:
                frame_item_file = QTreeWidgetItem(frame_item, [f'file name:{_frame.f_code.co_filename}'])
                frame_item.addChild(frame_item_file)
            else:
                frame_item_file = QTreeWidgetItem(frame_item, [f'relative file:{frame_file_path_relative}'])
                frame_item.addChild(frame_item_file)
            frame_item_code = QTreeWidgetItem(frame_item, [f'{frame_code_text}'])
            frame_item.addChild(frame_item_code)
        if frame_selected:
            self._index = len(self._frame_list) - 1
        select = frame_tree.topLevelItem(self._index)
        frame_tree.setCurrentItem(select)
        self.refresh_var_tree()

    def refresh_history_tree(self):
        history_tree: QTreeWidget = self.findChild(QTreeWidget, 'history_tree')
        history_tree.clear()
        self.update_history_tree()

    def update_history_tree(self):
        history_tree: QTreeWidget = self.findChild(QTreeWidget, 'history_tree')
        children_count = history_tree.topLevelItemCount()
        for _index, _execute in enumerate(self._execute_list[children_count:]):
            _index = _index + children_count
            simple_code = _execute.script.strip().split('\n')[0]
            if len(simple_code) > 40:
                simple_code = simple_code[:40] + '...'
            history_item = QTreeWidgetItem(history_tree, [f'{_index} {change_time_float_to_str(_execute.start_time)} {_execute.index} {simple_code}'])
            history_tree.addTopLevelItem(history_item)
            history_item_code = QTreeWidgetItem(history_item, [_execute.script])
            history_item.addChild(history_item_code)
            history_item.setData(0, Qt.UserRole, _index)
            for one_history in _execute.history:
                one_history_item = QTreeWidgetItem(history_item, [f'{change_time_float_to_str(one_history[0])} {one_history[1]} {one_history[2]}'])
                history_item.addChild(one_history_item)
            if _execute.error is None:
                history_item_value = QTreeWidgetItem(history_item, [f'return: {type(_execute.re_value).__name__} {_execute.re_value}'])
                history_item.addChild(history_item_value)
            else:
                history_item_error = QTreeWidgetItem(history_item, [f'error: {type(_execute.error).__name__} {_execute.error}'])
                history_item.addChild(history_item_error)
                history_item_traceback = QTreeWidgetItem(history_item, [f'{_execute.traceback.strip()}'])
                history_item.addChild(history_item_traceback)

    def refresh_var_tree(self):
        self.refresh_global_var_tree()
        self.refresh_local_var_tree()

    def refresh_global_var_tree(self):
        global_var_tree: QTreeWidget = self.findChild(QTreeWidget, 'global_var_tree')
        global_var_full_switch: QCheckBox = self.findChild(QCheckBox, 'global_var_full_switch')
        global_var_tree.clear()
        for _name, _value in self.frame.f_globals.items():
            if global_var_full_switch.isChecked() or not (_name.startswith('__') and _name.endswith('__')):
                global_var_item = QTreeWidgetItem(global_var_tree, [_name, type(_value).__name__, str(_value)])
                global_var_tree.addTopLevelItem(global_var_item)
                setattr(global_var_item, '__tree_object', _value)
                tree_item_can_expand(global_var_item)

    def refresh_local_var_tree(self):
        local_var_tree: QTreeWidget = self.findChild(QTreeWidget, 'local_var_tree')
        local_var_full_switch: QCheckBox = self.findChild(QCheckBox, 'local_var_full_switch')
        local_var_tree.clear()
        for _name, _value in self.frame.f_locals.items():
            if local_var_full_switch.isChecked() or not (_name.startswith('__') and _name.endswith('__')):
                local_var_item = QTreeWidgetItem(local_var_tree, [_name, type(_value).__name__, str(_value)])
                local_var_tree.addTopLevelItem(local_var_item)
                setattr(local_var_item, '__tree_object', _value)
                tree_item_can_expand(local_var_item)

    def action_double_click_frame_tree_item(self, item: QTreeWidgetItem):
        frame_tree: QTreeWidget = self.findChild(QTreeWidget, 'frame_tree')
        terminal_input_text: CodeTextEdit = self.findChild(CodeTextEdit, 'terminal_input_text')
        item_is_top = True
        while True:
            if item.parent() is None:
                break
            else:
                item = item.parent()
                item_is_top = False
        self._index = item.data(0, Qt.UserRole)
        item.treeWidget().collapseAll()
        item.setExpanded(not item_is_top)
        frame_tree.setCurrentItem(item)
        self.refresh_var_tree()
        frame_code_lines, frame_code_lineno = inspect.getsourcelines(self.frame.f_code)
        terminal_input_text.setPlainText(''.join(frame_code_lines).strip('\n'))

    def action_double_click_history_tree_item(self, item: QTreeWidgetItem):
        history_tree: QTreeWidget = self.findChild(QTreeWidget, 'history_tree')
        terminal_input_text: CodeTextEdit = self.findChild(CodeTextEdit, 'terminal_input_text')
        item_is_top = True
        while True:
            if item.parent() is None:
                break
            else:
                item = item.parent()
                item_is_top = False
        index = item.data(0, Qt.UserRole)
        item.treeWidget().collapseAll()
        item.setExpanded(not item_is_top)
        history_tree.setCurrentItem(item)
        terminal_input_text.insertPlainText(self._execute_list[index].script)

    def expand_global_var_tree_item_to_show_dir(self, item: QTreeWidgetItem):
        global_var_full_switch: QCheckBox = self.findChild(QCheckBox, 'global_var_full_switch')
        expand_tree_item_to_show_dir(
            item,
            {
                0: lambda k, v: str(k),
                1: lambda k, v: type(v).__name__,
                2: lambda k, v: str(v),
            },
            show_all=global_var_full_switch.isChecked(),
        )

    def expand_local_var_tree_item_to_show_dir(self, item: QTreeWidgetItem):
        local_var_full_switch: QCheckBox = self.findChild(QCheckBox, 'local_var_full_switch')
        expand_tree_item_to_show_dir(
            item,
            {
                0: lambda k, v: str(k),
                1: lambda k, v: type(v).__name__,
                2: lambda k, v: str(v),
            },
            show_all=local_var_full_switch.isChecked(),
        )

    def expand_tree_item_to_show_dir(self, item: QTreeWidgetItem):
        expand_tree_item_to_show_dir(
            item,
            {
                0: lambda k, v: str(k),
                1: lambda k, v: type(v).__name__,
                2: lambda k, v: str(v),
            },
        )

    def action_click_terminal_button_enter(self):
        terminal_input_text: QTextEdit = self.findChild(QTextEdit, 'terminal_input_text')
        text = terminal_input_text.toPlainText()
        if self._current_execute:  # 如果已经有程序在运行了，那么先pass
            pass
        else:  # 如果没有程序在运行，那么就创建一个新的
            terminal_input_text.clear()
            execute = FrameExecute(text, self.frame, self._index)
            self._execute_list.append(execute)
            execute.signal_terminal_start.connect(self.action_frame_execute_terminal_start)
            execute.signal_terminal_end.connect(self.action_frame_execute_terminal_end)
            execute.signal_text_new.connect(self.action_frame_execute_text_new)
            execute.start()

    def action_frame_execute_terminal_start(self):
        self._current_execute = True

    def action_frame_execute_terminal_end(self):
        self._current_execute = False
        self.update_history_tree()

    def action_frame_execute_text_new(self, new_time, style, text):
        terminal_info_text: QTextEdit = self.findChild(QTextEdit, 'terminal_info_text')
        terminal_info_text.append(f'{change_time_float_to_str(new_time)} {style} {text}')
        terminal_info_text.repaint()
        QApplication.processEvents()
