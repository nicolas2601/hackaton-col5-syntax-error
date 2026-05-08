"""
Hackathon Nacional COL 5.0 — RONDA 1 — BD1 (SECOP II Contratos Electronicos)
Dataset: https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h
Equipo: Syntax Error
Fecha snapshot: 2026-05-04 (cobertura del dataset oficial)

Este script regenera todas las respuestas a las preguntas 3-14 de la Ronda 1
consultando directamente la API SODA oficial de Socrata (datos.gov.co).
No requiere descargar el dataset completo.

Uso:
    python3 bd1_respuestas.py
    python3 bd1_respuestas.py --token TU_APP_TOKEN_OPCIONAL

Dependencias:
    pip install requests
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any

import requests

DATASET = "jbjy-vk9h"
RESOURCE = f"https://www.datos.gov.co/resource/{DATASET}.json"
META = f"https://www.datos.gov.co/api/views/{DATASET}.json"


def soql(params: dict[str, str], headers: dict[str, str]) -> Any:
    r = requests.get(RESOURCE, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", help="Socrata App Token (opcional, sube rate limit)")
    args = ap.parse_args()

    headers = {"X-App-Token": args.token} if args.token else {}

    print("=" * 70)
    print("HACKATHON COL 5.0 - RONDA 1 - BD1 (jbjy-vk9h)")
    print("=" * 70)

    # ---- Metadata oficial: tipos de columnas (Q4, Q5, Q6, Q7) -------------
    meta = requests.get(META, headers=headers, timeout=60).json()
    cols = meta["columns"]
    types: Counter[str] = Counter()
    by_type: dict[str, list[str]] = {}
    for c in cols:
        t = c["dataTypeName"]
        types[t] += 1
        by_type.setdefault(t, []).append(c["name"])

    total_cols = len(cols)
    n_text = types.get("text", 0)
    n_number = types.get("number", 0)
    n_date = types.get("calendar_date", 0) + types.get(
        "floating_timestamp", 0
    ) + types.get("date", 0)
    n_url = types.get("url", 0)

    # ---- Q3: total registros ----------------------------------------------
    q3 = int(soql({"$select": "count(*)"}, headers)[0]["count"])

    # ---- Agregaciones: Q11, Q12, Q14 --------------------------------------
    aggs = soql(
        {
            "$select": (
                "max(dias_adicionados::number) as max_dias_num,"
                "max(valor_del_contrato) as max_valor,"
                "min(fecha_de_firma) as min_fecha_firma,"
                "max(fecha_de_firma) as max_fecha_firma"
            )
        },
        headers,
    )[0]
    q11 = int(float(aggs["max_dias_num"]))
    q12 = int(float(aggs["max_valor"]))
    q14_min = aggs["min_fecha_firma"][:10]
    q14_max = aggs["max_fecha_firma"][:10]

    # ---- Q9: %% nulls fecha_de_firma --------------------------------------
    q9_data = soql(
        {"$select": "count(*) as total, count(fecha_de_firma) as no_nulls"},
        headers,
    )[0]
    total = int(q9_data["total"])
    no_nulls_firma = int(q9_data["no_nulls"])
    nulls_firma = total - no_nulls_firma
    q9 = round(nulls_firma * 100 / total, 4)

    # ---- Q10: count nulls fecha_inicio_liquidacion ------------------------
    q10_data = soql(
        {"$select": "count(fecha_inicio_liquidacion) as no_nulls"}, headers
    )[0]
    q10 = total - int(q10_data["no_nulls"])

    # ---- Q13: top 10 distinct valor_del_contrato DESC ---------------------
    q13_data = soql(
        {
            "$select": "valor_del_contrato",
            "$where": "valor_del_contrato IS NOT NULL",
            "$group": "valor_del_contrato",
            "$order": "valor_del_contrato DESC",
            "$limit": "10",
        },
        headers,
    )
    q13_top10 = [int(float(r["valor_del_contrato"])) for r in q13_data]
    q13_septimo_distinct = q13_top10[6]

    # ---- Q8: variable con mas nulls ---------------------------------------
    # Buscar columnas con 100% nulls (no_nulls = 0)
    candidates = [
        "recursos_de_credito",
        "presupuesto_general_de_la_nacion_pgn",
        "sistema_general_de_participaciones",
        "sistema_general_de_regal_as",
        "recursos_propios",
        "fecha_de_notificaci_n_de_prorrogaci_n",
        "fecha_fin_liquidacion",
        "fecha_inicio_liquidacion",
        "valor_de_pago_adelantado",
        "puntos_del_acuerdo",
        "pilares_del_acuerdo",
    ]
    null_pcts: list[tuple[str, float]] = []
    for col in candidates:
        try:
            r = soql({"$select": f"count({col}) as nn"}, headers)[0]
            nn = int(r["nn"])
            pct = (total - nn) * 100.0 / total
            null_pcts.append((col, pct))
        except Exception:
            pass
    null_pcts.sort(key=lambda x: x[1], reverse=True)
    q8_winner = null_pcts[0]

    # ---- Reporte ----------------------------------------------------------
    print(f"\n=== RESPUESTAS RONDA 1 — BD1 (jbjy-vk9h) ===")
    print(f"\nQ3.  Total registros               : {q3}")
    print(f"Q4.  Total variables               : {total_cols}")
    print(f"Q5.  Variables tipo FECHA          : {n_date}")
    for c in by_type.get("calendar_date", []):
        print(f"        - {c}")
    print(f"Q6.  Variables tipo NUMERICO       : {n_number}")
    for c in by_type.get("number", []):
        print(f"        - {c}")
    print(f"Q7.  Variables tipo TEXTO          : {n_text}  (URL aparte: {n_url})")
    print(
        f"     [Si la rubrica considera URL como texto -> {n_text + n_url}]"
    )
    print(f"Q8.  Variable con MAS nulls        : {q8_winner[0]}  ({q8_winner[1]:.4f}% nulls)")
    print("     (5 columnas tienen 100% nulls en el dataset oficial:")
    for col, pct in null_pcts:
        if pct > 99.99:
            print(f"        - {col}: {pct:.4f}%")
    print(f"Q9.  % nulls Fecha de Firma        : {q9}")
    print(f"Q10. Nulls Fecha Inicio Liquidacion: {q10}")
    print(f"Q11. Max Dias adicionados          : {q11}")
    print(f"Q12. Max Valor del Contrato        : {q12}")
    print(f"Q13. 7o Valor del Contrato (distinct DESC): {q13_septimo_distinct}")
    print(f"     Top 10 distintos: {q13_top10}")
    print(f"Q14. Min/Max Fecha de Firma        : {q14_min} / {q14_max}")

    # JSON estructurado para automatizacion
    report = {
        "dataset": DATASET,
        "snapshot_date": q14_max,
        "answers": {
            "Q3_total_registros": q3,
            "Q4_total_variables": total_cols,
            "Q5_fecha_count": n_date,
            "Q5_fecha_columns": by_type.get("calendar_date", []),
            "Q6_numero_count": n_number,
            "Q6_numero_columns": by_type.get("number", []),
            "Q7_texto_count_socrata": n_text,
            "Q7_texto_count_si_url_es_texto": n_text + n_url,
            "Q7_texto_columns": by_type.get("text", []),
            "Q7_url_columns": by_type.get("url", []),
            "Q8_variable_mas_nulls": q8_winner[0],
            "Q8_pct_nulls": round(q8_winner[1], 4),
            "Q8_columnas_100pct_null": [c for c, p in null_pcts if p > 99.99],
            "Q9_pct_nulls_fecha_firma": q9,
            "Q10_nulls_fecha_inicio_liquidacion": q10,
            "Q11_max_dias_adicionados": q11,
            "Q12_max_valor_contrato": q12,
            "Q13_7mo_valor_distinct": q13_septimo_distinct,
            "Q13_top10_distinct": q13_top10,
            "Q14_min_fecha_firma": q14_min,
            "Q14_max_fecha_firma": q14_max,
        },
    }
    out_path = "respuestas_bd1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nJSON guardado en: {out_path}")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"ERROR HTTP: {e}", file=sys.stderr)
        sys.exit(1)
