from databases import Database

from db_model import Asset, PumpUnit
from model.assets import TypeStationSchema, StatuStatisticSchema
from services.query_processors.asset import format_map_grouped_result
from services.query_processors.general import (
    format_double_grouped_result,
    format_single_grouped_result,
)


async def get_count_by_statu(conn: Database):
    query = "SELECT statu, COUNT(*) as cnt FROM `asset` where asset_level = 0 GROUP BY statu"
    res = await conn.fetch_all(query)
    res_dic = format_single_grouped_result(res=res, group_names=Asset.STATUS)
    return StatuStatisticSchema(**res_dic)


async def get_count_by_province(conn: Database):
    query = (
        "SELECT s.location, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id "
        "GROUP BY s.location"
    )
    res = await conn.fetch_all(query)
    return dict(res)


async def get_count_by_pipeline(conn: Database):
    query = (
        "SELECT p.name, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "JOIN pipeline p on pu.pipeline_id = p.id "
        "where a.asset_type=0 "
        "group by pu.pipeline_id"
    )
    res = await conn.fetch_all(query)
    return dict(res)


async def get_overall_avg(conn: Database):
    query = "SELECT avg(health_indicator) as avg from asset WHERE asset_level=0"
    res = await conn.fetch_one(query)
    return {"avg": res["avg"]}


async def get_count_by_oil_type(conn: Database):
    query = (
        "SELECT pu.oil_type, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "where a.asset_type=0 "
        "group by pu.oil_type"
    )
    res = await conn.fetch_all(query)
    res_dic = format_single_grouped_result(res=res, group_names=PumpUnit.OIL_TYPES)
    return res_dic


async def get_count_by_region_company(conn: Database):
    query = (
        "SELECT rc.name, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id join region_company rc on s.rc_id = rc.id "
        "where a.asset_type=0 "
        "group by rc.name"
    )
    res = await conn.fetch_all(query)
    return dict(res)


async def get_count_by_branch_company(conn: Database):
    query = (
        "SELECT bc.name, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id join branch_company bc on s.bc_id = bc.id "
        "where a.asset_type=0 "
        "group by bc.name"
    )
    res = await conn.fetch_all(query)
    return dict(res)


async def get_count_by_station(conn: Database):
    query = (
        "SELECT a.station_id as id, COUNT(*) as cnt, s.name as name "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id "
        "GROUP BY a.station_id"
    )
    res = await conn.fetch_all(query)
    station_mapper = {row["id"]: row["name"] for row in res}
    res_dic = format_single_grouped_result(res=res, group_names=station_mapper)
    return res_dic


async def get_count_by_asset_type(conn: Database):
    query = "SELECT asset_type, COUNT(*) as cnt " "FROM `asset` " "GROUP BY asset_type"
    res = await conn.fetch_all(query)
    res_dic = format_single_grouped_result(res=res, group_names=Asset.TYPES)
    return res_dic


async def get_count_by_isdomestic(conn: Database):
    query = (
        "SELECT pu.is_domestic, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "where a.asset_type=0 "
        "group by pu.is_domestic"
    )
    res = await conn.fetch_all(query)
    res_dic = format_single_grouped_result(
        res=res, group_names={0: "Improted", 1: "Domestic"}
    )
    return res_dic


async def get_count_by_manufacturer(conn: Database):
    query = (
        "SELECT m.name, COUNT(*) as cnt "
        "FROM `asset` "
        "join manufacturer m on asset.manufacturer_id = m.id "
        "where asset.asset_level=0 "
        "GROUP BY m.name"
    )
    res = await conn.fetch_all(query)
    return dict(res)


async def get_statu_count_by_station(conn: Database):
    query = (
        "SELECT station.NAME, statu, COUNT( * ),station.longitude, station.latitude AS cnt "
        "FROM `asset` "
        "JOIN station ON asset.station_id = station.id  "
        "WHERE asset.asset_level = 0 "
        "GROUP BY statu, station_id  "
        "ORDER BY statu"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_map_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_type(conn: Database):
    query = (
        "SELECT asset_type,statu, COUNT(*) as cnt "
        "FROM `asset` "
        "GROUP BY statu,asset_type "
        "ORDER BY statu"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=Asset.TYPES, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_province(conn: Database):
    query = (
        "SELECT s.location,a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id "
        "GROUP BY a.statu, s.location "
        "ORDER BY a.statu"
    )

    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )

    return formatted_res


async def get_statu_count_by_pipeline(conn: Database):
    query = (
        "SELECT p.name, a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "JOIN pipeline p on pu.pipeline_id = p.id "
        "where a.asset_type=0 "
        "group by a.statu, pu.pipeline_id "
        "ORDER BY a.statu"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_oiltype(conn: Database):
    query = (
        "SELECT pu.oil_type,a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "where a.asset_type=0 "
        "group by a.statu, pu.oil_type "
        "order by a.statu"
    )

    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=PumpUnit.OIL_TYPES, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_region_company(conn: Database):
    query = (
        "SELECT rc.name,a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id "
        "join region_company rc on s.rc_id = rc.id "
        "where a.asset_type=0 "
        "group by a.statu, rc.name "
        "order by a.statu"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_branch_company(conn: Database):
    query = (
        "SELECT bc.name,a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN station s on a.station_id = s.id "
        "join branch_company bc on s.bc_id = bc.id "
        "where a.asset_type=0 "
        "group by a.statu, bc.name"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_statu_count_by_isdomestic(conn: Database):
    query = (
        "SELECT pu.is_domestic,a.statu, COUNT(*) as cnt "
        "FROM asset a "
        "JOIN pump_unit pu on a.id = pu.asset_id "
        "where a.asset_type=0 "
        "group by a.statu, pu.is_domestic"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res,
        fisrt_group_names={0: "Imported", 1: "Domestic"},
        second_group_names=Asset.STATUS,
    )
    return formatted_res


async def get_statu_count_by_manufacturer(conn: Database):
    query = (
        "SELECT m.name,a.statu, COUNT(*) as cnt "
        "FROM `asset` a "
        "join manufacturer m on a.manufacturer_id = m.id "
        "where a.asset_level=0 "
        "GROUP BY a.statu,m.name"
    )
    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.STATUS
    )
    return formatted_res


async def get_type_count_by_station(conn: Database):
    query = (
        "SELECT  "
        "	s.name,  "
        "	a.asset_type,  "
        "	COUNT( * ) AS cnt   "
        "FROM  "
        "	asset a  "
        "Join station s on s.id = a.station_id  "
        "GROUP BY  "
        "	a.station_id,  "
        "	a.asset_type"
    )

    res = await conn.fetch_all(query)
    formatted_res = format_double_grouped_result(
        res, fisrt_group_names=None, second_group_names=Asset.TYPES
    )
    res_list = []
    for key in formatted_res.keys():
        formatted_res[key]["name"] = key
        res_list.append(formatted_res[key])
    # for i in range(5):
    #     res_list.append(res_list[0])
    query2 = "SELECT cr_time from asset order by cr_time desc limit 1"
    res2 = await conn.fetch_one(query2)

    return TypeStationSchema(res=res_list, update_time=res2["cr_time"])


crud_meth_mapper = {
    "statu": (get_count_by_statu,),
    "station": (
        get_count_by_station,
        get_statu_count_by_station,
        get_type_count_by_station,
    ),
    "type": (get_count_by_asset_type, get_statu_count_by_type),
    "province": (get_count_by_province, get_statu_count_by_province),
    "pipeline": (get_count_by_pipeline, get_statu_count_by_pipeline),
    "oil_type": (get_count_by_oil_type, get_statu_count_by_oiltype),
    "region_company": (get_count_by_region_company, get_statu_count_by_region_company),
    "branch_company": (get_count_by_branch_company, get_statu_count_by_branch_company),
    "isdomestic": (get_count_by_isdomestic, get_statu_count_by_isdomestic),
    "manufacturer": (get_count_by_manufacturer, get_statu_count_by_manufacturer),
    "avghi": (get_overall_avg,),
}
