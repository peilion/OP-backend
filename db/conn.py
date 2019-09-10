from sqlalchemy import create_engine

meta_engine = create_engine('mysql://git:Fpl8315814.@123.56.7.137/op_meta?charset=utf8', encoding='utf-8',
                            pool_pre_ping=True)

station_engines = [
    create_engine('mysql://git:Fpl8315814.@123.56.7.137/op_1?charset=utf8', convert_unicode=True,
                  pool_pre_ping=True),
    create_engine('mysql://git:Fpl8315814.@123.56.7.137/op_2?charset=utf8', convert_unicode=True,
                  pool_pre_ping=True),
    create_engine('mysql://git:Fpl8315814.@123.56.7.137/op_3?charset=utf8', convert_unicode=True,
                  pool_pre_ping=True)]
