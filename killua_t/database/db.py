import sqlite3

# Initialize SQLite connection
conn = sqlite3.connect("killua_t.db")
cursor = conn.cursor()

# Devices table
cursor.execute("""
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    watt_per_hour REAL NOT NULL
)
""")

# Daily records summary
cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_kwh REAL,
    total_cost REAL
)
""")

# Detailed items inside a record
cursor.execute("""
CREATE TABLE IF NOT EXISTS record_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    device_name TEXT,
    watt_per_hour REAL,
    duration_minutes REAL,
    kwh_used REAL,
    cost REAL
)
""")

conn.commit()
