from sqlalchemy import Table, MetaData
from db_config import engine, SHARDING_NUMBER
from sqlalchemy import text

metadata = MetaData()


def get_table_hash(motor_id):
    return motor_id % SHARDING_NUMBER


def get_statu_statistic():
    s = text('SELECT STATU, COUNT(*) FROM `motor` GROUP BY statu')
    conn = engine.connect()
    result = conn.execute(s)
    data = result.fetchall()
    result.close()
    return {row.values()[0]: row.values()[1] for row in data}


def get_comp_statistic():
    s = text(
        'SELECT m.id, m.name, '
        '( SELECT COUNT( * ) FROM bearing b WHERE b.motor_id = m.id ) as nb, '
        '( SELECT COUNT( * ) FROM rotor r WHERE r.motor_id = m.id ) as nr, '
        '( SELECT COUNT( * ) FROM stator s WHERE s.motor_id = m.id ) as ns '
        'FROM motor m GROUP BY m.id')
    conn = engine.connect()
    result = conn.execute(s)
    data = result.fetchall()
    result.close()
    return [{key: value for key, value in zip(row.keys(), row.values())} for row in data]


def get_warning_calendar():
    s = text('SELECT date(warninglog.cr_time) as date ,count(*) as num '
             'from warninglog '
             'GROUP BY date(warninglog.cr_time)')
    conn = engine.connect()
    result = conn.execute(s)
    data = result.fetchall()
    result.close()
    return [[row.values()[0].strftime('%Y-%m-%d'), row.values()[1]] for row in data]


def get_motor_trend(id, args):
    table_hash = get_table_hash(id)

    fields = ''
    for item in args['feature'].split(','):
        if item in ['rms', 'thd', 'max_current', 'min_current']:
            fields = fields + 'f.u' + item + ',' + \
                     'f.v' + item + ',' + \
                     'f.w' + item + ','
        else:
            fields = fields + 'f.' + item + ','
    fields = fields.rstrip(',')

    s = text(
        'SELECT elec.time as time,{0} from elecdata_{1} as elec '
        'LEFT OUTER JOIN feature_{1} as f on (elec.id = f.data_id)'
        'where elec.time between :timeafter and :timebefore;'.format(fields, table_hash))
    conn = engine.connect()
    query = conn.execute(s, timeafter=args['timeafter'], timebefore=args['timebefore'])
    result = query.fetchall()
    query.close()
    return result
    # result = conn.execute(s, :th = table_hash)


def get_motor_phase(id, args):
    table_hash = get_table_hash(id)
    fields = ''
    for phase in args['phase']:
        fields = fields + '{0}.wave as {0},'.format(phase)

    s = text('SELECT pack.id as id from currentspack_0 as pack '
             'INNER JOIN uphase_0 u on pack.id = u.pack_id '
             'INNER JOIN vphase_0 v on pack.id = v.pack_id '
             'INNER JOIN wphase_0 w on pack.id = w.pack_id '
             'WHERE pack.motor_id=:id '
             'ORDER BY pack.id desc '
             'LIMIT 1'
             )
