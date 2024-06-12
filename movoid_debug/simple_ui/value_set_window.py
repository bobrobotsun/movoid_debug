#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : value_set_window
# Author        : Sun YiFan-Movoid
# Time          : 2024/6/9 23:13
# Description   : 
"""
import traceback

from PySide6.QtWidgets import QWidget, QGridLayout, QApplication, QRadioButton, QVBoxLayout, QTextEdit, QTreeWidget, QHBoxLayout, QPushButton, QMessageBox, QDialog, QTreeWidgetItem, QLabel


class KeySetWindow(QDialog):
    def __init__(self, ori_dict: dict, ori_key: str):
        super().__init__()
        self.ori_dict = ori_dict
        self.ori_key = str(ori_key)
        self.re_value = False
        self.init_ui()

    def init_ui(self):
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_rect.width() * 0.4), int(screen_rect.height() * 0.4), int(screen_rect.width() * 0.2), int(screen_rect.height() * 0.2))
        main_grid = QGridLayout(self)
        main_grid.setObjectName('main_grid')
        self.setLayout(main_grid)

        text = QLabel(self)
        text.setText(f'当前的key是【{self.ori_key}】，请输入你想要修改的值：')
        main_grid.addWidget(text, 0, 0)

        key_input = QTextEdit(self)
        key_input.setObjectName('key_input')
        key_input.setText(self.ori_key)
        main_grid.addWidget(key_input, 1, 0)

        end_widget = QWidget(self)
        main_grid.addWidget(end_widget, 2, 0)
        end_grid = QHBoxLayout(end_widget)
        end_widget.setLayout(end_grid)

        end_grid.addStretch(1)

        reset_button = QPushButton(end_widget)
        reset_button.setText('重置为默认')
        end_grid.addWidget(reset_button)
        reset_button.clicked.connect(lambda: self.action_reset())

        end_grid.addStretch(1)

        ok_button = QPushButton(end_widget)
        ok_button.setText('确定')
        end_grid.addWidget(ok_button)
        ok_button.clicked.connect(lambda: self.action_ok())

        cancel_button = QPushButton(end_widget)
        cancel_button.setText('取消')
        end_grid.addWidget(cancel_button)
        cancel_button.clicked.connect(lambda: self.action_cancel())

    def action_reset(self):
        key_input: QTextEdit = self.findChild(QTextEdit, 'key_input')  # noqa
        key_input.setText(self.ori_key)

    def action_ok(self):
        key_input: QTextEdit = self.findChild(QTextEdit, 'key_input')  # noqa
        temp_key = key_input.toPlainText()
        if temp_key == '':
            QMessageBox.critical(self, 'key不能为空!', '不可以把dict的key设置为空！')
        elif temp_key == self.ori_key:
            self.close()
        elif temp_key in self.ori_dict:
            QMessageBox.critical(self, 'key不能为重复!', f'你设置的key:{temp_key}已经存在，请重新设置')
        else:
            self.re_value = True
            value = self.ori_dict.pop(self.ori_key)
            self.ori_dict[temp_key] = value
            self.close()

    def action_cancel(self):
        self.close()

    @classmethod
    def get_value(cls, ori_dict: dict, ori_key: str):
        temp = KeySetWindow(ori_dict, ori_key)
        temp.show()
        temp.exec()
        return temp.re_value


class ValueSetWindow(QDialog):
    def __init__(self, ori_value):
        super().__init__()
        self.ori_value = ori_value
        self.get_value = lambda: ''
        self.re_value = self.ori_value
        self.args = []
        self.init_ui()
        self.init_ori_value()

    def init_ui(self):
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(int(screen_rect.width() * 0.3), int(screen_rect.height() * 0.3), int(screen_rect.width() * 0.4), int(screen_rect.height() * 0.4))
        main_grid = QGridLayout(self)
        main_grid.setObjectName('main_grid')
        self.setLayout(main_grid)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 4)
        main_grid.setRowStretch(0, 4)
        main_grid.setRowStretch(1, 1)

        input_widget = QWidget(self)
        main_grid.addWidget(input_widget, 0, 1)
        input_grid = QGridLayout(input_widget)
        input_widget.setLayout(input_grid)
        input_text = QTextEdit(input_widget)
        input_text.setObjectName('input_text')
        input_grid.addWidget(input_text, 0, 0)
        arg_tree = QTreeWidget(input_widget)
        arg_tree.setObjectName('arg_tree')
        arg_tree.setHeaderLabels(['from', 'name', 'type', 'value'])
        input_grid.addWidget(arg_tree, 0, 1)
        arg_tree.itemExpanded.connect(self.expand_tree_item_to_show_dir)

        type_widget = QWidget(self)
        main_grid.addWidget(type_widget, 0, 0)
        type_grid = QVBoxLayout(type_widget)
        type_widget.setLayout(type_grid)

        int_radio = QRadioButton(type_widget)
        int_radio.setObjectName('int_radio')
        type_grid.addWidget(int_radio, 0)
        int_radio.setText('int')
        int_radio.clicked.connect(lambda: self.radio_choose_int())

        float_radio = QRadioButton(type_widget)
        float_radio.setObjectName('float_radio')
        type_grid.addWidget(float_radio, 1)
        float_radio.setText('float')
        float_radio.clicked.connect(lambda: self.radio_choose_float())

        str_radio = QRadioButton(type_widget)
        str_radio.setObjectName('str_radio')
        type_grid.addWidget(str_radio, 0)
        str_radio.setText('str')
        str_radio.clicked.connect(lambda: self.radio_choose_str())

        list_radio = QRadioButton(type_widget)
        list_radio.setObjectName('list_radio')
        type_grid.addWidget(list_radio, 0)
        list_radio.setText('list')
        list_radio.clicked.connect(lambda: self.radio_choose_list())

        dict_radio = QRadioButton(type_widget)
        dict_radio.setObjectName('dict_radio')
        type_grid.addWidget(dict_radio, 0)
        dict_radio.setText('dict')
        dict_radio.clicked.connect(lambda: self.radio_choose_dict())

        true_radio = QRadioButton(type_widget)
        true_radio.setObjectName('true_radio')
        type_grid.addWidget(true_radio, 0)
        true_radio.setText('True')
        true_radio.clicked.connect(lambda: self.radio_choose_true())

        false_radio = QRadioButton(type_widget)
        false_radio.setObjectName('false_radio')
        type_grid.addWidget(false_radio, 0)
        false_radio.setText('False')
        false_radio.clicked.connect(lambda: self.radio_choose_false())

        none_radio = QRadioButton(type_widget)
        none_radio.setObjectName('none_radio')
        type_grid.addWidget(none_radio, 0)
        none_radio.setText('None')
        none_radio.clicked.connect(lambda: self.radio_choose_none())

        object_radio = QRadioButton(type_widget)
        object_radio.setObjectName('object_radio')
        type_grid.addWidget(object_radio, 0)
        object_radio.setText('object')
        object_radio.clicked.connect(lambda: self.radio_choose_object())

        type_grid.addStretch(1)

        end_widget = QWidget(self)
        main_grid.addWidget(end_widget, 1, 0, 1, 2)
        end_grid = QHBoxLayout(end_widget)
        end_widget.setLayout(end_grid)

        end_grid.addStretch(4)
        end_ok = QPushButton(self)
        end_ok.setText('OK')
        end_grid.addWidget(end_ok)
        end_ok.clicked.connect(lambda: self.end_ok())

        end_grid.addStretch(1)
        end_cancel = QPushButton(self)
        end_cancel.setText('Cancel')
        end_grid.addWidget(end_cancel)
        end_cancel.clicked.connect(lambda: self.end_cancel())

    def init_ori_value(self):
        ori_type = type(self.ori_value)
        if ori_type is int:
            self.radio_choose_int(self.ori_value)
        elif ori_type is float:
            self.radio_choose_float(self.ori_value)
        elif ori_type is str:
            self.radio_choose_str(self.ori_value)
        elif ori_type in (list, tuple, set):
            self.radio_choose_list(self.ori_value)
        elif ori_type is dict:
            self.radio_choose_dict(self.ori_value)
        elif self.ori_value is None:
            self.radio_choose_none()
        else:
            self.args.append(self.ori_value)
            self.radio_choose_object()

    def radio_choose_int(self, init_text=None):
        self.get_value = self._get_int
        self.input_text_show(init_text=init_text)
        radio: QRadioButton = self.findChild(QRadioButton, 'int_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_float(self, init_text=None):
        self.get_value = self._get_float
        self.input_text_show(init_text=init_text)
        radio: QRadioButton = self.findChild(QRadioButton, 'float_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_str(self, init_text=None):
        self.get_value = self._get_str
        self.input_text_show(init_text=init_text)
        radio: QRadioButton = self.findChild(QRadioButton, 'str_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_list(self, init_text=None):
        self.get_value = self._get_list
        self.input_text_show(init_text=init_text)
        radio: QRadioButton = self.findChild(QRadioButton, 'list_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_dict(self, init_text=None):
        self.get_value = self._get_dict
        self.input_text_show(init_text=init_text)
        radio: QRadioButton = self.findChild(QRadioButton, 'dict_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_true(self):
        self.get_value = lambda: True
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'true_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_false(self):
        self.get_value = lambda: False
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'false_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_none(self):
        self.get_value = lambda: None
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'none_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_object(self):
        self.get_value = self._get_object
        self.input_text_show('arg_tree')
        radio: QRadioButton = self.findChild(QRadioButton, 'object_radio')  # noqa
        radio.setChecked(True)

    def input_text_show(self, object_name='input_text', init_text=None):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        arg_tree.setVisible(False)
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        input_text.setVisible(False)
        if object_name == 'input_text':
            input_text.setVisible(True)
            input_text.clear()
            if init_text:
                input_text.setText(str(init_text))
        elif object_name == 'arg_tree':
            arg_tree.setVisible(True)
            self.refresh_arg_tree()

    def refresh_arg_tree(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        arg_tree.clear()
        global_value = globals()
        for i in self.args:
            temp = QTreeWidgetItem(arg_tree)
            temp.setText(0, 'ori')
            temp.setText(2, type(i).__name__)
            temp.setText(3, str(i))
            setattr(temp, '__tree_object', i)
            arg_tree.setCurrentItem(temp)
            tree_item_can_expand(temp)
        for k, v in global_value.items():
            if not k.startswith('__'):
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(1, str(k))
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)

    def end_ok(self):
        try:
            self.re_value = self.get_value()
        except Exception:
            QMessageBox.critical(self, '获取值错误!', traceback.format_exc())
        else:
            self.done(0)

    def end_cancel(self):
        self.re_value = self.ori_value
        self.done(1)

    def _get_int(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        re_value = int(input_text.toPlainText())
        return re_value

    def _get_float(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        re_value = float(input_text.toPlainText())
        return re_value

    def _get_str(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        re_value = str(input_text.toPlainText())
        return re_value

    def _get_list(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        re_value = list(eval(input_text.toPlainText()))
        return re_value

    def _get_dict(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        re_value = dict(eval(input_text.toPlainText()))
        return re_value

    def _get_object(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        tar_arg = arg_tree.currentItem()
        return getattr(tar_arg, '__tree_object')

    def get_re_value(self):
        print('func', self, self.re_value)
        return self.re_value

    @classmethod
    def get_value(cls, ori_value):
        temp = ValueSetWindow(ori_value)
        temp.show()
        temp.exec()
        return temp.re_value

    @staticmethod
    def expand_tree_item_to_show_dir(item):
        expand_tree_item_to_show_dir(item, {
            1: lambda k, v: str(k),
            2: lambda k, v: type(v).__name__,
            3: lambda k, v: str(v),
        })


def tree_item_can_expand(item):
    value = getattr(item, '__tree_object')
    if type(value) in (int, float, bool, str, list, dict) or value is None:
        setattr(item, '__expand', False)
    else:
        temp = QTreeWidgetItem(item)
        setattr(temp, '__delete', True)


def expand_tree_item_to_show_dir(item: QTreeWidgetItem, show_dict: dict):
    if getattr(item, '__expand', True):
        for i in range(item.childCount() - 1, -1, -1):
            tar_item = item.child(i)
            if getattr(tar_item, '__delete'):
                item.removeChild(tar_item)
        value = getattr(item, '__tree_object')
        for k in dir(value):
            if not k.startswith('__'):
                v = getattr(value, k)
                if not callable(v):
                    temp = QTreeWidgetItem(item)
                    for k2, v2 in show_dict.items():
                        temp.setText(int(k2), v2(k, v))
                    setattr(temp, '__tree_object', v)
                    tree_item_can_expand(temp)
