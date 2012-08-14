# configuration

#DB_PATH = "db/pyhamlogger.db"

# FIXME remove following block (used for DEV)
try:
    with open('db/pyhamlogger_DEV.db') as f: DB_PATH = "db/pyhamlogger_DEV.db"
except IOError as e:
    DB_PATH = "db/pyhamlogger.db"