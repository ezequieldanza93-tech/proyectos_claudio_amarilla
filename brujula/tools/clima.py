#!/usr/bin/env python3
"""Trae el clima de cada centro de cultivo (weather/wx-<centro>) y del inicio (weather/wx-home).

Uso: python3 clima.py <carpeta con projects/*.json y weather/*.json exportados de la base> <carpeta de salida>
Lugares: centros de cultivo (projects.centers[].municipio), el inicio (projects.homeWeather) y proyectos con lugar propio (projects.weatherPlace).
Geocodifica con Open-Meteo (solo Argentina) y toma el pronóstico de MET Norway (api.met.no).
"""
import json, sys, glob, os, math, urllib.request, urllib.parse, datetime as dt

UA = {"User-Agent": "brujula-cultivo/1.0 (uso personal)"}
TZ = dt.timezone(dt.timedelta(hours=-3))  # America/Argentina/Buenos_Aires

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)

def geocode(name):
    q = "Buenos Aires" if "autónoma" in name.lower() or name.strip().upper() == "CABA" else name
    res = get("https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({"name": q, "count": 10, "language": "es", "countryCode": "AR"})).get("results") or []
    if not res:
        return None
    def score(r):
        s = 0
        if r.get("admin1") in ("Buenos Aires", "Ciudad Autónoma de Buenos Aires"): s += 4
        if name.lower() in (r.get("admin2") or "").lower(): s += 3
        if r.get("feature_code") in ("PPLA", "PPLA2", "PPLC"): s += 2
        return s + math.log10((r.get("population") or 1))
    r = max(res, key=score)
    return {"lat": round(r["latitude"], 3), "lon": round(r["longitude"], 3), "label": ", ".join(x for x in [r.get("name"), r.get("admin2"), r.get("admin1")] if x)}

def svp(t):
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))

def forecast(lat, lon):
    d = get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}")
    hours = []
    for ts in d["properties"]["timeseries"]:
        t = dt.datetime.fromisoformat(ts["time"].replace("Z", "+00:00")).astimezone(TZ)
        det = ts["data"]["instant"]["details"]
        rain = ((ts["data"].get("next_1_hours") or ts["data"].get("next_6_hours") or {}).get("details") or {}).get("precipitation_amount")
        span = 1 if ts["data"].get("next_1_hours") else 6
        hours.append({"t": t, "temp": det.get("air_temperature"), "hum": det.get("relative_humidity"), "rain": rain, "span": span})
    return hours

def build(key, kind, name, geo, hours, prev):
    now = dt.datetime.now(TZ)
    cur = min(hours, key=lambda h: abs((h["t"] - now).total_seconds()))
    days = {}
    for h in hours:
        if h["temp"] is None or h["hum"] is None: continue
        k = h["t"].date().isoformat()
        dd = days.setdefault(k, {"temps": [], "hums": [], "vpd": [], "rain": 0.0, "rainKnown": False})
        dd["temps"].append(h["temp"]); dd["hums"].append(h["hum"]); dd["vpd"].append(svp(h["temp"]) * (1 - h["hum"] / 100))
        if h["rain"] is not None: dd["rain"] += h["rain"]; dd["rainKnown"] = True
    out = []
    for k in sorted(days)[:7]:
        dd = days[k]
        out.append({"date": k, "tMax": round(max(dd["temps"]), 1), "tMin": round(min(dd["temps"]), 1), "humMean": round(sum(dd["hums"]) / len(dd["hums"])),
                    "humMin": round(min(dd["hums"])), "vpdMax": round(max(dd["vpd"]), 2), "rainMm": round(dd["rain"], 1) if dd["rainKnown"] else None})
    # historial: guarda el último pronóstico de cada día ya pasado (máx. 180 días)
    hist = dict((prev or {}).get("history") or {})
    for d in (prev or {}).get("days") or []:
        if d["date"] < now.date().isoformat(): hist[d["date"]] = d
    hist = dict(sorted(hist.items())[-180:])
    doc = {"kind": kind, "municipio": name, "place": geo["label"], "lat": geo["lat"], "lon": geo["lon"],
           "current": {"time": cur["t"].strftime("%Y-%m-%d %H:%M"), "temp": cur["temp"], "hum": cur["hum"]},
           "days": out, "history": hist, "source": "MET Norway (api.met.no); ubicación: Open-Meteo", "updatedAt": int(now.timestamp() * 1000), "updatedLocal": now.strftime("%d/%m %H:%M")}
    if kind == "center": doc["centerId"] = key
    if kind == "project": doc["projectId"] = key
    return doc

def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    prev = {}
    for f in glob.glob(os.path.join(src, "weather", "*.json")):
        d = json.load(open(f)); prev[os.path.basename(f)[:-5]] = d.get("data", d)
    targets = []  # (doc_id, kind, key, lugar)
    for f in sorted(glob.glob(os.path.join(src, "projects", "*.json"))):
        p = json.load(open(f)); p = p.get("data", p)
        for c in p.get("centers") or []:
            if (c.get("municipio") or "").strip(): targets.append(("wx-" + c["id"], "center", c["id"], c["municipio"].strip()))
        hw = (p.get("homeWeather") or "").strip() if isinstance(p.get("homeWeather"), str) else ""
        if hw: targets.append(("wx-home", "home", "home", hw))
        wp = p.get("weatherPlace") if isinstance(p.get("weatherPlace"), str) else ""
        if wp.strip(): targets.append(("wx-p-" + os.path.basename(f)[:-5], "project", os.path.basename(f)[:-5], wp.strip()))
    done = []
    for doc_id, kind, key, place in targets:
        geo = geocode(place)
        if not geo:
            print(f"SIN UBICACION {doc_id}: {place}"); continue
        w = build(key, kind, place, geo, forecast(geo["lat"], geo["lon"]), prev.get(doc_id))
        pth = os.path.join(dst, doc_id + ".json"); json.dump(w, open(pth, "w"), ensure_ascii=False)
        done.append(pth); print("OK", doc_id, place, "->", geo["label"], "ahora", w["current"])
    print("ARCHIVOS", json.dumps(done))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
