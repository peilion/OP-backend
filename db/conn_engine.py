from sqlalchemy import create_engine

META_URL = 'mysql://git:Fpl8315814.@123.56.7.137/op_meta?charset=utf8'
STATION_URLS = ['mysql://git:Fpl8315814.@123.56.7.137/op_1?charset=utf8',
                'mysql://git:Fpl8315814.@123.56.7.137/op_2?charset=utf8',
                'mysql://git:Fpl8315814.@123.56.7.137/op_3?charset=utf8']
INFO_URL = 'mysql://git:Fpl8315814.@123.56.7.137/information_schema?charset=utf8'
TEST_META_URL = 'mysql://git:Fpl8315814.@123.56.7.137/tmp_op_meta?charset=utf8'


meta_engine = create_engine(META_URL, encoding='utf-8',
                            pool_pre_ping=True)
test_meta_engine= create_engine(TEST_META_URL, encoding='utf-8',
                            pool_pre_ping=True)
station_engines = [
    create_engine(STATION_URLS[0], convert_unicode=True,
                  pool_pre_ping=True ),
    create_engine(STATION_URLS[1], convert_unicode=True,
                  pool_pre_ping=True),
    create_engine(STATION_URLS[2], convert_unicode=True,
                  pool_pre_ping=True)]
