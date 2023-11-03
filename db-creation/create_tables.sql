-- Country Table
CREATE TABLE Country (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- League Table
CREATE TABLE League (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    division INTEGER NOT NULL CHECK( division BETWEEN 1 AND 4 ),
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);

-- Season Table
CREATE TABLE Season (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL
);

-- Referee Table
CREATE TABLE Referee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);

-- Team Table
CREATE TABLE Team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);

-- Bookie Table
CREATE TABLE Bookie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Match Table
CREATE TABLE Match (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    referee_id INTEGER,
    date TEXT,
    time TEXT,
    ft_result TEXT NOT NULL CHECK( ft_result IN ('H', 'D', 'A') ),
    ht_result TEXT CHECK( ht_result IN ('H', 'D', 'A') ),
    FOREIGN KEY (league_id) REFERENCES League(id),
    FOREIGN KEY (season_id) REFERENCES Season(id),
    FOREIGN KEY (home_team_id) REFERENCES Team(id),
    FOREIGN KEY (away_team_id) REFERENCES Team(id),
    FOREIGN KEY (referee_id) REFERENCES Referee(id)
);

-- Odds Table
CREATE TABLE Odds (
    match_id INTEGER NOT NULL,
    bookie_id INTEGER NOT NULL,
    home_odds REAL NOT NULL,
    draw_odds REAL NOT NULL,
    away_odds REAL NOT NULL,
    PRIMARY KEY (match_id, bookie_id),
    FOREIGN KEY (match_id) REFERENCES Match(id),
    FOREIGN KEY (bookie_id) REFERENCES Bookie(id)
);

-- TeamMatchStats Table
CREATE TABLE TeamMatchStats (
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    is_home BOOLEAN NOT NULL,
    ft_goals INTEGER NOT NULL,
    ht_goals INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,
    corners INTEGER,
    fouls INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    PRIMARY KEY (match_id, team_id),
    FOREIGN KEY (match_id) REFERENCES Match(id),
    FOREIGN KEY (team_id) REFERENCES Team(id)
);