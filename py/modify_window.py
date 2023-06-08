from PyQt5 import QtWidgets, QtGui, QtCore

from connector.init_conn import SqlConn
from connector.utils import *
from connector.base_widget import *
import connector.type_enum as te


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
        self.pri_group = None
        self.labels = []

    def init_table(self, info: dict):
        type_items = te.TYPE_NAMES
        self.info = info
        self.pri_group = PriCheckGroup(func=self._inside_check_changed)
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
                        ans_check = PriCheck(row=row, col=col)
                        if value == "PRI":
                            ans_check.setCheckState(QtCore.Qt.Checked)
                        else:
                            ans_check.setCheckState(QtCore.Qt.Unchecked)
                        self.pri_group.add_button(ans_check)
                        self.setIndexWidget(self.tmodel.index(row, 4), ans_check)
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

        self.pri_group.conn_enabled()
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
        row, col = item.row(), item.column()
        old_data = self.info[row]["field"]
        assert col in [0, 2, 5]
        col2desc = {0: "field", 1: "type", 2: "type", 3: "isnull", 4: "key", 5: "default", 6: "extra"}
        data = [self.labels[row]]

        if col == 2:
            new_data = self.indexWidget(
                self.tmodel.index(row, 1)).currentText() + f"({self.tmodel.index(row, col).data()})"
        elif col == 0:
            new_data = f"`{self.tmodel.index(row, col).data()}`"

            _type = self.indexWidget(self.tmodel.index(row, 1)).currentText()
            if self.tmodel.index(row, 2).data():
                _type += f"({self.tmodel.index(row, 2).data()})"
            new_data += f" {_type}"

            _isnull = self.indexWidget(self.tmodel.index(row, 3)).currentText()
            if _isnull == "YES":
                _isnull = "NULL"
            else:
                _isnull = "NOT NULL"
            new_data += f" {_isnull}"

            _key = self.indexWidget(self.tmodel.index(row, 4)).checkState()
            if _key == 0:
                pass
            else:
                _key = f"PRIMARY KEY"
                new_data += f" {_key}"

            _default = self.tmodel.index(row, 5).data()
            if _default == 'None':
                pass
            else:
                _default = f"DEFAULT {_default}"
                new_data += f" {_default}"

            _extra = self.indexWidget(self.tmodel.index(row, 6)).currentText()
            if _extra == "auto_increment":
                new_data += " AUTO_INCREMENT"
            elif _extra == "on update CURRENT_TIMESTAMP":
                new_data += " on update CURRENT_TIMESTAMP"
            else:
                pass

            new_data += " FIRST"
        else:
            new_data = self.tmodel.index(row, col).data()
        data.append(new_data)

        flag, msg = self.handle.alter(db=self.info["db"], tb=self.info["tb"], data=data, mode=col2desc[col])
        if flag:
            self.parent.fresh_data()
            self.parent.fresh_widgets()
        else:
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)
            self.parent.fresh_info()

    def _inside_combo_changed(self, index):
        sender = self.sender()
        row, col = sender.index
        assert col in [1, 3, 6]
        col2desc = {0: "field", 1: "type", 2: "type", 3: "isnull", 4: "key", 5: "default", 6: "extra"}
        data = [self.labels[row]]

        if col in [3, 6]:
            new_data = self.indexWidget(self.tmodel.index(row, col)).currentText()
            if col == 6:
                if new_data == "None":
                    new_data = self.indexWidget(self.tmodel.index(row, 1)).currentText()
            else:
                ori_type = self.indexWidget(self.tmodel.index(row, 1)).currentText()
                ori_type += f"({self.tmodel.index(row, 2).data()})" if self.tmodel.index(row, 2).data() else ""
                if new_data == "YES":
                    new_data = f"{ori_type} NULL"
                else:
                    new_data = f"{ori_type} NOT NULL"
        else:
            self.tmodel.itemChanged.disconnect()
            new_data = self.indexWidget(self.tmodel.index(row, col)).currentText()
            self.tmodel.setItem(row, 2, QtGui.QStandardItem(""))
            self.tmodel.itemChanged.connect(self._item_changed)

        data.append(new_data)
        flag, msg = self.handle.alter(db=self.info["db"], tb=self.info["tb"], data=data, mode=col2desc[col])
        if flag:
            self.parent.fresh_data()
            self.parent.fresh_widgets()
        else:
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)
            self.parent.fresh_info()

    def _inside_check_changed(self, btn):
        row, col = btn.index
        assert col == 4
        col2desc = {0: "field", 1: "type", 2: "type", 3: "isnull", 4: "key", 5: "default", 6: "extra"}
        new_data = ""
        for row, button in enumerate(self.pri_group.buttons()):
            if button.checkState() in [1, 2]:
                new_data += f"`{self.tmodel.index(row, 0).data()}`, "
        data = [self.labels[row], new_data[:-2]]

        flag, msg = self.handle.alter(db=self.info["db"], tb=self.info["tb"], data=data, mode=col2desc[col])
        if flag:
            self.parent.fresh_data()
            self.parent.fresh_widgets()
        else:
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)
            self.parent.fresh_info()

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
                item = DataItem(data=str(data[row][col]), info=self.info[col])
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.tmodel.setItem(row, col, item)

        self.tmodel.itemChanged.connect(self._item_changed)
        self.setModel(self.tmodel)

    def _item_changed(self, item):
        row, col = item.row(), item.column()
        item.set_data(self.tmodel.index(row, col).data())
        data, pkey = self._prepare_mapper(row=row)
        flag, msg = self.handle.update(db=self.info["db"], tb=self.info["tb"], pkey=pkey, data=data)
        if flag:
            pass
        else:
            self.tmodel.itemChanged.disconnect()
            QtWidgets.QMessageBox.warning(self.parent, "ERROR", msg)
            self.parent.fresh_data()
            self.tmodel.itemChanged.connect(self._item_changed)

    def _prepare_mapper(self, row: int):
        data = [self.not_pkeys, []]
        pkey = [self.pkeys, []]
        for c in range(self.info["sum"]):
            label = self.tmodel.horizontalHeaderItem(c).text()
            item = self.tmodel.item(row, c).export_data()
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

            item = DataItem(data=ans, info=self.info[i])
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
        self.setWindowTitle(f"Now check => {db}.{tb}")
        self._center()

        self.handle = handle
        self.db = db
        self.tb = tb
        self.info = dict()

        self.info_table = InfoTable(handle=self.handle, parent=self)
        self.data_table = DataTable(handle=self.handle, parent=self)
        self.sql_editor = QTextEditWithLineNum()

        self.menu = self.menuBar()

        self._center()
        self._init_table()
        self._init_gui()
        self._init_menu()

    def _center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, ((screen.height() - size.height()) // 2) - 50)

    def _init_table(self):
        self.info = self.handle.select_info(db=self.db, tb=self.tb)
        all_item = self.handle.select_all(db=self.db, tb=self.tb)

        self.info_table.init_table(info=self.info)
        self.data_table.init_table(info=self.info, data=all_item)

    def _init_gui(self):
        self.all_tab = QtWidgets.QTabWidget()

        self.general_tab = QtWidgets.QWidget()
        self.customized_tab = QtWidgets.QWidget()
        self.relation_tab = QtWidgets.QWidget()

        self.all_tab.addTab(self.general_tab, "总览")
        self.all_tab.addTab(self.customized_tab, "语句视图")
        self.all_tab.addTab(self.relation_tab, "关系视图")

        self._init_tab1()
        self._init_tab2()
        self._init_tab3()

        self.setCentralWidget(self.all_tab)

    def _init_tab1(self):
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

        h_layout_3 = QtWidgets.QHBoxLayout()

        search_label = QtWidgets.QLabel("搜索功能 ==> ")
        self.search_col_box = QtWidgets.QComboBox()
        labels = self.data_table.labels
        labels.insert(0, "-- 请选择需要查询的列 --")
        self.search_col_box.addItems(labels)
        self.search_content_text = QtWidgets.QLineEdit()
        self.search_content_text.setPlaceholderText("Enter search text")
        self.limit_text = QtWidgets.QLineEdit()
        self.limit_text.setText("10")
        search_btn = QtWidgets.QPushButton("查询")
        search_btn.clicked.connect(self._search_func)
        self.search_res_box = QtWidgets.QComboBox()
        self.search_res_box.addItems(["-- 结果 --"])
        self.search_res_box.currentIndexChanged.connect(self._search_combo_changed)

        h_layout_3.addWidget(search_label)
        h_layout_3.addWidget(self.search_col_box)
        h_layout_3.addWidget(self.search_content_text)
        h_layout_3.addWidget(self.limit_text)
        h_layout_3.addWidget(search_btn)
        h_layout_3.addWidget(self.search_res_box)
        h_layout_3.addWidget(QtWidgets.QLabel())

        h_layout_3.setStretch(0, 1)
        h_layout_3.setStretch(1, 2)
        h_layout_3.setStretch(2, 2)
        h_layout_3.setStretch(3, 1)
        h_layout_3.setStretch(4, 1)
        h_layout_3.setStretch(5, 1)
        h_layout_3.setStretch(6, 1)

        v_layout_all.addLayout(h_layout_1)
        v_layout_all.addLayout(h_layout_3)
        v_layout_all.addLayout(h_layout_2)
        v_layout_all.setSpacing(10)
        v_layout_all.setContentsMargins(30, 20, 30, 20)

        self.general_tab.setLayout(v_layout_all)

    def _init_tab2(self):
        v_layout = QtWidgets.QVBoxLayout()
        h_layout = QtWidgets.QHBoxLayout()

        exec_btn = QtWidgets.QPushButton("执行")
        exec_btn.clicked.connect(self._sql_execute)
        clear_btn = QtWidgets.QPushButton("清空")
        clear_btn.clicked.connect(self._clear_sentence)
        h_layout.addWidget(exec_btn)
        h_layout.addWidget(clear_btn)

        v_layout.addWidget(self.sql_editor)
        v_layout.addLayout(h_layout)

        self.customized_tab.setLayout(v_layout)

    def _init_tab3(self):
        pass

    def _init_menu(self):
        quick = self.menu.addMenu("快捷")
        about = self.menu.addMenu("关于")

        rik = QtWidgets.QAction("Re-order increment key", self)
        rik.triggered.connect(self._pri_increment_reorder)
        quick.addAction(rik)

        about.addAction(QtWidgets.QAction("Help", self))
        about.addAction(QtWidgets.QAction("Version", self))

    def fresh_info(self):
        self.info = self.handle.select_info(db=self.db, tb=self.tb)
        self.info_table.tmodel = QtGui.QStandardItemModel()
        self.info_table.init_table(info=self.info)
        self.info_table.scrollToTop()

    def fresh_data(self):
        new_all_item = self.handle.select_all(db=self.db, tb=self.tb)
        self.data_table.tmodel = QtGui.QStandardItemModel()
        self.data_table.init_table(info=self.info, data=new_all_item)
        self.data_table.scrollToTop()

    def fresh_widgets(self):
        labels = self.data_table.labels
        self.search_col_box.clear()
        labels.insert(0, "-- 请选择需要查询的列 --")
        self.search_col_box.addItems(labels)

        self.search_res_box.currentIndexChanged.disconnect()
        self.search_res_box.clear()
        self.search_res_box.addItems(["-- 结果 -- "])
        self.search_res_box.currentIndexChanged.connect(self._search_combo_changed)

    def add_info(self):
        now_idx, now_label = self.info_table.insert_row()
        flag, msg = self.handle.alter_insert(db=self.db, tb=self.tb, now_idx=now_idx, now_label=now_label)
        if flag:
            self.fresh_info()
            self.fresh_data()
            self.fresh_widgets()
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
            self.fresh_data()

    def delete_info(self):
        field = self.info_table.delete_row()
        flag, msg = self.handle.delete_info(db=self.db, tb=self.tb, field=field)
        if flag:
            self.fresh_info()
            self.fresh_data()
            self.fresh_info()
            self.info_table.scrollToTop()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def delete_data(self):
        data, pkey = self.data_table.delete_row()
        flag, msg = self.handle.delete(db=self.db, tb=self.tb, pkey=pkey)
        if flag:
            self.fresh_data()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def _search_func(self):
        inp = self.search_content_text.text()
        col_name = self.search_col_box.currentText()
        limit = self.limit_text.text()
        res = []
        assert int(limit) == float(limit), QtWidgets.QMessageBox.warning(self, "ERROR", "最大展示数目需为整数")

        col = -1
        for i in range(self.info["sum"]):
            if self.info[i]["field"] == col_name:
                col = i
                break

        row_max = self.data_table.tmodel.rowCount()
        for row in range(row_max):
            data = self.data_table.tmodel.index(row, col).data()
            score = item_search(inp=inp, data=data)
            if score >= 75:
                res.append((row, score))
        res.sort(key=lambda x: x[-1], reverse=True)
        if len(res) > int(limit):
            res = res[:int(limit)]

        self.search_res_box.currentIndexChanged.disconnect()
        self.search_res_box.clear()
        res = [str(row) for row, _ in res]
        res.insert(0, "-- 结果 --")
        self.search_res_box.addItems(res)
        self.search_res_box.currentIndexChanged.connect(self._search_combo_changed)

    def _search_combo_changed(self, index):
        if index == 0:
            pass
        else:
            self.data_table.scrollTo(self.data_table.tmodel.index(int(self.search_res_box.currentText()), 0))

    def _pri_increment_reorder(self):
        row_idx = -1
        for i in range(self.info["sum"]):
            if self.info[i]["extra"] == "auto_increment":
                row_idx = i
        if row_idx == -1:
            QtWidgets.QMessageBox.information(self, "Notice", "该表没有自增字段")
            return

        flag, msg = self.handle.increment_reorder(db=self.db, tb=self.tb, field=self.info[row_idx]['field'])
        if flag:
            self.fresh_info()
            self.fresh_data()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def _sql_execute(self):
        sentence = self.sql_editor.toPlainText()
        sen_part = split_sql_sentence(sentence=sentence)
        flag, msg, mode = self.handle.arbitrary(sen_part=sen_part)

        if mode == "info":
            self.fresh_info()
            self.fresh_data()
        elif mode == "data":
            self.fresh_data()

        if flag:
            pass
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", msg)

    def _clear_sentence(self):
        self.sql_editor.clear()
