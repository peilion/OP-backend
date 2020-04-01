from enum import Enum
from typing import List

from databases import Database
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import ORJSONResponse

from core.dependencies import get_db
from crud.assets_stat import crud_meth_mapper

router = APIRouter()


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
    avghi = "avghi"


@router.get("/stat/", response_class=ORJSONResponse)
async def read_assets_statistic(
    group_by: List[GroupRule] = Query(None), conn: Database = Depends(get_db)
):
    """
    **Supported Query Mode** are listed follow, other query mode will be informed a 400 bad query parameter error.

    - One of the listed filed
    - Filed **'statu' and** one of the other fileds
    - Filed **'type' and 'station'**
    """

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
