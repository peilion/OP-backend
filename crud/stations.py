from databases import Database
from sqlalchemy.orm import Session

from crud.base import query2sql
from custom_lib.treelib import Tree
from db.db_config import session_make
from db_model import Asset
from db_model.organization import Station, BranchCompany, RegionCompany


async def get_multi(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = session.query(Station).order_by(Station.id).offset(skip).limit(limit)
    return await conn.fetch_all(query2sql(query))


async def get_weathers(conn: Database, session: Session = session_make(engine=None)):
    query = session.query(Station.id, Station.name, Station.weather).order_by(
        Station.id
    )
    return await conn.fetch_all(query2sql(query))


async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session.query(Station).filter(Station.id == id)

    return await conn.fetch_one(query2sql(query))


async def get_tree(conn: Database, session: Session = session_make(engine=None)):
    assets = await conn.fetch_all(
        query2sql(
            session.query(
                Asset.id, Asset.name, Asset.station_id.label("parent_id")
            ).filter(Asset.asset_level == 0)
        )
    )
    stations = await conn.fetch_all(
        query2sql(
            session.query(Station.id, Station.name, Station.bc_id.label("parent_id"))
        )
    )
    bcs = await conn.fetch_all(
        query2sql(
            session.query(
                BranchCompany.id,
                BranchCompany.name,
                BranchCompany.rc_id.label("parent_id"),
            )
        )
    )
    rcs = await conn.fetch_all(
        query2sql(session.query(RegionCompany.id, RegionCompany.name))
    )

    tree = Tree()
    tree.create_node(tag="root", identifier="root")

    def item_maker(item, parent_type, self_type, color, value):
        temp = dict(item)
        if parent_type:
            temp["parent_id"] = parent_type + str(temp["parent_id"])
        if self_type == "asset":
            temp["value"] = 1
        temp["id"] = self_type + str(temp["id"])
        temp["itemStyle"] = {"color": color}
        temp["am_value"] = value
        return temp

    color = ["#1a8bff", "#51a2f7", "#79b8ff", "#93ccff"]
    assets = [item_maker(row, "st", "asset", color[3], 40) for row in assets]
    stations = [item_maker(row, "bc", "st", color[2], 60) for row in stations]
    bcs = [item_maker(row, "rc", "bc", color[1], 80) for row in bcs]
    rcs = [item_maker(row, None, "rc", color[0], 130) for row in rcs]

    for item in rcs + bcs + stations + assets:
        tree.create_node(
            data=item,
            identifier=item["id"],
            parent=item["parent_id"] if "parent_id" in item else "root",
        )

    return tree.to_dict(with_data=True)["children"]


async def get_bc(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = (
        session.query(BranchCompany)
        .order_by(BranchCompany.id)
        .offset(skip)
        .limit(limit)
    )
    return await conn.fetch_all(query2sql(query))


async def get_rc(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = (
        session.query(RegionCompany)
        .order_by(RegionCompany.id)
        .offset(skip)
        .limit(limit)
    )
    return await conn.fetch_all(query2sql(query))
