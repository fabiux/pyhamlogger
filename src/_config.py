# configuration

#DB_PATH = "db/pyhamlogger.db"

# FIXME remove following block (used for DEV)
try:
    with open('db/pyhamlogger_DEV.db') as f: DB_PATH = "db/pyhamlogger_DEV.db"
except IOError as e:
    DB_PATH = "db/pyhamlogger.db"

# required ADIF fields
required_adif = ['qso_date', 'time_on', 'call', 'freq', 'mode', 'my_gridsquare']

# application-defined ADIF fields
appdefined_adif = []