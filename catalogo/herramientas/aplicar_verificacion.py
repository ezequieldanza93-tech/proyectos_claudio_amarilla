"""Aplica al catálogo los resultados de la verificación contra las fuentes.

Lee tmp/verificacion/<lote>-v1.json (verificador) y <lote>-v2.json (escéptico que intenta refutar):
- confirmado  -> se aplica valor_correcto_json al campo (si el producto sigue validando; si no, queda dudoso)
- refutado    -> no se toca
- dudoso      -> no se toca y va a pendientes
verificado = true solo si el producto se pudo abrir y no quedó ninguna observación dudosa.
Escribe tmp/verificacion/cambios.md y tmp/verificacion/pendientes_verificacion.md.

Uso (desde catalogo/): python -P herramientas/aplicar_verificacion.py [carpeta_de_la_corrida]
"""
import glob
import json
import os
import sys
from collections import defaultdict

from jsonschema import Draft202012Validator

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Carpeta con los <lote>-v1/-v2.json de UNA corrida (los lotes ya aplicados se archivan aparte para no re-aplicarlos)
VER = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RAIZ, "tmp", "verificacion")
ARCHIVOS = ["fertilizantes.json", "foliares.json", "sustratos.json", "luces.json", "carpas.json",
            "ventilacion.json", "clima.json", "geneticas.json"]


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def main():
    esquema = leer(os.path.join(RAIZ, "esquema", "catalogo.schema.json"))
    validador = Draft202012Validator(esquema["$defs"]["producto"] | {"$defs": esquema["$defs"]})
    datos, donde = {}, {}
    for a in ARCHIVOS:
        ruta = os.path.join(RAIZ, a)
        if os.path.exists(ruta):
            datos[a] = leer(ruta)
            for p in datos[a]:
                donde[p["id"]] = p

    estado, decisiones = {}, defaultdict(list)
    for r1 in sorted(glob.glob(os.path.join(VER, "*-v1.json"))):
        try:
            for r in leer(r1).get("resultados", []):
                estado[r["id"]] = r
        except Exception as e:
            print("No se pudo leer", r1, e)
        r2 = r1.replace("-v1.json", "-v2.json")
        if os.path.exists(r2):
            try:
                for d in leer(r2).get("decisiones", []):
                    decisiones[d["id"]].append(d)
            except Exception as e:
                print("No se pudo leer", r2, e)

    cambios, pendientes = [], []
    cont = defaultdict(int)
    for pid, r in estado.items():
        p = donde.get(pid)
        if p is None:
            pendientes.append(f"- `{pid}`: el verificador lo nombra pero no está en el catálogo.")
            continue
        dudas = 0
        if r.get("estado") == "fuente_no_disponible":
            dudas += 1
            pendientes.append(f"- `{pid}`: no se pudo reabrir ninguna fuente para verificarlo.")
        obs_campos = {o["campo"] for o in r.get("observaciones", [])}
        decididos = set()
        for d in decisiones.get(pid, []):
            decididos.add(d["campo"])
            if d["veredicto"] == "refutado":
                cont["refutado"] += 1
                continue
            if d["veredicto"] == "dudoso":
                dudas += 1
                cont["dudoso"] += 1
                pendientes.append(f"- `{pid}` · {d['campo']}: dudoso — {d.get('motivo', '')} ({d.get('url', '')})")
                continue
            # confirmado
            try:
                valor = json.loads(d["valor_correcto_json"]) if d.get("valor_correcto_json") is not None else None
            except Exception:
                dudas += 1
                cont["dudoso"] += 1
                pendientes.append(f"- `{pid}` · {d['campo']}: confirmado pero el valor no es JSON válido ({d.get('valor_correcto_json')!r}).")
                continue
            anterior = p.get(d["campo"], "<sin campo>")
            if anterior == valor:
                cont["refutado"] += 1
                continue
            p[d["campo"]] = valor
            errores = list(validador.iter_errors(p))
            if errores:
                if anterior == "<sin campo>":
                    p.pop(d["campo"], None)
                else:
                    p[d["campo"]] = anterior
                dudas += 1
                cont["dudoso"] += 1
                pendientes.append(f"- `{pid}` · {d['campo']}: confirmado ({d.get('motivo', '')}) pero el valor propuesto no valida con el esquema; queda como estaba.")
                continue
            cont["confirmado"] += 1
            cita = (d.get("cita") or "").replace("\n", " ")[:160]
            cambios.append(f"- `{pid}` · **{d['campo']}**: {json.dumps(anterior, ensure_ascii=False)[:120]} → {json.dumps(valor, ensure_ascii=False)[:120]} — {d.get('motivo', '')} [{d.get('url', '')}] «{cita}»")
        sin_decidir = obs_campos - decididos
        for c in sin_decidir:
            dudas += 1
            pendientes.append(f"- `{pid}` · {c}: observación del verificador sin segunda revisión.")
        p["verificado"] = dudas == 0
        cont["verificados" if dudas == 0 else "no_verificados"] += 1

    no_revisados = [pid for pid in donde if pid not in estado]
    for a, lista in datos.items():
        with open(os.path.join(RAIZ, a), "w", encoding="utf-8", newline="\n") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
            f.write("\n")
    with open(os.path.join(VER, "cambios.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(cambios) + "\n")
    with open(os.path.join(VER, "pendientes_verificacion.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(pendientes) + "\n")
    print(dict(cont), "| sin verificar todavía:", len(no_revisados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
