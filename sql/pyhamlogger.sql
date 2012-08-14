DROP TABLE IF EXISTS logs;
CREATE TABLE logs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR(255),
	description VARCHAR(255)
);

DROP TABLE IF EXISTS qso;
CREATE TABLE qso (
	id_qso CHAR(19),
	id_log INTEGER,
	CALL VARCHAR(20),
	FREQ VARCHAR(20),
	MODE VARCHAR(10),
	STATION_CALLSIGN VARCHAR(20),
	MY_GRIDSQUARE CHAR(6),
	PRIMARY KEY (id_qso, id_log)
);

DROP TABLE IF EXISTS qsoadif;
CREATE TABLE qsoadif (
	id_qso CHAR(19),
	id_log INTEGER,
	id VARCHAR(255),
	description VARCHAR(255),
	PRIMARY KEY (id_qso, id_log, id)
);

DROP TABLE IF EXISTS qsoprops;
CREATE TABLE qsoprops (
	id_qso CHAR(19),
	id_log INTEGER,
	dxcc_entity CHAR(3),
	PRIMARY KEY (id_qso, id_log)
);

DROP TABLE IF EXISTS qsl;
CREATE TABLE qsl (
	id_qso CHAR(19),
	id_log INTEGER,
	direct INTEGER,
	eqsl INTEGER,
	lotw INTEGER,
	direct_sent INTEGER,
	PRIMARY KEY (id_qso, id_log)
);
