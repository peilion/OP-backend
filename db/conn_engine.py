from sqlalchemy import create_engine
from core.config import DATABASE_CONNECTION_URL


META_URL = "mysql://{}/op_meta?charset=utf8".format(DATABASE_CONNECTION_URL)
STATION_URLS = [
    "mysql://{0}/equip_{1}?charset=utf8".format(DATABASE_CONNECTION_URL,i) for i in range(1,7)
]
INFO_URL = "mysql://{}/information_schema?charset=utf8".format(DATABASE_CONNECTION_URL)
TEST_META_URL = "mysql://{}/tmp_op_meta?charset=utf8".format(DATABASE_CONNECTION_URL)

meta_engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
test_meta_engine = create_engine(TEST_META_URL, encoding="utf-8", pool_pre_ping=True)
station_engines = [
    create_engine(url, convert_unicode=True, pool_pre_ping=True) for url in STATION_URLS
]
