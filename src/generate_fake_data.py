import csv
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURACIÓN
# -----------------------------

YEAR = 2025
OUTPUT_FILE = "data_2025.csv"

SITES = {
    "site_a": "https://simulatehttpcode.vercel.app/"
}

# Peticiones cada minuto
INTERVAL_MINUTES = 1

# Probabilidades de códigos
STATUS_PROB = {
    200: 0.96,
    500: 0.02,
    503: 0.01,
    404: 0.01,
}

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------

def choose_status():
    r = random.random()
    cumulative = 0
    for code, prob in STATUS_PROB.items():
        cumulative += prob
        if r <= cumulative:
            return code
    return 200

def simulate_latency(status):
    if status == 200:
        # Normal o degradado
        if random.random() < 0.05:  # 5% degradado
            return random.randint(2000, 4000)
        return random.randint(50, 800)
    else:
        # Latencia irrelevante en error
        return random.randint(100, 800)

# -----------------------------
# GENERADOR PRINCIPAL
# -----------------------------

def generate_year_data():
    start = datetime(YEAR, 1, 1, 0, 0, 0)
    end = datetime(YEAR, 12, 31, 23, 59, 59)

    current = start
    id_counter = 1

    # Estado por sitio
    site_state = {
        site: {
            "errors": 0,
            "oks": 0,
            "down": False,
            "lat_high": 0,   # latencias > 2000 ms consecutivas
            "lat_low": 0,    # latencias <= 2000 ms consecutivas
            "degraded": False
        }
        for site in SITES
    }

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "id", "timestamp", "url", "status_code",
            "latency_ms", "down", "degraded"
        ])

        while current <= end:
            for site_name, base_url in SITES.items():

                status = choose_status()
                latency = simulate_latency(status)

                st = site_state[site_name]

                # -----------------------------
                # DOWN / RECUPERACIÓN (3 errores / 3 OK)
                # -----------------------------
                if status != 200:
                    st["errors"] += 1
                    st["oks"] = 0
                else:
                    st["oks"] += 1
                    st["errors"] = 0

                if st["errors"] >= 3:
                    st["down"] = True

                if st["oks"] >= 3:
                    st["down"] = False

                # -----------------------------
                # DEGRADACIÓN (solo códigos 200)
                # -----------------------------
                if status == 200:
                    if latency > 2000:
                        st["lat_high"] += 1
                        st["lat_low"] = 0
                    else:
                        st["lat_low"] += 1
                        st["lat_high"] = 0
                else:
                    # errores NO cuentan para degradación, reiniciamos contadores
                    st["lat_high"] = 0
                    st["lat_low"] = 0

                # Activar degradación
                if st["lat_high"] >= 3:
                    st["degraded"] = True

                # Recuperar degradación
                if st["lat_low"] >= 3:
                    st["degraded"] = False

                # -----------------------------
                # Guardar fila
                # -----------------------------
                writer.writerow([
                    id_counter,
                    current.strftime("%Y-%m-%d %H:%M:%S"),
                    base_url,
                    status,
                    latency,
                    st["down"],
                    st["degraded"]
                ])

                id_counter += 1

            current += timedelta(minutes=INTERVAL_MINUTES)

    print(f"Datos generados en {OUTPUT_FILE}")

# -----------------------------
# EJECUCIÓN
# -----------------------------

if __name__ == "__main__":
    generate_year_data()
