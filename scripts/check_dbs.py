import sqlite3
import json
import os

print('--- Checking SQLite (killua_t.db) ---')
if os.path.exists('killua_t.db'):
    try:
        s = sqlite3.connect('killua_t.db')
        cur = s.cursor()
        cur.execute('SELECT id,name,watt_per_hour FROM devices')
        print('SQLite devices:')
        print(json.dumps(cur.fetchall(), indent=2))
        cur.execute('SELECT id,date,total_kwh,total_cost FROM records')
        print('SQLite records:')
        print(json.dumps(cur.fetchall(), indent=2))
        cur.close(); s.close()
    except Exception as e:
        print('SQLite error:', e)
else:
    print('SQLite file not found')

print('\n--- Checking MySQL (killua_t) ---')
try:
    import mysql.connector
    mconn = mysql.connector.connect(host='127.0.0.1', user='killua_user', password='KilluaPass123', database='killua_t')
    mcur = mconn.cursor()
    mcur.execute('SELECT id,name,watt_per_hour FROM devices')
    print('MySQL devices:')
    print(json.dumps(mcur.fetchall(), indent=2))
    mcur.execute('SELECT id,date,total_kwh,total_cost FROM records')
    print('MySQL records:')
    print(json.dumps(mcur.fetchall(), indent=2))
    mcur.close(); mconn.close()
except Exception as e:
    print('MySQL error:', e)
