from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QComboBox, QButtonGroup, QCheckBox
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
