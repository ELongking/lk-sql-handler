import pymysql as ms
from pymysql.err import MySQLError
from loguru import logger
from datetime import datetime as dt
import os

now_time = dt.now()
os.makedirs("./logs", exist_ok=True)
logger.add(f"./logs/sql-{now_time.strftime('%Y%m%d')}.log", rotation="1 day", retention="15 days")
logger.info("-" * 25 + " Start " + "-" * 25)
logger.info("-" * 13 + f" OpenTime: {now_time.strftime('%Y-%m-%d %H:%M:%S')} " + "-" * 13)


def trans_error(e: MySQLError):
    e = str(e)
    e = e[1:-1]
    error_part = e.split(",")
    code, msg = error_part[0], ",".join(error_part[1:])
    return code, msg


def alter_insert_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, now_idx: int, now_label: str):
    sql = f"ALTER TABLE `{db}`.`{tb}` ADD `col-{now_idx + 1}` varchar(10) AFTER `{now_label}`"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def alter_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, data: list, mode: str):
    field, new_data = data
    sql = ""
    if mode == "field":
        sql = f"ALTER TABLE `{db}`.`{tb}` CHANGE `{field}` {new_data}"
    elif mode == "type":
        sql = f"ALTER TABLE `{db}`.`{tb}` MODIFY COLUMN `{field}` {new_data}"
    elif mode == "isnull":
        sql = f"ALTER TABLE `{db}`.`{tb}` MODIFY COLUMN `{field}` {new_data}"
    elif mode == "key":
        sql = f"ALTER TABLE `{db}`.`{tb}` DROP PRIMARY KEY"
        logger.info(f"sql sentence => {sql}")
        try:
            cursor.execute(sql)
            conn.commit()
        except MySQLError as e:
            code, msg = trans_error(e)
            if code == "1091":
                pass
            else:
                logger.error(e)
                return False, msg

        sql = f"ALTER TABLE `{db}`.`{tb}` ADD PRIMARY KEY({new_data})"
    elif mode == "default":
        if not new_data:
            new_data = "null"
        sql = f"ALTER TABLE `{db}`.`{tb}` ALTER COLUMN `{field}` SET DEFAULT {new_data}"
    elif mode == "extra":
        sql = f"ALTER TABLE `{db}`.`{tb}` MODIFY COLUMN `{field}` {new_data}"

    logger.info(f"sql sentence => {sql}")

    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def select_info_mode(cursor: ms.connect.cursor, db: str, tb: str):
    items = ["field", "type", "isnull", "key", "default", "extra"]
    info = dict()
    sql = "SHOW COLUMNS FROM `{}`.`{}`".format(db, tb)
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        for n in range(len(res)):
            info[n] = dict()
            for i in range(len(items)):
                info[n][items[i]] = res[n][i]
        info["sum"] = len(res)
        info["tb"] = tb
        info["db"] = db
        return True, info
    except MySQLError as e:
        logger.warning(e)
        return False, trans_error(e)[1]


def select_all_mode(cursor: ms.connect.cursor, db: str, tb: str):
    sql = f"SELECT * FROM `{db}`.`{tb}`"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        return True, res
    except MySQLError as e:
        logger.warning(e)
        return False, trans_error(e)[1]


def insert_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list, data: list):
    data_name, data_val = data
    pkey_name, pkey_val = pkey

    field, value = [*data_name, *pkey_name], [*data_val, *pkey_val]
    field = [f"`{f}`" for f in field]
    field_sql = ", ".join(field)
    value_sql = ", ".join(value)

    sql = f"INSERT INTO `{db}`.`{tb}` ({field_sql}) VALUES ({value_sql})"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def update_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list, data: list):
    data_name, data_val = data
    pkey_name, pkey_val = pkey
    value_sql = ", ".join([f"`{name}`={val}" for name, val in zip(data_name, data_val)])
    where_sql = ", ".join([f"`{name}`={val}" for name, val in zip(pkey_name, pkey_val)])

    sql = f"UPDATE `{db}`.`{tb}` SET {value_sql} WHERE {where_sql}"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def delete_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list):
    pkey_name, pkey_val = pkey
    where_sql = ", ".join([f"`{name}`={val}" for name, val in zip(pkey_name, pkey_val)])

    sql = f"DELETE FROM `{db}`.`{tb}` WHERE {where_sql}"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def alter_delete_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, field: str):
    sql = f"ALTER TABLE `{db}`.`{tb}` DROP `{field}`"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]


def increment_reorder_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, field: str):
    try:
        sql = f"ALTER TABLE tafang.info DROP `{field}`"
        logger.info(f"sql sentence => {sql}")
        cursor.execute(sql)
        conn.commit()
        try:
            sql = f"ALTER TABLE `{db}`.`{tb}` ADD `{field}` int(10) PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST "
            logger.info(f"sql sentence => {sql}")
            cursor.execute(sql)
            conn.commit()
        except MySQLError as e:
            logger.error(e)
            return False, trans_error(e)[1]
    except MySQLError as e:
        logger.error(e)
        return False, trans_error(e)[1]

    return True, ""


def arbitrary_mode(conn: ms.connect, cursor: ms.connect.cursor, sen_part: list):
    for sentence in sen_part:
        try:
            logger.info(f"CUSTOMIZED sql sentence => {sentence}")
            cursor.execute(sentence)
            res = cursor.fetchall()
            conn.commit()
        except MySQLError as e:
            logger.error(e)
            return False, trans_error(e)[1]

    return True, ""
