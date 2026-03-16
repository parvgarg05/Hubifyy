import sqlite3

# Connect to the database file
connection = sqlite3.connect("college_hub.db")
cursor = connection.cursor()

print("--- 1. LIST OF ALL TABLES ---")
# Ask the database: "What tables do you have?"
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n--- 2. CONTENTS OF 'USER' TABLE ---")
# Get all users
cursor.execute("SELECT id, email, full_name, role FROM user")
users = cursor.fetchall()

if not users:
    print("The user table is empty!")
else:
    for u in users:
        print(f"ID: {u[0]} | Name: {u[2]} | Email: {u[1]} | Role: {u[3]}")

connection.close()