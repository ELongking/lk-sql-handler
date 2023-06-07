import time

from PyQt5 import QtWidgets, QtGui
import sys

from connector.init_conn import SqlConn
from modify_window import ModifyWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.handle = None

        self.setWindowTitle("lk-sql-handler; Python version")
        self.resize(800, 600)
        self._center()

        self._init_gui()

    def _center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, ((screen.height() - size.height()) // 2) - 50)

    def _init_gui(self):
        widget = QtWidgets.QWidget()
        v_layout_all = QtWidgets.QVBoxLayout()
        v_layout_1 = QtWidgets.QVBoxLayout()
        h_layout_2 = QtWidgets.QHBoxLayout()
        h_layout_3 = QtWidgets.QHBoxLayout()

        h_layout_v_1 = QtWidgets.QHBoxLayout()
        host_label = QtWidgets.QLabel("Host:")
        self.host_text = QtWidgets.QLineEdit()
        self.host_text.setText("localhost")
        self.host_text.setPlaceholderText("Enter host url")
        h_layout_v_1.addWidget(host_label)
        h_layout_v_1.addWidget(self.host_text)
        h_layout_v_1.setSpacing(100)

        h_layout_v_2 = QtWidgets.QHBoxLayout()
        username_label = QtWidgets.QLabel("Username:")
        self.username_text = QtWidgets.QLineEdit()
        self.username_text.setText("root")
        self.username_text.setPlaceholderText("Enter username")
        h_layout_v_2.addWidget(username_label)
        h_layout_v_2.addWidget(self.username_text)
        h_layout_v_2.setSpacing(100)

        h_layout_v_3 = QtWidgets.QHBoxLayout()
        pwd_label = QtWidgets.QLabel("Password:")
        self.pwd_text = QtWidgets.QLineEdit()
        self.pwd_text.setText("19980917")
        self.pwd_text.setPlaceholderText("Enter password")
        h_layout_v_3.addWidget(pwd_label)
        h_layout_v_3.addWidget(self.pwd_text)
        h_layout_v_3.setSpacing(100)

        h_layout_v_4 = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("登录")
        login_btn.clicked.connect(self.login)
        reset_btn = QtWidgets.QPushButton("重置")
        reset_btn.clicked.connect(self.reset)
        h_layout_v_4.addWidget(login_btn)
        h_layout_v_4.addWidget(reset_btn)
        h_layout_v_4.setSpacing(100)
        h_layout_v_4.setContentsMargins(100, 0, 100, 0)

        v_layout_1.addLayout(h_layout_v_1)
        v_layout_1.addLayout(h_layout_v_2)
        v_layout_1.addLayout(h_layout_v_3)
        v_layout_1.addLayout(h_layout_v_4)
        v_layout_1.setSpacing(20)

        self.database_box = QtWidgets.QComboBox()
        self.database_box.setEditable(False)
        self.database_box.setEnabled(False)
        self.table_box = QtWidgets.QComboBox()
        self.table_box.setEditable(False)
        self.table_box.setEnabled(False)
        self.database_box.currentIndexChanged.connect(self.table_item_change)
        self.enter_btn = QtWidgets.QPushButton("进入")
        self.enter_btn.clicked.connect(self.enter_modify)
        self.enter_btn.setEnabled(False)

        h_layout_2.addWidget(self.database_box)
        h_layout_2.addWidget(self.table_box)
        h_layout_2.setSpacing(100)
        h_layout_2.setContentsMargins(40, 40, 40, 40)
        h_layout_3.addWidget(self.enter_btn)
        h_layout_3.setContentsMargins(40, 40, 40, 40)

        v_layout_all.addLayout(v_layout_1)
        v_layout_all.addLayout(h_layout_2)
        v_layout_all.addLayout(h_layout_3)
        v_layout_all.setContentsMargins(60, 80, 60, 80)
        v_layout_all.setSpacing(40)

        widget.setLayout(v_layout_all)
        self.setCentralWidget(widget)

    def login(self):
        self.database_box.clear()
        self.database_box.currentIndexChanged.disconnect()
        if self.handle:
            self.handle.close()

        host, username, password = self.host_text.text(), self.username_text.text(), self.pwd_text.text()
        self.handle = SqlConn(host=host, user=username, pwd=password)

        self.database_box.setEnabled(True)
        self.table_box.setEnabled(True)
        self.enter_btn.setEnabled(True)
        dbs = ["---", *self.handle.databases]
        self.database_box.addItems(dbs)
        time.sleep(0.1)
        self.database_box.currentIndexChanged.connect(self.table_item_change)

    def reset(self):
        self.host_text.clear()
        self.username_text.clear()
        self.pwd_text.clear()

        self.database_box.setEnabled(False)
        self.table_box.setEnabled(False)
        self.enter_btn.setEnabled(False)

    def table_item_change(self) -> None:
        now_database = self.database_box.currentText()
        self.table_box.clear()
        if now_database and now_database != "---":
            self.table_box.addItems(self.handle.tables[now_database])

    def enter_modify(self) -> None:
        db, tb = self.database_box.currentText(), self.table_box.currentText()
        if db != "---" and tb:
            self.mw = ModifyWindow(handle=self.handle, db=db, tb=tb)
            self.mw.show()
            self.showMinimized()
        else:
            QtWidgets.QMessageBox.warning(self, "ERROR", "请选择符合要求的数据库和表名")

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("CLOSE")
        if self.handle:
            self.handle.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    with open("./assets/main.qss", 'r', encoding='utf-8') as f:  # 读取QSS样式文件
        app.setStyleSheet(f.read())
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
