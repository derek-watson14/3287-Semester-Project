# import sqlite3
# import json

# with open("../data-gathering/json/strong_entities.json", "r") as file:
#     strong = json.load(file)

# with open("../data-gathering/json/weak_entities.json", "r") as file:
#     weak = json.load(file)

# # Get the records to insert for STRONG ENTITES
# countries = strong["Country"]["instances"]
# countries_to_insert = [(entry["id"], entry["name"]) for entry in countries]

# leagues = strong["League"]["instances"]
# leagues_to_insert = [
#     (entry["id"], entry["name"], entry["division"], entry["country_id"]) for entry in leagues
# ]

# seasons = strong["Season"]["instances"]
# seasons_to_insert = [
#     (entry["id"], entry["name"], entry["start_year"], entry["end_year"]) for entry in seasons
# ]

# referee = strong["Referee"]["instances"]
# referee_to_insert = [(entry["id"], entry["name"], entry["country_id"]) for entry in referee]

# team = strong["Team"]["instances"]
# team_to_insert = [(entry["id"], entry["name"], entry["country_id"]) for entry in team]

# bookie = strong["Bookie"]["instances"]
# bookie_to_insert = [(entry["id"], entry["name"]) for entry in bookie]

# # Get the records to insert for WEAK ENTITES
# matches = weak["Match"]["instances"]
# matches_to_insert = [
#     (
#         entry["id"],
#         entry["league_id"],
#         entry["season_id"],
#         entry["home_team_id"],
#         entry["away_team_id"],
#         entry["referee_id"],
#         entry["date"],
#         entry["time"],
#         entry["ft_result"],
#         entry["ht_result"],
#     )
#     for entry in matches
# ]

# odds = weak["Odds"]["instances"]
# odds_to_insert = [
#     (
#         entry["match_id"],
#         entry["bookie_id"],
#         entry["home_odds"],
#         entry["draw_odds"],
#         entry["away_odds"],
#     )
#     for entry in odds
# ]

# team_match_stats = weak["TeamMatchStats"]["instances"]
# team_match_stats_to_insert = [
#     (
#         entry["match_id"],
#         entry["team_id"],
#         entry["is_home"],
#         entry["ft_goals"],
#         entry["ht_goals"],
#         entry["shots"],
#         entry["shots_on_target"],
#         entry["corners"],
#         entry["fouls"],
#         entry["yellow_cards"],
#         entry["red_cards"],
#     )
#     for entry in team_match_stats
# ]

# # Connect to the SQLite database (or create one if it doesn't exist)
# conn = sqlite3.connect("mydatabase.db")
# cursor = conn.cursor()


# # Batch insert the records
# insert_query = "INSERT INTO Country (id, name) VALUES (?, ?)"
# cursor.executemany(insert_query, countries_to_insert)

# insert_query = "INSERT INTO League (id, name, division, country_id) VALUES (?, ?, ?, ?)"
# cursor.executemany(insert_query, leagues_to_insert)

# insert_query = "INSERT INTO Season (id, name, start_year, end_year) VALUES (?, ?, ?, ?)"
# cursor.executemany(insert_query, seasons_to_insert)

# insert_query = "INSERT INTO Referee (id, name, country_id) VALUES (?, ?, ?)"
# cursor.executemany(insert_query, referee_to_insert)

# insert_query = "INSERT INTO Team (id, name, country_id) VALUES (?, ?, ?)"
# cursor.executemany(insert_query, team_to_insert)

# insert_query = "INSERT INTO Bookie (id, name) VALUES (?, ?)"
# cursor.executemany(insert_query, bookie_to_insert)

# insert_query = "INSERT INTO Match (id, league_id, season_id, home_team_id, away_team_id, referee_id, date, time, ft_result, ht_result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
# cursor.executemany(insert_query, matches_to_insert)

# insert_query = (
#     "INSERT INTO Odds (match_id, bookie_id, home_odds, draw_odds, away_odds) VALUES (?, ?, ?, ?, ?)"
# )
# cursor.executemany(insert_query, odds_to_insert)

# insert_query = "INSERT INTO TeamMatchStats (match_id, team_id, is_home, ft_goals, ht_goals, shots, shots_on_target, corners, fouls, yellow_cards, red_cards) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
# cursor.executemany(insert_query, team_match_stats_to_insert)

# # Commit the changes and close the connection
# conn.commit()
# conn.close()

import pandas as pd
import sqlite3
import json

# Load JSON data into dataframes
with open("../data-gathering/json/strong_entities.json", "r") as file:
    strong = json.load(file)

with open("../data-gathering/json/weak_entities.json", "r") as file:
    weak = json.load(file)

df_countries = pd.DataFrame(strong["Country"]["instances"])
df_leagues = pd.DataFrame(strong["League"]["instances"])
df_seasons = pd.DataFrame(strong["Season"]["instances"])
df_referee = pd.DataFrame(strong["Referee"]["instances"])
df_team = pd.DataFrame(strong["Team"]["instances"])
df_bookie = pd.DataFrame(strong["Bookie"]["instances"])

df_matches = pd.DataFrame(weak["Match"]["instances"])
df_odds = pd.DataFrame(weak["Odds"]["instances"])
df_team_match_stats = pd.DataFrame(weak["TeamMatchStats"]["instances"])
cols_to_int = [
    "ft_goals",
    "ht_goals",
    "shots",
    "shots_on_target",
    "corners",
    "fouls",
    "yellow_cards",
    "red_cards",
]
df_team_match_stats[cols_to_int] = df_team_match_stats[cols_to_int].astype("Int64")

# Connect to SQLite
conn = sqlite3.connect("../soccer.db")

# Insert dataframes into SQLite
df_countries.to_sql("Country", conn, if_exists="append", index=False)
df_leagues.to_sql("League", conn, if_exists="append", index=False)
df_seasons.to_sql("Season", conn, if_exists="append", index=False)
df_referee.to_sql("Referee", conn, if_exists="append", index=False)
df_team.to_sql("Team", conn, if_exists="append", index=False)
df_bookie.to_sql("Bookie", conn, if_exists="append", index=False)
df_matches.to_sql("Match", conn, if_exists="append", index=False)
df_odds.to_sql("Odds", conn, if_exists="append", index=False)
df_team_match_stats.to_sql("TeamMatchStats", conn, if_exists="append", index=False)

# Close the connection
conn.close()
