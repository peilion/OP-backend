from sqlalchemy import create_engine
from core.config import DATABASE_CONNECTION_URL


META_URL = "mysql://{}/op_meta?charset=utf8".format(DATABASE_CONNECTION_URL)
STATION_URLS = [
    "mysql://{}/op_1?charset=utf8".format(DATABASE_CONNECTION_URL),
    "mysql://{}/op_2?charset=utf8".format(DATABASE_CONNECTION_URL),
    "mysql://{}/op_3?charset=utf8".format(DATABASE_CONNECTION_URL),
]
INFO_URL = "mysql://{}/information_schema?charset=utf8".format(DATABASE_CONNECTION_URL)
TEST_META_URL = "mysql://{}/tmp_op_meta?charset=utf8".format(DATABASE_CONNECTION_URL)

meta_engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
test_meta_engine = create_engine(TEST_META_URL, encoding="utf-8", pool_pre_ping=True)
station_engines = [
    create_engine(STATION_URLS[0], convert_unicode=True, pool_pre_ping=True),
    create_engine(STATION_URLS[1], convert_unicode=True, pool_pre_ping=True),
    create_engine(STATION_URLS[2], convert_unicode=True, pool_pre_ping=True),
]
