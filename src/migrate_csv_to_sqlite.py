import sqlite3
import csv
from datetime import datetime

# -----------------------------
# CREAR TABLA monitor
# -----------------------------

conn = sqlite3.connect("monitor.db")
cur = conn.cursor()

# cur.execute("DROP TABLE IF EXISTS monitor;")
# conn.commit()

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

def to_bool(value):
    value = value.strip().lower()
    return 1 if value in ("true", "1", "verdadero", "yes") else 0

with open("data_requests.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    rows = []

    for r in reader:
        # Se genera bien, se añadió porque se abrió con Excel y le cambió el formato de fecha, ya no es necesario
        # Convertir timestamp DD/MM/YYYY H:MM → YYYY-MM-DD HH:MM:SS
        raw_ts = r["timestamp"]
        # dt = datetime.strptime(raw_ts, "%d/%m/%Y %H:%M")
        # iso_ts = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Convertir booleanos "TRUE"/"FALSE" → 1/0
        down = to_bool(r["down"])
        degraded = to_bool(r["degraded"])
        down_event = to_bool(r["down_event"])
        degraded_event = to_bool(r["degraded_event"])

        rows.append((
            int(r["id"]),
            raw_ts,
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
