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
