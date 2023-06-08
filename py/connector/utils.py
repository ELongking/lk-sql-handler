import re

from fuzzywuzzy import fuzz


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
        if isnull == "YES":
            res = default
        else:
            res = "null"

    return res


def item_search(inp: str, data: str) -> int:
    score = fuzz.partial_token_set_ratio(inp, data)
    return score


def split_sql_sentence(sentence: str) -> list:
    sen_part = re.split(r"\s+", sentence)
    sen_part = list(map(lambda x: x.strip(), sen_part))
    sentence = " ".join(sen_part)

    res = re.split(r";\s*", sentence)
    res = [r for r in res if r]
    return res
