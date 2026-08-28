# 🔐 SECURITY.md — Política de Seguridad y Privacidad

> Hackathon COL 5.0 — Equipo Tikno.
> Cumplimiento normativo colombiano + reporte responsable de vulnerabilidades.

---

## 📑 Índice

- [Privacidad de datos](#-privacidad-de-datos)
- [Cumplimiento Ley 1712 (Transparencia)](#-cumplimiento-ley-1712-transparencia)
- [Cumplimiento Ley 1581 (Habeas Data)](#-cumplimiento-ley-1581-habeas-data)
- [Reporte de vulnerabilidades](#-reporte-de-vulnerabilidades)
- [Buenas prácticas operativas](#-buenas-prácticas-operativas)

---

## 🔏 Privacidad de datos

### Origen y carácter público

Todos los datos analizados provienen del portal **Datos Abiertos del Gobierno de Colombia** (`datos.gov.co`) y específicamente del sistema **SECOP II** (Sistema Electrónico de Contratación Pública). Estos datos son:

- ✅ **Públicos por mandato legal** (Ley 1712 de 2014).
- ✅ **Anonimizados** parcialmente — no contienen documentos de identidad de personas naturales contratistas más allá del NIT (que es público).
- ✅ **Reutilizables** bajo licencia abierta (`CC BY 4.0` o equivalente declarada por la entidad).

### Lo que NO almacenamos

❌ Direcciones IP de visitantes del dashboard (más allá de los logs efímeros del proxy).
❌ Cookies de tracking de terceros (no Google Analytics, no Facebook Pixel).
❌ Credenciales o cualquier tipo de PII sensible.

### Datos en tránsito

- 🔒 **TLS 1.3** obligatorio en `panel.tikno.pro` y `api-ronda2.tikno.pro`.
- 🔒 HSTS con `max-age=31536000; includeSubDomains; preload`.
- 🔒 Certificados Let's Encrypt con renovación automática.

### Datos en reposo

- 🗄️ Snapshot CSV almacenado en infraestructura tikno (servidor `ssh.tikno.pro`).
- 🗄️ DuckDB local **read-only** para los workers de la API.
- 🗄️ Backups encriptados con `age` (X25519) en almacenamiento offsite semanal.

---

## 📜 Cumplimiento Ley 1712 (Transparencia)

> **Ley 1712 de 2014** — Ley de Transparencia y del Derecho de Acceso a la Información Pública Nacional.

### Cómo este proyecto la honra

| Principio Ley 1712 | Implementación |
|--------------------|----------------|
| **Máxima publicidad** | Toda la API es pública, sin auth, sin paywall |
| **Buena fe** | Datos publicados sin filtrado editorial |
| **Calidad de la información** | Validaciones cruzadas (Socrata + tikno + pandas) |
| **Divulgación proactiva** | Dashboard accesible 24/7 |
| **Facilitación** | API REST + descarga CSV + Swagger |
| **No discriminación** | Sin geofencing, sin login |
| **Gratuidad** | Acceso 100% gratuito |
| **Idioma oficial** | Español |

### Trazabilidad

- Cada KPI muestra **fecha del snapshot** de origen.
- Cada anomalía detectada incluye **registro original** para auditoría.
- Histórico de cambios en `docs/CHANGELOG.md`.

---

## 🛡️ Cumplimiento Ley 1581 (Habeas Data)

> **Ley 1581 de 2012** + **Decreto 1377 de 2013** — Régimen General de Protección de Datos Personales.

### Datos personales en el corpus

El SECOP II incluye **algunos datos personales tratados con fines de transparencia pública**:

- **Nombre del representante legal** del contratista.
- **Género del representante legal**.
- **NIT/Cédula** del contratista (cuando es persona natural).

### Base legal del tratamiento

Art. 10 lit. b) Ley 1581: **"el tratamiento sea necesario para el ejercicio de funciones públicas"**, en concordancia con el principio constitucional de transparencia (Art. 209 CP) y la Ley 1712.

### Derechos del titular

Cualquier persona cuyo nombre aparezca en el corpus puede ejercer derechos ARCO:

- **A**cceso
- **R**ectificación
- **C**ancelación
- **O**posición

#### Cómo ejercerlos

1. Email a: **nm5571762@gmail.com** con asunto `[HABEAS DATA] <su solicitud>`.
2. Plazo de respuesta: **10 días hábiles** (max. 15 según Decreto 1377).
3. Adjuntar documento de identidad y descripción específica del registro.

> **Nota**: como los datos son réplica de la fuente oficial (`datos.gov.co`), redirigiremos también la solicitud a Colombia Compra Eficiente cuando aplique.

### No tomamos decisiones automatizadas

El sistema **no perfila individuos** ni produce decisiones automatizadas con efectos legales. Es un sistema de **análisis agregado** de contratación pública.

---

## 🚨 Reporte de vulnerabilidades

### Qué reportar

- 🔴 **Críticas**: RCE, SQLi, XSS persistente, exposición de credenciales, IDOR.
- 🟠 **Altas**: SSRF, LFI, exposición de PII, bypass de auth.
- 🟡 **Medias**: CSRF, clickjacking, fugas de info en headers, dependencias vulnerables.
- 🟢 **Bajas / informativas**: misconfig sin impacto inmediato.

### Cómo reportar

**Canal seguro**:

- 📧 Email: `nm5571762@gmail.com`
- 🔑 Asunto: `[SECURITY] <título corto>`
- 🕒 Respuesta inicial: **48h** (días hábiles).

### Qué incluir

```markdown
## Resumen
[1 frase]

## Severidad estimada
[Crítica / Alta / Media / Baja]

## Pasos para reproducir
1. ...
2. ...

## Impacto
[Qué puede hacer un atacante]

## PoC
[código / URL / screenshots]

## Sugerencia de fix (opcional)
[...]

## Contacto
[tu nombre, handle o anónimo]
```

### Disclosure

- 🤝 **Coordinated Disclosure**: 90 días antes de hacer público.
- 🏆 **Hall of Fame**: con tu permiso, te listamos en `SECURITY-HOF.md`.
- 💸 **Bounty**: este es un proyecto de hackathon sin presupuesto formal de bounty, pero ofrecemos **kudos públicos** y reconocimiento.

### Lo que NO hacer

❌ No tests destructivos en producción (`DROP`, `rm -rf`, defacement).
❌ No DoS/DDoS.
❌ No ingeniería social al equipo.
❌ No acceder a datos de terceros más allá de demostrar la vulnerabilidad.

---

## 🛡️ Buenas prácticas operativas

### Para revisores y usuarios

- ✅ Verificar el certificado TLS al acceder al dashboard.
- ✅ Nunca enviar credenciales propias por curiosidad — la API es pública sin auth.
- ✅ Reportar comportamiento sospechoso al email indicado.

### Para contribuidores

- 🔐 No hardcodear API keys ni secrets — usar `.env` (que está gitignored).
- 🔐 Pre-commit hooks con `gitleaks` o `trufflehog` recomendados.
- 🔐 Rotar tokens de despliegue tras cada release.
- 🔐 Dependabot habilitado en el repo público.

### Stack de seguridad

| Capa | Tecnología |
|------|------------|
| TLS | Let's Encrypt + Caddy |
| WAF | Cloudflare (rate limit + bot mitigation) |
| Headers | `Content-Security-Policy`, `X-Frame-Options: DENY` |
| Secrets | `age` + sops + GH Actions secrets |
| Logs | Cloudflare R2 (60 días retención) |
| Audit | Trivy en CI para imágenes Docker |

---

## 📚 Referencias normativas

- [Ley 1712 de 2014](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=56882) — Transparencia.
- [Ley 1581 de 2012](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981) — Habeas Data.
- [Decreto 1377 de 2013](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646) — Reglamentario Ley 1581.
- [SIC — Superintendencia de Industria y Comercio](https://www.sic.gov.co/) — Autoridad de control.

---

## 📞 Contactos

| Rol | Contacto |
|-----|----------|
| Security lead | nm5571762@gmail.com |
| Habeas Data | nm5571762@gmail.com (asunto `[HABEAS DATA]`) |
| Vulnerabilidades | nm5571762@gmail.com (asunto `[SECURITY]`) |

---

*Documento mantenido para Hackathon COL 5.0 — Equipo Tikno.*
*Última revisión: 2025-05-08.*
