# 🚀 USAGE.md — Guía de Uso Hackathon COL 5.0

> Cómo usar el dashboard interactivo y la API REST para revisores, periodistas, investigadores y desarrolladores.

---

## 🎯 Quickstart (3 pasos)

1. **Dashboard**: abrir [`https://panel.tikno.pro`](https://panel.tikno.pro).
2. **API**: explorar [`https://api-ronda2.tikno.pro/docs`](https://api-ronda2.tikno.pro/docs) (Swagger UI).
3. **Datos crudos**: descargar el snapshot CSV en [`https://api-ronda2.tikno.pro/dataset/snapshot.csv.gz`](https://api-ronda2.tikno.pro/dataset/snapshot.csv.gz) (1.7 GB).

---

## 🖥️ 1. Dashboard `panel.tikno.pro`

### Acceso

- **URL**: https://panel.tikno.pro
- **Login**: no requiere autenticación (read-only).

### Secciones

| Sección | Descripción |
|---------|-------------|
| 🏠 **Overview** | KPIs globales: total registros, %Pymes, top entidades |
| 🗺️ **Mapa Colombia** | Coropleta por departamento (volumen y valor) |
| 🧾 **Modalidades** | Distribución de modalidades de contratación |
| 🏛️ **Entidades** | Ranking interactivo + drill-down |
| 👥 **Género** | Brecha + filtros por departamento/modalidad |
| ⚠️ **Anomalías** | Listado con clasificación y veredictos |
| 📈 **Pareto** | Curva acumulada interactiva |
| 🌱 **Ambiental** | Contratos ESG |

### Tips de navegación

- **Filtros**: panel lateral izquierdo. Se combinan con AND.
- **Drill-down**: click en cualquier barra/segmento abre detalle.
- **Export**: cada panel tiene botón `⬇️ CSV / PNG`.
- **Compartir**: cada vista tiene URL permanente con filtros encodeados.

### Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `g h` | Ir a Home |
| `g a` | Ir a Anomalías |
| `g p` | Ir a Pareto |
| `f` | Abrir filtros |
| `?` | Ayuda |

---

## 📡 2. API REST `api-ronda2.tikno.pro`

### Documentación interactiva

- **Swagger UI**: https://api-ronda2.tikno.pro/docs
- **ReDoc**: https://api-ronda2.tikno.pro/redoc
- **OpenAPI JSON**: https://api-ronda2.tikno.pro/openapi.json

### Verificar que está viva

```bash
curl -s https://api-ronda2.tikno.pro/health
# → {"status":"ok","uptime_s":123456}
```

### Rate limits

- **60 req/min por IP** (público).
- Usar header `Accept: application/json` siempre.

---

## 🔍 3. Queries Comunes

### A) "¿Cuántos contratos tiene el dataset?"

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/stats/overview | jq .total_registros
# → 1003902
```

### B) "Top 10 departamentos por volumen"

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/departamentos/top?limit=10' | jq
```

### C) "¿Cuál es la brecha de género?"

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/genero/brecha | jq
# → {"hombre_promedio": 141000000, "mujer_promedio": 84000000, "brecha_pct": 40.5}
```

### D) "Listar anomalías monetarias"

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/anomalias/listado?categoria=monetario&limit=10' | jq
```

### E) Análisis Pareto en una línea

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/pareto/entidades | jq
```

---

## 🐍 4. Cliente Python (httpx)

```python
import httpx, pandas as pd

BASE = "https://api-ronda2.tikno.pro/api/v1"
client = httpx.Client(base_url=BASE, timeout=60)

# 1) Overview
overview = client.get("/stats/overview").json()
print(f"Total: {overview['total_registros']:,}")

# 2) Top 10 deptos a DataFrame
deptos = pd.DataFrame(client.get("/departamentos/top", params={"limit": 10}).json())
print(deptos)

# 3) Brecha de género
brecha = client.get("/genero/brecha").json()
print(f"Brecha: {brecha['brecha_pct']}%")
```

---

## 🟢 5. Cliente Node (fetch)

```javascript
const BASE = "https://api-ronda2.tikno.pro/api/v1";

async function main() {
  const overview = await fetch(`${BASE}/stats/overview`).then(r => r.json());
  console.log("Total:", overview.total_registros.toLocaleString());

  const top = await fetch(`${BASE}/entidades/top?limit=3`).then(r => r.json());
  console.table(top);
}

main();
```

---

## 🎨 6. Casos de Uso

### 📰 Periodismo de datos

> "Quiero hacer una nota sobre la concentración del gasto público."

1. Llamar `/api/v1/pareto/entidades` → obtener `7.23% / 80%`.
2. Cruzar con `/api/v1/entidades/top?limit=20`.
3. Exportar gráfico desde el dashboard.

### 🏛️ Vigilancia ciudadana

> "Quiero auditar contratos de mi alcaldía."

1. Filtrar dashboard por `departamento = X`.
2. Ordenar por valor descendente.
3. Revisar anomalías cruzadas: `/api/v1/anomalias/listado`.

### 🎓 Investigación académica

> "Necesito el dataset completo para mi tesis."

1. Descargar snapshot: `/dataset/snapshot.csv.gz` (1.7 GB).
2. Cargar en DuckDB:
   ```sql
   CREATE TABLE c AS SELECT * FROM read_csv_auto('snapshot.csv');
   ```
3. Citar como: *Hackathon COL 5.0 — Equipo Tikno, 2025.*

### 💻 Desarrollo de apps

> "Quiero embeber estadísticas en mi app."

```javascript
// Widget React simple
import { useEffect, useState } from "react";

function PymeKpi() {
  const [pct, setPct] = useState(null);
  useEffect(() => {
    fetch("https://api-ronda2.tikno.pro/api/v1/pyme/distribution")
      .then(r => r.json())
      .then(d => setPct(d.pct_pyme));
  }, []);
  return <div>Pymes: {pct ?? "…"}%</div>;
}
```

---

## 🛠️ 7. Troubleshooting

| Problema | Solución |
|----------|----------|
| `429 Too Many Requests` | Esperar 60s, agregar backoff exponencial |
| Respuesta vacía `[]` | Verificar params (puede ser filtro muy estricto) |
| `CORS error` en navegador | Usar fetch desde server o proxy |
| Dashboard no carga gráficos | Forzar refresh con `?nocache=1` |
| Datos parecen desactualizados | El snapshot se regenera diariamente a las 03:00 COT |

---

## 📞 8. Soporte

- **Issues**: https://github.com/nicolas-tikno/hackaton-col5/issues
- **Email**: nm5571762@gmail.com
- **Twitter**: @tikno_studio

---

*Generado para Hackathon COL 5.0 — Equipo Tikno.*
