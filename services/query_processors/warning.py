import json
from db_model import WarningLog


def warning_description_formatter(res: list):
    items = [dict(row) for row in res]
    for item in items:
        if "t_name" not in item.keys() or item["t_name"] == "diagnosis_warning":
            formatted_description = ""
            description = json.loads(item["description"])
            for key in description.keys():
                formatted_description += (
                    (WarningLog.SEVERITIES[description[key] - 1] + key + ";")
                    if description[key] > 0
                    else ""
                )
            item["description"] = formatted_description
    return items


def threshold_formatter(res: list):
    items = [dict(row) for row in res]
    for item in items:
        item["diag_threshold"] = item["diag_threshold"]
    return items
