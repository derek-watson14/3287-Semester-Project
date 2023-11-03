import pandas as pd
import os
import numpy as np
import re
import json

directory = "../downloaded_csvs"

# Constants
TYPE_MAPPING = {
    "integer": "Int64",
    "float": np.float64,
    "string": "object",
}

COUNTRY_MAPPING = {
    "E": "England",
    "F": "France",
    "D": "Germany",
    "I": "Italy",
    "SP": "Spain",
    "P": "Portugal",
    "N": "Netherlands",
}

LEAGUE_MAPPING = {
    "E0": "Premier League",
    "E1": "Championship",
    "F1": "Ligue 1",
    "F2": "Ligue 2",
    "D1": "Bundesliga",
    "D2": "2. Bundesliga",
    "I1": "Serie A",
    "I2": "Serie B",
    "SP1": "La Liga",
    "SP2": "Segunda Division",
    "P1": "Primeira Liga",
    "N1": "Eredivisie",
}

YEAR_CODES = [
    "2223",
    "2122",
    "2021",
    "1920",
    "1819",
    "1718",
    "1617",
    "1516",
    "1415",
    "1314",
    "1213",
    "1112",
    "1011",
    "0910",
    "0809",
]

FILENAME_PATTERN = re.compile(r"([A-Z]{1,2}\d{1})-(\d{4})\.csv")

global ROW_ID
global BAD_LINES_COUNT
global TOTAL_LINES

ROW_ID = 1
BAD_LINES_COUNT = 0
TOTAL_LINES = 0

# Load column definitions
with open("../json/column_definitions.json", "r") as file:
    column_definitions = json.load(file)
    DESIRED_COLUMNS = list(column_definitions["Columns"].keys())
    COLUMN_DEFS = column_definitions["Columns"]


def process_csv(file_path, filename):
    global BAD_LINES_COUNT
    global TOTAL_LINES
    global ROW_ID

    df = pd.read_csv(
        file_path, on_bad_lines=handle_bad_line, encoding="ISO-8859-1", engine="python"
    )

    for col in DESIRED_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(TYPE_MAPPING[COLUMN_DEFS[col]["type"]])
        else:
            df[col] = None

    df = df[DESIRED_COLUMNS]
    na_rows_count = df[df.isna().all(axis=1)].shape[0]
    BAD_LINES_COUNT += na_rows_count

    df.dropna(how="all", inplace=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    match = FILENAME_PATTERN.match(filename)
    df["Season"] = f"20{match.group(2)[:2]}-{match.group(2)[2:]}"
    df["Country"] = COUNTRY_MAPPING[match.group(1)[:-1]]
    df["League"] = LEAGUE_MAPPING[match.group(1)]
    df["id"] = ROW_ID + df.index
    ROW_ID += df.shape[0]

    TOTAL_LINES += df.shape[0]

    return df


def handle_bad_line(bad_line):
    bad_line = [line.strip() for line in bad_line if line.strip()]
    if len(bad_line) != len(DESIRED_COLUMNS):
        global BAD_LINES_COUNT
        BAD_LINES_COUNT += 1
        return None
    return bad_line


def main():
    global BAD_LINES_COUNT
    global TOTAL_LINES

    dfs = []

    for filename in os.listdir(directory):
        match = FILENAME_PATTERN.match(filename)
        if not match or match.group(2) not in YEAR_CODES:
            continue

        file_path = os.path.join(directory, filename)
        print(f"Processing {filename}...")

        try:
            dfs.append(process_csv(file_path, filename))
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.to_csv("../combined.csv", index=False)
    else:
        print("No data to process.")

    print(f"Total lines: {TOTAL_LINES}")
    print(f"Total bad lines: {BAD_LINES_COUNT}")
    print(f"Proportion of bad lines: {BAD_LINES_COUNT / TOTAL_LINES:.4f}")


if __name__ == "__main__":
    main()
