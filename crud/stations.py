from databases import Database
from sqlalchemy.orm import Session

from crud.base import con_warpper, query2sql
from custom_lib.treelib import Tree
from db.db_config import session_make
from db_model import Asset
from db_model.organization import Station, BranchCompany, RegionCompany


@con_warpper
async def get_multi(
    conn: Database, skip: int, limit: int, session: Session = session_make(engine=None)
):
    query = session.query(Station).order_by(Station.id).offset(skip).limit(limit)
    return await conn.fetch_all(query2sql(query))


@con_warpper
async def get(conn: Database, id: int, session: Session = session_make(engine=None)):
    query = session.query(Station).filter(Station.id == id)

    return await conn.fetch_one(query2sql(query))


@con_warpper
async def get_tree(conn: Database, session: Session = session_make(engine=None)):
    query1 = session.query(Station.id, Station.name, Station.bc_id)
    query2 = session.query(BranchCompany.id, BranchCompany.name, BranchCompany.rc_id)
    query3 = session.query(RegionCompany.id, RegionCompany.name)
    query4 = session.query(Asset.id, Asset.name, Asset.station_id).filter(
        Asset.asset_level == 0
    )
    assets = await conn.fetch_all(query2sql(query4))
    stations = await conn.fetch_all(query2sql(query1))
    bcs = await conn.fetch_all(query2sql(query2))
    rcs = await conn.fetch_all(query2sql(query3))

    tree = Tree()
    tree.create_node(tag="root", identifier="root")

    stations = [dict(row) for row in stations]
    bcs = [dict(row) for row in bcs]
    rcs = [dict(row) for row in rcs]
    assets = [dict(row) for row in assets]

    color = ["#2D5F73", "#538EA6", "#F2D1B3", "#F2B8A2", "#F28C8C"]
    import random

    random.choice(color)
    for item in assets:
        tree.create_node(
            data={
                "name": item["name"],
                "parent_st_id": item["station_id"],
                "value": 1,
                "itemStyle": {"color": random.choice(color)},
            },
            identifier="asset" + str(item["id"]),
            parent="root",
        )

    for item in stations:
        tree.create_node(
            data={
                "name": item["name"],
                "parent_bc_id": item["bc_id"],
                "itemStyle": {"color": random.choice(color)},
            },
            identifier="st" + str(item["id"]),
            parent="root",
        )

    for item in bcs:
        tree.create_node(
            data={
                "name": item["name"],
                "parent_rc_id": item["rc_id"],
                "itemStyle": {"color": random.choice(color)},
            },
            identifier="bc" + str(item["id"]),
            parent="root",
        )

    for item in rcs:
        tree.create_node(
            data={"name": item["name"], "itemStyle": {"color": random.choice(color)}},
            identifier="rc" + str(item["id"]),
            parent="root",
        )

    for node in tree.expand_tree(mode=Tree.WIDTH):
        if node != "root":
            if "parent_st_id" in tree[node].data:
                parent_node_id = "st" + str(tree[node].data["parent_st_id"])
                tree.move_node(node, parent_node_id)
                # tree[parent_node_id].data['value'] += 1
            if "parent_bc_id" in tree[node].data:
                parent_node_id = "bc" + str(tree[node].data["parent_bc_id"])
                tree.move_node(node, parent_node_id)
                # tree[parent_node_id].data['value'] += 1
            if "parent_rc_id" in tree[node].data:
                parent_node_id = "rc" + str(tree[node].data["parent_rc_id"])
                tree.move_node(node, parent_node_id)
                # tree[parent_node_id].data['value'] += 1

    return tree.to_dict(with_data=True)["children"]


@con_warpper
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


@con_warpper
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
