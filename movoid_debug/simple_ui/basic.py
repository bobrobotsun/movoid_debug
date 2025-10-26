#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : basic
# Author        : Sun YiFan-Movoid
# Time          : 2025/10/22 10:30
# Description   : 
"""
import time
from datetime import datetime

from PySide6.QtCore import Signal, QSize, QRect
from PySide6.QtGui import QPainter, QColor, Qt, QTextFormat
from PySide6.QtWidgets import QMainWindow, QDialog, QTreeWidgetItem, QWidget, QTextEdit


class BasicMainWindow(QMainWindow):
    signal_close = Signal(QMainWindow)

    def closeEvent(self, event):
        self.signal_close.emit(self)
        event.accept()


class BasicDialog(QDialog):
    pass


def change_time_float_to_str(date_time: datetime, formmat="%Y-%m-%d %H:%M:%S.%f"):
    return date_time.strftime(formmat)


def tree_item_can_expand(item):
    value = getattr(item, '__tree_object')
    if type(value) in (int, float, bool, str, list, dict, tuple, set) or value is None:
        setattr(item, '__expand', False)
    else:
        temp = QTreeWidgetItem(item)
        setattr(temp, '__delete', True)


def expand_tree_item_to_show_dir(item: QTreeWidgetItem, show_dict: dict, show_all: bool = False):
    if getattr(item, '__expand', True):
        for i in range(item.childCount() - 1, -1, -1):
            tar_item = item.child(i)
            if getattr(tar_item, '__delete'):
                item.removeChild(tar_item)
        value = getattr(item, '__tree_object')
        count = 0
        for k in dir(value):
            if show_all or (not (k.startswith('__') and k.endswith('__'))):
                v = getattr(value, k)
                temp = QTreeWidgetItem(item)
                for k2, v2 in show_dict.items():
                    temp.setText(int(k2), v2(k, v))
                setattr(temp, '__tree_object', v)
                tree_item_can_expand(temp)
                count += 1
        if count == 0:
            temp = QTreeWidgetItem(item)
            temp.setText(0, 'no attribute')


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(240, 240, 240))  # 背景色
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.darkGray)
                # 绘制行号，右对齐
                painter.drawText(0, top, self.width() - 2, self.editor.fontMetrics().height(),
                                 Qt.AlignRight, str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1


class QTextEditWithLineNum(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth()

    def lineNumberAreaWidth(self):
        digits = 1
        max_lines = max(1, self.blockCount())
        while max_lines >= 10:
            max_lines //= 10
            digits += 1
        return 3 + self.fontMetrics().horizontalAdvance('9') * digits

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
        self.append()

    def highlightCurrentLine(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = self.ExtraSelection()
            line_color = QColor(Qt.blue).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
