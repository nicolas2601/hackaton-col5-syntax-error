"""Hackathon COL 5.0 RONDA 2 - Analisis SECOP II snapshot 2026-05-06.

CSV: /tmp/ronda2/SECOP_II_-_Contratos_Electronicos_20260506.csv (1.7GB, 1.71M filas, 84 cols)
Output: respuestas_ronda2.json

Dependencias: pip install duckdb
"""
from __future__ import annotations

import json
from pathlib import Path

import duckdb

CSV = "/tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv"
OUT = Path(__file__).parent / "respuestas_ronda2.json"


def main() -> None:
    con = duckdb.connect()
    con.execute(
        f"""
        CREATE OR REPLACE VIEW c AS
        SELECT * FROM read_csv_auto('{CSV}', SAMPLE_SIZE=-1, header=true, all_varchar=true);
        """
    )

    r: dict = {}

    # Q3: total registros
    total = con.execute("SELECT COUNT(*) FROM c").fetchone()[0]
    r["Q3_total"] = total
    print(f"Q3 total registros: {total}")

    # Q4: total columnas
    cols_info = con.execute("DESCRIBE c").fetchall()
    r["Q4_cols"] = len(cols_info)
    print(f"Q4 total cols: {len(cols_info)}")

    # Rango fechas (para entender el snapshot)
    fmin, fmax = con.execute(
        'SELECT MIN("Fecha de Firma"), MAX("Fecha de Firma") FROM c'
    ).fetchone()
    r["fecha_firma_min"] = fmin
    r["fecha_firma_max"] = fmax
    print(f"Rango fecha_firma: {fmin} -> {fmax}")

    # Q5: registros 2025 (Fecha de Firma)
    q5 = con.execute(
        """SELECT COUNT(*) FROM c
        WHERE TRY_CAST(SUBSTR("Fecha de Firma", 7, 4) AS INT) = 2025
        OR TRY_CAST(SUBSTR("Fecha de Firma", 1, 4) AS INT) = 2025"""
    ).fetchone()[0]
    r["Q5_2025"] = q5
    print(f"Q5 contratos 2025: {q5}")

    # Q6/Q7: Pymes
    pymes = con.execute("""SELECT COUNT(*) FROM c WHERE "Es Pyme" = 'Si'""").fetchone()[0]
    r["Q6_pyme_pct"] = round(pymes * 100 / total, 2)
    r["Q7_pyme_count"] = pymes
    print(f"Q6/Q7 Pymes: {pymes} ({r['Q6_pyme_pct']}%)")

    # Q8: Top 10 departamentos
    top10 = con.execute(
        """SELECT "Departamento", COUNT(*) as n FROM c
        GROUP BY "Departamento" ORDER BY n DESC LIMIT 10"""
    ).fetchall()
    r["Q8_top10_deptos"] = top10
    print("Q8 Top 10 deptos:")
    for d, n in top10:
        print(f"  {d}: {n}")

    # Q9: Posición 6
    if len(top10) >= 6:
        r["Q9_pos6_dept"] = top10[5][0]
        r["Q9_pos6_count"] = top10[5][1]
        print(f"Q9 pos6: {top10[5][0]} = {top10[5][1]}")

    # Q10/Q11: Modalidad preferida
    modalidades = con.execute(
        """SELECT "Modalidad de Contratacion", COUNT(*) as n FROM c
        GROUP BY "Modalidad de Contratacion" ORDER BY n DESC LIMIT 5"""
    ).fetchall()
    r["top5_modalidades"] = modalidades
    if modalidades:
        r["Q10_modalidad"] = modalidades[0][0]
        r["Q11_count_modalidad"] = modalidades[0][1]
    print(f"Q10/Q11 modalidad top: {modalidades[0]}")

    # Q12: Top 3 entidades por valor
    top_ent = con.execute(
        """SELECT "Nombre Entidad", SUM(TRY_CAST(REGEXP_REPLACE("Valor del Contrato", '[$,]', '', 'g') AS DOUBLE)) as total
        FROM c WHERE "Valor del Contrato" IS NOT NULL
        GROUP BY "Nombre Entidad" ORDER BY total DESC LIMIT 5"""
    ).fetchall()
    r["Q12_top3_entidades"] = top_ent[:3]
    r["Q12_top5_entidades"] = top_ent
    print("Q12 Top entidades:")
    for ent, val in top_ent:
        print(f"  {ent}: {(val or 0):,.0f}")

    # Q13: Top 5 tipos de contrato
    tipos = con.execute(
        """SELECT "Tipo de Contrato", COUNT(*) as n FROM c
        GROUP BY "Tipo de Contrato" ORDER BY n DESC LIMIT 5"""
    ).fetchall()
    r["Q13_top5_tipos"] = tipos
    print("Q13 Top 5 tipos:")
    for t, n in tipos:
        print(f"  {t}: {n}")

    # Q14: % del top 1 tipo
    if tipos:
        r["Q14_pct_top1"] = round(tipos[0][1] * 100 / total, 2)
        print(f"Q14 % top1: {r['Q14_pct_top1']}%")

    # Q15: top valores anomalos
    top_anom = con.execute(
        """SELECT "Nombre Entidad", "Proveedor Adjudicado", "Documento Proveedor",
        TRY_CAST(REGEXP_REPLACE("Valor del Contrato", '[$,]', '', 'g') AS DOUBLE) as valor, "ID Contrato",
        "Fecha de Firma", "Modalidad de Contratacion"
        FROM c WHERE "Valor del Contrato" IS NOT NULL
        ORDER BY valor DESC LIMIT 10"""
    ).fetchall()
    r["Q15_top10_valores"] = top_anom
    print("Q15 Top 10 valores anomalos:")
    for row in top_anom[:5]:
        print(f"  {(row[0] or '')[:50]} | {(row[1] or '')[:30]} | {(row[3] or 0):,.0f}")

    # Q16: % pago adelantado
    adelantado = con.execute(
        """SELECT COUNT(*) FROM c WHERE "Habilita Pago Adelantado" = 'Si'"""
    ).fetchone()[0]
    r["Q16_pct_adelantado"] = round(adelantado * 100 / total, 2)
    r["Q16_count_adelantado"] = adelantado
    print(f"Q16 % adelantado: {r['Q16_pct_adelantado']}%")

    # Q17: contratos con obligacion ambiental
    ambiental = con.execute(
        """SELECT COUNT(*) FROM c WHERE "Obligación Ambiental" = 'Si'"""
    ).fetchone()[0]
    r["Q17_ambiental"] = ambiental
    print(f"Q17 ambiental: {ambiental}")

    # Q18: Pareto - top 20% proveedores controlan X% del valor
    pareto = con.execute(
        """WITH provs AS (
            SELECT "Documento Proveedor",
                   SUM(TRY_CAST(REGEXP_REPLACE("Valor del Contrato", '[$,]', '', 'g') AS DOUBLE)) as total
            FROM c WHERE "Valor del Contrato" IS NOT NULL
              AND "Documento Proveedor" IS NOT NULL
            GROUP BY "Documento Proveedor"
        ),
        ranked AS (
            SELECT *, NTILE(5) OVER (ORDER BY total DESC) as q
            FROM provs
        )
        SELECT q, SUM(total) as suma, COUNT(*) as n
        FROM ranked GROUP BY q ORDER BY q"""
    ).fetchall()
    r["Q18_pareto_quintiles"] = pareto
    if pareto:
        total_val = sum(row[1] or 0 for row in pareto)
        top20 = (pareto[0][1] or 0) / total_val * 100 if total_val else 0
        r["Q18_top20_pct"] = round(top20, 2)
        r["Q18_total_proveedores"] = sum(row[2] for row in pareto)
        print(f"Q18 Top 20% proveedores controlan: {top20:.2f}% del valor")
        for q, suma, n in pareto:
            pct = (suma or 0) / total_val * 100 if total_val else 0
            print(f"  Quintil {q}: {n} provs, ${suma:,.0f} ({pct:.1f}%)")

    # Q19: Brecha de genero
    genero = con.execute(
        """SELECT "Género Representante Legal", COUNT(*) as n,
        SUM(TRY_CAST(REGEXP_REPLACE("Valor del Contrato", '[$,]', '', 'g') AS DOUBLE)) as total,
        AVG(TRY_CAST(REGEXP_REPLACE("Valor del Contrato", '[$,]', '', 'g') AS DOUBLE)) as promedio
        FROM c WHERE "Género Representante Legal" IS NOT NULL
        GROUP BY "Género Representante Legal" ORDER BY total DESC NULLS LAST"""
    ).fetchall()
    r["Q19_genero"] = genero
    print("Q19 Brecha genero:")
    for g, n, total_g, prom in genero:
        print(f"  {g}: {n} contratos | ${total_g or 0:,.0f} | promedio ${prom or 0:,.0f}")

    # Q20: anomalias tipo (manual basado en CSV)
    r["Q20_anomalias"] = (
        "Las 84 columnas vienen como TEXT en CSV. Anomalias de tipo donde "
        "deberian ser numerico/fecha/booleano: "
        "(1) Valor del Contrato y todos los Valor* deberian ser DECIMAL/numeric, vienen como string. "
        "(2) Fecha de Firma y todas las Fecha* deberian ser DATE, vienen como string. "
        "(3) Es Pyme, Es Grupo, Habilita Pago Adelantado, Obligacion Ambiental deberian ser BOOLEAN, vienen como Si/No. "
        "(4) Dias Adicionados deberia ser INTEGER. "
        "(5) Nit Entidad y Documento Proveedor deberian ser STRING (NIT/CC) pero a veces se castea a NUMBER perdiendo el digito de verificacion."
    )

    # Save
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, default=str, ensure_ascii=False)
    print(f"\n=> Resultados guardados en {OUT}")


if __name__ == "__main__":
    main()
