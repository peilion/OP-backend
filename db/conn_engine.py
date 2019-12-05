from sqlalchemy import create_engine

from core.config import DATABASE_CONNECTION_URL

META_URL = "mysql://{}/op_meta?charset=utf8".format(DATABASE_CONNECTION_URL)

INFO_URL = "mysql://{}/information_schema?charset=utf8".format(DATABASE_CONNECTION_URL)

meta_engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
