from databases import Database
from services.query_processors.warning import warning_description_formatter


async def get_recent_asset_event(conn: Database, asset_id: int):
    query = (
        "SELECT cr_time,description,'mainte' as t_name "
        "FROM `maintenance_record` WHERE asset_id = {0} "
        "UNION "
        "SELECT cr_time,description,'warning' as t_name "
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
        "	'warning' AS t_name, "
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
