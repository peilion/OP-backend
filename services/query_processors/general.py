from typing import Optional


def format_double_grouped_result(
    res: list, fisrt_group_names: Optional[dict], second_group_names: dict
):
    res_dict = {}

    for item in res:
        first_name = (
            fisrt_group_names[item[0]] if (fisrt_group_names is not None) else (item[0])
        )
        second_name = second_group_names[item[1]]
        res_dict.setdefault(first_name, {})
        res_dict[first_name][second_name] = item[2]
    return res_dict


def format_single_grouped_result(res: list, group_names: dict):
    res_dict = {}
    for row in res:
        res_dict[group_names[row[0]]] = row[1]
    return res_dict
