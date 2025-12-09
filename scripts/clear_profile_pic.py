"""Clear or set a user's profile_pic column.

Usage:
  "C:\Program Files\Python313\python.exe" scripts\clear_profile_pic.py --user lucio
  "C:\Program Files\Python313\python.exe" scripts\clear_profile_pic.py --user lucio --set "profiles/3.png"

By default the script sets `profile_pic` to NULL/empty. Use --set to assign a path.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'killua_t')))

from database import db as _db

cur = _db.cursor
conn = _db.conn

parser = argparse.ArgumentParser()
parser.add_argument('--user', '-u', required=True, help='Username to modify')
parser.add_argument('--set', help='Set profile_pic to this value (relative to assets/). If omitted, clears the value.')
args = parser.parse_args()

try:
    if args.set:
        cur.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (args.set, args.user))
    else:
        # Use NULL for MySQL or empty for SQLite; both are handled by queries when checking truthiness
        # We'll set NULL by passing None
        cur.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (None, args.user))
    conn.commit()
    print('Updated', args.user)
    cur.execute("SELECT id, username, profile_pic FROM users WHERE username = ?", (args.user,))
    print(cur.fetchone())
except Exception as e:
    try:
        conn.rollback()
    except Exception:
        pass
    print('Error updating user:', e)
    raise
