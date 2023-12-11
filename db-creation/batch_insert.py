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
cols_to_int = [
    "h_ft_goals",
    "a_ft_goals",
    "h_ht_goals",
    "a_ht_goals",
    "h_shots",
    "a_shots",
    "h_shots_on_target",
    "a_shots_on_target",
    "h_corners",
    "a_corners",
    "h_fouls",
    "a_fouls",
    "h_yellow_cards",
    "a_yellow_cards",
    "h_red_cards",
    "a_red_cards",
]
df_matches[cols_to_int] = df_matches[cols_to_int].astype("Int64")
df_odds = pd.DataFrame(weak["Odds"]["instances"])

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

# Close the connection
conn.close()
