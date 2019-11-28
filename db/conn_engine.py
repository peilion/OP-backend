from sqlalchemy import create_engine
from core.config import DATABASE_LOCALTION

UPH = ''
if DATABASE_LOCALTION == 'REMOTE':
    UPH = 'git:Fpl8315814.@123.56.7.137'
elif DATABASE_LOCALTION =='LOCAL':
    UPH = 'root:8315814@127.0.0.1'

META_URL = "mysql://{}/op_meta?charset=utf8".format(UPH)
STATION_URLS = [
    "mysql://{}/op_1?charset=utf8".format(UPH),
    "mysql://{}/op_2?charset=utf8".format(UPH),
    "mysql://{}/op_3?charset=utf8".format(UPH),
]
INFO_URL = "mysql://{}/information_schema?charset=utf8".format(UPH)
TEST_META_URL = "mysql://{}/tmp_op_meta?charset=utf8".format(UPH)

meta_engine = create_engine(META_URL, encoding="utf-8", pool_pre_ping=True)
test_meta_engine = create_engine(TEST_META_URL, encoding="utf-8", pool_pre_ping=True)
station_engines = [
    create_engine(STATION_URLS[0], convert_unicode=True, pool_pre_ping=True),
    create_engine(STATION_URLS[1], convert_unicode=True, pool_pre_ping=True),
    create_engine(STATION_URLS[2], convert_unicode=True, pool_pre_ping=True),
]
