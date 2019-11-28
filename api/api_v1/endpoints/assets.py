from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from starlette.responses import UJSONResponse

from crud.assets import get_multi, get, get_info, create
from crud.assets_hi import (
    get_avg_hi_during_time,
    get_avg_hi_pre,
    get_avg_hi_before_limit,
    get_avg_hi_multi,
)
from crud.assets_stat import *
from custom_lib.treelib import Tree
from db import session_make
from db.conn_engine import meta_engine, META_URL
from model.assets import (
    FlattenAssetSchema,
    FlattenAssetListSchema,
    NestAssetSchema,
    AssetPostSchema,
)

router = APIRouter()

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
    "avghi":(get_overall_avg,)
}


class GroupRule(str, Enum):
    station = "station"
    statu = "statu"
    type = "type"
    province = "province"
    pipeline = "pipeline"
    oil_type = "oil_type"
    region_company = "region_company"
    branch_company = "branch_company"
    isdomestic = "isdomestic"
    manufacturer = "manufacturer"
    avghi = 'avghi'


@router.get("/", response_class=UJSONResponse)
async def read_assets(
        skip: int = None,
        limit: int = None,
        iftree: bool = False,
        type: int = None,
        level: int = None,
        station_name: str = None,
        station_id: int = None,
):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_multi(
        conn=conn,
        skip=skip,
        limit=limit,
        type=type,
        level=level,
        station_name=station_name,
        station_id=station_id,
    )
    if not iftree:
        return FlattenAssetListSchema(asset=items)
    elif iftree:
        tree = Tree()
        tree.create_node(tag="root", identifier="root")
        items = [dict(row) for row in items]
        for item in items:
            # For tree table editable fields
            item = {**item, "originalSTtime": item["st_time"], "edit": False}
            tree.create_node(data=item, identifier=item["id"], parent="root")

        for node in tree.expand_tree(mode=Tree.WIDTH):
            if node != "root":
                if tree[node].data["parent_id"]:
                    tree.move_node(node, tree[node].data["parent_id"])
        return tree.to_dict(with_data=True)["children"]
    # return NestAssetListSchema(asset=res)


@router.get("/stat/", response_class=UJSONResponse)
async def read_assets_statistic(group_by: List[GroupRule] = Query(None), ):
    """
    **Supported Query Mode** are listed follow, other query mode will be informed a 400 bad query parameter error.

    - One of the listed filed
    - Filed **'statu' and** one of the other fileds
    - Filed **'type' and 'station'**
    """
    conn = Database(META_URL)

    if len(group_by) == 1:
        crud_meth = crud_meth_mapper[group_by[0]][0]
        res = await crud_meth(conn=conn)
        return res

    elif len(group_by) == 2:
        if "statu" in group_by:
            group_by.pop(group_by.index("statu"))
            crud_meth = crud_meth_mapper[group_by[0]][1]
            res = await crud_meth(conn=conn)
            return res
        elif "type" in group_by:
            group_by.pop(group_by.index("type"))
            crud_meth = crud_meth_mapper[group_by[0]][2]
            res = await crud_meth(conn=conn)

            return res

    else:
        raise HTTPException(status_code=400, detail="Bad query parameter")


@router.get("/{id}/", response_class=UJSONResponse,response_model=FlattenAssetSchema)
async def read_by_id(id: int):
    """
    Get Asset by ID.
    """
    conn = Database(META_URL)
    res = await get(conn=conn, id=id)
    if not res:
        raise HTTPException(status_code=400, detail="Item not found")
    return res


@router.get("/{id}/info/", response_class=UJSONResponse)
async def read_asset_info(id: int, ):
    """
    Get Asset Info by ID.
    """
    conn = Database(META_URL)
    session = session_make(meta_engine)
    info = await get_info(session=session, conn=conn, id=id)
    if not info:
        raise HTTPException(
            status_code=400,
            detail="Item not found. / Asset Information have not been record.",
        )
    return dict(info)

@router.get("/{id}/avghi/", response_class=UJSONResponse)
async def read_asset_avghi(
        id: int,
        time_before: str = Query(None, description="e.x. 2016-07-01 00:00:00"),
        time_after: str = Query(None, description="e.x. 2016-01-10 00:00:00"),
        interval: int = None,
        limit: int = None,
        pre_query: bool = True,
):
    """
    Get avg Asset HI by time range and interval.
    """
    conn = Database(META_URL)
    if pre_query:
        res = await get_avg_hi_pre(conn=conn)
        return res
    if not pre_query:
        if (limit is not None) & (interval is not None):
            res = await get_avg_hi_before_limit(
                conn=conn, asset_id=id, interval=interval, limit=limit
            )

        elif (limit is None) & (interval is not None):
            res = await get_avg_hi_during_time(
                conn=conn,
                asset_id=id,
                time_before=time_before,
                time_after=time_after,
                interval=interval,
            )
        elif (limit is not None) & (interval is None):
            res = await get_avg_hi_multi(
                conn=conn, asset_id=id, time_before=time_before, limit=limit
            )

        if not res["time_list"]:
            raise HTTPException(
                status_code=400,
                detail="No health indicator calculated in the time range",
            )
        return res


@router.post("/", response_class=UJSONResponse)
async def create_asset(asset: AssetPostSchema):
    try:
        conn = Database(META_URL)
        res = await create(conn=conn, data = asset)
        if res == True:
            return {"msg": "Asset successfully added."}
        else:
            raise HTTPException(
                status_code=409, detail="Error happened when creating table."
            )
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Conflict asset already exsit in the database."
        )
    # finally:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Unexpected error.")
