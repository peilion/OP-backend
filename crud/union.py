import json

from databases import Database
from services.query_processors.warning import warning_description_formatter


async def get_recent_asset_event(conn: Database, asset_id: int):
    query = (
        "SELECT cr_time,description,'mainte' as t_name "
        "FROM `maintenance_record` WHERE asset_id = {0} "
        "UNION "
        "SELECT cr_time,description,'diagnosis_warning' as t_name "
        "FROM `warning_log` WHERE asset_id = {0} "
        "UNION "
        "SELECT cr_time,description,'mset_warning' as t_name "
        "FROM `mset_warning_log` WHERE asset_id = {0} "
        "ORDER BY cr_time desc "
        "limit 10".format(asset_id)
    )
    res = await conn.fetch_all(query)
    res = warning_description_formatter(res)
    return res


async def get_recent_warning(conn: Database):
    query = (
        "SELECT "
        "	warning_log.cr_time, "
        "	warning_log.description,"
        "   warning_log.severity as severity, "
        "	'diagnosis_warning' AS t_name, "
        "	asset.name AS asset_name  "
        "FROM "
        "	`warning_log` JOIN asset ON asset.id = warning_log.asset_id  "
        "UNION "
        "SELECT "
        "	mset_warning_log.cr_time, "
        "	mset_warning_log.description, "
        "   1 as severity, "
        "	'mset_warning' AS t_name,"
        "	asset.NAME AS asset_name  "
        "FROM "
        "	`mset_warning_log` JOIN asset ON asset.id = mset_warning_log.asset_id  "
        "ORDER BY "
        "	cr_time DESC  "
        "	LIMIT 10"
    )
    res = await conn.fetch_all(query)
    res = warning_description_formatter(res)
    return res


async def get_warning_table(conn: Database):
    query = (
        "SELECT "
        "	warning_log.id, "
        "	warning_log.cr_time, "
        "	warning_log.description,"
        "   warning_log.severity as severity, "
        "   warning_log.is_read as is_read, "
        "   measure_point.name as mp_name, "
        "   warning_log.data_id as data_id, "
        "	'diagnosis_warning' AS t_name, "
        "	asset.name AS asset_name,  "
        "	asset.mp_configuration AS mp_configuration,  "
        "	asset.id AS asset_id,  "
        "	measure_point.id AS mp_id  "
        "FROM "
        "	`warning_log` JOIN asset ON asset.id = warning_log.asset_id JOIN measure_point ON measure_point.id = warning_log.mp_id  "
        "UNION "
        "SELECT "
        "	mset_warning_log.id, "
        "	mset_warning_log.cr_time, "
        "	mset_warning_log.description, "
        "   1 as severity, "
        "   true as is_read, "
        "   null as mp_name, "
        "   mset_warning_log.reporter_id as data_id, "
        "	'mset_warning' AS t_name,"
        "	asset.NAME AS asset_name,  "
        "	asset.mp_configuration AS mp_configuration,  "
        "	asset.id AS asset_id,  "
        "	null AS mp_id  "

        "FROM "
        "	`mset_warning_log` JOIN asset ON asset.id = mset_warning_log.asset_id  "
        "ORDER BY "
        "	cr_time DESC  "
        "	LIMIT 200"
    )
    res = await conn.fetch_all(query)
    return res
