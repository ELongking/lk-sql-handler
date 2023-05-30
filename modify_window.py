from PyQt5 import QtWidgets, QtGui, QtCore
from connector.init_conn import SqlConn
from connector.utils import *
import connector.type_enum as te


class ItemCombo(QtWidgets.QComboBox):
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


class BaseTable(QtWidgets.QTableView):
    def __init__(self, parent):
        super(BaseTable, self).__init__(parent=parent)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setShowGrid(True)
        self.tmodel = QtGui.QStandardItemModel()


class InfoTable(BaseTable):
    def __init__(self, handle: SqlConn, parent):
        super(InfoTable, self).__init__(parent=parent)
        self.handle = handle
        self.parent = parent

        self.info = dict()
        self.labels = []

    def init_table(self, info: dict):
        type_items = [k for k in te.NAME2TYPE.keys()]
        self.info = info
        self.labels = [self.info[i]["field"] for i in range(self.info["sum"])]
        labels = list(info[0].keys())
        labels.insert(2, "<length>")

        self.tmodel = QtGui.QStandardItemModel(info["sum"], len(labels))
        self.tmodel.setHorizontalHeaderLabels(labels)
        self.setModel(self.tmodel)

        for row in range(info["sum"]):
            for col in range(len(labels)):
                if col == 2:
                    pass
                else:
                    value = str(info[row][labels[col]])
                    if col == 1:
                        ans_box = ItemCombo(func=self._inside_combo_changed, index=(row, col), items=type_items)
                        if "(" in value:
                            length = value[value.index("(") + 1: -1]
                            value = value[:value.index("(")]
                            assert int(length) * 0 == 0
                            assert value in type_items
                        else:
                            length = ""
                        ans_box.setCurrentText(value)
                        ans_box.conn_enabled()
                        self.setIndexWidget(self.tmodel.index(row, 1), ans_box)

                        item = QtGui.QStandardItem(str(length))
                        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        self.tmodel.setItem(row, 2, item)
                    elif col == 3:
                        ans_box = ItemCombo(func=self._inside_combo_changed, index=(row, col), items=["YES", "NO"])
                        ans_box.setCurrentText(value)
                        ans_box.conn_enabled()
                        self.setIndexWidget(self.tmodel.index(row, 3), ans_box)
                    elif col == 4:
                        ans_box = ItemCombo(func=self._inside_combo_changed, index=(row, col), items=["None", "PRI"])
                        ans_box.setCurrentText(value)
                        ans_box.conn_enabled()
                        self.setIndexWidget(self.tmodel.index(row, 4), ans_box)
                    elif col == 6:
                        ans_box = ItemCombo(func=self._inside_combo_changed,
                                            index=(row, col),
                                            items=["None", "auto_increment", "on update CURRENT_TIMESTAMP"])
                        ans_box.setCurrentText(value)
                        ans_box.conn_enabled()
                        self.setIndexWidget(self.tmodel.index(row, 6), ans_box)
                    else:
                        item = QtGui.QStandardItem(value)
                        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        self.tmodel.setItem(row, col, item)

        self.tmodel.itemChanged.connect(self._item_changed)

    def insert_row(self):
        now_idx = self.info["sum"] - 1
        selected_index = self.selectionModel().selectedRows()
        assert len(selected_index) <= 1
        if len(selected_index) == 0:
            pass
        elif len(selected_index) == 1:
            now_idx = selected_index[0].row()
        else:
            raise ValueError

        now_label = self.info[now_idx]["field"]
        return now_idx, now_label

    def _item_changed(self, item):
        old_data = item.data()
        row, col = item.row(), item.column()
        assert col in [0, 2, 5]
        col2desc = {0: "field", 1: "type", 2: "type", 3: "isnull", 4: "key", 5: "default", 6: "extra"}
        data = [self.labels[row]]

        if col == 2:
            new_data = self.indexWidget(
                self.tmodel.index(row, 1)).currentText() + f"({self.tmodel.index(row, col).data()})"
        else:
            new_data = self.tmodel.index(row, col).data()
        data.append(new_data)

        flag, msg = self.handle.alter(db=self.info["db"], tb=self.info["tb"], data=data, mode=col2desc[col])
        if flag:
            pass
        else:
            self.tmodel.itemChanged.disconnect()
            self.tmodel.setItem(row, col, QtGui.QStandardItem(old_data))
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)
            self.tmodel.itemChanged.connect(self._item_changed)

    def _inside_combo_changed(self, index):
        sender = self.sender()
        row, col = sender.index
        assert col in [1, 3, 4, 6]
        col2desc = {0: "field", 1: "type", 2: "type", 3: "isnull", 4: "key", 5: "default", 6: "extra"}
        data = [self.labels[row]]

        if col in [3, 4, 6]:
            new_data = self.indexWidget(self.tmodel.index(row, col)).currentText()
            if col == 6:
                if new_data == "None":
                    new_data = self.indexWidget(self.tmodel.index(row, 1)).currentText()
        else:
            self.tmodel.itemChanged.disconnect()
            new_data = self.indexWidget(self.tmodel.index(row, col)).currentText()
            self.tmodel.setItem(row, 2, QtGui.QStandardItem(""))
            self.tmodel.itemChanged.connect(self._item_changed)

        data.append(new_data)
        flag, msg = self.handle.alter(db=self.info["db"], tb=self.info["tb"], data=data, mode=col2desc[col])
        if flag:
            pass
        else:
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)

    def delete_row(self):
        try:
            row = self.currentIndex().row()
            data = self.tmodel.index(row, 0).data()
            self.tmodel.removeRow(row)
            return data
        except:
            QtWidgets.QMessageBox.warning(self.parent, "Notice", "Have not selected row")


class DataTable(BaseTable):
    def __init__(self, handle: SqlConn, parent):
        super(DataTable, self).__init__(parent=parent)
        self.handle = handle
        self.parent = parent

        self.info = dict()
        self.labels = []
        self.not_pkeys = []
        self.pkeys = []

    def generate_part(self):
        if self.info:
            self.labels = [self.info[i]["field"] for i in range(self.info["sum"])]
            self.not_pkeys = [self.info[i]["field"] for i in range(self.info["sum"]) if self.info[i]["key"] != "PRI"]
            self.pkeys = [self.info[i]["field"] for i in range(self.info["sum"]) if self.info[i]["key"] == "PRI"]

    def init_table(self, info: dict, data: tuple):
        self.info = info
        self.generate_part()
        self.tmodel = QtGui.QStandardItemModel(len(data), self.info["sum"])
        self.tmodel.setHorizontalHeaderLabels(self.labels)

        for row in range(len(data)):
            for col in range(self.info["sum"]):
                item = QtGui.QStandardItem(str(data[row][col]))
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.tmodel.setItem(row, col, item)

        self.tmodel.itemChanged.connect(self._item_changed)
        self.setModel(self.tmodel)

    def _item_changed(self, item):
        row, col = item.row(), item.column()
        data, pkey = self._prepare_mapper(row=row)
        flag, msg = self.handle.update(db=self.info["db"], tb=self.info["tb"], pkey=pkey, data=data)
        if flag:
            pass
        else:
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)

    def _prepare_mapper(self, row: int):
        data = [self.not_pkeys, []]
        pkey = [self.pkeys, []]
        for c in range(self.info["sum"]):
            label = self.tmodel.horizontalHeaderItem(c).text()
            item = self.tmodel.index(row, c).data()
            if item == "None":
                item = "null"

            if label in data[0]:
                data[1].append(item)
            else:
                pkey[1].append(item)
        return data, pkey

    def insert_row(self, data: list):
        self.tmodel.itemChanged.disconnect()
        row_idx = self.tmodel.rowCount()
        self.tmodel.insertRow(row_idx)
        for i in range(len(data)):
            if data[i] == "<add>":
                previous = int(self.tmodel.data(self.tmodel.index(row_idx - 1, i)))
                ans = str(previous + 1)
            else:
                ans = data[i]
            item = QtGui.QStandardItem(ans)
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.tmodel.setItem(row_idx, i, item)

        self.tmodel.itemChanged.connect(self._item_changed)
        data, pkey = self._prepare_mapper(row=row_idx)
        return data, pkey

    def delete_row(self):
        row = self.currentIndex().row()
        data, pkey = self._prepare_mapper(row=row)
        self.tmodel.removeRow(row)
        return data, pkey


class ModifyWindow(QtWidgets.QMainWindow):
    def __init__(self, handle: SqlConn, db: str, tb: str):
        super(ModifyWindow, self).__init__()
        self.resize(1280, 800)
        self._center()

        self.handle = handle
        self.db = db
        self.tb = tb
        self.info = dict()

        self.info_table = InfoTable(handle=self.handle, parent=self)
        self.data_table = DataTable(handle=self.handle, parent=self)

        self._center()
        self._init_table()
        self._init_gui()

    def _center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, ((screen.height() - size.height()) // 2) - 50)

    def _init_table(self):
        self.info = self.handle.get_info(db=self.db, tb=self.tb)
        all_item = self.handle.select_all(db=self.db, tb=self.tb)

        self.info_table.init_table(info=self.info)
        self.data_table.init_table(info=self.info, data=all_item)

    def _init_gui(self):
        widget = QtWidgets.QWidget()
        v_layout_all = QtWidgets.QVBoxLayout()

        h_layout_1 = QtWidgets.QHBoxLayout()
        h_layout_h1_1 = QtWidgets.QHBoxLayout()
        v_layout_h1_2 = QtWidgets.QVBoxLayout()
        h_layout_h1_1.addWidget(self.info_table)

        info_save_btn = QtWidgets.QPushButton("刷新")
        info_save_btn.clicked.connect(self.fresh_info)
        info_add_btn = QtWidgets.QPushButton("添加")
        info_add_btn.clicked.connect(self.add_info)
        info_del_btn = QtWidgets.QPushButton("删除")
        info_del_btn.clicked.connect(self.delete_info)

        v_layout_h1_2.addWidget(info_save_btn)
        v_layout_h1_2.addWidget(info_add_btn)
        v_layout_h1_2.addWidget(info_del_btn)
        h_layout_1.addLayout(h_layout_h1_1)
        h_layout_1.addLayout(v_layout_h1_2)
        h_layout_1.setSpacing(40)
        h_layout_1.setStretch(0, 9)
        h_layout_1.setStretch(1, 1)

        h_layout_2 = QtWidgets.QHBoxLayout()
        h_layout_h2_1 = QtWidgets.QHBoxLayout()
        v_layout_h2_2 = QtWidgets.QVBoxLayout()
        h_layout_h2_1.addWidget(self.data_table)

        data_fresh_btn = QtWidgets.QPushButton("刷新")
        data_fresh_btn.clicked.connect(self.fresh_data)
        data_add_btn = QtWidgets.QPushButton("添加")
        data_add_btn.clicked.connect(self.add_data)
        data_del_btn = QtWidgets.QPushButton("删除")
        data_del_btn.clicked.connect(self.delete_data)

        v_layout_h2_2.addWidget(data_fresh_btn)
        v_layout_h2_2.addWidget(data_add_btn)
        v_layout_h2_2.addWidget(data_del_btn)
        h_layout_2.addLayout(h_layout_h2_1)
        h_layout_2.addLayout(v_layout_h2_2)
        h_layout_2.setSpacing(40)
        h_layout_2.setStretch(0, 9)
        h_layout_2.setStretch(1, 1)

        v_layout_all.addLayout(h_layout_1)
        v_layout_all.addLayout(h_layout_2)
        v_layout_all.setSpacing(20)
        v_layout_all.setContentsMargins(30, 20, 30, 20)

        widget.setLayout(v_layout_all)
        self.setCentralWidget(widget)

    def fresh_info(self):
        new_info = self.handle.get_info(db=self.db, tb=self.tb)
        self.info = new_info
        self.info_table.tmodel = QtGui.QStandardItemModel()
        self.info_table.init_table(info=self.info)
        self.info_table.scrollToTop()

    def fresh_data(self):
        new_all_item = self.handle.select_all(db=self.db, tb=self.tb)
        self.data_table.tmodel = QtGui.QStandardItemModel()
        self.data_table.init_table(info=self.info, data=new_all_item)
        self.data_table.scrollToTop()

    def add_info(self):
        now_idx, now_label = self.info_table.insert_row()
        flag, msg = self.handle.alter_insert(db=self.db, tb=self.tb, now_idx=now_idx, now_label=now_label)
        if flag:
            self.fresh_info()
            self.fresh_data()
            self.info_table.scrollTo(self.info_table.tmodel.index(now_idx + 1, 0))
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def add_data(self):
        res = [set_default_item(item=self.info[i]) for i in range(self.info["sum"])]
        data, pkey = self.data_table.insert_row(data=res)
        flag, msg = self.handle.insert(db=self.db, tb=self.tb, pkey=pkey, data=data)
        if flag:
            self.data_table.scrollToBottom()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def delete_info(self):
        field = self.info_table.delete_row()
        flag, msg = self.handle.delete_info(db=self.db, tb=self.tb, field=field)
        if flag:
            self.fresh_info()
            self.fresh_data()
            self.info_table.scrollToTop()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def delete_data(self):
        data, pkey = self.data_table.delete_row()
        flag, msg = self.handle.delete(db=self.db, tb=self.tb, pkey=pkey)
        if flag:
            pass
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)
