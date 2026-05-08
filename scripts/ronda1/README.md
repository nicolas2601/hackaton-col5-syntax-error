# Ronda 1 — Hackathon Nacional COL 5.0

Equipo: **Syntax Error**

## Estructura

- `bd1_respuestas.py` — Script Python que regenera todas las respuestas BD1 (preguntas 3-14) consultando directamente la API SODA oficial de datos.gov.co. Auditable, reproducible, no necesita la replica local.
- `respuestas_bd1.json` — Output del script (generado).

## Uso

```bash
pip install requests
python3 bd1_respuestas.py
# con app token (recomendado para evitar rate limit):
python3 bd1_respuestas.py --token TU_APP_TOKEN
```

## Fuentes de verdad

| Fuente | Cuándo usar |
|---|---|
| **Socrata oficial** (`https://www.datos.gov.co/resource/jbjy-vk9h.json`) | Respuestas que el jurado verifica → max/min/count exactos |
| **api.tikno.pro** (réplica self-hosted, 5.6M filas) | Análisis pesados (joins, agregaciones, full-text) sin rate limit |

## Notas sobre las respuestas

- **Q7 texto = 57 (Socrata) o 58 (si rúbrica considera URL como texto)**. El script reporta ambos.
- **Q8** — hay **5 columnas con 100% null** en el dataset oficial (todas de fondos: Recursos de Crédito, PGN, SGP, Regalías, Recursos Propios). Empate técnico, el script ordena alfabéticamente.
- **Q11** — `dias_adicionados` está como TEXT en datos.gov.co. Cast `::number` da max=730,533. (Nuestra DB self-hosted tenía bug que limitaba a 994 — fix pendiente).
- **Q13** — interpretación natural "7º valor más alto" = 7º distinto descendente = `9,610,000,000,000`. Si quieren 7º absoluto (offset 6 con duplicados) = `9,645,115,773,936`.
