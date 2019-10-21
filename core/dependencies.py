from db import session_make, meta_engine
from db_model import MeasurePoint

measure_point_regsiter = {}

def get_mp_mapper():
    if len(measure_point_regsiter) == 0:
        session = session_make(meta_engine)
        res = session.query(MeasurePoint.id, MeasurePoint.station_id, MeasurePoint.id_inner_station,MeasurePoint.type).all()
        for row in res:
            measure_point_regsiter[row.id] = {'station_id': row.station_id, 'inner_id': row.id_inner_station,'type':row.type}
        session.close()
    return measure_point_regsiter

def mp_change_commit():
    measure_point_regsiter = {}