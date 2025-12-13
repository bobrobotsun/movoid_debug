from movoid_function import STACK
from movoid_debug import *


class Test_class_Stack:
    def test_01_STACK_initial_ignore_list(self):
        assert len(STACK.ignore_list) == 12
        STACK.self_check()

    def test_01_01_STACK_ui_ignore_list(self):
        from movoid_debug import simple_ui
        assert len(STACK.ignore_list) == 13
        STACK.self_check()
