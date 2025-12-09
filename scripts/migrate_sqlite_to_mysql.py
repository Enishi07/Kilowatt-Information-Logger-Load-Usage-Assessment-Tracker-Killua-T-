"""
Migration helper: copy data from SQLite `killua_t.db` into a MySQL database.

Usage (after you created MySQL DB and installed mysql-connector-python):

    set KILLUA_DB_TYPE=mysql
    set KILLUA_DB_HOST=127.0.0.1
    set KILLUA_DB_USER=killua_user
    set KILLUA_DB_PASS=KilluaPass123
    set KILLUA_DB_NAME=killua_t

    python scripts\migrate_sqlite_to_mysql.py --sqlite-file ../killua_t.db

This script creates tables in the target MySQL DB (if not present) and inserts rows.
It is idempotent for basic usage but you should backup your SQLite DB before running.
"""

import argparse
import sqlite3
import os
import sys

try:
    import mysql.connector
except Exception:
    print("Please install mysql-connector-python before running: python -m pip install mysql-connector-python")
    sys.exit(1)


def migrate(sqlite_file, mysql_cfg):
    # Connect SQLite
    if not os.path.exists(sqlite_file):
        raise FileNotFoundError(f"SQLite file not found: {sqlite_file}")

    sconn = sqlite3.connect(sqlite_file)
    scur = sconn.cursor()

    # Connect MySQL
    mconn = mysql.connector.connect(
        host=mysql_cfg['host'],
        port=mysql_cfg['port'],
        user=mysql_cfg['user'],
        password=mysql_cfg['password'],
        database=mysql_cfg['database']
    )
    mcur = mconn.cursor()

    # Ensure target tables exist (same DDL as db_mysql.py)
    mcur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        watt_per_hour DOUBLE NOT NULL
    )
    """)

    mcur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date VARCHAR(50) NOT NULL,
        total_kwh DOUBLE,
        total_cost DECIMAL(12,2)
    )
    """)

    mcur.execute("""
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
    mconn.commit()

    # Copy devices
    scur.execute("SELECT id, name, watt_per_hour FROM devices")
    rows = scur.fetchall()
    if rows:
        # Insert using REPLACE INTO by id could be used but we'll insert rows without id to let MySQL assign new ids
        inserts = [(r[1], r[2]) for r in rows]
        mcur.executemany("INSERT INTO devices (name, watt_per_hour) VALUES (%s, %s)", inserts)
        mconn.commit()

    # Copy records
    scur.execute("SELECT id, date, total_kwh, total_cost FROM records")
    rows = scur.fetchall()
    if rows:
        inserts = [(r[1], r[2], r[3]) for r in rows]
        mcur.executemany("INSERT INTO records (date, total_kwh, total_cost) VALUES (%s, %s, %s)", inserts)
        mconn.commit()

    # Copy record_items
    scur.execute("SELECT id, record_id, device_name, watt_per_hour, duration_minutes, kwh_used, cost FROM record_items")
    rows = scur.fetchall()
    if rows:
        inserts = [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
        mcur.executemany(
            "INSERT INTO record_items (record_id, device_name, watt_per_hour, duration_minutes, kwh_used, cost) VALUES (%s, %s, %s, %s, %s, %s)",
            inserts
        )
        mconn.commit()

    print("Migration completed.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sqlite-file", default="../killua_t.db")
    p.add_argument("--mysql-host", default=os.getenv('KILLUA_DB_HOST', 'localhost'))
    p.add_argument("--mysql-port", type=int, default=int(os.getenv('KILLUA_DB_PORT', 3306)))
    p.add_argument("--mysql-user", default=os.getenv('KILLUA_DB_USER', 'killua_user'))
    p.add_argument("--mysql-pass", default=os.getenv('KILLUA_DB_PASS', 'KilluaPass123'))
    p.add_argument("--mysql-db", default=os.getenv('KILLUA_DB_NAME', 'killua_t'))

    args = p.parse_args()

    cfg = {
        'host': args.mysql_host,
        'port': args.mysql_port,
        'user': args.mysql_user,
        'password': args.mysql_pass,
        'database': args.mysql_db
    }

    migrate(args.sqlite_file, cfg)


if __name__ == '__main__':
    main()
