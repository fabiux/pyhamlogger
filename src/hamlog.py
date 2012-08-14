'''
@author: Fabio Pani (IZ2UQF)
@version: 0.1 [DEV]
'''

import types
import sqlite3 as sqlite
import _config
import adif

class Hamlog():
    '''This class defines a hamradio log object.
    '''
    _conn = None

    def __init__(self, db=_config.DB_PATH):      # FIXME create file if it doesn't exist
        '''Constructor.
        Connect to database.
        @param db: database file path
        '''
        try:
            self._conn = sqlite.connect(db)

        except sqlite.Error, e:
            pass    # FIXME error reporting?

    def __del__(self):
        '''Destructor.
        Close database connection.
        '''
        if self._conn:
            self._conn.close()

    def _doQuery(self, sql, params={}):
        """Execute an SQL statement (or a list of statements).
        Autocommit/rollback.
        @param sql: SQL statement(s) (single statement or list of)
        @param params: optional SQL parameters (the same one for SQL statement list)
        @return: cursor or False if error
        """
        if not self._conn:
            return False

        cur = self._conn.cursor()

        try:
            with self._conn:
                if isinstance(sql, types.StringTypes):
                    cur.execute(sql, params)
                else:
                    for stat in sql:
                        cur.execute(stat, params)
        except sqlite.Error, e:
            return False

        return cur

    def _recordExists(self, sql, params):
        """Check if a record exists.
        @param sql: SQL statement
        @param params: SQL parameters
        @return: True if record exists
        """
        cur = self._doQuery(sql, params)
        if not cur:
            return False

        row = cur.fetchone()
        if row == None:
            return False
        else:
            return row[0] > 0

    def _logExists(self, logid):
        """Check if a log exists.
        @param logid: log id
        @return: True if log exists
        """
        return self._recordExists("SELECT COUNT(*) AS tot FROM logs WHERE id = :logid", {'logid': str(logid)})

    def _qsoExists(self, qsoid, logid):
        """Tell if a QSO exists
        @param qsoid: QSO id
        @param logid: existing log id
        @return: True if QSO exists
        """
        return self._recordExists("SELECT COUNT(*) AS tot FROM qso WHERE (id_qso = :qsoid) AND (id_log = :logid)", {'qsoid': qsoid, 'logid': str(logid)})

    def _getQSOKey(self, qso):
        """Get primary key of QSO.
        @param qso: the QSO
        @return: primary key or False if error
        FIXME error management
        """
        try:
            pkdate = qso['qso_date']
            pktime = qso['time_on']
        except KeyError as e:
            return False

        # add more value checking
        return pkdate[:4] + "-" + pkdate[4:6] + "-" + pkdate[6:8] + " " + pktime[:2] + ":" + pktime[2:4] + ":00"

    def importFromAdif(self, filename, logid):
        """Import a log from an ADIF file and store QSOs in database.
        Always merge data.
        @param filename: source ADIF file path and name
        @param logid: existing log id
        @return: True if no errors (?) FIXME
        """
        # check if logid is valid = check if log exists
        if not self._logExists(logid):
            return False

        if not self._conn:
            return False

        qsos = adif.adiParse(filename)
        for i in range(len(qsos)):
            self.addQSO(qsos[i], logid)
        return True

    def exportToAdif(self, filename, logid):
        """Export a log from database into an ADIF file
        @param filename: destination ADIF file path and name
        @param logid: existing log id
        @return: True if no errors
        FIXME TODO
        """
        if not self._conn:
            return False

        return True

    def addQSO(self, qso, logid):
        """Add or update a QSO to a log.
        If QSO already exists, then update its properties.
        @param qso: QSO object
        @param logid: existing log id
        @return: False if errors
        FIXME TODO
        """
        # FIXME: check if QSO is valid (?)
        qso = dict((k.lower(), qso[k]) for k in qso)
        pk = self._getQSOKey(qso)
        if self._qsoExists(pk, logid):
            # FIXME update QSO TODO
            print pk
        else:
            # FIXME add new QSO
            return self._doQuery("INSERT INTO qso (id_qso, id_log) VALUES (:pk, :logid)", {'pk': pk, 'logid': str(logid)})

    def deleteQSO(self, qsoid, logid):
        """Delete QSO from a log.
        @param qsoid: existing QSO id
        @param logid: existing log id
        @return: False if error
        """
        sql = []
        sql.append("DELETE FROM qso WHERE (id_qso = :qsoid) AND (id_log = :logid)")
        sql.append("DELETE FROM qsoadif WHERE (id_qso = :qsoid) AND (id_log = :logid)")
        sql.append("DELETE FROM qsoprops WHERE (id_qso = :qsoid) AND (id_log = :logid)")
        sql.append("DELETE FROM qsl WHERE (id_qso = :qsoid) AND (id_log = :logid)")
        return self._doQuery(sql, {'qsoid': qsoid, 'logid': str(logid)})

    def addLog(self, name, description):
        """Add a new log in the database.
        @param name: log name
        @param description: log description
        @return: False if error
        """
        return self._doQuery("INSERT INTO logs (name, description) VALUES (:name, :description)", {'name': name, 'description': description})

    def deleteLog(self, logid):
        """Delete a log and all related entries (QSOs) from database.
        @param logid: log id
        @return: False if error
        """
        sql = []
        sql.append("DELETE FROM logs WHERE id = :logid")
        sql.append("DELETE FROM qso WHERE id_log = :logid")
        sql.append("DELETE FROM qsoadif WHERE id_log = :logid")
        sql.append("DELETE FROM qsoprops WHERE id_log = :logid")
        sql.append("DELETE FROM qsl WHERE id_log = :logid")
        return self._doQuery(sql, {'logid': str(logid)})