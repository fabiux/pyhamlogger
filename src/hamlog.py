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

        except:
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
        except:
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

    def _qsoIsValid(self, qso):
        """Check if a QSO is valid.
        In order to log a QSO, some properties are required:
        qso_date, time_on, call, freq, mode, station_callsign and my_gridsquare.
        @param qso: the QSO to check
        @return: True if QSO is valid
        FIXME TODO more value checking?
        """
        if not 'station_callsign' in qso and not 'operator' in qso:
            return False

        for field in _config.required_adif:
            if not field in qso:
                return False

        return True

    def _normalizeQSO(self, qso):
        """Do some normalization in original QSO, according to ADIF specifications (v. 2.2.7).
        QSO must be previously checked as valid.
        Set `operator`, `station_callsign` and `owner_callsign` ADIF values.
        @param qso: QSO to normalize
        @return: normalized QSO
        FIXME TODO run test!
        """
        # `operator` or `station_callsign` exist
        if not 'operator' in qso:
            qso['operator'] = qso['station_callsign']
        elif not 'station_callsign' in qso:
            qso['station_callsign'] = qso['operator']

        if not 'owner_callsign' in qso:
            qso['owner_callsign'] = qso['station_callsign']

        return qso

    def _getQSOKey(self, qso):
        """Get primary key of QSO.
        @param qso: the QSO
        @return: primary key or False if error
        """
        try:
            pkdate = qso['qso_date']
            pktime = qso['time_on']
        except:
            return False

        # add more value checking?
        return pkdate[:4] + "-" + pkdate[4:6] + "-" + pkdate[6:8] + " " + pktime[:2] + ":" + pktime[2:4] + ":00"

    def _updateAdifFields(self, qso):
        """Update all ADIF fields for the specified QSO.
        qso already contains non-ADIF id_qso and id_log fields.
        @param qso: the QSO
        @return: True if no errors
        """
        pk = {}
        pk['id_qso'] = qso['id_qso']
        pk['id_log'] = qso['id_log']
        del(qso['id_qso'])
        del(qso['id_log'])
        try:
            with self._conn:
                self._doQuery("DELETE FROM qsoadif WHERE (id_qso = :idqso) AND (id_log = :idlog)", pk)
                for k in qso:
                    if not k in _config.required_adif:
                        params = pk
                        params['id'] = k
                        params['description'] = qso[k]
                        if k in _config.appdefined_adif:
                            params['appdefined'] = 1
                        else:
                            params['appdefined'] = 0
                        self._doQuery("INSERT INTO qsoadif VALUES (:id_qso, :id_log, :id, :description, :appdefined)", params)
        except:
            return False

        return True

    def addOrUpdateQSO(self, qso, logid):
        """Add or update a QSO to a log.
        If QSO already exists, then update its properties.
        About related QSO tables in database:
        - `qso`: this is the main header table which contains mandatory ADIF fields,
        plus primary key fields;
        - `qsoadif`: for each QSO, this table contains all related ADIF fields;
        for application-defined fields this value must be set to 1 (True)
        @param qso: QSO object
        @param logid: existing log id
        @return: False if errors
        """
        qso = dict((k.lower(), qso[k]) for k in qso)
        if not self._qsoIsValid(qso):
            return False

        qso = self._normalizeQSO(qso)
        pk = self._getQSOKey(qso)
        qso['id_qso'] = pk
        qso['id_log'] = str(logid)

        try:
            with self._conn:
                self._doQuery("DELETE FROM qso WHERE (id_qso = :id_qso) AND (id_log = :id_log)", pk)
                self._doQuery("INSERT INTO qso VALUES (:id_qso, :id_log, :call, :freq, :mode, :operator, :my_gridsquare)", qso)
                self._updateAdifFields(qso)
        except:
            return False

        return True

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
            self.addOrUpdateQSO(qsos[i], logid)
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

    def deleteQSO(self, qsoid, logid):
        """Delete QSO from a log.
        @param qsoid: existing QSO id
        @param logid: existing log id
        @return: False if error
        """
        sql = []
        sql.append("DELETE FROM qso WHERE (id_qso = :qsoid) AND (id_log = :logid)")
        sql.append("DELETE FROM qsoadif WHERE (id_qso = :qsoid) AND (id_log = :logid)")
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
        return self._doQuery(sql, {'logid': str(logid)})