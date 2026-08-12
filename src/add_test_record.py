import sqlite3
from datetime import datetime

conn = sqlite3.connect("monitor.db")
cur = conn.cursor()

now = datetime.now()
timestamp = now.isoformat()

cur.execute(f"""
INSERT INTO monitor VALUES (1000000, '{timestamp}', 'http://www.mytesturl.com/', 200, 100, 0, 0, 0, 0)
""")

conn.commit()

# -----------------------------
# PROBAR PERSISTENCIA
# -----------------------------
cur.execute("SELECT * FROM monitor WHERE id = 1000000;")
rows = cur.fetchall()

print("Probar persistencia:")
for row in rows:
    print(row)

conn.close()
