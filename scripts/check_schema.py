import sqlite3

conn = sqlite3.connect('hullzero.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(maintenance_events)")
columns = cursor.fetchall()
for col in columns:
    print(col)
conn.close()
