"""
Utility script to clear records and record_items from the configured database.
By default this will remove all records for all users. Use --username to target a specific user.

Usage (Windows cmd):
    set KILLUA_DB_TYPE=mysql
    set KILLUA_DB_HOST=localhost
    set KILLUA_DB_USER=killua_user
    set KILLUA_DB_PASS=KilluaPass123
    set KILLUA_DB_NAME=killua_t
    "C:\Program Files\Python313\python.exe" scripts\clear_records.py --username alice

If --username is omitted, all records and record_items will be deleted.
This script does NOT delete users or devices; it only clears records and record_items.
"""
import argparse
import os
import sys

# Ensure project package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import db as _db

parser = argparse.ArgumentParser()
parser.add_argument('--username', '-u', help='Username whose records should be deleted. If omitted, deletes all records.')
args = parser.parse_args()

conn = _db.conn
cursor = _db.cursor

try:
    if args.username:
        # Find user id
        cursor.execute("SELECT id FROM users WHERE username = ?", (args.username,))
        row = cursor.fetchone()
        if not row:
            print(f"User '{args.username}' not found.")
            raise SystemExit(1)
        uid = row[0]
        # Delete record_items for those records
        cursor.execute("SELECT id FROM records WHERE user_id = ?", (uid,))
        rec_ids = [r[0] for r in cursor.fetchall()]
        if rec_ids:
            # Use executemany to delete by id
            cursor.executemany("DELETE FROM record_items WHERE record_id = ?", [(rid,) for rid in rec_ids])
        cursor.execute("DELETE FROM records WHERE user_id = ?", (uid,))
        conn.commit()
        print(f"Deleted records for user '{args.username}'.")
    else:
        cursor.execute("DELETE FROM record_items")
        cursor.execute("DELETE FROM records")
        conn.commit()
        print("Deleted all records and record_items.")
except Exception as e:
    try:
        conn.rollback()
    except Exception:
        pass
    print("Error while clearing records:", e)
    raise
