import sqlite3

# Connect to a database (or create it if it doesn't exist)
conn = sqlite3.connect("../soccer.db")
cursor = conn.cursor()

create_table_country = """
CREATE TABLE Country (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
"""

create_table_season = """
CREATE TABLE Season (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL
);
"""

create_table_bookie = """
CREATE TABLE Bookie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
"""

create_table_referee = """
CREATE TABLE Referee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);
"""

create_table_league = """
CREATE TABLE League (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    division INTEGER NOT NULL CHECK( division BETWEEN 1 AND 4 ),
    FOREIGN KEY (country_id) REFERENCES Country(id)
);
"""

create_table_team = """
CREATE TABLE Team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);
"""

create_table_match = """
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
"""

create_table_odds = """
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
"""

create_table_team_match_stats = """
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
"""

cursor.execute(create_table_country)
cursor.execute(create_table_season)
cursor.execute(create_table_bookie)
cursor.execute(create_table_referee)
cursor.execute(create_table_league)
cursor.execute(create_table_team)
cursor.execute(create_table_match)
cursor.execute(create_table_odds)
cursor.execute(create_table_team_match_stats)

conn.commit()

conn.close()
