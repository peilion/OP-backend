"""
Using this config by:

from db_config import session
session.query...    #do something

Making sure that the init_db method has been called before app run.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

table_args = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}

Base = declarative_base()


def session_make(engine) -> Session:
    # assert engine in [station_engines, meta_engine]
    session = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    return session()
