import sqlite3

conn = sqlite3.connect("../soccer.db")
cursor = conn.cursor()

# Get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables[1:]:
    cursor.execute(f"DROP TABLE {table[0]};")

conn.commit()
conn.close()
