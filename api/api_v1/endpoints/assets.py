from enum import Enum
from typing import List

from databases import Database
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import UJSONResponse
from treelib import Tree

from crud.assets import get_multi, get, get_tree, get_count_by_statu, get_count_by_station, \
    get_count_by_both, get_info
from db import session_make
from db.conn_engine import meta_engine, META_URL
from model.assets import FlattenAssetSchema, FlattenAssetListSchema, NestAssetSchema, StatuStatisticSchema, \
    StationStatisticSchema

router = APIRouter()


class GroupRule(str, Enum):
    station = "station"
    statu = "statu"


@router.get("/", response_class=UJSONResponse)
async def read_assets(
        skip: int = None,
        limit: int = None,
        iftree: bool = False,
):
    """
    Get Asset List.
    """
    conn = Database(META_URL)
    items = await get_multi(conn=conn, skip=skip, limit=limit)
    if not iftree:
        return FlattenAssetListSchema(asset=items)
    elif iftree:
        tree = Tree()
        tree.create_node(tag='root', identifier='root')
        items = [dict(row) for row in items]
        for item in items:
            tree.create_node(data=item, identifier=item['id'], parent='root')

        for node in tree.expand_tree(mode=Tree.WIDTH):
            if node != 'root':
                if tree[node].data['parent_id']:
                    tree.move_node(node, tree[node].data['parent_id'])
        return tree.to_dict(with_data=True)['root']['children']
    # return NestAssetListSchema(asset=res)


@router.get("/stat/", response_class=UJSONResponse)
async def read_assets_statistic(
        group_by: List[GroupRule] = Query(None),
):
    try:
        if len(group_by) == 1:
            if group_by[0] == GroupRule.statu:
                conn = Database(META_URL)
                res = await get_count_by_statu(conn=conn)
                return StatuStatisticSchema.parse_obj(res)
            elif group_by[0] == GroupRule.station:
                conn = Database(META_URL)
                res = await get_count_by_station(conn=conn)
                return StationStatisticSchema(res=res)
        elif len(group_by) == 2:
            conn = Database(META_URL)
            res = await get_count_by_both(conn=conn)
            return res
    except:
        raise HTTPException(status_code=400, detail="Bad query parameter")


@router.get("/{id}/", response_class=UJSONResponse)
async def read_by_id(
        id: int,
        iftree: bool = False
):
    """
    Get Asset by ID.
    """
    if not iftree:
        conn = Database(META_URL)
        item = await get(conn=conn, id=id)
        if not item:
            raise HTTPException(status_code=400, detail="Item not found")
        return FlattenAssetSchema(**item)
    elif iftree:
        session = session_make(meta_engine)
        item = get_tree(session=session, id=id)
        return NestAssetSchema.from_orm(item)


@router.get("/{id}/info/", response_class=UJSONResponse)
async def read_asset_info(
        id: int,
):
    """
    Get Asset Info by ID.
    """
    conn = Database(META_URL)
    session = session_make(meta_engine)
    info = await get_info(session=session,conn=conn,id=id)
    if not info:
        raise HTTPException(status_code=400, detail="Item not found. / Asset Information have not been record.")
    return dict(info)