# 🌮 Sabor Mexicano — Big Data & Minería de Datos

[![CI](https://github.com/zusldev/bigdata-mineriadatos/actions/workflows/ci.yml/badge.svg)](https://github.com/zusldev/bigdata-mineriadatos/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Proyecto integral de **Big Data y Minería de Datos** que analiza una cadena de **10 sucursales** de comida mexicana en México. Cubre ventas, rentabilidad, inventario, pronóstico de demanda, segmentación de clientes y marketing digital mediante un pipeline end-to-end reproducible.

---

## Tecnologías

| Categoría | Herramientas |
|-----------|-------------|
| Lenguaje | Python 3.12 |
| Datos | Pandas · NumPy · PyArrow · Polars (opcional) |
| Machine Learning | Scikit-learn (KMeans, RFM) · Statsmodels (Holt-Winters) |
| Visualización | Plotly · Kaleido |
| Dashboard | Streamlit |
| Reportes | python-docx |
| Config | PyYAML · schema_map.yml · recipe_map.yml |
| CI/CD | GitHub Actions · ruff · pytest |
| Contenedores | Docker |

---

## Quickstart

```bash
# 1. Clonar
git clone https://github.com/zusldev/bigdata-mineriadatos.git
cd bigdata-mineriadatos

# 2. Entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate    # Linux/Mac

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar pipeline completo
python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id 2026-02-17-a
```

> **Nota:** Antes de correr el pipeline, actualizar `docs/STUDY_LOG.md` con el Run ID. El pipeline valida trazabilidad en modo fail-fast.

---

## Estructura del Proyecto

```
.
├── apps/dashboard/app.py            # Dashboard interactivo (Streamlit)
├── config/
│   ├── settings.yml                 # Configuración general del pipeline
│   ├── schema_map.yml               # Mapeo de columnas español → canónico
│   └── recipe_map.yml               # Categorías y recetas
├── src/
│   ├── pipeline/run_all.py          # Orquestador principal — ejecuta todo
│   ├── data/
│   │   ├── load.py                  # Ingesta JSON/CSV/XLSX (prioridad JSON)
│   │   ├── clean.py                 # Limpieza, tipado, imputación
│   │   └── validate.py              # Validación de calidad post-limpieza
│   ├── features/build_features.py   # Feature engineering (RFM, daypart, etc.)
│   ├── eda/                         # Análisis exploratorio
│   ├── analysis/                    # Rentabilidad · Inventario · Marketing digital
│   ├── models/                      # KMeans (segmentación) · Holt-Winters (pronóstico)
│   ├── reco/                        # Motor de recomendaciones
│   └── report/                      # Generador de gráficas PNG + informe .docx
├── data/
│   ├── raw/                         # Datos crudos (JSON, CSV, XLSX)
│   └── processed/                   # Datos limpios (Parquet/CSV)
├── outputs/
│   ├── charts/                      # 19 visualizaciones (HTML + PNG)
│   ├── tables/                      # 22 tablas analíticas CSV
│   ├── models/                      # Artefactos serializados (.pkl)
│   ├── logs/                        # Resumen de ejecución
│   └── manifests/                   # Registro de artefactos generados
├── reports/                         # Informes finales (.md, .docx)
├── tests/                           # Suite de tests (pytest)
└── docs/                            # Metodología, supuestos, glosario
```

---

## Pipeline

El pipeline ejecuta **4 fases secuenciales** con un solo comando:

```bash
python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id <RUN_ID>
```

| Fase | Módulos | Descripción |
|------|---------|-------------|
| 1 | `load` → `clean` → `validate` → `eda` | Ingesta, limpieza, validación y análisis exploratorio |
| 2 | `profitability` · `inventory` · `digital` | Análisis de rentabilidad, inventario y marketing digital |
| 3 | `forecast` · `segmentation` | Pronóstico Holt-Winters + Segmentación KMeans |
| 4 | `recommendations` · `report` | Recomendaciones accionables + generación de reportes |

---

## Dashboard

```bash
streamlit run apps/dashboard/app.py
```

Dashboard interactivo con pestañas de visualización, filtros por sucursal/periodo, y modo de estudio integrado.

---

## Generación de Informes

```bash
python src/report/generate_charts_informe.py   # 10 gráficas PNG para el informe
python src/report/build_docx.py                 # Genera reports/informe_caso_estudio.docx
```

---

## Comandos Makefile

```bash
make setup      # Instalar dependencias
make lint       # Linting con ruff
make test       # Tests con pytest
make pipeline   # Pipeline completo
make dashboard  # Lanzar Streamlit
make all        # lint + test + pipeline
```

---

## Docker

```bash
docker build -t sabor-mexicano .

# Pipeline
docker run --rm sabor-mexicano

# Dashboard
docker run --rm -p 8501:8501 sabor-mexicano \
  streamlit run apps/dashboard/app.py --server.address=0.0.0.0
```

---

## Reproducibilidad

| Aspecto | Implementación |
|---------|---------------|
| Seed | `--seed 42` (controlado globalmente) |
| Persistencia | Parquet preferente, fallback automático a CSV |
| Artefactos | `outputs/manifests/artifacts_manifest.csv` |
| CI | GitHub Actions: lint + test + pipeline smoke en cada push |
| Polars | Opcional: `POLARS=1 python -m src.pipeline.run_all ...` |

---

## Archivos de Salida

| Carpeta | Contenido |
|---------|-----------|
| `outputs/charts/` | 19 visualizaciones (HTML interactivas + PNG estáticas) |
| `outputs/tables/` | 22 tablas analíticas CSV |
| `outputs/models/` | Modelos serializados (.pkl) |
| `outputs/logs/` | Resumen automático de cada ejecución |
| `reports/` | Informe caso de estudio (.md + .docx), limpieza de datos, resumen ejecutivo |
| `docs/` | Metodología, supuestos, diccionario de datos, glosario, study log |

---

## 📄 Informes del Proyecto

<details>
<summary><strong>🧹 Informe de Limpieza de Datos</strong> — ETL completo sobre 9,710 registros y 102 columnas</summary>

&nbsp;

### Resumen Ejecutivo

Se trabajaron **5 datasets** (9,710 registros, 102 columnas). El ETL se ejecutó en 4 fases: **carga → limpieza → validación → feature engineering**. Principales problemas: columnas monetarias como texto con comas, strings vacíos como nulos ocultos, booleanos en formato `"Sí"/"No"`, y tipos incorrectos.

### Inventario de Datasets

| # | Dataset | Archivo | Filas | Columnas |
|---|---------|---------|-------|----------|
| 1 | Ventas | `ventascsv.json` | 5,000 | 18 |
| 2 | Clientes | `clientes.json` | 1,500 | 17 |
| 3 | Sucursales | `sucursales.json` | 10 | 24 |
| 4 | Inventarios | `inventarios.json` | 2,000 | 23 |
| 5 | Canales Digitales | `canales_digitales.json` | 1,200 | 20 |
| — | **TOTAL** | — | **9,710** | **102** |

### Flujo ETL

```
CARGA (load.py) → LIMPIEZA (clean.py) → VALIDACIÓN (validate.py) → FEATURES (build_features.py)
```

### Detalle por Dataset

**Ventas** — 5,000 filas × 18 columnas

| Problema | Columna | Corrección |
|----------|---------|------------|
| String con comas | `Total_con_Propina` | `_to_numeric()`: elimina `,`/`$` → `pd.to_numeric` |
| Fecha como string | `Fecha` | `pd.to_datetime(errors="coerce")` |
| Hora como string | `Hora` | Trunca a `HH:MM`, extrae `hour` entero |
| Sin franja horaria | — | Crea `daypart`: Mañana/Comida/Tarde/Noche |
| NaN en total | `total_sale` | `fillna(unit_price × quantity)` |
| NaN en costo | `ingredient_cost` | Media por categoría; fallback 35% de `total_sale` |

**Clientes** — 1,500 filas × 17 columnas

| Problema | Columna | Corrección |
|----------|---------|------------|
| 1,077 strings con comas | `Gasto_Total_Estimado` | `_to_numeric()` → float64 |
| Booleano texto | `Miembro_Lealtad`, `Acepta_Promociones` | `_to_boolean()` → True/False |
| Fecha string | `Fecha_Registro`, `Ultima_Visita` | `pd.to_datetime()` |
| NaN derivado | `estimated_total_spend` | `fillna(avg_spend × visits_last_year)` |

**Sucursales** — 10 filas × 24 columnas

| Problema | Columna(s) | Corrección |
|----------|-----------|------------|
| 7 cols monetarias string | `Renta_Mensual`, `Nomina_Mensual`, etc. | `_to_numeric()` |
| Año con coma de miles | `Año_Apertura` (`"2,018.00"`) | `_to_numeric()` → 2018 |
| Tipo mixto | `Codigo_Postal` | `_to_string()` |

**Inventarios** — 2,000 filas × 23 columnas

| Problema | Columna | Corrección |
|----------|---------|------------|
| 1,304 strings con comas | `Costo_Total_Compra` | `_to_numeric()` |
| 122 strings con comas | `Costo_Desperdicio` | `_to_numeric()` |
| Booleano texto | `Necesita_Reorden` | `_to_boolean()` |
| Negativos posibles | `waste_pct` | `clip(lower=0)` |

**Canales Digitales** — 1,200 filas × 20 columnas

| Problema | Columna | Corrección |
|----------|---------|------------|
| 738 strings vacíos | `Calificacion` | `""` → NaN → `_to_numeric()` |
| 1,107 strings vacíos | `Tiempo_Respuesta_Horas` | `""` → NaN (solo 93 valores reales) |
| String con comas | `Alcance` | `_to_numeric()` |
| Booleano texto | `Respondido`, `Conversion` | `_to_boolean()` |

### Validación Post-Limpieza

| Dataset | Filas | Duplicados | Nulos críticos | Estado |
|---------|-------|------------|----------------|--------|
| Ventas | 5,000 | 0 | 0% | ✅ |
| Clientes | 1,500 | 0 | 0% | ✅ |
| Sucursales | 10 | 0 | 0% | ✅ |
| Inventarios | 2,000 | 0 | 0% | ✅ |
| Digital | 1,200 | 0 | 0% | ✅ |

### Resumen de Problemas Resueltos

| # | Tipo | Cantidad | Método |
|---|------|----------|--------|
| 1 | Monetarios como string con comas | ~2,510 valores | `_to_numeric()` |
| 2 | Strings vacíos (nulos ocultos) | 1,845 valores | `fullmatch(r"\s*")` → NaN |
| 3 | Booleanos `"Sí"/"No"` | 5 columnas | `_to_boolean()` |
| 4 | Fechas como string | 5 columnas | `pd.to_datetime()` |
| 5 | Nombres con acentos | 102 columnas | `_normalize_token()` + `schema_map.yml` |
| 6 | Año con separador miles | 10 valores | `_to_numeric()` |

### Conclusiones

- **0 registros perdidos** — los 9,710 originales se conservaron íntegros
- **Problema de formato, no de datos faltantes** — principalmente valores monetarios `"85,000.00"`
- **1,845 nulos ocultos** en Canales Digitales resueltos
- **102 columnas** renombradas a snake_case canónico

> 📄 Detalle completo: [`reports/informe_limpieza_datos.md`](reports/informe_limpieza_datos.md)

</details>

<details>
<summary><strong>📊 Informe del Caso de Estudio</strong> — Análisis integral de 10 sucursales</summary>

&nbsp;

### Resumen Ejecutivo

| Indicador | Resultado |
|-----------|-----------|
| Sucursal líder en ingresos | **Cancún** — $118,067 MXN |
| Mejor eficiencia operativa | **León** — menor costo ($143,500/mes) |
| Mayor oportunidad de mejora | **Cancún** — utilidad proxy -$4.5M pese a mayores ingresos |
| Platillo estrella | **Mole Poblano** — $134,575 en ingresos |
| Hora pico | **13:00 hrs** (lun-vie), segundo pico 19:00–20:00 |
| Principal driver de merma | **Carne de Res en Mérida** — $10,470 |
| Segmento más grande | **Ocasionales** — 1,180 clientes (78.7%) |
| Mes pico pronosticado | **Julio 2026** |
| Canal digital top | **TikTok** — 6–12× engagement por peso |

### Top 5 Platillos por Ingresos

| # | Platillo | Ingresos | Unidades |
|---|----------|----------|----------|
| 1 | Mole Poblano | $134,575 | 769 |
| 2 | Enchiladas Verdes | $96,660 | 716 |
| 3 | Margarita | $67,925 | 715 |
| 4 | Tacos al Pastor | $60,775 | 715 |
| 5 | Guacamole con Totopos | $58,473 | 657 |

### Ranking de Sucursales

| Pos | Sucursal | Ingresos | Margen Bruto | Tickets | Ticket Prom. |
|-----|----------|----------|-------------|---------|-------------|
| 1 | Cancún | $118,067 | $82,503 | 650 | $181.64 |
| 2 | CDMX Centro | $108,934 | $76,365 | 629 | $173.19 |
| 3 | Monterrey | $101,214 | $70,907 | 570 | $177.57 |
| 4 | Guadalajara | $93,049 | $65,367 | 542 | $171.68 |
| 5 | Querétaro | $85,947 | $60,197 | 483 | $177.94 |
| 6 | CDMX Sur | $83,567 | $58,656 | 527 | $158.57 |
| 7 | León | $71,777 | $50,230 | 386 | **$185.95** |
| 8 | Tijuana | $71,327 | $49,873 | 405 | $176.12 |
| 9 | Mérida | $70,821 | $49,660 | 405 | $174.87 |
| 10 | Puebla | $66,585 | $46,529 | 403 | $165.22 |

**Métodos de pago:** Tarjeta Crédito 40.2% · Débito 26.1% · Efectivo 21.9% · App 11.8%

### Problemas Identificados

**Rentabilidad — La paradoja Cancún:**
- Mayores ingresos pero peor utilidad proxy (-$4.5M) por costos de $382,000/mes
- León: mejor eficiencia con solo $143,500/mes y ticket más alto ($185.95)

**Inventario — $627,550 en merma total:**

| Sucursal | Costo Merma | Tasa Quiebre |
|----------|-------------|-------------|
| Puebla (peor) | $91,963 | 7.1% |
| Mérida | $85,285 | 8.5% |
| Guadalajara (mejor) | $41,095 | 8.9% |
| Monterrey | $43,645 | 9.5% |

### Pronóstico de Demanda

**Modelo:** Holt-Winters (tendencia aditiva, horizonte 6 meses)

| Sucursal | Ingrediente | Mes Pico | Cantidad |
|----------|------------|----------|----------|
| Puebla | Carne de Res | Mar 2026 | 394.56 |
| Monterrey | Tequila | Jul 2026 | 376.73 |
| Querétaro | Frijoles | Abr 2026 | 259.00 |
| León | Cilantro | Jun 2026 | 258.33 |

### Segmentación de Clientes

**Método:** RFM proxy + KMeans (k por Silhouette Score)

| Segmento | Clientes | % | Frecuencia | Gasto | Lealtad |
|----------|---------|---|------------|-------|---------|
| Leales Premium | 320 | 21.3% | 17/año | $4,409 | 100% |
| Ocasionales | 1,180 | 78.7% | ~6/año | ~$1,500 | ~11% |

### Plan 30-60-90 Días

- **30 días:** FEFO en Puebla/Mérida, reorden automática, campaña TikTok piloto
- **60 días:** Campañas segmentadas, programa lealtad ampliado, proveedores alternos
- **90 días:** Menú express hora comida, "Noche Mexicana" sábados, reestructuración costos Cancún

### Visualizaciones (19 gráficas)

| Tipo | Archivos |
|------|----------|
| Tendencias | `sales_trend_daily.html`, `sales_trend_monthly.html` |
| Distribución | `sales_by_city.html`, `sales_by_hour_day.html`, `payment_method_mix.html` |
| Ranking | `branch_ranking_sales_margin.html`, `branch_revenue_ranking.png` |
| Rentabilidad | `waterfall_cancún.png`, `waterfall_león.png`, `cost_structure_branches.png` |
| Platillos | `top_dishes_by_region_daypart.html`, `pareto_dishes.png` |
| Inventario | `inventory_waste_shortage_heatmap.html`, `waste_cost_by_branch.png` |
| Pronóstico | `forecast_peaks_top15.png` |
| Segmentación | `rfm_scatter_segments.png`, `personas_summary.png` |
| Digital | `digital_sentiment_platform.html`, `radar_branches.png` |

> 📄 Informe completo: [`reports/informe_caso_estudio.md`](reports/informe_caso_estudio.md)
> 📎 Versión Word: [`reports/informe_caso_estudio.docx`](reports/informe_caso_estudio.docx)

</details>
