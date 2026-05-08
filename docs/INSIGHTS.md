# 💡 INSIGHTS.md — Hallazgos Analíticos Hackathon COL 5.0

> Síntesis de hallazgos críticos del análisis de SECOP II (snapshot 2025).
> Visualizaciones ASCII para facilitar lectura sin dependencias externas.

---

## 🚩 1. Hiperconcentración en Contratación Directa (75.7%)

**Bandera roja de transparencia**. La modalidad "contratación directa" — la que **menos competencia exige** — domina abrumadoramente.

```
Contratación directa  ███████████████████████████████████████ 75.7%
Mínima cuantía        ██████ 11.5%
Selección abreviada   ███ 5.7%
Licitación pública    ██ 3.3%
Concurso de méritos   █ 1.5%
Otras                 ██ 2.4%
```

**Implicación**: Sólo **3.3% de los contratos** pasan por licitación pública abierta — el mecanismo que maximiza competencia y minimiza arbitrariedad.

> **📉 Hipótesis**: si el 75.7% se mantiene constante año tras año, hay riesgo sistémico de captura institucional.

---

## 📈 2. Pareto 7/80 — Hiperconcentración Estructural

**No es Pareto clásico 80/20**. Encontramos **Pareto 7/80**: sólo el **7.23% de las entidades** concentran el **80% del valor total contratado**.

```
% acumulado del valor
100% ┤                                           ╭──────
 90% ┤                                      ╭────
 80% ┤                                ╭─────       ← 7.23% de entidades
 70% ┤                          ╭─────
 60% ┤                    ╭─────
 50% ┤              ╭─────
 40% ┤        ╭─────
 30% ┤   ╭────
 20% ┤╭──
 10% ┤
  0% └─────────────────────────────────────────────
     0%   10%   20%   30%   40%   50%   60%   70%
                  % entidades (ordenadas)
```

**Interpretación**: el reparto es **3x más extremo que un Pareto clásico**. Un puñado de entidades concentra la mayor parte del gasto público.

---

## 👥 3. Brecha de Género del 40.5%

Los contratos firmados por **representantes legales hombres** valen, en promedio, **40.5% más** que los firmados por mujeres.

```
Hombre  ████████████████████████████████ $141,000,000 COP
Mujer   ███████████████████             $84,000,000 COP
                                         ↑
                                     Δ −40.5%
```

**Caveat**: el dato refleja el **valor promedio**, no el conteo. Mujeres firman menos contratos Y de menor valor — doble brecha.

> **📊 Recomendación**: política afirmativa para licitaciones donde la representante sea mujer, especialmente en obra pública (donde la brecha se profundiza).

---

## 🕳️ 4. Cinco Columnas 100% Nulas (Datos Fantasma)

5 columnas del esquema están **completamente vacías** en el snapshot 2025:

| Columna | % nulos |
|---------|---------|
| `fondos_origen_1` | 100% |
| `fondos_origen_2` | 100% |
| `fondos_origen_3` | 100% |
| `fondos_destino_alt` | 100% |
| `partida_presupuestal_aux` | 100% |

**Implicación**: Pérdida de **trazabilidad presupuestal**. La estructura está, pero nadie la llena.

---

## 🧬 5. Anomalías de Tipo — 7 Categorías

```
┌─────────────────────┬────────────────────────────────────────┐
│ Categoría           │ Ejemplo                                │
├─────────────────────┼────────────────────────────────────────┤
│ datetime            │ 45123 (Excel serial) vs ISO-8601       │
│ monetario           │ "$1,200.50.00" vs 1200.50              │
│ NIT                 │ 8/9/10 dígitos sin DV                  │
│ código              │ UNSPSC truncado a 6 vs 8 dígitos       │
│ booleano            │ "Si"/"SI"/"sí"/"1"/"true"/"yes"        │
│ duración            │ "180 días" vs "6 meses" sin normalizar │
│ identificadores     │ UUID vs int vs string mezclados        │
└─────────────────────┴────────────────────────────────────────┘
```

**Costo estimado**: ~12-18% de los registros requieren **limpieza manual** antes de cualquier análisis confiable.

---

## 🔍 6. Tres Anomalías Validadas Manualmente

| # | Caso | Valor | Veredicto |
|---|------|-------|-----------|
| 1 | MinMinas / GECELCA | $1.8 B | ✅ **Verídico** — interconexión eléctrica regional |
| 2 | MinCIT / Zona Franca | $890 M | ❌ **Falso positivo** — datos inconsistentes en SECOP |
| 3 | RNEC elecciones | $2.1 B | ✅ **Verídico** — logística electoral nacional |

**Tasa de verdadero positivo del detector de anomalías: 2/3 = 66.7%** — aceptable para alerta, no para acción automática.

---

## 🌱 7. Sólo 2.13% de Contratos con Cláusula Ambiental

De **1,003,902 contratos**, sólo **21,347** tienen obligaciones ambientales explícitas.

```
Sin cláusula ambiental ████████████████████████████████████████ 97.87%
Con cláusula           █ 2.13%
```

**Implicación**: La integración **ESG** en la contratación pública es **marginal**. Hay margen amplio para política pública.

---

## 📅 8. Estacionalidad Fiscal Extrema

**Diciembre 2024** registró **2.1M archivos subidos** vs media mensual de ~1.4M (BD2). Patrón clásico de **gasto de cierre fiscal**.

```
ene ████████ 1.3M
feb ████████ 1.3M
mar █████████ 1.4M
abr ████████ 1.3M
may █████████ 1.4M
jun ██████████ 1.5M
jul █████████ 1.4M
ago █████████ 1.4M
sep ██████████ 1.5M
oct ██████████ 1.5M
nov ███████████ 1.7M
dic █████████████ 2.1M  ← spike fiscal
```

---

## 🎯 9. Tipos de Contrato — Concentración Crítica

**85.76% son "Prestación de servicios"** (860,913 contratos). El resto se reparte en migajas:

```
Prestación servicios ████████████████████████████████ 85.76%
Compraventa          ██ 5.10%
Suministro           █ 3.80%
Obra                 █ 2.79%
Consultoría          ▌ 1.45%
Otros                ▌ 1.10%
```

**Riesgo**: contratos de prestación de servicios suelen ser **vehículos para vinculación temporal** que evita prestaciones laborales.

---

## 💰 10. Anticipos Casi Inexistentes (0.08%)

Sólo **803 contratos** (de 1M+) reportan anticipos. Esto puede deberse a:
- Disciplina fiscal real,
- O **falta de reporte** (campo opcional mal llenado).

**Recomendación**: cross-check con tesorería para distinguir.

---

## 📌 TL;DR — 10 Hallazgos Críticos

1. 🚨 **75.7%** de contratos son de **contratación directa**.
2. 📈 **Pareto 7/80** — hiperconcentración estructural.
3. 👥 **Brecha de género 40.5%** en valor promedio.
4. 🕳️ **5 columnas** 100% nulas — pérdida de trazabilidad.
5. 🧬 **7 categorías** de anomalías de tipo.
6. 🔍 **66.7%** de tasa de verdadero positivo en detector.
7. 🌱 Sólo **2.13%** con cláusula ambiental.
8. 📅 **Spike fiscal** en diciembre (+50% vs media).
9. 🎯 **85.76%** son "prestación de servicios".
10. 💰 Anticipos: **0.08%** — sospechosamente bajo.

---

*Documento generado para Hackathon COL 5.0 — Equipo Tikno.*
