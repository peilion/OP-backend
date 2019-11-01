from databases import Database

from crud.decorator import con_warpper


@con_warpper
async def get_warning_and_maintenace(conn: Database, asset_id: int):
    query = (
        "SELECT cr_time,description,'mainte' as t_name "
        "FROM `maintenance_record` WHERE asset_id = {0} "
        "UNION "
        "SELECT cr_time,description,'warning' as t_name "
        "FROM `warning_log` WHERE asset_id = {0} "
        "ORDER BY cr_time desc "
        "limit 10".format(asset_id)
    )
    res = await conn.fetch_all(query)
    return res
