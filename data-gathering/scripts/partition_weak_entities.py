import pandas as pd
import json

df = pd.read_csv("../combined.csv", low_memory=False)

# Read json file into a dictionary
with open("../json/strong_entities.json", "r") as file:
    strong_entities = json.load(file)

match_records = {
    "Match": {
        "description": "A match between two teams",
        "instance_count": len(df),
        "instances": [],
    }
}

odds_records = {
    "Odds": {
        "description": "Odds for a match from a bookie",
        "instance_count": 0,
        "instances": [],
    }
}

team_match_stats_records = {
    "TeamMatchStats": {
        "description": "Statistics for a team in a match",
        "instance_count": len(df) * 2,
        "instances": [],
    }
}

country_dict = {item["name"]: item["id"] for item in strong_entities["Country"]["instances"]}
league_dict = {item["name"]: item["id"] for item in strong_entities["League"]["instances"]}
season_dict = {item["name"]: item["id"] for item in strong_entities["Season"]["instances"]}
referee_dict = {item["name"]: item["id"] for item in strong_entities["Referee"]["instances"]}
team_dict = {item["name"]: item["id"] for item in strong_entities["Team"]["instances"]}
bookie_dict = {item["name"]: item["id"] for item in strong_entities["Bookie"]["instances"]}

for idx, row in df.iterrows():
    # Replace all columns with nan with None
    row = row.where(pd.notnull(row), None)

    match_records["Match"]["instances"].append(
        {
            "id": row["id"],
            "league_id": league_dict[row["League"]],
            "season_id": season_dict[row["Season"]],
            "home_team_id": team_dict[row["HomeTeam"]],
            "away_team_id": team_dict[row["AwayTeam"]],
            "referee_id": referee_dict.get(row["Referee"], None),
            "date": row["Date"],
            "time": row["Time"],
            "ft_result": row["FTR"],
            "ht_result": row["HTR"],
        }
    )

    if row["B365H"] and row["B365D"] and row["B365A"]:
        odds_records["Odds"]["instances"].append(
            {
                "match_id": row["id"],
                "bookie_id": bookie_dict["Bet365"],
                "home_odds": row["B365H"],
                "draw_odds": row["B365D"],
                "away_odds": row["B365A"],
            }
        )
        odds_records["Odds"]["instance_count"] += 1

    if row["IWH"] and row["IWD"] and row["IWA"]:
        odds_records["Odds"]["instances"].append(
            {
                "match_id": row["id"],
                "bookie_id": bookie_dict["Interwetten"],
                "home_odds": row["IWH"],
                "draw_odds": row["IWD"],
                "away_odds": row["IWA"],
            }
        )
        odds_records["Odds"]["instance_count"] += 1

    if row["WHH"] and row["WHD"] and row["WHA"]:
        odds_records["Odds"]["instances"].append(
            {
                "match_id": row["id"],
                "bookie_id": bookie_dict["William Hill"],
                "home_odds": row["WHH"],
                "draw_odds": row["WHD"],
                "away_odds": row["WHA"],
            }
        )
        odds_records["Odds"]["instance_count"] += 1

    team_match_stats_records["TeamMatchStats"]["instances"].append(
        {
            "match_id": row["id"],
            "team_id": team_dict[row["HomeTeam"]],
            "is_home": True,
            "ft_goals": row["FTHG"],
            "ht_goals": row["HTHG"],
            "shots": row["HS"],
            "shots_on_target": row["HST"],
            "corners": row["HC"],
            "fouls": row["HF"],
            "yellow_cards": row["HY"],
            "red_cards": row["HR"],
        }
    )

    team_match_stats_records["TeamMatchStats"]["instances"].append(
        {
            "match_id": row["id"],
            "team_id": team_dict[row["AwayTeam"]],
            "is_home": False,
            "ft_goals": row["FTAG"],
            "ht_goals": row["HTAG"],
            "shots": row["AS"],
            "shots_on_target": row["AST"],
            "corners": row["AC"],
            "fouls": row["AF"],
            "yellow_cards": row["AY"],
            "red_cards": row["AR"],
        }
    )

combined_records = {**match_records, **odds_records, **team_match_stats_records}

with open("../json/weak_entities.json", "w") as f:
    json.dump(combined_records, f, indent=4)
