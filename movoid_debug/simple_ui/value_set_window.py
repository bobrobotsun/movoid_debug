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

from .basic import tree_item_can_expand, expand_tree_item_to_show_dir


class KeySetWindow(QDialog):
    def __init__(self, ori_dict: dict, ori_key: str, parent=None):
        super().__init__(parent=parent)
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
    def get_value(cls, ori_dict: dict, ori_key: str, parent=None):
        temp = KeySetWindow(ori_dict, ori_key, parent=parent)
        temp.show()
        temp.exec()
        return temp.re_value


class ValueSetWindow(QDialog):
    def __init__(self, ori_value, parent=None):
        super().__init__(parent=parent)
        self.ori_value = ori_value
        self.re_value = self.ori_value
        self.args = []
        self.select_type = ''
        self.temp_input = {
            'str': '',
            'int': '',
            'float': '',
            'list': '',
            'dict': '',
            'eval': '',
        }
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

        global_local_radio = QRadioButton(type_widget)
        global_local_radio.setObjectName('global_local_radio')
        type_grid.addWidget(global_local_radio, 0)
        global_local_radio.setText('global & local')
        global_local_radio.clicked.connect(lambda: self.radio_choose_global_local())

        eval_radio = QRadioButton(type_widget)
        eval_radio.setObjectName('eval_radio')
        type_grid.addWidget(eval_radio, 0)
        eval_radio.setText('eval_object')
        eval_radio.clicked.connect(lambda: self.radio_choose_eval())

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
        self.ori_type = type(self.ori_value)
        self.temp_input['eval'] = repr(self.ori_value)
        if self.ori_type is int:
            self.temp_input['int'] = str(self.ori_value)
            self.radio_choose_int()
        elif self.ori_type is float:
            self.temp_input['float'] = str(self.ori_value)
            self.radio_choose_float()
        elif self.ori_type is str:
            self.temp_input['str'] = str(self.ori_value)
            self.radio_choose_str()
        elif self.ori_type is list:
            self.temp_input['list'] = str(self.ori_value)
            self.radio_choose_list()
        elif self.ori_type is dict:
            self.temp_input['dict'] = str(self.ori_value)
            self.radio_choose_dict()
        elif self.ori_value is None:
            self.radio_choose_none()
        else:
            self.radio_choose_eval()

    def radio_choose_setup(self):
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        input_str = input_text.toPlainText()
        if self.select_type == 'int':
            self.temp_input['int'] = input_str
        elif self.select_type == 'float':
            self.temp_input['float'] = input_str
        elif self.select_type == 'str':
            self.temp_input['str'] = input_str
        elif self.select_type == 'list':
            self.temp_input['list'] = input_str
        elif self.select_type == 'dict':
            self.temp_input['dict'] = input_str
        elif self.select_type == 'eval':
            self.temp_input['eval'] = input_str

    def radio_choose_int(self):
        self.radio_choose_setup()
        self.select_type = 'int'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'int_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_float(self):
        self.radio_choose_setup()
        self.select_type = 'float'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'float_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_str(self):
        self.radio_choose_setup()
        self.select_type = 'str'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'str_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_list(self):
        self.radio_choose_setup()
        self.select_type = 'list'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'list_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_dict(self):
        self.radio_choose_setup()
        self.select_type = 'dict'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'dict_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_true(self):
        self.radio_choose_setup()
        self.select_type = 'true'
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'true_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_false(self):
        self.radio_choose_setup()
        self.select_type = 'false'
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'false_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_none(self):
        self.radio_choose_setup()
        self.select_type = 'none'
        self.input_text_show('')
        radio: QRadioButton = self.findChild(QRadioButton, 'none_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_global_local(self):
        self.radio_choose_setup()
        self.select_type = 'global_local'
        self.input_text_show('arg_tree')
        radio: QRadioButton = self.findChild(QRadioButton, 'global_local_radio')  # noqa
        radio.setChecked(True)

    def radio_choose_eval(self):
        self.radio_choose_setup()
        self.select_type = 'eval'
        self.input_text_show()
        radio: QRadioButton = self.findChild(QRadioButton, 'eval_radio')  # noqa
        radio.setChecked(True)

    def input_text_show(self, object_name='input_text'):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        arg_tree.setVisible(False)
        input_text: QTextEdit = self.findChild(QTextEdit, 'input_text')  # noqa
        input_text.setVisible(False)
        if object_name == 'input_text':
            input_text.setVisible(True)
            input_text.clear()
            input_text.setText(self.temp_input.get(self.select_type, ''))
        elif object_name == 'arg_tree':
            arg_tree.setVisible(True)
            self.refresh_arg_tree()

    def refresh_arg_tree(self):
        arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
        arg_tree.clear()
        global_value = self.parent().flow.error_frame.frame.f_globals
        local_value = self.parent().flow.error_frame.frame.f_locals
        temp = QTreeWidgetItem(arg_tree)
        temp.setText(0, 'ori')
        temp.setText(2, type(self.ori_value).__name__)
        temp.setText(3, str(self.ori_value))
        setattr(temp, '__tree_object', self.ori_value)
        arg_tree.setCurrentItem(temp)
        tree_item_can_expand(temp)
        for k, v in {**global_value, **local_value}.items():
            if not k.startswith('__'):
                temp = QTreeWidgetItem(arg_tree)
                temp.setText(1, str(k))
                temp.setText(2, type(v).__name__)
                temp.setText(3, str(v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)

    def end_ok(self):
        try:
            self.re_value = self.get_return()
        except Exception:
            QMessageBox.critical(self, '获取值错误!', traceback.format_exc())
        else:
            self.done(0)

    def end_cancel(self):
        self.re_value = self.ori_value
        self.done(1)

    def get_return(self):
        self.radio_choose_setup()
        if self.select_type == 'int':
            return int(self.temp_input['int'])
        elif self.select_type == 'float':
            return float(self.temp_input['float'])
        elif self.select_type == 'str':
            return str(self.temp_input['str'])
        elif self.select_type == 'list':
            return list(eval(self.temp_input['list'], self.parent().flow.error_frame.frame.f_globals, self.parent().flow.error_frame.frame.f_locals))
        elif self.select_type == 'dict':
            return dict(eval(self.temp_input['dict'], self.parent().flow.error_frame.frame.f_globals, self.parent().flow.error_frame.frame.f_locals))
        elif self.select_type == 'eval':
            return eval(self.temp_input['eval'], self.parent().flow.error_frame.frame.f_globals, self.parent().flow.error_frame.frame.f_locals)
        elif self.select_type == 'none':
            return None
        elif self.select_type == 'true':
            return True
        elif self.select_type == 'false':
            return False
        elif self.select_type == 'global_local':
            arg_tree: QTreeWidget = self.findChild(QTreeWidget, 'arg_tree')  # noqa
            tar_arg = arg_tree.currentItem()
            return getattr(tar_arg, '__tree_object')
        else:
            raise Exception(f'error select type:{self.select_type}')

    @classmethod
    def get_value(cls, ori_value, parent=None):
        temp = ValueSetWindow(ori_value, parent=parent)
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
