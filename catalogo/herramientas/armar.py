"""Arma y valida el catálogo.

Uso:
  python -P herramientas/armar.py validar [archivo.json ...]   valida contra el esquema (sin args: los finales)
  python -P herramientas/armar.py unir archivo.json [...]      une tmp/<agente>/<archivo>.json en ESOS finales (los pisa),
                                                               regenera marcas.json, fuentes.csv y marcas_sugeridas.json
                                                               y valida todo
  python -P herramientas/armar.py indices                      solo regenera marcas.json, fuentes.csv y marcas_sugeridas.json
                                                               desde los finales (no toca productos) y valida

Se corre desde la carpeta catalogo/. Solo usa la biblioteca estándar + jsonschema.
"""
import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict

from jsonschema import Draft202012Validator

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS = {
    "fertilizantes.json": "fertilizante",
    "foliares.json": "foliar",
    "sustratos.json": "sustrato",
    "luces.json": "luz",
    "carpas.json": "carpa",
    "ventilacion.json": "ventilacion",
    "clima.json": "clima",
    "geneticas.json": "genetica",
}
CLAVE_MARCAS = {"luz": "luces", "carpa": "carpas", "ventilacion": "ventilacion", "clima": "clima",
                "fertilizante": "fertilizantes", "foliar": "foliares", "sustrato": "sustratos", "genetica": "geneticas"}


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validar(rutas):
    esquema = leer(os.path.join(RAIZ, "esquema", "catalogo.schema.json"))
    validador = Draft202012Validator(esquema)
    errores, ids = [], Counter()
    total = 0
    for ruta in rutas:
        nombre = os.path.basename(ruta)
        try:
            datos = leer(ruta)
        except Exception as e:  # JSON roto
            errores.append(f"{ruta}: no se puede leer ({e})")
            continue
        for err in sorted(validador.iter_errors(datos), key=lambda e: list(e.path)):
            ruta_err = "/".join(str(p) for p in err.path)
            errores.append(f"{nombre} [{ruta_err}]: {err.message[:200]}")
        if not isinstance(datos, list):
            continue
        esperada = ARCHIVOS.get(nombre)
        for p in datos:
            if not isinstance(p, dict):
                continue
            total += 1
            ids[p.get("id")] += 1
            if esperada and p.get("categoria") != esperada:
                errores.append(f"{nombre}: {p.get('id')} tiene categoria {p.get('categoria')!r}, se esperaba {esperada!r}")
            if not p.get("fuentes"):
                errores.append(f"{nombre}: {p.get('id')} no tiene fuente")
            for c in p.get("conflictos") or []:
                if p.get(c.get("campo")) not in (None, [], ""):
                    errores.append(f"{nombre}: {p.get('id')} tiene conflicto en {c.get('campo')} pero el campo no está en null (no se elige entre fuentes)")
    for i, n in ids.items():
        if n > 1:
            errores.append(f"id duplicado entre archivos: {i} (x{n})")
    print(f"Productos revisados: {total} en {len(rutas)} archivo(s)")
    if errores:
        print(f"ERRORES ({len(errores)}):")
        for e in errores[:300]:
            print("  -", e)
        return False
    print("OK: esquema válido, todos con fuente, sin ids duplicados")
    return True


def unir(solo=None):
    """solo: lista de archivos finales a regenerar (ej. ["geneticas.json"]); None = todos."""
    tmp = os.path.join(RAIZ, "tmp")
    por_archivo = defaultdict(list)
    sugeridas, vistos = [], set()
    for ruta in sorted(glob.glob(os.path.join(tmp, "*", "*.json"))):
        nombre = os.path.basename(ruta)
        if nombre == "sugeridas.json":
            for s in leer(ruta):
                clave = (s.get("categoria"), (s.get("marca") or "").lower())
                if clave not in vistos:
                    vistos.add(clave)
                    sugeridas.append(s)
        elif nombre in ARCHIVOS and (solo is None or nombre in solo):
            por_archivo[nombre].extend(leer(ruta))
    for nombre, productos in por_archivo.items():
        productos.sort(key=lambda p: (p["marca"].lower(), (p.get("linea") or "").lower(), p["producto"].lower(), (p.get("modelo") or "").lower()))
        escribir_json(os.path.join(RAIZ, nombre), productos)
    return indices(sugeridas)


def indices(sugeridas=None):
    """Regenera marcas.json y fuentes.csv desde los archivos finales (no toca los productos)."""
    if sugeridas is None:
        sugeridas, vistos = [], set()
        for ruta in sorted(glob.glob(os.path.join(RAIZ, "tmp", "*", "sugeridas.json"))):
            for s in leer(ruta):
                clave = (s.get("categoria"), (s.get("marca") or "").lower())
                if clave not in vistos:
                    vistos.add(clave)
                    sugeridas.append(s)
    # marcas.json y fuentes.csv salen de los archivos finales que existan
    marcas = {k: [] for k in ["luces", "carpas", "ventilacion", "clima", "fertilizantes", "foliares", "sustratos", "geneticas"]}
    filas = []
    finales = [os.path.join(RAIZ, n) for n in ARCHIVOS if os.path.exists(os.path.join(RAIZ, n))]
    for ruta in finales:
        for p in leer(ruta):
            clave = CLAVE_MARCAS[p["categoria"]]
            if p["marca"] not in marcas[clave]:
                marcas[clave].append(p["marca"])
            for f in p["fuentes"]:
                filas.append([p["id"], f["url"], f["fuente_tipo"], f["fecha_captura"]])
    for k in marcas:
        marcas[k].sort(key=str.lower)
    escribir_json(os.path.join(RAIZ, "marcas.json"), marcas)
    with open(os.path.join(RAIZ, "fuentes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "url", "fuente_tipo", "fecha_captura"])
        w.writerows(filas)
    sugeridas.sort(key=lambda s: (s.get("categoria") or "", (s.get("marca") or "").lower()))
    escribir_json(os.path.join(RAIZ, "marcas_sugeridas.json"), sugeridas)
    conteo = {n: len(leer(os.path.join(RAIZ, n))) for n in ARCHIVOS if os.path.exists(os.path.join(RAIZ, n))}
    print("Productos por archivo:", conteo)
    return validar(finales)


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "validar"
    if accion == "unir":
        if len(sys.argv) < 3:
            sys.exit("unir pisa los archivos finales con lo de tmp/: nombrá los archivos (ej. unir luces.json). Para solo regenerar índices: indices")
        ok = unir(sys.argv[2:])
    elif accion == "indices":
        ok = indices()
    else:
        rutas = sys.argv[2:] or [os.path.join(RAIZ, n) for n in ARCHIVOS if os.path.exists(os.path.join(RAIZ, n))]
        ok = validar(rutas)
    sys.exit(0 if ok else 1)
