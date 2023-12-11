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
# Will be able to search teams by name
create_index_team_name = """
CREATE INDEX idx_team_name ON Team (name);
"""

# Combined Match and TeamMatchStats tables into one
# Reduces the number of joins required to get all the data
# Allows triggers to be used to ensure data integrity
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
    h_ft_goals INTEGER NOT NULL,
    a_ft_goals INTEGER NOT NULL,
    h_ht_goals INTEGER,
    a_ht_goals INTEGER,
    h_shots INTEGER,
    a_shots INTEGER,
    h_shots_on_target INTEGER,
    a_shots_on_target INTEGER,
    h_corners INTEGER,
    a_corners INTEGER,
    h_fouls INTEGER,
    a_fouls INTEGER,
    h_yellow_cards INTEGER,
    a_yellow_cards INTEGER,
    h_red_cards INTEGER,
    a_red_cards INTEGER,
    FOREIGN KEY (league_id) REFERENCES League(id),
    FOREIGN KEY (season_id) REFERENCES Season(id),
    FOREIGN KEY (home_team_id) REFERENCES Team(id),
    FOREIGN KEY (away_team_id) REFERENCES Team(id),
    FOREIGN KEY (referee_id) REFERENCES Referee(id)
);
"""

result_triggers_data = [
    ("ft", "UPDATE"),
    ("ht", "UPDATE"),
    ("ft", "INSERT"),
    ("ht", "INSERT"),
]

result_triggers = []

# Write triggers for all combinations of result and insert/update
for time, action in result_triggers_data:
    create_trigger = f"""
    CREATE TRIGGER ensure_{time}_result_in_range_{action.lower()}
    BEFORE {action} ON Match
    FOR EACH ROW
    BEGIN
        SELECT 
        CASE
            WHEN NEW.h_{time}_goals > NEW.a_{time}_goals AND NEW.{time}_result != 'H' THEN
                RAISE(FAIL, 'Result must be H if home team scored more goals')
            WHEN NEW.h_{time}_goals < NEW.a_{time}_goals AND NEW.{time}_result != 'A' THEN
                RAISE(FAIL, 'Result must be A if away team scored more goals')
            WHEN NEW.h_{time}_goals = NEW.a_{time}_goals AND NEW.{time}_result != 'D' THEN
                RAISE(FAIL, 'Result must be D if both teams scored the same number of goals')
        END;
    END;
    """
    result_triggers.append(create_trigger)

# Will often be querying/joining by league_id, season_id, home_team_id, away_team_id
match_indicies = [
    "CREATE INDEX idx_match_league_id ON Match (league_id);",
    "CREATE INDEX idx_match_season_id ON Match (season_id);",
    "CREATE INDEX idx_match_home_team_id ON Match (home_team_id);",
    "CREATE INDEX idx_match_away_team_id ON Match (away_team_id);",
]


create_table_odds = """
CREATE TABLE Odds (
    match_id INTEGER NOT NULL,
    bookie_id INTEGER NOT NULL,
    home_odds REAL NOT NULL,
    draw_odds REAL NOT NULL,
    away_odds REAL NOT NULL,
    PRIMARY KEY (match_id, bookie_id),
    FOREIGN KEY (match_id) REFERENCES Match(id) ON DELETE CASCADE,
    FOREIGN KEY (bookie_id) REFERENCES Bookie(id)
);
"""

# Will often be querying/joining by match_id, bookie_id
create_index_match_id = "CREATE INDEX idx_odds_match_id ON Odds (match_id);"

cursor.execute(create_table_country)
cursor.execute(create_table_season)
cursor.execute(create_table_bookie)
cursor.execute(create_table_referee)
cursor.execute(create_table_league)
cursor.execute(create_table_team)
cursor.execute(create_index_team_name)
cursor.execute(create_table_match)
for trigger in result_triggers:
    cursor.execute(trigger)
for index in match_indicies:
    cursor.execute(index)
cursor.execute(create_table_odds)
cursor.execute(create_index_match_id)

conn.commit()

conn.close()
