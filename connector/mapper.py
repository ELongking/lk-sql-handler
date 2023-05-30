import pymysql as ms
from pymysql.err import MySQLError
from loguru import logger
from datetime import datetime as dt
import os

now_time = dt.now()
os.makedirs("./logs")
logger.add(f"./logs/sql-{now_time.strftime('%Y%m%d')}.log", rotation="1 day", retention="15 days")
logger.info("-" * 25 + " Start " + "-" * 25)
logger.info("-" * 13 + f" OpenTime: {now_time.strftime('%Y-%m-%d %H:%M:%S')} " + "-" * 13)


def check_data(data: str, label: str, info: dict):
    pass


def alter_insert_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, now_idx: int, now_label: str):
    sql = f"ALTER TABLE {db}.{tb} ADD `col-{now_idx + 1}` varchar(10) AFTER `{now_label}`"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)


def alter_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, data: list, mode: str):
    field, new_data = data
    sql = ""
    if mode == "field":
        sql = f"ALTER TABLE {db}.{tb} CHANGE `{field}` {new_data}"
    elif mode == "type":
        sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` {new_data}"
    elif mode == "isnull":
        if new_data == "YES":
            sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` NULL"
        else:
            sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` NOT NULL"
    elif mode == "key":
        if new_data == "None":
            sql = f"ALTER TABLE {db}.{tb} DROP PRIMARY KEY({new_data})"
        else:
            sql = f"ALTER TABLE {db}.{tb} ADD PRIMARY KEY({new_data})"
    elif mode == "default":
        if not new_data:
            new_data = "null"
        sql = f"ALTER TABLE {db}.{tb} ALTER COLUMN `{field}` SET DEFAULT {new_data}"
    elif mode == "extra":
        if new_data == "auto_increment":
            sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` AUTO_INCREMENT"
        elif new_data == "on update CURRENT_TIMESTAMP":
            sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` on update CURRENT_TIMESTAMP"
        else:
            sql = f"ALTER TABLE {db}.{tb} MODIFY COLUMN `{field}` {new_data}"
    logger.info(f"sql sentence => {sql}")

    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)


def select_all_mode(cursor: ms.connect.cursor, db: str, tb: str):
    sql = f"SELECT * FROM {db}.{tb}"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        return True, res
    except MySQLError as e:
        logger.warning(e)
        return False, str(e)


def insert_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list, data: list):
    data_name, data_val = data
    pkey_name, pkey_val = pkey

    field, value = [*data_name, *pkey_name], [*data_val, *pkey_val]
    field = [f"`{f}`" for f in field]
    field_sql = ", ".join(field)
    value_sql = ", ".join(value)

    sql = f"INSERT INTO {db}.{tb} ({field_sql}) VALUES ({value_sql})"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)


def update_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list, data: list):
    data_name, data_val = data
    pkey_name, pkey_val = pkey
    value_sql = ", ".join([f"`{name}`={val}" for name, val in zip(data_name, data_val)])
    where_sql = ", ".join([f"`{name}`={val}" for name, val in zip(pkey_name, pkey_val)])

    sql = f"UPDATE {db}.{tb} SET {value_sql} WHERE {where_sql}"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)


def delete_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, pkey: list):
    pkey_name, pkey_val = pkey
    where_sql = ", ".join([f"`{name}`={val}" for name, val in zip(pkey_name, pkey_val)])

    sql = f"DELETE FROM {db}.{tb} WHERE {where_sql}"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)


def alter_delete_mode(conn: ms.connect, cursor: ms.connect.cursor, db: str, tb: str, field: str):
    sql = f"ALTER TABLE {db}.{tb} DROP `{field}`"
    logger.info(f"sql sentence => {sql}")
    try:
        cursor.execute(sql)
        conn.commit()
        return True, ""
    except MySQLError as e:
        logger.error(e)
        return False, str(e)
