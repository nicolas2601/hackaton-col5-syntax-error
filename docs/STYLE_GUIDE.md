# Style Guide — Lightdash Reference

> Codebase blueprint on frosted glass — light theme con Electric Violet accent

## Tokens

### Colors

```css
--color-midnight-ink: #1a1b25;       /* Primary text, headings */
--color-charcoal-slate: #272835;     /* Hero text, secondary */
--color-deep-indigo: #36394a;        /* Body text, input bg */
--color-steel-gray: #666d80;         /* Secondary body */
--color-cloud-gray: #818898;         /* Tertiary text */
--color-stone-wash: #a4abb8;         /* Helper text */
--color-off-white: #f8fafb;          /* Subtle bg cards */
--color-canvas-white: #ffffff;       /* Page bg */
--color-lava-cloud: #eceff3;         /* Alt section bg */
--color-ghost-fill: #f6f8fa;         /* Hover, active */
--color-electric-violet: #5e4cff;    /* PRIMARY ACTION ⚡ */
--color-lavender-mist: #dfdbff;      /* Tertiary button bg */
--color-pixel-purple: #c8ccf3;       /* Decorative pattern */
```

### Typography

| Role | Font | Size | Line Height | Letter Spacing |
|---|---|---|---|---|
| **display** | Britti Sans Semibold | 76px | 0.9 | -0.025em |
| **heading-lg** | Britti Sans Semibold | 48px | 1.0 | -0.025em |
| **heading** | Britti Sans Medium | 32px | 1.14 | -0.020em |
| **heading-sm** | Britti Sans Medium | 24px | 1.25 | -0.010em |
| **subheading** | Britti Sans Medium | 18px | 1.30 | -0.010em |
| **body** | Inter | 14px | 1.43 | -0.010em |
| **mono** | IBM Plex Mono | 12-14px | 1.50 | -0.020em |

**Substitutos** (cuando Britti Sans no esté disponible):
- `Britti Sans Semibold` → `Montserrat 600`
- `Britti Sans Medium` → `Montserrat 500`
- `Inter` → `Inter` (Google Fonts)
- `IBM Plex Mono` → `IBM Plex Mono` (Google Fonts)

### Spacing & Shape

```css
--spacing-unit: 4px;
/* Escala: 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 72, 80, 180 */

--radius-tags: 999px;        /* Pills */
--radius-cards: 12px;        /* Cards estándar */
--radius-inputs: 0px;        /* Inputs sharp */
--radius-buttons: 8px;       /* Botones */
--radius-elevated: 20px;     /* Cards elevadas */

--card-padding: 24-32px;
--section-gap: 40-64px;
--element-gap: 8px;
```

### Shadows

```css
--shadow-subtle-2: rgba(39, 40, 53, 0.1) 0px 0px 0px 1px;
--shadow-subtle-4: rgba(39, 40, 53, 0.05) 0px 0px 0px 1px,
                   rgba(39, 40, 53, 0.01) 0px 50px 20px 0px,
                   rgba(39, 40, 53, 0.02) 0px 30px 18px 0px,
                   rgba(39, 40, 53, 0.04) 0px 13px 13px 0px,
                   rgba(39, 40, 53, 0.05) 0px 3px 7px 0px;
--shadow-lg:       rgba(0, 0, 0, 0.01) 0px 54px 21px 0px,
                   rgba(0, 0, 0, 0.05) 0px 30px 18px 0px,
                   rgba(0, 0, 0, 0.09) 0px 13px 13px 0px,
                   rgba(0, 0, 0, 0.10) 0px 3px 7px 0px;
```

## Componentes

### Primary Action Button
- Background: `--color-electric-violet`
- Text: `#ffffff`
- Border-radius: `8px`
- Padding: `12px 20px`
- Font: Inter 500 14px

### Secondary Ghost Button
- Background: transparent
- Border: 1px `--color-midnight-ink`
- Text: `--color-midnight-ink`
- Border-radius: `8px`
- Padding: `12px 20px`

### Elevated Feature Card
- Background: `--color-canvas-white`
- Border-radius: `20px`
- Shadow: `--shadow-subtle-4`
- Padding: `24px 32px 20px`

### Simple Information Card
- Background: `--color-canvas-white`
- Border-radius: `12px`
- Shadow: `--shadow-subtle-2`
- Padding: `28px 22px`

### Interactive Chip / Pill
- Background: `rgba(5, 5, 19, 0.04)`
- Border-radius: `999px`
- Padding: `12px`

## Reglas de uso (Do's & Don'ts)

### ✅ Do
- Usar Electric Violet **EXCLUSIVAMENTE** para CTA primarios y highlights críticos
- Aplicar Britti Sans Semibold para todos los headings con la letter-spacing especificada
- Mantener jerarquía visual limitando colores saturados
- Canvas White (`#ffffff`) como background dominante
- 8px radius en botones, 12px en cards
- IBM Plex Mono para code blocks y data técnica

### ❌ Don't
- No introducir hues saturados fuera de Electric Violet y sus tints
- No drop shadows en UI funcional excepto Elevated Feature Card
- No variar letter-spacing fuera de las specs
- No usar fuentes del sistema donde se especifica Britti Sans/Inter
- No Electric Violet para body text o bloques grandes
- No backgrounds muy oscuros — light mode predomina
- No 20px radius en elementos que no sean Elevated Card o pills

## Imagery

- Patrones abstractos pixelados (Pixel Purple `#c8ccf3`)
- Screenshots de UI sobre fondos oscuros con elementos contained
- Iconos outline, stroke fino, minimalismo preciso
- Densidad balanceada — texto lidera, imagery soporta

## Layout

- Max-width contenido, centrado
- Hero centered con headline display sobre bg con violet accents
- Section rhythm: spacing vertical consistente + alternar Canvas White / Lava Cloud
- Two-column layouts: text-left/image-right
- Sticky top nav

## Quick reference para agentes

```css
text: #272835
background: #ffffff
border: #b4acff
accent: #c8ccf3
primary action: #5e4cff
```

## Brands similares

Vercel · Linear · Supabase · Figma
