# 📡 API.md — API Reference Hackathon COL 5.0

> Referencia completa de la API REST del proyecto. Base URL pública:
>
> ```
> https://api-ronda2.tikno.pro
> ```
>
> Spec OpenAPI interactiva: [`/docs`](https://api-ronda2.tikno.pro/docs)

---

## 📑 Índice

- [Convenciones](#convenciones)
- [Stats](#-stats)
- [Pyme](#-pyme)
- [Departamentos](#-departamentos)
- [Modalidades](#-modalidades)
- [Entidades](#-entidades)
- [Tipos](#-tipos)
- [Anomalías](#-anomalías)
- [Pareto](#-pareto)
- [Género](#-género)
- [Ambiental](#-ambiental)

---

## Convenciones

- Todas las respuestas son **JSON UTF-8**.
- Errores siguen [RFC 7807 Problem Details](https://datatracker.ietf.org/doc/html/rfc7807).
- Los montos están en **COP (pesos colombianos)** sin redondeo.
- Paginación con `?page=1&page_size=50` (max 500).

```python
# Cliente Python httpx común
import httpx
BASE = "https://api-ronda2.tikno.pro/api/v1"
client = httpx.Client(base_url=BASE, timeout=30)
```

---

## 📊 Stats

### `GET /api/v1/stats/overview`

**Descripción**: KPIs globales del dataset (total registros, año cubierto, %Pymes, etc.)

**Params**: ninguno.

**Response schema**:

```json
{
  "total_registros": "int",
  "anio_dominante": "int",
  "registros_anio": "int",
  "pct_pymes": "float",
  "total_entidades": "int",
  "valor_total_cop": "float"
}
```

**Ejemplo response**:
```json
{
  "total_registros": 1003902,
  "anio_dominante": 2025,
  "registros_anio": 999490,
  "pct_pymes": 13.20,
  "total_entidades": 4218,
  "valor_total_cop": 198400000000000
}
```

**Ejemplos**:

```bash
# curl
curl -s https://api-ronda2.tikno.pro/api/v1/stats/overview | jq
```

```python
# Python httpx
r = client.get("/stats/overview")
print(r.json())
```

```javascript
// Node fetch
const r = await fetch("https://api-ronda2.tikno.pro/api/v1/stats/overview");
console.log(await r.json());
```

---

### `GET /api/v1/stats/timeseries`

Distribución temporal por mes del año dominante.

**Params**: `?granularity=month|week|day` (default `month`).

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/stats/timeseries?granularity=month'
```

```json
[
  {"period": "2025-01", "count": 88_010, "valor_cop": 17_400_000_000_000},
  {"period": "2025-02", "count": 92_410, "valor_cop": 18_900_000_000_000}
]
```

---

## 🏢 Pyme

### `GET /api/v1/pyme/distribution`

**Descripción**: Distribución Pyme vs no-Pyme.

**Response schema**:
```json
{
  "pyme_count": "int",
  "no_pyme_count": "int",
  "pct_pyme": "float"
}
```

**Ejemplo response**:
```json
{ "pyme_count": 132479, "no_pyme_count": 871423, "pct_pyme": 13.20 }
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/pyme/distribution
```

```python
client.get("/pyme/distribution").json()
```

```javascript
fetch(`${BASE}/pyme/distribution`).then(r => r.json());
```

---

### `GET /api/v1/pyme/by-departamento`

Top departamentos con mayor adopción Pyme.

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/pyme/by-departamento?limit=10'
```

---

## 🗺️ Departamentos

### `GET /api/v1/departamentos/top`

**Descripción**: Top departamentos por volumen.

**Params**: `?limit=10&order_by=count|valor_total`.

**Response**:
```json
[
  {"departamento": "Bogotá D.C.", "count": 311_209, "valor_total": 60_400_000_000_000},
  {"departamento": "Valle del Cauca", "count": 102_811, "valor_total": 18_900_000_000_000}
]
```

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/departamentos/top?limit=10'
```

```python
client.get("/departamentos/top", params={"limit": 10}).json()
```

```javascript
fetch(`${BASE}/departamentos/top?limit=10`).then(r => r.json());
```

---

### `GET /api/v1/departamentos/{nombre}`

Detalle de un departamento específico.

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/departamentos/Antioquia
```

---

## 🧾 Modalidades

### `GET /api/v1/modalidades/distribution`

**Descripción**: Distribución por modalidad de contratación.

**Response**:
```json
[
  {"modalidad": "Contratación directa", "count": 759993, "pct": 75.70},
  {"modalidad": "Mínima cuantía", "count": 115420, "pct": 11.50}
]
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/modalidades/distribution
```

```python
client.get("/modalidades/distribution").json()
```

---

## 🏛️ Entidades

### `GET /api/v1/entidades/top`

**Descripción**: Top entidades por monto contratado.

**Params**: `?limit=3&order_by=valor|count`.

**Response**:
```json
[
  {"entidad": "Distrito CTI Medellín", "valor_total": 7190000000000, "count": 12044},
  {"entidad": "Ministerio de Minas y Energía", "valor_total": 5120000000000, "count": 8401},
  {"entidad": "Gobernación de Antioquia", "valor_total": 3840000000000, "count": 9821}
]
```

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/entidades/top?limit=3'
```

```python
client.get("/entidades/top", params={"limit": 3}).json()
```

```javascript
const r = await fetch(`${BASE}/entidades/top?limit=3`);
```

---

## 📂 Tipos

### `GET /api/v1/tipos/distribution`

**Descripción**: Distribución por tipo de contrato.

**Response**:
```json
[
  {"tipo": "Prestación de servicios", "count": 860913, "pct": 85.76},
  {"tipo": "Compraventa", "count": 51200, "pct": 5.10}
]
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/tipos/distribution
```

---

## ⚠️ Anomalías

### `GET /api/v1/anomalias/listado`

**Descripción**: Lista de anomalías detectadas + clasificación.

**Params**: `?categoria=datetime|monetario|nit|codigo|booleano|duracion|identificadores&limit=20`.

**Response schema**:
```json
{
  "categorias": ["datetime", "monetario", "nit", "codigo", "booleano", "duracion", "identificadores"],
  "items": [
    {"id": "uuid", "categoria": "monetario", "campo": "valor_del_contrato",
     "valor_original": "$1,200.50.00", "veredicto": "inconsistente"}
  ]
}
```

```bash
curl -s 'https://api-ronda2.tikno.pro/api/v1/anomalias/listado?categoria=monetario&limit=5'
```

```python
client.get("/anomalias/listado", params={"categoria": "monetario", "limit": 5}).json()
```

---

### `GET /api/v1/anomalias/validadas`

Top 3 valores anómalos validados manualmente:

```json
[
  {"caso": "MinMinas/GECELCA", "valor": 1800000000, "veredicto": "veridico"},
  {"caso": "MinCIT/Zona Franca", "valor": 890000000, "veredicto": "falso_positivo"},
  {"caso": "RNEC elecciones", "valor": 2100000000, "veredicto": "veridico"}
]
```

---

## 📈 Pareto

### `GET /api/v1/pareto/entidades`

**Descripción**: Análisis Pareto del valor por entidad.

**Response**:
```json
{
  "pct_entidades": 7.23,
  "pct_valor": 80.0,
  "interpretacion": "Hiperconcentración: 7.23% de entidades acumulan 80% del valor total."
}
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/pareto/entidades
```

```python
client.get("/pareto/entidades").json()
```

```javascript
fetch(`${BASE}/pareto/entidades`).then(r => r.json());
```

---

## 👥 Género

### `GET /api/v1/genero/brecha`

**Descripción**: Brecha de género en valor promedio.

**Response**:
```json
{
  "hombre_promedio": 141000000,
  "mujer_promedio": 84000000,
  "brecha_pct": 40.5,
  "moneda": "COP"
}
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/genero/brecha
```

```python
client.get("/genero/brecha").json()
```

---

### `GET /api/v1/genero/by-modalidad`

Brecha desagregada por modalidad de contratación.

---

## 🌱 Ambiental

### `GET /api/v1/ambiental/contratos`

**Descripción**: Contratos con cláusulas u obligaciones ambientales.

**Response**:
```json
{
  "total_contratos_ambientales": 21347,
  "pct_total": 2.13,
  "top_entidades": [
    {"entidad": "ANLA", "count": 4012},
    {"entidad": "MinAmbiente", "count": 3120}
  ]
}
```

```bash
curl -s https://api-ronda2.tikno.pro/api/v1/ambiental/contratos
```

```python
client.get("/ambiental/contratos").json()
```

```javascript
fetch(`${BASE}/ambiental/contratos`).then(r => r.json());
```

---

## ⚙️ Errores comunes

| HTTP | Significado |
|------|-------------|
| `400` | Parámetros inválidos |
| `404` | Recurso no encontrado (departamento/entidad) |
| `429` | Rate limit (60 req/min por IP) |
| `500` | Error interno (reportar al equipo) |

---

*Generado para Hackathon COL 5.0 — Equipo Tikno.*
