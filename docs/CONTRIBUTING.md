# 🤝 CONTRIBUTING.md — Guía de Contribución

> Hackathon COL 5.0 — Equipo Tikno. Bienvenidas/os a contribuir 💚

---

## 📑 Índice

- [Setup local](#setup-local)
- [Estilo de código](#estilo-de-código)
- [Convenciones de commits](#convenciones-de-commits)
- [Testing](#testing)
- [PR template](#pr-template)
- [Code of Conduct](#code-of-conduct)

---

## 💻 Setup local

### Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python | 3.11+ |
| Node | 20+ |
| Docker | 24+ |
| DuckDB | 0.10+ |
| `make` | cualquiera reciente |

### Pasos

```bash
# 1. Clonar
git clone https://github.com/nicolas-tikno/hackaton-col5.git
cd hackaton-col5

# 2. Backend (FastAPI)
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Frontend (React + Vite)
cd ../frontend
npm install

# 4. Datos
make download-dataset   # descarga snapshot 2025 (1.7 GB)
make build-duckdb       # construye .duckdb local

# 5. Levantar todo
make up                 # docker-compose con backend + frontend + db
```

### Verificar que está vivo

```bash
curl http://localhost:8000/health
# → {"status":"ok"}

open http://localhost:5173    # dashboard local
open http://localhost:8000/docs  # swagger
```

---

## 🎨 Estilo de código

### Python (backend)

- **Formatter**: `ruff format` (configurado en `pyproject.toml`).
- **Linter**: `ruff check --fix`.
- **Type hints**: obligatorios en funciones públicas. `mypy --strict`.
- **Docstrings**: estilo Google.
- **Imports**: ordenados con `ruff` (isort-compatible).

```python
def get_pareto_ratio(values: list[float], target_pct: float = 0.8) -> float:
    """Calcula el % de entidades que acumulan target_pct del valor total.

    Args:
        values: lista de valores ordenados descendente.
        target_pct: umbral acumulado (default 0.8).

    Returns:
        Porcentaje de entidades que cubren target_pct.
    """
    ...
```

### TypeScript (frontend)

- **Formatter**: `prettier`.
- **Linter**: `eslint` con `@typescript-eslint`.
- **Estilo**: funcional, hooks, no class components.
- **Imports**: absolute imports vía `@/` (ver `tsconfig.json`).
- **Componentes**: PascalCase + un componente por archivo.

### SQL / DuckDB

- Keywords en MAYÚSCULAS (`SELECT`, `FROM`, `WHERE`).
- Identificadores en snake_case.
- CTEs preferidos sobre subqueries anidados.
- Comentarios `-- explicar el porqué, no el qué`.

---

## ✏️ Convenciones de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
<tipo>(<scope>): <descripción corta>

[cuerpo opcional explicando el porqué]

[footer: closes #123]
```

### Tipos permitidos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Bugfix |
| `docs` | Documentación |
| `style` | Formato (sin cambio de lógica) |
| `refactor` | Reescritura sin cambio funcional |
| `perf` | Mejora de performance |
| `test` | Añadir/corregir tests |
| `chore` | Mantenimiento, deps, configs |
| `ci` | Pipeline CI/CD |

### Ejemplos buenos

```
feat(api): add /api/v1/pareto/entidades endpoint
fix(dashboard): corregir labels en mapa de departamentos
docs(rounds): actualizar tabla Q18 con cifra Pareto 7/80
perf(duckdb): índice HNSW en valor_del_contrato (-40% latencia)
```

### Ejemplos malos ❌

```
update files
fix bug
WIP
asdasd
```

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest -v
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

- **Cobertura mínima**: 80% líneas, 70% branches.
- **Naming**: `test_<funcion>_<caso>.py`.
- **Mocks**: `pytest-mock` + fixtures.
- **Datos de prueba**: `tests/fixtures/*.csv` (subset 1k filas).

### Frontend

```bash
cd frontend
npm run test          # Vitest
npm run test:e2e      # Playwright
```

- Smoke tests obligatorios para nuevos componentes.
- E2E sólo para flujos críticos (drill-down, filtros).

### CI

GitHub Actions corre en cada PR:

- ✅ `ruff check`
- ✅ `mypy --strict`
- ✅ `pytest --cov`
- ✅ `npm run lint`
- ✅ `npm run test`
- ✅ Build Docker images

---

## 📋 PR template

Al abrir un PR, este template se autocompleta:

```markdown
## 🎯 Qué cambia este PR

[Describí en 1-2 frases]

## 🤔 Por qué

[Contexto / issue relacionado]

## 🧪 Cómo lo probaste

- [ ] Tests unitarios pasan
- [ ] Probado en local con datos reales
- [ ] Probado en `panel.tikno.pro` staging

## 📸 Screenshots (si aplica UI)

[paste]

## ✅ Checklist

- [ ] Code follows style guidelines
- [ ] Tests added / updated
- [ ] Docs updated (`docs/`)
- [ ] No secrets / API keys committed
- [ ] Closes #issue

## 🔗 Links

- Issue: #
- Discussion: #
```

### Reglas para PRs

1. **Pequeños y enfocados**. Máx 400 líneas modificadas.
2. **Branch naming**: `feat/<scope>-<short>`, `fix/<scope>-<short>`.
3. **2 reviewers** mínimo para `main`.
4. **Squash merge** preferido (mantiene historial limpio).

---

## 🚦 Code of Conduct

Adoptamos [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

Resumen:

- ✅ **Sé respetuosa/o** y profesional.
- ✅ **Constructivo** > destructivo.
- ✅ **Inclusión** sobre exclusión.
- ❌ **No tolerancia** al acoso, discriminación o ataques personales.

Reportes a: agenciacreativalab@gmail.com (confidencial).

---

## 🎁 Reconocimientos

Las contribuciones se listan en `AUTHORS.md` y aparecen en el footer del dashboard.

---

*Gracias por contribuir al Hackathon COL 5.0 — Equipo Tikno.* 💚
