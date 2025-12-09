"""
Create the application database and user on a local MySQL server.
Usage: adjust ROOT_PASSWORD if needed, or set env vars before running.
"""
import os
import sys
try:
    import mysql.connector
except Exception as e:
    print("Please install mysql-connector-python: python -m pip install mysql-connector-python")
    raise

ROOT_USER = os.getenv('MYSQL_ROOT_USER', 'root')
ROOT_PASS = os.getenv('MYSQL_ROOT_PASS', 'killua-t')
HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
PORT = int(os.getenv('MYSQL_PORT', 3306))

APP_DB = os.getenv('KILLUA_DB_NAME', 'killua_t')
APP_USER = os.getenv('KILLUA_DB_USER', 'killua_user')
APP_PASS = os.getenv('KILLUA_DB_PASS', 'KilluaPass123')

def main():
    try:
        conn = mysql.connector.connect(host=HOST, port=PORT, user=ROOT_USER, password=ROOT_PASS)
    except Exception as e:
        print(f"Failed to connect to MySQL as root: {e}")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{APP_DB}`")
        # Create user. Try the simple IDENTIFIED BY first (uses server default plugin).
        try:
            cur.execute("CREATE USER IF NOT EXISTS '%s'@'localhost' IDENTIFIED BY %s" % (APP_USER, "%s"), (APP_PASS,))
        except Exception:
            # fallback: explicitly try caching_sha2_password
            try:
                cur.execute("CREATE USER IF NOT EXISTS '%s'@'localhost' IDENTIFIED WITH caching_sha2_password BY %s" % (APP_USER, "%s"), (APP_PASS,))
            except Exception:
                # Last resort: inline password (may fail if password contains quotes)
                cur.execute(f"CREATE USER IF NOT EXISTS '{APP_USER}'@'localhost' IDENTIFIED BY '{APP_PASS}'")

        # Grant privileges (identifiers must be inlined)
        cur.execute(f"GRANT ALL PRIVILEGES ON `{APP_DB}`.* TO '{APP_USER}'@'localhost'")
        cur.execute("FLUSH PRIVILEGES")
        conn.commit()
        print(f"Database '{APP_DB}' and user '{APP_USER}' ensured.")
    except Exception as e:
        print(f"Error creating DB/user: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
