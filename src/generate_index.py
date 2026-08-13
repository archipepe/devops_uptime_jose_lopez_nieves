import os
import re
import sqlite3
import matplotlib.pyplot as plt

def sanitize(url):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url)

def clean_assets():
    folder = "assets"
    if not os.path.exists(folder):
        os.makedirs(folder)
        return

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            os.remove(path)

def get_sites():
    conn = sqlite3.connect("monitor.db")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT url FROM monitor ORDER BY url")
    sites = [row[0] for row in cur.fetchall()]
    conn.close()
    return sites

def generate_site_links(sites):
    html = ""
    for site in sites:
        html += f'<a href="#site-{site}" class="list-group-item list-group-item-action">{site}</a>\n'
    return html

def get_global_metrics():
    conn = sqlite3.connect("monitor.db")
    cur = conn.cursor()

    # Disponibilidad global
    cur.execute("""
        SELECT 
            SUM(CASE WHEN down = 1 THEN 1 ELSE 0 END),
            COUNT(*)
        FROM monitor
    """)
    minutos_caidos, minutos_totales = cur.fetchone()
    disponibilidad = 1 - (minutos_caidos / minutos_totales)

    # Latencia media global (solo códigos 200–299)
    cur.execute("""
        SELECT AVG(latency_ms)
        FROM monitor
        WHERE status_code BETWEEN 200 AND 299
    """)
    lat_media_global = cur.fetchone()[0]

    # Top webs peor disponibilidad
    cur.execute("""
        SELECT url,
               SUM(CASE WHEN down = 1 THEN 1 ELSE 0 END) AS caidos,
               COUNT(*) AS total
        FROM monitor
        GROUP BY url
        ORDER BY caidos DESC
        LIMIT 5
    """)
    top_peor_disp = cur.fetchall()

    # Top webs mayor latencia (solo códigos 200–299)
    cur.execute("""
        SELECT url, AVG(latency_ms) AS lat_media
        FROM monitor
        WHERE status_code BETWEEN 200 AND 299
        GROUP BY url
        ORDER BY lat_media DESC
        LIMIT 5
    """)
    top_latencia = cur.fetchall()

    # Caídas del día
    cur.execute("""
        SELECT COUNT(*)
        FROM monitor
        WHERE down_event = 1
          AND date(timestamp) = date('now', 'localtime')
    """)
    caidas_hoy = cur.fetchone()[0]

    conn.close()

    return {
        "disponibilidad": disponibilidad,
        "lat_media_global": lat_media_global,
        "top_peor_disp": top_peor_disp,
        "top_latencia": top_latencia,
        "caidas_hoy": caidas_hoy
    }

def render_header(metrics):
    disp_pct = round(metrics["disponibilidad"] * 100, 2)
    lat_media = round(metrics["lat_media_global"], 2)

    # Top webs peor disponibilidad
    peor_disp_html = "".join([
        f"<li>{url}: {round(caidos/total*100, 2)}%</li>"
        for url, caidos, total in metrics["top_peor_disp"]
    ])

    # Top webs mayor latencia
    peor_lat_html = "".join([
        f"<li>{url}: {round(lat, 2)} ms</li>"
        for url, lat in metrics["top_latencia"]
    ])

    return f"""
    <div id="header" class="p-3">
        <h2 class="mb-0">Panel de Monitorización</h2>

        <div class="mt-3">
            <span class="badge bg-success">Disponibilidad global: {disp_pct}%</span>
            <span class="badge bg-primary">Latencia media global: {lat_media} ms</span>
            <span class="badge bg-warning">Caídas hoy: {metrics["caidas_hoy"]}</span>
        </div>

        <div class="row mt-3">
            <div class="col-md-6">
                <h6>Top webs peor disponibilidad</h6>
                <ul>{peor_disp_html}</ul>
            </div>

            <div class="col-md-6">
                <h6>Top webs mayor latencia</h6>
                <ul>{peor_lat_html}</ul>
            </div>
        </div>
    </div>
    """

def get_site_metrics(url):
    conn = sqlite3.connect("monitor.db")
    cur = conn.cursor()

    # Disponibilidad mensual
    cur.execute("""
        SELECT strftime('%Y-%m', timestamp), 
               SUM(CASE WHEN down = 1 THEN 1 ELSE 0 END),
               COUNT(*)
        FROM monitor
        WHERE url = ?
        GROUP BY strftime('%Y-%m', timestamp)
        ORDER BY strftime('%Y-%m', timestamp) DESC
    """, (url,))
    disp_mensual = cur.fetchall()

    # Disponibilidad anual
    cur.execute("""
        SELECT strftime('%Y', timestamp), 
               SUM(CASE WHEN down = 1 THEN 1 ELSE 0 END),
               COUNT(*)
        FROM monitor
        WHERE url = ?
        GROUP BY strftime('%Y', timestamp)
        ORDER BY strftime('%Y', timestamp) DESC
    """, (url,))
    disp_anual = cur.fetchall()

    # Latencia media
    cur.execute("""
        SELECT AVG(latency_ms)
        FROM monitor
        WHERE url = ?
          AND status_code BETWEEN 200 AND 299
    """, (url,))
    lat_media = cur.fetchone()[0]

    # Latencias para percentiles
    cur.execute("""
        SELECT latency_ms
        FROM monitor
        WHERE url = ?
          AND status_code BETWEEN 200 AND 299
        ORDER BY latency_ms
    """, (url,))
    latencias = [row[0] for row in cur.fetchall()]

    def percentile(data, p):
        if not data:
            return None
        k = int(len(data) * p)
        return data[k]

    p95 = percentile(latencias, 0.95)
    p99 = percentile(latencias, 0.99)

    # Tiempo caído
    cur.execute("""
        SELECT SUM(CASE WHEN down = 1 THEN 1 ELSE 0 END)
        FROM monitor
        WHERE url = ?
    """, (url,))
    tiempo_caido = cur.fetchone()[0]

    # Tiempo degradado
    cur.execute("""
        SELECT SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END)
        FROM monitor
        WHERE url = ?
    """, (url,))
    tiempo_degradado = cur.fetchone()[0]

    # Eventos
    cur.execute("""
        SELECT timestamp, status_code, latency_ms, down_event, degraded_event
        FROM monitor
        WHERE url = ?
          AND (down_event = 1 OR degraded_event = 1)
        ORDER BY timestamp DESC
    """, (url,))
    eventos = cur.fetchall()

    conn.close()

    return {
        "disp_mensual": disp_mensual,
        "disp_anual": disp_anual,
        "lat_media": lat_media,
        "p95": p95,
        "p99": p99,
        "tiempo_caido": tiempo_caido,
        "tiempo_degradado": tiempo_degradado,
        "eventos": eventos
    }

def render_site_block(url, metrics):
    # Disponibilidad mensual
    disp_m_html = "".join([
        f"<li>{mes}: {round((1 - caidos/total)*100, 2)}%</li>"
        for mes, caidos, total in metrics["disp_mensual"]
    ])

    # Disponibilidad anual
    disp_a_html = "".join([
        f"<li>{año}: {round((1 - caidos/total)*100, 2)}%</li>"
        for año, caidos, total in metrics["disp_anual"]
    ])

    # Eventos
    eventos_html = "".join([
        f"<tr><td>{ts}</td><td>{sc}</td><td>{lat}</td>"
        f"<td>{'Sí' if de==1 else 'No'}</td>"
        f"<td>{'Sí' if dg==1 else 'No'}</td></tr>"
        for ts, sc, lat, de, dg in metrics["eventos"]
    ])

    disp_img = plot_disp_mensual(url, metrics["disp_mensual"])
    lat_img = plot_latencia_diaria(url)
    evt_img = plot_eventos(url)

    return f"""
    <div id="site-{url}" class="mt-5">
        <h3>{url}</h3>

        <h5 class="mt-4">Disponibilidad mensual</h5>
        <ul>{disp_m_html}</ul>

        <h5 class="mt-4">Disponibilidad anual</h5>
        <ul>{disp_a_html}</ul>

        <h5 class="mt-4">Latencia</h5>
        <p>Media: {round(metrics["lat_media"], 2)} ms</p>
        <p>P95: {metrics["p95"]} ms</p>
        <p>P99: {metrics["p99"]} ms</p>

        <h5 class="mt-4">Estado</h5>
        <p>Tiempo caído total: {metrics["tiempo_caido"]} minutos</p>
        <p>Tiempo degradado total: {metrics["tiempo_degradado"]} minutos</p>

        <img src="{disp_img}" class="img-fluid mt-3">
        <img src="{lat_img}" class="img-fluid mt-3">
        <img src="{evt_img}" class="img-fluid mt-3">

        <h5 class="mt-4">Eventos</h5>
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Status</th>
                    <th>Latencia</th>
                    <th>Caída</th>
                    <th>Degradación</th>
                </tr>
            </thead>
            <tbody>
                {eventos_html}
            </tbody>
        </table>
    </div>
    """

def plot_disp_mensual(url, disp_mensual):
    meses = [m for m, _, _ in disp_mensual]
    valores = [round((1 - caidos/total)*100, 2) for _, caidos, total in disp_mensual]

    plt.figure(figsize=(8,4))
    plt.plot(meses, valores, marker='o')
    plt.title(f"Disponibilidad mensual - {url}")
    plt.ylabel("Disponibilidad (%)")
    plt.xticks(rotation=45)
    plt.grid(True)
    filename = f"assets/{sanitize(url)}_disp.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename

def plot_latencia_diaria(url):
    conn = sqlite3.connect("monitor.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT date(timestamp), AVG(latency_ms)
        FROM monitor
        WHERE url = ?
          AND status_code BETWEEN 200 AND 299
        GROUP BY date(timestamp)
        ORDER BY date(timestamp)
    """, (url,))
    rows = cur.fetchall()

    if not rows:
        return None

    dias = [r[0] for r in rows]
    lat = [round(r[1], 2) for r in rows]

    plt.figure(figsize=(8,4))
    plt.plot(dias, lat, marker='o', color='orange')
    plt.title(f"Latencia media diaria - {url}")
    plt.ylabel("Latencia (ms)")
    plt.xticks(rotation=45)
    plt.grid(True)
    filename = f"assets/{sanitize(url)}_latencia.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename

def plot_eventos(url):
    conn = sqlite3.connect("monitor.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT date(timestamp),
               SUM(CASE WHEN down_event = 1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN degraded_event = 1 THEN 1 ELSE 0 END)
        FROM monitor
        WHERE url = ?
        GROUP BY date(timestamp)
        ORDER BY date(timestamp)
    """, (url,))
    rows = cur.fetchall()

    if not rows:
        return None

    dias = [r[0] for r in rows]
    caidas = [r[1] for r in rows]
    degrad = [r[2] for r in rows]

    plt.figure(figsize=(8,4))
    plt.bar(dias, caidas, label="Caídas", color="red")
    plt.bar(dias, degrad, bottom=caidas, label="Degradaciones", color="gold")
    plt.title(f"Eventos por día - {url}")
    plt.ylabel("Eventos")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    filename = f"assets/{sanitize(url)}_eventos.png"
    plt.savefig(filename)
    plt.close()
    return filename

clean_assets()

sites = get_sites()
site_links = generate_site_links(sites)
global_metrics = get_global_metrics()
header_html = render_header(global_metrics)
site_blocks = ""
for s in sites:
    metrics = get_site_metrics(s)
    site_blocks += render_site_block(s, metrics)

HTML = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitor de Disponibilidad</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body {{
            overflow-x: hidden;
        }}
        #sidebar {{
            height: 100vh;
            overflow-y: auto;
        }}
        #header {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: #fff;
            border-bottom: 1px solid #ddd;
        }}
    </style>
</head>

<body>

    {header_html}

    <!-- BOTÓN MÓVIL -->
    <button class="btn btn-primary d-md-none m-3" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarCanvas">
        Menú
    </button>

    <div class="container-fluid">
        <div class="row">

            <!-- SIDEBAR ESCRITORIO -->
            <nav id="sidebar" class="col-md-3 d-none d-md-block p-3 border-end">
                <h5>Sitios monitorizados</h5>
                <div class="list-group">
                    {site_links}
                </div>
            </nav>

            <!-- SIDEBAR MÓVIL -->
            <div class="offcanvas offcanvas-start" tabindex="-1" id="sidebarCanvas">
                <div class="offcanvas-header">
                    <h5 class="offcanvas-title">Sitios monitorizados</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
                </div>
                <div class="offcanvas-body">
                    <div class="list-group">
                        {site_links}
                    </div>
                </div>
            </div>

            <!-- PANEL DERECHO -->
            <main class="col-md-9 p-4">
                <h4>Selecciona un sitio para ver sus métricas</h4>
                <p class="text-muted">En la Fase 3 y 4 se rellenará esta sección.</p>

                <!-- CONTENEDORES VACÍOS POR SITIO -->
                {site_blocks}
            </main>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("index.html generado (Fase 5 completada)")
