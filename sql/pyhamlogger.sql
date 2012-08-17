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
	`call` VARCHAR(20),
	freq VARCHAR(20),
	mode VARCHAR(10),
	operator VARCHAR(20),
	my_gridsquare CHAR(6),
	PRIMARY KEY (id_qso, id_log)
);

DROP TABLE IF EXISTS qsoadif;
CREATE TABLE qsoadif (
	id_qso CHAR(19),
	id_log INTEGER,
	id VARCHAR(255),
	description VARCHAR(255),
	appdefined INTEGER DEFAULT 0,
	PRIMARY KEY (id_qso, id_log, id)
);
