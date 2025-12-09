import os
import sqlite3

# Switchable DB driver: default is MySQL (use SQLite as a backup).
# To force SQLite set environment variable `KILLUA_DB_TYPE=sqlite`.
# To use MySQL explicitly set `KILLUA_DB_TYPE=mysql` and configure the
# MySQL connection env vars (see README instructions).

DB_TYPE = os.getenv("KILLUA_DB_TYPE", "mysql").lower()

if DB_TYPE == "mysql":
    # Lazy import of MySQL module to avoid requiring it for SQLite usage
    try:
        import mysql.connector
    except Exception as e:
        raise RuntimeError("MySQL selected but mysql-connector-python is not installed: " + str(e))

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

    # Wrap the mysql.connector cursor so existing code that uses
    # SQLite-style ? placeholders will keep working. We translate
    # '?' -> '%s' before executing when using MySQL.
    class _ParamTranslateCursor:
        def __init__(self, real_cursor):
            self._cur = real_cursor

        def _translate(self, sql):
            # simple replace of SQLite '?' with MySQL '%s'
            if sql is None:
                return sql
            return sql.replace('?', '%s')

        def execute(self, sql, params=None):
            sql2 = self._translate(sql)
            if params is None:
                return self._cur.execute(sql2)
            return self._cur.execute(sql2, params)

        def executemany(self, sql, seq_of_params):
            sql2 = self._translate(sql)
            return self._cur.executemany(sql2, seq_of_params)

        def __getattr__(self, name):
            return getattr(self._cur, name)

    cursor = _ParamTranslateCursor(conn.cursor())

    # Create tables (MySQL-compatible)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        watt_per_hour DOUBLE NOT NULL,
        user_id INT NULL
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

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(150) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        profile_pic VARCHAR(255) NULL,
        bio TEXT NULL
    )
    """)

    # If the DB existed before we added `user_id` columns, ALTER TABLE to add them.
    try:
        # devices.user_id
        cursor.execute("SHOW COLUMNS FROM devices LIKE 'user_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE devices ADD COLUMN user_id INT NULL")

        # records.user_id (may be missing on older DBs)
        cursor.execute("SHOW COLUMNS FROM records LIKE 'user_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE records ADD COLUMN user_id INT NULL")
        # users.profile_pic and users.bio
        cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_pic'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255) NULL")
        cursor.execute("SHOW COLUMNS FROM users LIKE 'bio'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT NULL")
    except Exception:
        # If any of these fail (older MySQL versions, permissions), ignore and continue;
        # the app will raise clearer errors later when attempting to use the columns.
        pass

    conn.commit()

else:
    # SQLite (default)
    DB_FILE = os.getenv("KILLUA_SQLITE_FILE", os.path.join(os.path.dirname(__file__), "..", "killua_t.db"))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Devices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        watt_per_hour REAL NOT NULL,
        user_id INTEGER
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

    # Users table (SQLite)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        profile_pic TEXT,
        bio TEXT
    )
    """)

    conn.commit()
