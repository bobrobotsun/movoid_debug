#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Version: 3.8.10
Creator:        sunyifan0649
Create Date:    2024/5/20
Description:    
"""
import inspect
import traceback
from tkinter import Tk, Label, Text, Button, END

from movoid_function import wraps


class SimpleHotPause:
    def __init__(self):
        pass

    def pause(self):
        self.end = 'skip'
        self.tk = Tk()
        self.tk.geometry('1024x768+120+80')
        self.label1 = Label(self.tk, text='错误信息')
        self.label1.grid(row=0, column=0, columnspan=10)
        self.text1 = Text(self.tk, width=80)
        self.text1.grid(row=1, column=0, columnspan=10)
        self.label2 = Label(self.tk, text='重新执行的结果')
        self.label2.grid(row=0, column=10, columnspan=10)
        self.text2 = Text(self.tk, width=80)
        self.text2.grid(row=1, column=10, columnspan=10)
        self.label3 = Label(self.tk, text='重新执行的参数')
        self.label3.grid(row=2, column=0)
        self.text3 = Text(self.tk, height=2, width=140)
        self.text3.grid(row=2, column=1, columnspan=19)
        self.button1 = Button(self.tk, text="重新执行", command=self.pause_rerun)
        self.button1.grid(row=3, column=0)
        self.button2 = Button(self.tk, text="跳过步骤", command=self.pause_skip)
        self.button2.grid(row=3, column=10)
        self.button3 = Button(self.tk, text="报错退出", command=self.pause_error)
        self.button3.grid(row=3, column=12)
        self.text1.insert(END, f'args:{self.args}\n')
        self.text1.insert(END, f'kwargs:{self.kwargs}\n')
        self.text1.insert(END, traceback.format_exc())
        self.tk.mainloop()
        if self.end == 'error':
            raise self.error

    def pause_rerun(self):
        text = [_.strip() for _ in self.text3.get(1.0, END).split(',')]
        args = []
        param_keys = list(inspect.signature(self.func).parameters.keys())
        if len(param_keys) > 0 and param_keys[0] in ('self', 'cls') and len(self.args) > 0:
            args.append(self.args[0])
        kwargs = {}
        for index, text_arg in enumerate(text):
            if '=' in text_arg:
                key, value = text_arg.split('=', 1)
                kwargs[key] = self.analyse_text(value)
            elif text_arg:
                args.append(self.analyse_text(text_arg))
        try:
            re_value = self.func(*args, **kwargs)
        except:
            self.text2.delete(1.0, END)
            self.text2.insert(1.0, '执行失败！\n')
            self.text2.insert(END, f'args:{args}\n')
            self.text2.insert(END, f'kwargs:{kwargs}\n')
            self.text2.insert(END, traceback.format_exc())
        else:
            self.text2.delete(1.0, END)
            self.text2.insert(1.0, f'执行成功！\nargs:{args}\nkwargs:{kwargs}\n返回值：{re_value}')

    def analyse_text(self, text: str):
        if text.startswith('"') and text.endswith('"'):
            re_value = text[1:-1]
        elif text.startswith("'") and text.endswith("'"):
            re_value = text[1:-1]
        elif text.lower() in ['true']:
            re_value = True
        elif text.lower() in ['false']:
            re_value = False
        elif text.lower() in ['none', 'null']:
            re_value = None
        else:
            try:
                re_value = int(text)
            except:
                try:
                    re_value = float(text)
                except:
                    re_value = text
        return re_value

    def pause_skip(self):
        self.end = 'skip'
        self.tk.destroy()

    def pause_error(self):
        self.end = 'error'
        self.tk.destroy()

    def class_register(self, hot_pause=True, except_function=None):
        except_function = [] if except_function is None else list(except_function)

        def dec(clazz: type):
            for key in dir(clazz):
                element = getattr(clazz, key)
                if inspect.isfunction(element) and not key.startswith('__') and key not in except_function:
                    setattr(clazz, key, self.function_register(hot_pause)(element))
            return clazz

        return dec

    def function_register(self, hot_pause=True):
        if isinstance(hot_pause, bool):
            def dec(func):
                @wraps(func)
                def wrapping(*args, **kwargs):
                    try:
                        re_value = func(*args, **kwargs)
                    except Exception as err:
                        if getattr(wrapping, 'hot_pause', False):
                            self.func = func
                            self.args = args
                            self.kwargs = kwargs
                            self.error = err
                            self.pause()
                        else:
                            raise err
                    else:
                        return re_value

                setattr(wrapping, 'hot_pause', hot_pause)
                return wrapping

            return dec
        else:
            return self.function_register()(hot_pause)

    def function_reset(self, hot_pause=False):
        """
        如果使用了class_register，但是部分函数又不需要这个功能，那就重新删除掉就行了
        """
        if isinstance(hot_pause, bool):
            def dec(func):
                setattr(func, 'hot_pause', hot_pause)
                return func

            return dec
        else:
            return self.function_reset()(hot_pause)


HOT_PAUSE = SimpleHotPause()
