import pandas as pd
import os
import numpy as np
import re
import json

directory = "./downloaded_csvs"

# Load the column definitions from the specified JSON
with open("column_definitions.json", "r") as file:
    column_definitions = json.load(file)

# Get the columns list from the definitions
desired_columns = list(column_definitions["Columns"].keys())

dfs = []

current_filename = None
file_bad_lines = {}
total_lines = 0


year_codes = [
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

filename_pattern = re.compile(r"([A-Z]{1,2}\d{1})-(\d{4})\.csv")


def handle_bad_line(bad_line):
    while bad_line and not bad_line[-1].strip():
        bad_line.pop()

    if len(bad_line) == len(desired_columns):
        return bad_line
    else:
        if current_filename not in file_bad_lines:
            file_bad_lines[current_filename] = 0
        file_bad_lines[current_filename] += 1

        with open("bad_lines.txt", "a") as f:
            f.write(",".join(bad_line) + "\n")
        return None


for filename in os.listdir(directory):
    match = filename_pattern.match(filename)
    if not match or match.group(2) not in year_codes:
        continue

    file_path = os.path.join(directory, filename)
    print(f"Processing {filename}...")

    with open(file_path, "r", encoding="ISO-8859-1") as f:
        current_total_lines = sum(1 for line in f)
    total_lines += current_total_lines

    try:
        df = pd.read_csv(
            file_path, on_bad_lines=handle_bad_line, encoding="ISO-8859-1", engine="python"
        )

        for col in desired_columns:
            if col not in df.columns:
                df[col] = np.nan

        df = df[desired_columns]
        df.dropna(how="all", inplace=True)
        dfs.append(df)
    except Exception as e:
        print(f"Error processing {filename}: {e}")


if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv("./combined.csv", index=False)
else:
    print("No data to process.")


for filename, bad_count in file_bad_lines.items():
    match = filename_pattern.match(filename)
    if match:
        league, season = match.groups()
        file_bad_lines[filename] = {
            "League": league,
            "Season": season,
            "Proportion": bad_count / total_lines,
        }


with open("bad_line_proportions.json", "w") as f:
    json.dump(file_bad_lines, f, indent=4)

print(f"Total lines: {total_lines}")
print(f"Total bad lines: {sum(file_bad_lines.values())}")
print(f"Proportion of bad lines: {sum(file_bad_lines.values()) / total_lines:.4f}")
