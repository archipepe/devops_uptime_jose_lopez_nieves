import sqlite3

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

sites = get_sites()
site_links = generate_site_links(sites)

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

    <div id="header" class="p-3">
        <h2 class="mb-0">Panel de Monitorización</h2>
        <small class="text-muted">Resumen global (Fase 3)</small>
    </div>

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
                {"".join([f'<div id="site-{s}" class="mt-5"><h3>{s}</h3><p class="text-muted">Aquí irán las métricas.</p></div>' for s in sites])}
            </main>

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("index.html generado (Fase 2 completada)")
