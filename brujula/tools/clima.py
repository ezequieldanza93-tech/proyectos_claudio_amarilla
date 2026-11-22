#!/usr/bin/env python3
"""Trae el clima del municipio de cada espacio de cultivo y arma los documentos weather/wx-<espacio>.

Uso: python3 clima.py <carpeta con spaces/*.json exportados de la base> <carpeta de salida>
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

def build(space, geo, hours):
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
    for k in sorted(days)[:6]:
        dd = days[k]
        out.append({"date": k, "tMax": round(max(dd["temps"]), 1), "tMin": round(min(dd["temps"]), 1), "humMean": round(sum(dd["hums"]) / len(dd["hums"])),
                    "humMin": round(min(dd["hums"])), "vpdMax": round(max(dd["vpd"]), 2), "rainMm": round(dd["rain"], 1) if dd["rainKnown"] else None})
    return {"spaceId": space["id"], "municipio": space["municipio"], "place": geo["label"], "lat": geo["lat"], "lon": geo["lon"],
            "current": {"time": cur["t"].strftime("%Y-%m-%d %H:%M"), "temp": cur["temp"], "hum": cur["hum"]},
            "days": out, "source": "MET Norway (api.met.no); ubicación: Open-Meteo", "updatedAt": int(now.timestamp() * 1000), "updatedLocal": now.strftime("%d/%m %H:%M")}

def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    done = []
    for f in sorted(glob.glob(os.path.join(src, "spaces", "*.json"))):
        doc = json.load(open(f))
        data = doc.get("data", doc)
        sid = os.path.basename(f)[:-5]
        muni = (data.get("municipio") or "").strip()
        if not muni or data.get("enabled") is False: continue
        geo = geocode(muni)
        if not geo:
            print(f"SIN UBICACION {sid}: {muni}"); continue
        w = build({"id": sid, "municipio": muni}, geo, forecast(geo["lat"], geo["lon"]))
        p = os.path.join(dst, f"wx-{sid}.json"); json.dump(w, open(p, "w"), ensure_ascii=False)
        done.append(p); print("OK", sid, muni, "->", geo["label"], "ahora", w["current"])
    print("ARCHIVOS", json.dumps(done))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
