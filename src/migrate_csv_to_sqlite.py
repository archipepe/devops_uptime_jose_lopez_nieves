import sqlite3
import csv
from datetime import datetime

# -----------------------------
# CREAR TABLA monitor
# -----------------------------

conn = sqlite3.connect("monitor.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS monitor;")
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS monitor (
    id INTEGER,
    timestamp TEXT,
    url TEXT,
    status_code INTEGER,
    latency_ms INTEGER,
    down INTEGER,
    degraded INTEGER,
    down_event INTEGER,
    degraded_event INTEGER
)
""")
conn.commit()

# -----------------------------
# MIGRAR DATOS
# -----------------------------

with open("data_2025.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    rows = []

    for r in reader:
        # Convertir timestamp DD/MM/YYYY H:MM → YYYY-MM-DD HH:MM:SS
        raw_ts = r["timestamp"]
        dt = datetime.strptime(raw_ts, "%d/%m/%Y %H:%M")
        iso_ts = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Convertir booleanos "TRUE"/"FALSE" → 1/0
        down = 1 if r["down"] == "TRUE" else 0
        degraded = 1 if r["degraded"] == "TRUE" else 0
        down_event = 1 if r["down_event"] == "TRUE" else 0
        degraded_event = 1 if r["degraded_event"] == "TRUE" else 0

        rows.append((
            int(r["id"]),
            iso_ts,
            r["url"],
            int(r["status_code"]),
            int(r["latency_ms"]),
            down,
            degraded,
            down_event,
            degraded_event
        ))

cur.executemany("""
INSERT INTO monitor VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()
conn.close()
