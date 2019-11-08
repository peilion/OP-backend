import datetime
from typing import Optional


def format_map_grouped_result(
    res: list, fisrt_group_names: Optional[dict], second_group_names: dict
):
    res_dict = {}

    for item in res:
        first_name = (
            fisrt_group_names[item[0]] if (fisrt_group_names is not None) else (item[0])
        )
        second_name = second_group_names[item[1]]

        res_dict.setdefault(first_name, {})
        res_dict[first_name].setdefault("status", {})
        res_dict[first_name]["status"].setdefault(second_name, item[2])

        if res_dict.get("geo") is None:
            res_dict[first_name]["geo"] = [item[4], item[3]]
    return res_dict


def format_timediff_result(res: list, time_after: str, interval: int):
    time_list = []
    res_list = []
    initial_time = datetime.datetime.strptime(time_after, "%Y-%m-%d %H:%M:%S")

    for item in res:
        time_list.append(
            (initial_time + datetime.timedelta(days=interval * item["diff"])).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        res_list.append(item["avg"])
    return {"time_list": time_list, "res_list": res_list}