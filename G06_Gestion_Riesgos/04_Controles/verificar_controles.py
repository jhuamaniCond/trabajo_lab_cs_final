"""Verifica en el sistema en ejecución los tres controles implantados de G06.

    python verificar_controles.py [http://localhost:5080]

Requiere la API 1.1.1 corriendo (Sistema_Logistico_Condor_final\\ejecutar.ps1 -Api)
y el contenedor de PostgreSQL Cas_condor. Escribe verificacion_controles.md con
cada comprobación: lo esperado, lo obtenido y el resultado.

  S1 Autorización por roles (RF-03, CRQ-12, RNF-03)      — riesgos R01, R02
  S2 Validación de entradas en el servidor (CRQ-07, CRQ-14, DEF-01) — riesgo R03
  S3 Respaldo y restauración (RF-16, RNF-07)              — riesgos R05, R06
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
SALIDA = Path(__file__).resolve().parent / "verificacion_controles.md"
filas = []


def pedir(metodo, ruta, cuerpo=None, token=None):
    cab = {"Content-Type": "application/json"}
    if token:
        cab["Authorization"] = f"Bearer {token}"
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(URL + ruta, data=datos, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            txt = r.read().decode()
            return r.status, json.loads(txt) if txt.strip() else None
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, txt


def comprobar(control, prueba, esperado, obtenido, ok):
    filas.append((control, prueba, esperado, obtenido, "✔ cumple" if ok else "✘ NO cumple"))
    print(f"[{'OK' if ok else 'FALLA'}] {control} · {prueba}: {obtenido}")


def ingresar(usuario, clave):
    estado, cuerpo = pedir("POST", "/api/auth/login", {"usuario": usuario, "clave": clave})
    return estado, (cuerpo or {}).get("token") if isinstance(cuerpo, dict) else None


# --- S1 Autorización por roles --------------------------------------------------
_, t_vend = ingresar("vendedor1", "Vendedor2026!")
_, t_enc = ingresar("encargado", "Encargado2026!")
estado, _ = pedir("GET", "/api/productos?texto=cem")
comprobar("S1", "Sin token: GET /api/productos", "401", estado, estado == 401)
RUTAS_ENCARGADO = [("GET", "/api/reportes/ventas"), ("GET", "/api/proveedores"), ("GET", "/api/respaldos"),
                   ("POST", "/api/escritorio/compras/buscar"), ("POST", "/api/escritorio/guias/buscar"),
                   ("GET", "/api/escritorio/respaldos")]
negadas = 0
for metodo, ruta in RUTAS_ENCARGADO:
    cuerpo = {} if metodo == "POST" else None
    e_v, _ = pedir(metodo, ruta, cuerpo, t_vend)
    e_e, _ = pedir(metodo, ruta, cuerpo, t_enc)
    negadas += e_v == 403
    comprobar("S1", f"{metodo} {ruta}: Vendedor / Encargado", "403 / 200", f"{e_v} / {e_e}", e_v == 403 and e_e == 200)
comprobar("S1", "Indicador: rutas del Encargado que rechazan al Vendedor", "100 %",
          f"{100 * negadas // len(RUTAS_ENCARGADO)} % ({negadas}/{len(RUTAS_ENCARGADO)})", negadas == len(RUTAS_ENCARGADO))
for i in range(5):
    pedir("POST", "/api/auth/login", {"usuario": "vendedor2", "clave": "clave-equivocada"})
estado, _ = ingresar("vendedor2", "Vendedor2026!")
comprobar("S1", "Bloqueo: 5 intentos fallidos de vendedor2 y luego la clave correcta", "423 (bloqueada 15 min)",
          estado, estado == 423)
cuenta = subprocess.run(["docker", "exec", "Cas_condor", "psql", "-U", "condor_app", "-d", "condor", "-tAc",
                         "select count(*) from usuario where hash_clave like 'pbkdf2-sha256$100000$%'"],
                        capture_output=True, text=True).stdout.strip()
comprobar("S1", "Contraseñas guardadas como hash PBKDF2 (100 000 iteraciones)", "3 de 3 usuarios", f"{cuenta} de 3", cuenta == "3")

# --- S2 Validación de entradas en el servidor ------------------------------------
_, productos = pedir("GET", "/api/productos?texto=cemento&limite=1", token=t_vend)
p = productos[0]
_, terminal = pedir("POST", "/api/escritorio/terminales", {"nombre": "PC-G06-PRUEBA"}, t_vend)


def nota(precio, cantidad=1, producto=None, lineas=1):
    return {"tipoComprobante": "NV", "serieCodigo": "NV01", "terminalId": terminal["id"],
            "detalle": [{"item": i + 1, "productoId": producto or p["id"], "descripcion": "Regalo", "unidad": p["unidad"],
                         "cantidad": cantidad, "precioUnitario": precio, "importe": precio * cantidad}
                        for i in range(lineas)]}


estado, emitida = pedir("POST", "/api/escritorio/comprobantes", nota(0.10), t_vend)
precio_guardado = emitida["detalle"][0]["precioUnitario"] if estado == 200 else None
comprobar("S2", f"Nota de venta con precio manipulado S/ 0.10 (catálogo S/ {p['precio']:.2f})",
          f"se guarda S/ {p['precio']:.2f} y la descripción del catálogo",
          f"HTTP {estado}; precio S/ {precio_guardado}; «{emitida['detalle'][0]['descripcion']}» ({emitida['serieCodigo']}-{emitida['numero']})",
          estado == 200 and abs(precio_guardado - p["precio"]) < 0.001 and emitida["detalle"][0]["descripcion"] == p["nombre"])
for etiqueta, cuerpo in [("cantidad 100 000 (> 99 999)", nota(p["precio"], 100000)),
                         ("cantidad 1.0005 (más de 3 decimales)", nota(p["precio"], 1.0005)),
                         ("101 líneas", nota(p["precio"], 1, lineas=101)),
                         ("producto inexistente", nota(p["precio"], 1, producto=999999))]:
    estado, cuerpo_r = pedir("POST", "/api/escritorio/comprobantes", cuerpo, t_vend)
    detalle = cuerpo_r.get("title") or cuerpo_r.get("detail") if isinstance(cuerpo_r, dict) else cuerpo_r
    comprobar("S2", f"Rechazo de {etiqueta}", "400 y no se emite", f"{estado}: {detalle}", estado == 400)

# --- S3 Respaldo y restauración ------------------------------------------------------
TABLAS = ["producto", "cliente", "comprobante", "comprobante_detalle", "proveedor", "compra", "guia_remision", "usuario"]


def conteos(base):
    sql = " union all ".join(f"select '{t}', count(*) from {t}" for t in TABLAS)
    out = subprocess.run(["docker", "exec", "Cas_condor", "psql", "-U", "condor_app", "-d", base, "-tAc", sql],
                         capture_output=True, text=True).stdout
    return dict(l.split("|") for l in out.strip().splitlines())


def sh(cmd):
    r = subprocess.run(["docker", "exec", "Cas_condor", "sh", "-c", cmd], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


antes = conteos("condor")
rc1, _ = sh("pg_dump -U condor_app -d condor -Fc -f /tmp/condor_g06.backup && ls -l /tmp/condor_g06.backup")
_, tam = sh("stat -c %s /tmp/condor_g06.backup")
comprobar("S3", "pg_dump -Fc de la base condor (formato de RF-16)", "archivo generado", f"código {rc1}; {tam} bytes", rc1 == 0)
sh("dropdb -U condor_app --if-exists condor_restaurada")
rc2, salida = sh("createdb -U condor_app condor_restaurada && pg_restore -U condor_app -d condor_restaurada /tmp/condor_g06.backup")
comprobar("S3", "pg_restore en una base vacía (condor_restaurada)", "sin errores", f"código {rc2} {salida[:120]}", rc2 == 0)
despues = conteos("condor_restaurada")
iguales = antes == despues
comprobar("S3", "Conteo de filas por tabla: original frente a restaurada", "idénticos",
          "; ".join(f"{t} {antes.get(t)}/{despues.get(t)}" for t in TABLAS), iguales)
sh("dropdb -U condor_app condor_restaurada; rm -f /tmp/condor_g06.backup")

# --- Informe -------------------------------------------------------------------------
lineas = ["# Verificación de los controles implantados (G06)", "",
          f"Fecha: {datetime.now():%Y-%m-%d %H:%M} · API {URL} (producto 1.1.1) · base PostgreSQL `condor` (contenedor Cas_condor)", "",
          "Generado con `verificar_controles.py`. Cada fila es una comprobación contra el sistema en ejecución.", "",
          "| Control | Prueba | Esperado | Obtenido | Resultado |", "|---|---|---|---|---|"]
lineas += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in filas]
ok = sum(1 for f in filas if f[4].startswith("✔"))
lineas += ["", f"**Resultado: {ok} de {len(filas)} comprobaciones cumplen.**", "",
           "Efectos en la base de demostración: se emitió una nota de venta de prueba (NV01, no va a la SUNAT), se registró la terminal "
           "`PC-G06-PRUEBA` y `vendedor2` quedó bloqueado 15 minutos. La base restaurada se eliminó al terminar."]
SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print(f"{ok}/{len(filas)} → {SALIDA}")
