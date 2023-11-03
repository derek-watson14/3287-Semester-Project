import pandas as pd
import json

# Load the column definitions from the specified JSON
with open("../json/column_definitions.json", "r") as file:
    column_definitions = json.load(file)

# Get the columns list from the definitions
columns = column_definitions["Columns"]
columns["Season"] = "Season name with <full start year>-<short end year> format"
columns["Country"] = "Country where the league is located"
columns["League"] = "League name"
columns["id"] = "Unique identifier for the match"

# Read combined.csv using the columns from the JSON
df = pd.read_csv("../combined.csv", usecols=columns, low_memory=False)

# Calculate the proportion of nulls for each column
null_proportions = df.isnull().sum() / len(df)

# Generate summary statistics for numeric columns
numeric_stats = df.describe().to_dict()

# Compute unique values for non-numeric columns
unique_values = {}
for column in df.select_dtypes(include=["object"]).columns:
    unique_values[column] = df[column].nunique()

# Assemble the summary
summary = {}
for column in columns:
    summary[column] = {
        "definition": columns[column],
        "null_proportion": null_proportions[column],
        "unique_values": unique_values.get(column, None),
        "numeric_stats": numeric_stats.get(column, None),
    }

summary_list = list(summary.items())
summary_list.sort(key=lambda x: x[1]["null_proportion"], reverse=True)
sorted_summary = dict(summary_list)

# Save the summary to summary.json
with open("../json/summary.json", "w") as json_file:
    json.dump(sorted_summary, json_file, indent=4)

print("Summary written to summary.json")
