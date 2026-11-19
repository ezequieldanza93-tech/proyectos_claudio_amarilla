"""Revisión de muestra: elige N productos al azar (semilla fija, reproducible), vuelve a abrir sus fuentes
y busca cada dato no nulo en el texto de la fuente. Imprime OK / NO ENCONTRADO por campo para revisar a mano.

Uso (desde catalogo/): python -P herramientas/revisar_muestra.py [N=10] [semilla=2026-11-19]
No abre mercadolibre.com.ar (su robots.txt prohíbe a Claude) ni amnesiagrow.com.ar (crawl-delay 60 s).
"""
import html
import io
import json
import os
import random
import re
import sys
import time
import unicodedata

import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS = ["fertilizantes.json", "foliares.json", "sustratos.json", "luces.json", "carpas.json",
            "ventilacion.json", "clima.json", "geneticas.json"]
NO_REVISAR = {"id", "categoria", "fuentes", "conflictos", "verificado", "notas", "descripcion_corta", "uso", "unidad"}
PROHIBIDOS = ("mercadolibre.com.ar", "amnesiagrow.com.ar")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catalogo-personal/0.1"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    return re.sub(r"\s+", " ", s)


def texto(url):
    r = requests.get(url, headers=UA, timeout=40)
    if url.lower().endswith(".pdf") or "pdf" in r.headers.get("content-type", ""):
        import fitz
        return "".join(p.get_text() for p in fitz.open(stream=io.BytesIO(r.content), filetype="pdf"))
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", r.text)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def numeros(v):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", norm(v))]


def aparece(valor, fuente_n, nums_fuente):
    if isinstance(valor, bool):
        return None  # booleanos no se buscan como texto
    if isinstance(valor, (int, float)):
        cands = {float(valor)}
        if valor >= 1000 and valor % 1000 == 0:
            cands.add(valor / 1000)  # 1000 ml = 1 L
        return any(c in nums_fuente for c in cands)
    if isinstance(valor, list):
        res = [aparece(x, fuente_n, nums_fuente) for x in valor]
        res = [x for x in res if x is not None]
        return all(res) if res else None
    if isinstance(valor, dict):
        res = [aparece(v, fuente_n, nums_fuente) for k, v in valor.items() if k in ("min", "max", "cantidad", "diametro") and v is not None]
        return all(res) if res else None
    v = norm(valor)
    if v in fuente_n:
        return True
    ns = numeros(v)
    if ns:
        return all(n in nums_fuente for n in ns)
    palabras = [w for w in re.findall(r"[a-z]{4,}", v)]
    return bool(palabras) and sum(w in fuente_n for w in palabras) / len(palabras) >= 0.6


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    semilla = sys.argv[2] if len(sys.argv) > 2 else "2026-11-19"
    todos = []
    for a in ARCHIVOS:
        ruta = os.path.join(RAIZ, a)
        if os.path.exists(ruta):
            todos += json.load(open(ruta, encoding="utf-8"))
    muestra = random.Random(semilla).sample(todos, n)
    for p in muestra:
        print(f"\n### {p['id']} ({p['categoria']}, {p['marca']})")
        corpus = ""
        for f in p["fuentes"]:
            if any(d in f["url"] for d in PROHIBIDOS):
                print(f"  fuente omitida (prohibida): {f['url']}")
                continue
            try:
                corpus += " " + texto(f["url"])
                print(f"  fuente abierta: {f['url']}")
            except Exception as e:
                print(f"  fuente NO disponible: {f['url']} ({type(e).__name__})")
            time.sleep(1.6)
        fn = norm(corpus)
        nums = set(float(x) for x in re.findall(r"\d+(?:\.\d+)?", fn))
        for k, v in p.items():
            if k in NO_REVISAR or v is None or v == [] or v == "":
                continue
            r = aparece(v, fn, nums) if corpus else None
            marca = "OK" if r else ("—" if r is None else "NO ENCONTRADO")
            print(f"  {marca:13} {k}: {json.dumps(v, ensure_ascii=False)[:110]}")


if __name__ == "__main__":
    main()
