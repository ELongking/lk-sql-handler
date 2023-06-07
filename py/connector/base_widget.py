from PyQt5.QtGui import QStandardItem, QPainter, QFont
from PyQt5.QtCore import Qt, QRect, QSize, QPoint
from PyQt5.QtWidgets import QTextEdit, QComboBox, QButtonGroup, QCheckBox, QWidget
from .type_enum import *


class DataItem(QStandardItem):
    def __init__(self, data: str, info: dict):
        super(DataItem, self).__init__()
        self.data = data
        self.info = info
        self.type_items = TYPE_NAMES
        self._init_data()

    def _init_data(self):
        self.setText(self.data)

    def set_data(self, data):
        self.setText(data)

    def export_data(self):
        res = self.data
        t_val = self.info["type"]

        if "(" in t_val:
            length = t_val[t_val.index("(") + 1: -1]
            t_val = t_val[:t_val.index("(")]
            assert int(length) * 0 == 0
            assert t_val in self.type_items

        if NAME2TYPE[t_val]["type"] == "str":
            res = f"'{self.data}'"
        elif NAME2TYPE[t_val]["type"] == "time":
            if res.lower() == "now":
                res = res + "()"

        return res


class ItemCombo(QComboBox):
    def __init__(self, func, index: tuple, items: list, conn=False):
        super(ItemCombo, self).__init__()
        self.func = func
        self.index = index
        self.addItems(items)
        if conn:
            self.conn_enabled()
        else:
            self.conn_disabled()

    def conn_enabled(self):
        self.currentIndexChanged.connect(self.func)

    def conn_disabled(self):
        try:
            self.currentIndexChanged.disconnect()
        except:
            pass


class PriCheck(QCheckBox):
    def __init__(self, row, col):
        super(PriCheck, self).__init__()
        self.index = (row, col)
        self.setTristate(True)


class PriCheckGroup(QButtonGroup):
    def __init__(self, func):
        super(PriCheckGroup, self).__init__()
        self.num = 0
        self.func = func
        self.conn_disabled()

    def add_button(self, check: QCheckBox):
        self.addButton(check, self.num)
        self.num += 1

    def conn_enabled(self):
        self.buttonClicked.connect(self.func)

    def conn_disabled(self):
        try:
            self.buttonClicked.disconnect()
        except:
            pass


class QTextEditWithLineNum(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Times New Roman", 14, 1))
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.lineNumberArea = LineNumPaint(self)
        self.document().blockCountChanged.connect(self.update_line_num_width)
        self.verticalScrollBar().valueChanged.connect(self.lineNumberArea.update)
        self.textChanged.connect(self.lineNumberArea.update)
        self.cursorPositionChanged.connect(self.lineNumberArea.update)
        self.update_line_num_width()

    def set_line_number_area_width(self):
        block_count = self.document().blockCount()
        max_value = max(1, block_count)
        d_count = len(str(max_value))
        _width = self.fontMetrics().width('9') * d_count + 5
        return _width

    def update_line_num_width(self):
        self.setViewportMargins(self.set_line_number_area_width(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.set_line_number_area_width(), cr.height()))

    def set_line_area_paint_event(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        first_visible_block_number = self.cursorForPosition(QPoint(0, 1)).blockNumber()
        block_number = first_visible_block_number
        block = self.document().findBlockByNumber(block_number)
        top = self.viewport().geometry().top()
        if block_number == 0:
            additional_margin = int(self.document().documentMargin() - 1 - self.verticalScrollBar().sliderPosition())
        else:
            prev_block = self.document().findBlockByNumber(block_number - 1)
            additional_margin = int(self.document().documentLayout().blockBoundingRect(
                prev_block).bottom()) - self.verticalScrollBar().sliderPosition()
        top += additional_margin
        bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
        last_block_number = self.cursorForPosition(QPoint(0, self.height() - 1)).blockNumber()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()) and block_number <= last_block_number:
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
            block_number += 1


class LineNumPaint(QWidget):
    def __init__(self, q_edit):
        super().__init__(q_edit)
        self.q_edit_line_num = q_edit

    def sizeHint(self):
        return QSize(self.q_edit_line_num.set_line_number_area_width(), 0)

    def paintEvent(self, event):
        self.q_edit_line_num.set_line_area_paint_event(event)
