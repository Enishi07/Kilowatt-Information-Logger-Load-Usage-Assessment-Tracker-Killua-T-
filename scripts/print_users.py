"""Print user records for quick inspection.

Usage (Windows cmd):
  "C:\Program Files\Python313\python.exe" scripts\print_users.py

This script imports the project's `database.db` module and prints the
`id`, `username`, and `profile_pic` for a short list of usernames.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'killua_t')))

from database import db as _db

cur = _db.cursor

parser = argparse.ArgumentParser(description='Print user(s) and profile_pic info.')
parser.add_argument('--all', action='store_true', help='Print all users')
parser.add_argument('--user', '-u', action='append', help='Username to query (can specify multiple)')
args = parser.parse_args()

if args.all:
  try:
    cur.execute("SELECT id, username, profile_pic FROM users ORDER BY id")
    rows = cur.fetchall()
    for r in rows:
      print(r)
  except Exception as e:
    print('Error querying all users:', e)
    sys.exit(1)
else:
  usernames = args.user or ['enishi', 'kenny']
  for u in usernames:
    try:
      cur.execute("SELECT id, username, profile_pic FROM users WHERE username = ?", (u,))
      row = cur.fetchone()
      print(u, '=>', row)
    except Exception as e:
      print('Error querying', u, e)
