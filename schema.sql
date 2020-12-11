CREATE TABLE Users (
	id SERIAL PRIMARY KEY,
    	username TEXT UNIQUE,
    	password TEXT,
		admin INT DEFAULT 0
);
CREATE TABLE Teams (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	wins INT,
	losses INT
);
CREATE TABLE Players (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES Teams ON DELETE CASCADE,
    member_id INTEGER REFERENCES Users ON DELETE CASCADE
 );
CREATE TABLE Matches (
	id SERIAL PRIMARY KEY,
	team1_id INT REFERENCES Teams ON DELETE CASCADE,
	team2_id INT REFERENCES Teams ON DELETE CASCADE,
	home_points INT,
	away_points INT,
	date TIMESTAMP
);
CREATE TABLE Messages (
   	id SERIAL PRIMARY KEY,
  	user_id INT REFERENCES Users ON DELETE CASCADE,
    	match_id INT REFERENCES Matches ON DELETE CASCADE,
    	message TEXT,
    	date TIMESTAMP
);
CREATE TABLE Ratings (
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES Users ON DELETE CASCADE,
	match_id INT REFERENCES Matches ON DELETE CASCADE,
	rating INT,
	UNIQUE (user_id, match_id)
);
