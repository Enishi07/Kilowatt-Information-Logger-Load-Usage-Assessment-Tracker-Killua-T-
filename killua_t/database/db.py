import os
# Database connection and setup for Killua-T application.
# Supports MySQL as the backend database.
# To use MySQL explicitly set `KILLUA_DB_TYPE=mysql` and configure the
# MySQL connection env vars as needed.

DB_TYPE = "mysql"
DEFAULT_MERALCO_RATE = float(os.getenv("DEFAULT_MERALCO_RATE", "12.64"))

if DB_TYPE == "mysql":
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

    # Meralco rate history
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meralco_rates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rate DOUBLE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

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

    # Seed default rate if missing
    try:
        cursor.execute("SELECT rate FROM meralco_rates ORDER BY created_at DESC LIMIT 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO meralco_rates (rate) VALUES (%s)", (DEFAULT_MERALCO_RATE,))
            conn.commit()
    except Exception:
        pass

else:
    raise RuntimeError("This build is configured for MySQL only.")


def get_current_rate(default: float = DEFAULT_MERALCO_RATE) -> float:
    """Return the latest stored Meralco rate, falling back to default if none exists."""
    try:
        cursor.execute("SELECT rate FROM meralco_rates ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0] is not None:
            return float(row[0])
    except Exception:
        pass
    return float(default)


def add_meralco_rate(rate: float):
    """Insert a new Meralco rate entry (MySQL)."""
    try:
        cursor.execute("INSERT INTO meralco_rates (rate) VALUES (%s)", (float(rate),))
        conn.commit()
    except Exception:
        conn.rollback()


def get_rate_history(limit: int = 50):
    """Return (created_at, rate) tuples ordered oldest->newest."""
    try:
        # MySQL connector may not support parameter for LIMIT; format safely
        lim = int(limit)
        cursor.execute(f"SELECT created_at, rate FROM meralco_rates ORDER BY created_at ASC LIMIT {lim}")
        return cursor.fetchall()
    except Exception:
        return []
