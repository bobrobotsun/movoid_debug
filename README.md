这个是一系列函数、类的装饰器，在运行时，如果报错，那么将会进入调试状态
默认情况下：
- 1：将所有Exception raise 出去，不做任何处理
- 2：将Exception保存下来，可以在任意的地方调用某个方法抛出

debug状态下： 
- 0：直接进入debug模式，弹出窗口，并进行操作
- 1：将所有Exception raise 出去，不做任何处理
- 2：将Exception保存下来，可以在任意的地方调用某个方法抛出

# 启动方法
## 命令行
在命令行运行python脚本时，可以在命令行中额外输入`__debug=1`或`__debug=debug`来启动debug状态，其他指令均为默认情况
## 代码
在代码中可以通过以下方式来直接开启debug模式
```
from movoid_debug import FLOW
FLOW.debug_type=1
```
