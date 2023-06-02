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
            res = "None"

    return res


def item_search(inp: str, data: str) -> int:
    score = fuzz.partial_token_set_ratio(inp, data)
    return score
