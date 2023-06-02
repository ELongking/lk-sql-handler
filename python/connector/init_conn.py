import pymysql as ms
from .mapper import *


class SqlConn:
    def __init__(self, host, user, pwd):
        self.db = ms.connect(host=host, user=user, password=pwd)
        self.cursor = self.db.cursor()
        self.databases = []
        self.tables = dict()

        self._init_info()

    def __get_all_databases(self) -> None:
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "SHOW DATABASES"
        resp = self.cursor.execute(sql)
        res = self.cursor.fetchall()
        res = [item[0] for item in res if item[0] not in exclude_list]
        self.databases = res

    def __get_all_tables(self) -> None:
        assert self.databases
        for db in self.databases:
            sql = "SHOW TABLES FROM {}".format(db)
            resp = self.cursor.execute(sql)
            res = self.cursor.fetchall()
            if res:
                res = [tb[0] for tb in res]
                self.tables[db] = res

    def _init_info(self):
        self.__get_all_databases()
        self.__get_all_tables()

    def get_info(self, db, tb) -> dict:
        items = ["field", "type", "isnull", "key", "default", "extra"]
        info = dict()
        sql = "SHOW COLUMNS FROM `{}`.`{}`".format(db, tb)
        resp = self.cursor.execute(sql)
        res = self.cursor.fetchall()

        for n in range(len(res)):
            info[n] = dict()
            for i in range(len(items)):
                info[n][items[i]] = res[n][i]
        info["sum"] = len(res)
        info["tb"] = tb
        info["db"] = db

        return info

    def select_all(self, db, tb):
        flag, res = select_all_mode(cursor=self.cursor, db=db, tb=tb)
        return res

    def select(self):
        pass

    def insert(self, db: str, tb: str, pkey: list, data: list):
        flag, msg = insert_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, pkey=pkey, data=data)
        return flag, msg

    def update(self, db: str, tb: str, pkey: list, data: list):
        flag, msg = update_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, pkey=pkey, data=data)
        return flag, msg

    def delete(self, db: str, tb: str, pkey: list):
        flag, msg = delete_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, pkey=pkey)
        return flag, msg

    def delete_info(self, db: str, tb: str, field: str):
        flag, msg = alter_delete_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, field=field)
        return flag, msg

    def alter_insert(self, db: str, tb: str, now_idx: int, now_label: str):
        flag, msg = alter_insert_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, now_idx=now_idx, now_label=now_label)
        return flag, msg

    def alter(self, db: str, tb: str, data: list, mode: str):
        flag, msg = alter_mode(conn=self.db, cursor=self.cursor, db=db, tb=tb, data=data, mode=mode)
        return flag, msg

    def close(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    handle = SqlConn(host="localhost", user="root", pwd="19980917")
    print(handle.databases, handle.tables, sep="\n")
    print(handle.get_info("tafang", "info"))
    handle.close()
