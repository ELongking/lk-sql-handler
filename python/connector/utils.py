def set_default_item(item: dict):
    res = "null"
    isnull = item["isnull"]
    default = item["default"]

    if isnull == "YES":
        pass
    else:
        extra = item["extra"]

        if extra == "auto_increment":
            res = "<add>"

    if default:
        res = default

    return res

# def check_data_format(data, t: str):
#     if t in ["int", "float"]:
#         if data == "inf" or "-inf":
#             return False
#         try:
#             ret = float(data)
#             return True
#         except:
#             return False
