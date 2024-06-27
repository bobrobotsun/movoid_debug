#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/6/21
Description:    
"""
import inspect
import pathlib
import re
import traceback
from types import CodeType, FrameType
from typing import List, Tuple


class Code:
    FUNCTION = 'function'
    CLASS_FUNCTION = 'class_function'
    GETTER = 'getter'
    SETTER = 'setter'
    DELETER = 'deleter'

    def __init__(self, code: CodeType, frame: FrameType = None):
        self._frame = frame
        self._code: CodeType = code
        self._style = self.FUNCTION
        self._style_info = {}
        self._change_list = []
        self.init()

    @property
    def id(self):
        return id(self._code)

    @property
    def code(self):
        return self._code

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        value = value.lowert()
        if value in (self.FUNCTION, self.CLASS_FUNCTION, self.GETTER, self.SETTER, self.DELETER):
            self._style = value
        else:
            self._style = self.FUNCTION

    def init(self):
        self._analyse_ori_source_file()
        self._find_code_in_frame()

    def _analyse_ori_source_file(self):
        source_lines = inspect.getsourcelines(self._code)
        pure_lines, start_blank = self._get_pure_source_lines_and_blank()
        pure_text = ''.join(pure_lines).strip('\n')
        if start_blank:
            ori_path = pathlib.Path(self._code.co_filename)
            with ori_path.open(mode='r', encoding='utf8') as f:
                file_lines = f.readlines()
            lineno = source_lines[1]
            for i in range(lineno - 1, -1, -1):
                line_text = file_lines[i]
                if len(line_text) > len(start_blank) and line_text.startswith(start_blank):
                    continue
                elif line_text != '\n':
                    pure_line_text = line_text
                    while pure_line_text.startswith(' ') or pure_line_text.startswith('\t'):
                        pure_line_text = pure_line_text[1:]
                    if pure_line_text.startswith('class'):
                        re_result = re.match(r'class (.*)[(:]', pure_line_text)
                        if re_result:
                            self._style_info['class_name'] = re_result.group(1)
                        for line in pure_lines:
                            if line.startswith('@'):
                                if line.startswith('@property'):
                                    self._style = self.GETTER
                                    break
                                elif re.match(r'@.*\.getter$', line):
                                    self._style = self.GETTER
                                    break
                                elif re.match(r'@.*\.setter$', line):
                                    self._style = self.SETTER
                                    break
                                elif re.match(r'@.*\.deleter$', line):
                                    self._style = self.DELETER
                                    break
                        else:
                            self._style = self.CLASS_FUNCTION
                    else:
                        self._style = self.FUNCTION
                    break
            else:
                self._style = self.FUNCTION
        else:
            self._style = self.FUNCTION
        self._change_list = [self.id, self.code, pure_text, -1]

    def _get_pure_source_lines_and_blank(self) -> Tuple[List[str], str]:
        lines = inspect.getsourcelines(self._code)[0]
        first_line = lines[0]
        start_blank = ''
        for i in first_line:
            if i in (' ', '\t'):
                start_blank += i
            else:
                break
        blank_len = len(start_blank)
        for index, line in enumerate(lines):
            if line.startswith(start_blank):
                lines[index] = line[blank_len:]
            elif len(line) - 1 < blank_len:
                lines[index] = '\n'
            else:
                raise SyntaxError(f'目标行异常，应当以【{start_blank}】起始，但是其为【{line}】')
        return lines, start_blank

    def _find_code_in_frame(self):
        if self._frame is not None:
            if self._style == self.FUNCTION:
                if self._code.co_name in self._frame.f_globals and self._frame.f_globals[self._code.co_name].__code__ == self._code:
                    self._style_info['target'] = [('attr', 'f_globals'), ('key', self._code.co_name)]
                else:
                    for k, v in self._frame.f_globals.items():
                        if hasattr(v, '__code__') and getattr(v, '__code__') == self._code:
                            self._style_info['target'] = [('attr', 'f_globals'), ('key', k)]
            elif self._style in [self.CLASS_FUNCTION, self.GETTER, self.SETTER, self.DELETER]:
                class_name = self._style_info.get('class_name')
                tar_class_list = []
                if class_name and class_name in self._frame.f_globals:
                    tar_class_list.append([class_name, self._frame.f_globals[class_name]])
                for k, v in self._frame.f_globals.items():
                    if inspect.isclass(v) and k != class_name:
                        tar_class_list.append([k, v])
                for class_name, tar_class in tar_class_list:
                    tar_func_list = []
                    if hasattr(tar_class, self._code.co_name):
                        tar_func_list.append([self._code.co_name, getattr(tar_class, self._code.co_name)])
                    for i in dir(tar_class):
                        v = getattr(tar_class, i)
                        tar_func_list.append([i, v])
                    for func_name, tar_func in tar_func_list:
                        if self._style == self.CLASS_FUNCTION and hasattr(tar_func, '__code__') and tar_func.__code__ == self._code:
                            self._style_info['target'] = [('attr', 'f_globals'), ('key', class_name), ('attr', func_name)]
                            break
                        elif self._style == self.GETTER and hasattr(tar_func, 'fget') and hasattr(tar_func.fget, '__code__') and tar_func.fget.__code__ == self._code:
                            self._style_info['target'] = [('attr', 'f_globals'), ('key', class_name), ('attr', func_name)]
                            break
                        elif self._style == self.SETTER and hasattr(tar_func, 'fset') and hasattr(tar_func.fset, '__code__') and tar_func.fset.__code__ == self._code:
                            self._style_info['target'] = [('attr', 'f_globals'), ('key', class_name), ('attr', func_name)]
                            break
                        elif self._style == self.DELETER and hasattr(tar_func, 'fdel') and hasattr(tar_func.fdel, '__code__') and tar_func.fdel.__code__ == self._code:
                            self._style_info['target'] = [('attr', 'f_globals'), ('key', class_name), ('attr', func_name)]
                            break
                    if self._style_info.get('target'):
                        break

    def replace_by_new_text(self, new_function):
        if self._style_info.get('target'):
            try:
                exec(new_function, self._frame.f_globals, self._frame.f_locals)
                re_func_name = re.search(r'def (.*)\(', new_function)
                if re_func_name:
                    func_name = re_func_name.group(1)
                    func = self._frame.f_locals.get(func_name)
                    func_code = func.__code__
                    target_list = self._style_info['target']
                    if self._style in (self.FUNCTION, self.CLASS_FUNCTION):
                        new_value = func
                    else:
                        new_value = self._get_value_from_frame(target_list)
                        if self._style == self.GETTER:
                            new_value = new_value.getter(func)
                        elif self._style == self.SETTER:
                            new_value = new_value.setter(func)
                        elif self._style == self.DELETER:
                            new_value = new_value.deleter(func)
                        else:
                            raise Exception(f'不存在这样的类型：{self._style}')
                    self._set_value_from_frame(target_list, new_value)
                else:
                    raise Exception('错误的代码')
            except Exception as err:
                traceback.print_exc()
            else:
                self._change_list.append([id(func_code), func_code, new_function, -1])
        else:
            raise Exception('没有找到有效替代项，请重新设置替代目标')

    def _get_value_from_frame(self, key_list):
        temp = self._frame
        for son_type, son_key in key_list:
            if son_type == 'attr':
                temp = getattr(temp, son_key)
            elif son_type == 'key':
                temp = temp[son_key]
        return temp

    def _set_value_from_frame(self, key_list, value):
        temp = self._get_value_from_frame(key_list[:-1])
        son_type, son_key = key_list[-1]
        if son_type == 'attr':
            setattr(temp, son_key, value)
        elif son_type == 'key':
            temp[son_key] = value

    def replace_by_old_func(self, index):
        index = max(0, min(len(self._change_list) - 1, int(index)))
        self._change_list.append(self._change_list[:3] + [index])


class CodeHistory:
    def __init__(self):
        self.code_dict = {}
