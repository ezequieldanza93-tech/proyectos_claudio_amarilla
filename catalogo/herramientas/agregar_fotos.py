"""Busca el link a la foto de cada producto en las páginas que ya son sus fuentes.

Uso (desde catalogo/):
  python -P herramientas/agregar_fotos.py buscar     # arma tmp/fotos/resultado.json (no toca el catálogo)
  python -P herramientas/agregar_fotos.py completar  # reintenta solo los que quedaron sin foto (usa la caché)
  python -P herramientas/agregar_fotos.py aplicar    # escribe imagen_url en los archivos finales

Reglas: solo páginas que ya están en `fuentes` (fabricante > distribuidor > vendedor), nunca Mercado Libre,
respeta robots.txt (para «*» y para Claude-User), pausa ≥ 1,6 s por dominio (61 s en amnesiagrow.com.ar,
que pide Crawl-delay 60) y guarda las páginas en .cache/fotos/. La foto es la que la página declara como
principal (og:image); en Santa Planta, la primera imagen de su API pública. Una imagen que la página no
asocia al producto (portada del sitio, logo) no cuenta: sin foto propia, imagen_url queda en null.
"""
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS = ["fertilizantes.json", "foliares.json", "sustratos.json", "luces.json", "carpas.json",
            "ventilacion.json", "clima.json", "geneticas.json"]
CACHE = os.path.join(RAIZ, ".cache", "fotos")
SALIDA = os.path.join(RAIZ, "tmp", "fotos", "resultado.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) catalogo-personal/0.1"}
PRIORIDAD = {"fabricante": 0, "distribuidor": 1, "vendedor": 2}
AMNESIA_GUARDADAS = os.path.join(RAIZ, "tmp", "gap-amnesia", "paginas")
_ultimo, _robots = {}, {}


def pausa(dominio):
    espera = 61 if "amnesiagrow" in dominio else 1.6
    t = _ultimo.get(dominio, 0) + espera - time.time()
    if t > 0:
        time.sleep(t)
    _ultimo[dominio] = time.time()


def permitido(url):
    d = urlparse(url)
    base = f"{d.scheme}://{d.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            pausa(d.netloc)
            r = requests.get(base + "/robots.txt", headers=UA, timeout=20)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except Exception:
            rp.parse([])
        _robots[base] = rp
    rp = _robots[base]
    return rp.can_fetch("*", url) and rp.can_fetch("Claude-User", url) and rp.can_fetch("ClaudeBot", url)


def pagina(url):
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".html")
    if os.path.exists(ruta):
        return open(ruta, encoding="utf-8", errors="ignore").read()
    slug = url.rstrip("/").split("/")[-1]
    guardada = os.path.join(AMNESIA_GUARDADAS, slug + ".html")
    if "amnesiagrow" in url and os.path.exists(guardada):
        return open(guardada, encoding="utf-8", errors="ignore").read()
    pausa(urlparse(url).netloc)
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    open(ruta, "w", encoding="utf-8").write(r.text)
    return r.text


def og_image(h):
    for prop in ("og:image:secure_url", "og:image", "twitter:image"):
        for patron in (rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']+)["\']',
                       rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{prop}["\']'):
            m = re.search(patron, h, re.I)
            if m:
                u = html.unescape(m.group(1)).strip()
                return "https:" + u if u.startswith("//") else u
    return None


NO_PRODUCTO = re.compile(r"(?i)(icono|icon|marca-|logo|cert-|datafiscal|telas|banner|placeholder)")


def imagen_principal(h, url):
    """og:image; si la página no lo declara, la imagen principal que marca la plantilla del sitio."""
    img = og_image(h)
    if img and not NO_PRODUCTO.search(img.rsplit("/", 1)[-1]):  # algunas tiendas declaran su logo como og:image
        return img
    m = re.search(r'<img[^>]+class="[^"]*\b(?:amp-main-image|wp-post-image)\b[^"]*"[^>]*>', h)
    if m:
        s = re.search(r'(?:data-src|src)="([^"]+)"', m.group(0))
        if s:
            return html.unescape(s.group(1))
    if "terrafertil.com/productos/" in url:
        # Terrafertil: la primera imagen es el banner («hero»); la foto del producto es la del bloque «p-thumbnail».
        k = h.find("p-thumbnail")
        if k >= 0:
            s = re.search(r'<img[^>]+src="([^"]+)"', h[k:k + 1500])
            if s and not NO_PRODUCTO.search(s.group(1).rsplit("/", 1)[-1]):
                return html.unescape(s.group(1))
    return None


def santa_planta(url):
    slug = url.rstrip("/").split("/")[-1]
    api = "https://santaplanta.com.ar/wp-json/wc/store/v1/products"
    pausa("santaplanta.com.ar")
    r = requests.get(api, params={"slug": slug}, headers=UA, timeout=30)
    d = r.json() if r.status_code == 200 else []
    return d[0]["images"][0]["src"] if d and d[0].get("images") else None


def es_portada(url):
    return urlparse(url).path.strip("/") == ""


def buscar(solo_faltantes=False):
    previo = json.load(open(SALIDA, encoding="utf-8")) if solo_faltantes and os.path.exists(SALIDA) else {}
    resultado = dict(previo)
    for a in ARCHIVOS:
        for p in json.load(open(os.path.join(RAIZ, a), encoding="utf-8")):
            if solo_faltantes and (previo.get(p["id"]) or {}).get("imagen_url"):
                continue
            elegido = None
            for f in sorted(p["fuentes"], key=lambda f: PRIORIDAD[f["fuente_tipo"]]):
                u = f["url"]
                if u.lower().endswith(".pdf") or "mercadolibre" in u or es_portada(u):
                    continue
                try:
                    if not permitido(u):
                        print("robots no permite:", u)
                        continue
                    img = santa_planta(u) if "santaplanta.com.ar/producto/" in u else imagen_principal(pagina(u), u)
                except Exception as e:
                    print("error", u, type(e).__name__)
                    continue
                if img:
                    elegido = {"imagen_url": img, "desde": u}
                    break
            resultado[p["id"]] = elegido or {"imagen_url": None, "desde": None}
            print(("OK  " if elegido else "--  ") + p["id"], flush=True)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(resultado, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def aplicar():
    res = json.load(open(SALIDA, encoding="utf-8"))
    for a in ARCHIVOS:
        ruta = os.path.join(RAIZ, a)
        d = json.load(open(ruta, encoding="utf-8"))
        for p in d:
            p["imagen_url"] = (res.get(p["id"]) or {}).get("imagen_url")
        with open(ruta, "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("con foto:", sum(1 for v in res.values() if v.get("imagen_url")), "de", len(res))


if __name__ == "__main__":
    {"buscar": buscar, "completar": lambda: buscar(solo_faltantes=True), "aplicar": aplicar}[sys.argv[1] if len(sys.argv) > 1 else "buscar"]()
