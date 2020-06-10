from sqlalchemy.dialects import mysql
from sqlalchemy.orm.query import Query


def con_warpper(func):
    async def make_decorater(*args, **kwargs):
        await kwargs["conn"].connect()
        function = await func(*args, **kwargs)
        await kwargs["conn"].disconnect()
        return function

    return make_decorater


def query2sql(query: Query):
    return str(
        query.statement.compile(
            dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


def multi_result_to_array(res, ignore_filed: tuple = ()):
    dic = {}
    keys = res[0].keys()
    for row in res:
        for key in keys:
            if key == "time":
                dic.setdefault(key, []).append(str(row[key]))
            elif key in ignore_filed:
                continue
            else:
                dic.setdefault(key, []).append(row[key])
    return dic
