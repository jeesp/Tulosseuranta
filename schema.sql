CREATE TABLE users (
	id SERIAL PRIMARY KEY,
    	username TEXT UNIQUE,
    	password TEXT,
		admin INT DEFAULT 0
);
CREATE TABLE Joukkueet (
	id SERIAL PRIMARY KEY,
	nimi TEXT UNIQUE,
	voitot INT,
	haviot INT
);
CREATE TABLE Joukkueidenpelaajat (
    id SERIAL PRIMARY KEY,
    joukkue_id INTEGER REFERENCES Joukkueet,
    jasen_id INTEGER REFERENCES users
 );
CREATE TABLE Ottelut (
	id SERIAL PRIMARY KEY,
	joukkue1_id INT REFERENCES Joukkueet,
	joukkue2_id INT REFERENCES Joukkueet,
	pisteet_koti INT,
	pisteet_vieras INT,
	ajankohta TIMESTAMP
);
CREATE TABLE kommentit (
   	id SERIAL PRIMARY KEY,
  	kayttaja_id INT REFERENCES users,
    	ottelu_id INT REFERENCES Ottelut,
    	viesti TEXT,
    	aika TIMESTAMP
);
CREATE TABLE Arviot (
	id SERIAL PRIMARY KEY,
	kayttaja_id INT REFERENCES users,
	ottelu_id INT REFERENCES Ottelut,
	arvio INT,
	UNIQUE (kayttaja_id, ottelu_id)
);
