TINYINT = {"name": "tinyint", "type": "int", "range": (-8, 8)}
TINYINT_UNSIGNED = {"name": "tinyint_unsigned", "type": "int", "range": (0, 9)}
SMALLINT = {"name": "smallint", "type": "int", "range": (-16, 16)}
SMALLINT_UNSIGNED = {"name": "smallint_unsigned", "type": "int", "range": (0, 17)}
MEDIUMINT = {"name": "mediumint", "type": "int", "range": (-24, 24)}
MEDIUMINT_UNSIGNED = {"name": "mediumint_unsigned", "type": "int", "range": (0, 25)}
INT = {"name": "int", "type": "int", "range": (-32, 32)}
INT_UNSIGNED = {"name": "int_unsigned", "type": "int", "range": (0, 33)}
FLOAT = {"name": "float", "type": "float", "range": (-128, 128)}
FLOAT_UNSIGNED = {"name": "float_unsigned", "type": "float", "range": (0, 128)}
DOUBLE = {"name": "double", "type": "float", "range": (-1024, 1024)}
DOUBLE_UNSIGNED = {"name": "double_unsigned", "type": "float", "range": (0, 1024)}

CHAR = {"name": "char", "type": "str", "range": (0, 9)}
VARCHAR = {"name": "varchar", "type": "str", "range": (0, 17)}
TINYBLOB = {"name": "tinyblob", "type": "bin", "range": (0, 9)}
BLOB = {"name": "blob", "type": "bin", "range": (0, 17)}
TEXT = {"name": "text", "type": "str", "range": (0, 17)}
MEDIUMBLOB = {"name": "mediumblob", "type": "bin", "range": (0, 25)}
MEDIUMTEXT = {"name": "mediumtext", "type": "str", "range": (0, 25)}
LONGBLOB = {"name": "longblob", "type": "bin", "range": (0, 33)}
LONGTEXT = {"name": "longtext", "type": "bin", "range": (0, 33)}

DATE = {"name": "date", "type": "time", "range": None}
TIME = {"name": "time", "type": "time", "range": None}
YEAR = {"name": "year", "type": "time", "range": None}
DATETIME = {"name": "datetime", "type": "time", "range": None}
TIMESTAMP = {"name": "timestamp", "type": "time", "range": None}

SUM_TYPE = [TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED,
            MEDIUMINT, MEDIUMINT_UNSIGNED, INT, INT_UNSIGNED,
            FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED,
            CHAR, VARCHAR, TINYBLOB, BLOB,
            TEXT, MEDIUMBLOB, MEDIUMTEXT, LONGBLOB, LONGTEXT,
            DATE, TIME, YEAR, DATETIME, TIMESTAMP]
NAME2TYPE = {_item["name"]: _item for _item in SUM_TYPE}
