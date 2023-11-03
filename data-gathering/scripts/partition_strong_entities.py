import pandas as pd
import json

outfile = "../json/strong_entities.json"
df = pd.read_csv("../combined.csv", low_memory=False)

league_division_mapping = {
    "Premier League": 1,
    "Ligue 1": 1,
    "Bundesliga": 1,
    "Serie A": 1,
    "La Liga": 1,
    "Eredivisie": 1,
    "Primeira Liga": 1,
    "Championship": 2,
    "Ligue 2": 2,
    "2. Bundesliga": 2,
    "Serie B": 2,
    "Segunda Division": 2,
}

country_ids = {country: (1 + idx) for idx, country in enumerate(df["Country"].unique())}
leagues = df["League"].unique()
seasons = df["Season"].unique()
referees = df["Referee"].dropna().unique()
teams = set(df["HomeTeam"]).union(set(df["AwayTeam"]))

# Precompute the mappings
league_to_country = df.dropna(subset=["League", "Country"]).set_index("League")["Country"].to_dict()
referee_to_country = (
    df.dropna(subset=["Referee", "Country"]).set_index("Referee")["Country"].to_dict()
)
team_to_country = {
    team: df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)]["Country"].iloc[0]
    for team in teams
}


def get_country_id(value, mappings):
    return country_ids.get(mappings.get(value))


def get_country_id_for_value(value, column_names):
    if not isinstance(column_names, list):
        column_names = [column_names]

    for col in column_names:
        filtered_df = df.dropna(subset=[col, "Country"])
        country_series = filtered_df[filtered_df[col] == value]["Country"]
        if not country_series.empty:
            return country_ids[country_series.iloc[0]]

    return None


instance_definitions = {
    "Country": {
        "description": "Country where the league is located",
        "instance_count": len(country_ids),
        "instances": [{"id": idx, "name": name} for name, idx in country_ids.items()],
    },
    "League": {
        "description": "League name",
        "instance_count": len(leagues),
        "instances": [
            {
                "id": (1 + idx),
                "name": league,
                "division": league_division_mapping[league],
                "country_id": get_country_id(league, league_to_country),
            }
            for idx, league in enumerate(leagues)
        ],
    },
    "Season": {
        "description": "Season name with <full start year>-<short end year> format",
        "instance_count": len(seasons),
        "instances": [
            {
                "id": (1 + idx),
                "name": season,
                "start_year": int(season[:4]),
                "end_year": 2000 + int(season[5:]),
            }
            for idx, season in enumerate(seasons)
        ],
    },
    "Referee": {
        "description": "Referee name",
        "instance_count": len(referees),
        "instances": [
            {
                "id": (1 + idx),
                "name": referee,
                "country_id": get_country_id(referee, referee_to_country),
            }
            for idx, referee in enumerate(referees)
        ],
    },
    "Team": {
        "description": "Team name",
        "instance_count": len(teams),
        "instances": [
            {
                "id": (1 + idx),
                "name": team,
                "country_id": get_country_id(team, team_to_country),
            }
            for idx, team in enumerate(teams)
        ],
    },
    "Bookie": {
        "description": "Bookie name",
        "instance_count": 3,
        "instances": [
            {"id": (1 + idx), "name": bookie}
            for idx, bookie in enumerate(["Bet365", "Interwetten", "William Hill"])
        ],
    },
}

with open(outfile, "w") as f:
    json.dump(instance_definitions, f, indent=4)
