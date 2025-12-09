import os
import mysql.connector

# Simple MySQL helper module (alternative entrypoint). The main `database/db.py`
# will import mysql when KILLUA_DB_TYPE=mysql is set. This file can be used directly
# if you prefer.

DB_HOST = os.getenv("KILLUA_DB_HOST", "localhost")
DB_PORT = int(os.getenv("KILLUA_DB_PORT", 3306))
DB_USER = os.getenv("KILLUA_DB_USER", "killua_user")
DB_PASS = os.getenv("KILLUA_DB_PASS", "KilluaPass123")
DB_NAME = os.getenv("KILLUA_DB_NAME", "killua_t")

conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    autocommit=False,
    charset='utf8mb4'
)
cursor = conn.cursor()

# Create tables (MySQL-compatible)
cursor.execute("""
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    watt_per_hour DOUBLE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(50) NOT NULL,
    total_kwh DOUBLE,
    total_cost DECIMAL(12,2)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS record_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT,
    device_name VARCHAR(255),
    watt_per_hour DOUBLE,
    duration_minutes DOUBLE,
    kwh_used DOUBLE,
    cost DECIMAL(12,2)
)
""")

conn.commit()
