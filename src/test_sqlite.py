import sqlite3

conn = sqlite3.connect("monitor.db")
cur = conn.cursor()

# -----------------------------
# CONSULTA 1
# -----------------------------
cur.execute("SELECT * FROM monitor;")
rows = cur.fetchmany(10)

print("SELECT * FROM monitor LIMIT 10;")
for row in rows:
    print(row)

# -----------------------------
# CONSULTA 2
# -----------------------------
cur.execute("SELECT * FROM monitor WHERE date(timestamp) = '2025-03-14';")
rows = cur.fetchall()

print("Registros del día 2025-03-14:")
print("SELECT * FROM monitor WHERE date(timestamp) = '2025-03-14';")
for row in rows:
    print(row)

print(len(rows))

# -----------------------------
# CONSULTA 3
# -----------------------------
cur.execute("""
SELECT strftime('%Y-%m', timestamp), COUNT(*)
FROM monitor
GROUP BY strftime('%Y-%m', timestamp);
""")

rows = cur.fetchall()

print("Registros agrupados por mes:")
for row in rows:
    print(row)

# -----------------------------
# CONSULTA 4
# -----------------------------
cur.execute("""
SELECT *
FROM monitor
WHERE timestamp BETWEEN '2025-03-01' AND '2025-04-01';
""")

rows = cur.fetchall()

print("Registros entre 2025-03-01 (inc.) y 2025-04-01 (exc.):")
for row in rows:
    print(row)

print(len(rows))

# -----------------------------
# CONSULTA 5
# -----------------------------
cur.execute("SELECT COUNT(*) FROM monitor WHERE down_event = 1;")

rows = cur.fetchall()

print("Caídas totales:")
for row in rows:
    print(row)

# -----------------------------
# CONSULTA 6
# -----------------------------
cur.execute("SELECT COUNT(*) FROM monitor WHERE degraded_event = 1;")

rows = cur.fetchall()

print("Degradaciones totales:")
for row in rows:
    print(row)

# -----------------------------
# CONSULTA 7
# -----------------------------
cur.execute("SELECT DISTINCT strftime('%m', timestamp) FROM monitor;")

rows = cur.fetchall()

print("Obtener todos los meses:")
for row in rows:
    print(row)

# -----------------------------
# CONSULTA 8
# -----------------------------
cur.execute("SELECT DISTINCT strftime('%Y', timestamp) FROM monitor;")

rows = cur.fetchall()

print("Obtener todos los años:")
for row in rows:
    print(row)


# -----------------------------
# CONSULTA 9
# -----------------------------
cur.execute("""
SELECT *
FROM monitor
WHERE strftime('%Y-%m', timestamp) = '2025-03';
""")

rows = cur.fetchall()

print("Registros del mes 2025-03:")
for row in rows:
    print(row)

print(len(rows))

# -----------------------------
# CONSULTA 10
# -----------------------------
cur.execute("""
SELECT *
FROM monitor
WHERE status_code <> 200;
""")

rows = cur.fetchall()

print("Todos los errores:")
for row in rows:
    print(row)

print(len(rows))

conn.close()
