from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

html = f"""
<html>
    <head>
        <title>Monitorización</title>
    </head>
    <body>
        <h1>Disponibilidad</h1>
        <p>Última actualización: {now}</p>
        <p>Este panel se actualizará automáticamente con cada ejecución del <i>workflow</i>.</p>
    </body>
</html>
"""

with open("../index.html", "w", encoding="utf-8") as f:
    f.write(html)
