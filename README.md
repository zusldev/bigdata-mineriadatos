# 🌮 Sabor Mexicano — Big Data & Minería de Datos

Proyecto integral para analizar una cadena de **10 sucursales** de comida mexicana en México: ventas, rentabilidad, inventario, pronóstico de demanda, segmentación de clientes y marketing digital.

**Stack:** Python 3.12 · Pandas · Scikit-learn · Statsmodels · Plotly · Streamlit · python-docx

---

<details>
<summary><h2>📋 1. Instrucciones de Uso</h2></summary>

### Requisitos

- Python `3.11+`
- Datos crudos en `data/raw/json/*.json` (o `csv/` / `xlsx/`)

### Instalación

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O con Make:

```bash
make setup
```

### Estructura del proyecto

```
.
├── apps/dashboard/app.py          # Dashboard interactivo Streamlit
├── config/
│   ├── settings.yml               # Configuración del pipeline
│   ├── schema_map.yml             # Mapeo de columnas (español → canónico)
│   └── recipe_map.yml             # Mapeo de recetas y categorías
├── src/
│   ├── pipeline/run_all.py        # Pipeline principal (ejecuta todo)
│   ├── data/load.py               # Carga de datos JSON/CSV/XLSX
│   ├── data/clean.py              # Limpieza y transformación
│   ├── data/validate.py           # Validación de calidad
│   ├── features/build_features.py # Ingeniería de features (RFM, etc.)
│   ├── analysis/                  # Análisis: rentabilidad, inventario, digital
│   ├── models/                    # Segmentación (KMeans) y pronóstico (Holt-Winters)
│   ├── reco/                      # Motor de recomendaciones
│   └── report/                    # Generación de gráficas e informe .docx
├── data/raw/                      # Datos crudos (JSON, CSV, XLSX)
├── data/processed/                # Datos limpios (Parquet/CSV)
├── outputs/
│   ├── charts/                    # Visualizaciones HTML + PNG
│   ├── tables/                    # Tablas analíticas CSV
│   └── models/                    # Artefactos de modelos
├── reports/                       # Informes finales (.md, .docx)
└── docs/                          # Documentación metodológica
```

### Ejecución del pipeline

```bash
python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id <RUN_ID>
```

Ejecuta 4 fases secuenciales:
1. **Ingesta + Limpieza + Validación + EDA**
2. **Análisis** de rentabilidad, inventario y marketing digital
3. **Modelado:** Pronóstico de demanda (Holt-Winters) + Segmentación (KMeans)
4. **Recomendaciones** + Generación de reportes

> **Nota:** Antes de correr, actualizar `docs/STUDY_LOG.md` con el Run ID. El pipeline valida trazabilidad en modo fail-fast.

### Dashboard interactivo

```bash
streamlit run apps/dashboard/app.py
```

### Generación del informe .docx

```bash
python src/report/generate_charts_informe.py   # Genera 10 gráficas PNG
python src/report/build_docx.py                 # Genera reports/informe_caso_estudio.docx
```

### Comandos Makefile

```bash
make lint       # Linting con ruff
make test       # Tests con pytest
make pipeline   # Pipeline completo
make dashboard  # Lanzar Streamlit
make all        # lint + test + pipeline
```

### Modo Polars (opcional)

```bash
POLARS=1 python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12
```

### Docker (opcional)

```bash
docker build -t sabor-mexicano .
docker run --rm sabor-mexicano                                           # Pipeline
docker run --rm -p 8501:8501 sabor-mexicano streamlit run apps/dashboard/app.py --server.address=0.0.0.0  # Dashboard
```

### Archivos de salida

| Carpeta | Contenido |
|---------|-----------|
| `outputs/charts/` | 19 visualizaciones (HTML interactivas + PNG estáticas) |
| `outputs/tables/` | 22 tablas analíticas CSV |
| `outputs/models/` | Artefactos de modelos (.pkl) |
| `outputs/logs/` | Resumen de ejecución |
| `reports/` | Informe final (.md + .docx), resumen ejecutivo, informe de limpieza |
| `docs/` | Metodología, supuestos, diccionario de datos, glosario |

### Reproducibilidad

- **Seed:** Controlado globalmente (`--seed 42`)
- **Persistencia:** Parquet preferente, fallback automático a CSV
- **Manifest:** `outputs/manifests/artifacts_manifest.csv` registra todos los artefactos
- **CI:** GitHub Actions ejecuta lint + test + pipeline smoke en cada push

</details>

---

<details>
<summary><h2>🧹 2. Informe de Limpieza de Datos</h2></summary>

## Informe de Limpieza y Preparación de Datos

**Proyecto:** Sabor Mexicano — Caso de Estudio Big Data & Minería de Datos
**Pipeline:** `src/data/load.py` → `src/data/clean.py` → `src/data/validate.py` → `src/features/build_features.py`

---

### 1. Resumen Ejecutivo

Se trabajaron **5 datasets** con un total de **9,710 registros** y **102 columnas originales**. El proceso de ETL (Extract, Transform, Load) se ejecutó en 4 fases secuenciales: **carga → limpieza → validación → ingeniería de features**. Los principales problemas encontrados fueron: columnas monetarias almacenadas como texto con comas y signos de pesos, strings vacíos (`""`) interpretados como valores presentes en lugar de nulos, columnas booleanas en formato texto (`"Sí"/"No"`), y tipos de dato incorrectos en columnas numéricas.

---

### 2. Inventario de Datasets Crudos

| # | Dataset | Archivo Fuente | Formato | Filas | Columnas |
|---|---------|---------------|---------|-------|----------|
| 1 | Ventas | `data/raw/json/ventascsv.json` | JSON | 5,000 | 18 |
| 2 | Clientes | `data/raw/json/clientes.json` | JSON | 1,500 | 17 |
| 3 | Sucursales | `data/raw/json/sucursales.json` | JSON | 10 | 24 |
| 4 | Inventarios | `data/raw/json/inventarios.json` | JSON | 2,000 | 23 |
| 5 | Canales Digitales | `data/raw/json/canales_digitales.json` | JSON | 1,200 | 20 |
| — | **TOTAL** | — | — | **9,710** | **102** |

> También existen copias en `.xlsx` en `data/raw/xlsx/`. El pipeline prioriza JSON > CSV > XLSX.

---

### 3. Flujo Completo de Limpieza (ETL)

```
┌─────────────────────────────────────────────────────────────────────┐
│  FASE 1: CARGA (src/data/load.py)                                  │
│  ─ Lee archivos JSON/CSV/XLSX según prioridad                      │
│  ─ Detecta dataset por nombre de archivo (fuzzy match)             │
│  ─ Genera profile inicial (filas, columnas, % nulos)               │
├─────────────────────────────────────────────────────────────────────┤
│  FASE 2: LIMPIEZA (src/data/clean.py)                              │
│  ─ Renombra columnas a nombres canónicos (snake_case)              │
│  ─ Convierte tipos de dato (numérico, fecha, booleano)             │
│  ─ Reemplaza strings vacíos ("") → NaN                             │
│  ─ Imputa valores faltantes con reglas específicas                 │
│  ─ Elimina filas duplicadas                                        │
│  ─ Genera columnas derivadas (daypart, year_month, etc.)           │
├─────────────────────────────────────────────────────────────────────┤
│  FASE 3: VALIDACIÓN (src/data/validate.py)                         │
│  ─ Verifica columnas requeridas existan                            │
│  ─ Calcula % de nulos en columnas críticas                         │
│  ─ Detecta filas duplicadas restantes                              │
│  ─ Genera reporte de validación                                    │
├─────────────────────────────────────────────────────────────────────┤
│  FASE 4: INGENIERÍA DE FEATURES (src/features/build_features.py)   │
│  ─ Construye tabla analítica branch × day × hour                   │
│  ─ Calcula RFM (Recency, Frequency, Monetary) por cliente          │
│  ─ Agrega sentiment_score numérico                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4. Detalle por Dataset

#### 4.1 Ventas (`ventascsv.json`) — 5,000 filas × 18 columnas

| Problema | Columna | Detalle | Corrección |
|----------|---------|---------|------------|
| Tipo incorrecto | `Total_con_Propina` | 4 valores no numéricos (string con comas) | `_to_numeric()`: elimina comas/`$` → `pd.to_numeric(errors="coerce")` |
| Tipo incorrecto | `Fecha` | String `"2025-01-15"` | `pd.to_datetime(errors="coerce")` |
| Tipo incorrecto | `Hora` | String `"13:45:00"` | Trunca a `HH:MM`, extrae `hour` como entero |
| Sin columna derivada | — | No había franja horaria | Crea `daypart`: 6-11→Mañana, 12-16→Comida, 17-20→Tarde, otro→Noche |
| Fallback imputación | `total_sale` | NaN posibles | `fillna(unit_price × quantity)` |
| Fallback imputación | `ingredient_cost` | NaN posibles | Media por categoría; si aún NaN → 35% de `total_sale` |

#### 4.2 Clientes (`clientes.json`) — 1,500 filas × 17 columnas

| Problema | Columna | Detalle | Corrección |
|----------|---------|---------|------------|
| **Formato con comas** | `Gasto_Total_Estimado` | 1,077 de 1,500 valores son strings: `"5,668.20"` | `_to_numeric()`: remueve comas → float64 |
| Formato con comas | `Puntos_Lealtad` | 1 valor mixto: `"1,185.00"` | `_to_numeric()` |
| Booleano como texto | `Miembro_Lealtad` | `"Sí"/"No"` como string | `_to_boolean()`: normaliza Unicode → `True/False` |
| Booleano como texto | `Acepta_Promociones` | `"Sí"/"No"` como string | `_to_boolean()` |
| Fecha como string | `Fecha_Registro`, `Ultima_Visita` | Strings ISO | `pd.to_datetime(errors="coerce")` |
| Imputación derivada | `estimated_total_spend` | NaN tras conversión | `fillna(avg_spend × visits_last_year)` |

#### 4.3 Sucursales (`sucursales.json`) — 10 filas × 24 columnas

| Problema | Columna(s) | Detalle | Corrección |
|----------|-----------|---------|------------|
| **7 cols monetarias como string** | `Renta_Mensual`, `Servicios_Mensual`, `Nomina_Mensual`, `Costos_Operativos_Total`, `Ingresos_Promedio_Mensual`, `Margen_Operativo` | `"85,000.00"` con comas de miles | `_to_numeric()`: remueve comas → float64 |
| **Año con coma de miles** | `Año_Apertura` | `"2,018.00"` (¡2018 con coma!) | `_to_numeric()` remueve la coma → 2018.0 |
| Tipo mixto texto/int | `Codigo_Postal` | `"06600"` vs `44160` | `_to_string()` → fuerza todo a `string` |

#### 4.4 Inventarios (`inventarios.json`) — 2,000 filas × 23 columnas

| Problema | Columna | Detalle | Corrección |
|----------|---------|---------|------------|
| Formato con comas | `Costo_Total_Compra` | 1,304 de 2,000 son strings con comas | `_to_numeric()` |
| Formato con comas | `Costo_Desperdicio` | 122 de 2,000 son strings con comas | `_to_numeric()` |
| Booleano como texto | `Necesita_Reorden` | `"Sí"/"No"` | `_to_boolean()` |
| Valores negativos | `waste_pct` | Posibles negativos | `clip(lower=0)` |

#### 4.5 Canales Digitales (`canales_digitales.json`) — 1,200 filas × 20 columnas

| Problema | Columna | Detalle | Corrección |
|----------|---------|---------|------------|
| **738 strings vacíos** | `Calificacion` | 738 de 1,200 son `""` (no aplica) | `""` → `NaN` → `_to_numeric()` → float64 |
| **1,107 strings vacíos** | `Tiempo_Respuesta_Horas` | Solo 93 tienen valor real (7.75%) | `""` → `NaN` → `_to_numeric()`. Media calculada solo con los 93 reales |
| Formato con comas | `Alcance` | `"2,857.00"` | `_to_numeric()` |
| Numérico como texto | `Engagement` | `"258"` como string | `_to_numeric()` |
| Booleano como texto | `Respondido`, `Conversion` | `"Sí"/"No"` | `_to_boolean()` |
| Sin normalizar | `Sentimiento` | Variaciones mayúsculas/espacios | `.str.strip().str.lower()` |

---

### 5. Operaciones Transversales

| Operación | Función | Qué hace |
|-----------|---------|----------|
| Normalización de columnas | `_normalize_token()` | Unicode NFKD (quita acentos) → minúsculas → snake_case |
| Strings vacíos → NaN | `str.fullmatch(r"\s*")` | `""`, `" "`, `"   "` → `pd.NA` |
| Conversión numérica | `_to_numeric()` | Remueve `,` `$` ` ` → `pd.to_numeric(errors="coerce")` |
| Conversión booleana | `_to_boolean()` | `si/sí/yes/true/1/y` → True; `no/false/0/n` → False |
| Eliminación duplicados | `drop_duplicates()` | 0 duplicados encontrados en los 5 datasets |

---

### 6. Validación Post-Limpieza

| Dataset | Filas | Duplicados | Nulos en cols requeridas | Estado |
|---------|-------|------------|--------------------------|--------|
| Ventas | 5,000 | 0 | 0% | ✅ |
| Clientes | 1,500 | 0 | 0% | ✅ |
| Sucursales | 10 | 0 | 0% | ✅ |
| Inventarios | 2,000 | 0 | 0% | ✅ |
| Digital | 1,200 | 0 | 0% | ✅ |

---

### 7. Resumen de Problemas Resueltos

| # | Tipo | Datasets Afectados | Cantidad | Método |
|---|------|--------------------|----------|--------|
| 1 | Columnas monetarias como string con comas | Sucursales, Inventarios, Clientes, Digital, Ventas | ~2,510 valores | `_to_numeric()` |
| 2 | Strings vacíos como nulos ocultos | Digital (2 cols) | 1,845 valores | `fullmatch(r"\s*")` → `pd.NA` |
| 3 | Booleanos como texto `"Sí"/"No"` | Clientes, Inventarios, Digital | 5 columnas | `_to_boolean()` |
| 4 | Fechas como string | Ventas, Clientes, Inventarios, Digital | 5 columnas | `pd.to_datetime()` |
| 5 | Nombres en español con acentos | Todos | 102 columnas | `_normalize_token()` + `schema_map.yml` |
| 6 | Tipo mixto int/string | Sucursales, Clientes | ~11 valores | `_to_string()` / `_to_numeric()` |
| 7 | Año con separador de miles | Sucursales (`"2,018.00"`) | 10 valores | `_to_numeric()` |
| 8 | Valores negativos potenciales | Inventarios (`waste_pct`) | Preventivo | `clip(lower=0)` |

### 8. Conclusiones

1. **0 registros perdidos.** Los 9,710 registros originales se conservaron íntegros.
2. **El problema fue de formato, no de datos faltantes.** Principalmente valores monetarios como `"85,000.00"` que impedían cálculos.
3. **1,845 nulos ocultos** en Canales Digitales: strings vacíos `""` que Pandas no reconoce como NaN.
4. **La estandarización fue clave:** 102 columnas renombradas de español con acentos a snake_case canónico.
5. **Imputaciones conservadoras:** Solo donde existe fórmula lógica (`total = price × qty`, `spend = avg × visits`).

> 📄 Informe completo: [`reports/informe_limpieza_datos.md`](reports/informe_limpieza_datos.md)

</details>

---

<details>
<summary><h2>📊 3. Informe del Caso de Estudio</h2></summary>

## Informe Integral — Caso de Estudio: "Sabor Mexicano"

**Materia:** Big Data y Minería de Datos
**Fecha:** Febrero 2026
**Cadena analizada:** 10 sucursales en México

---

### Resumen Ejecutivo

| Indicador | Resultado |
|-----------|-----------|
| Sucursal líder en ingresos | **Cancún** — $118,067 MXN |
| Mejor eficiencia operativa | **León** — menor costo ($143,500/mes), mejor utilidad proxy |
| Mayor oportunidad de mejora | **Cancún** — peor utilidad proxy (-$4.5M) pese a mayores ingresos |
| Platillo estrella | **Mole Poblano** — $134,575 en ingresos |
| Hora pico | **13:00 hrs** (lun-vie), segundo pico 19:00–20:00 |
| Principal driver de merma | **Carne de Res en Mérida** — $10,470 por caducidad |
| Segmento más grande | **Ocasionales** — 1,180 clientes (78.7%) |
| Mes pico pronosticado | **Julio 2026** |
| Canal digital más efectivo | **TikTok** — 6–12× engagement por peso |

---

### Análisis Exploratorio

**Top 5 platillos por ingresos:**

| # | Platillo | Ingresos | Unidades |
|---|----------|----------|----------|
| 1 | Mole Poblano | $134,575 | 769 |
| 2 | Enchiladas Verdes | $96,660 | 716 |
| 3 | Margarita | $67,925 | 715 |
| 4 | Tacos al Pastor | $60,775 | 715 |
| 5 | Guacamole con Totopos | $58,473 | 657 |

**Ranking de sucursales por ingresos:**

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

---

### Identificación de Problemas

**Rentabilidad — La paradoja Cancún:**
- Cancún genera los mayores ingresos pero la peor utilidad proxy (-$4.5M) por costos operativos de $382,000/mes
- León, con solo $143,500/mes de costos, tiene la mejor eficiencia y el ticket más alto ($185.95)

**Inventario — $627,550 en merma total:**

| Sucursal | Costo Merma | Tasa Quiebre |
|----------|-------------|-------------|
| Puebla (peor) | $91,963 | 7.1% |
| Mérida | $85,285 | 8.5% |
| Guadalajara (mejor) | $41,095 | 8.9% |
| Monterrey | $43,645 | 9.5% (peor quiebre) |

**Top quiebres de inventario:** Salsa Verde 50% (CDMX Centro), Cebolla 50% (Cancún), Pollo 43% (Guadalajara)

---

### Predicción y Decisión

**Modelo:** Suavización Exponencial Holt-Winters (tendencia aditiva, 6 meses de horizonte)

**Top picos de demanda pronosticados:**

| Sucursal | Ingrediente | Mes Pico | Cantidad |
|----------|------------|----------|----------|
| Puebla | Carne de Res | Mar 2026 | 394.56 |
| Monterrey | Tequila | Jul 2026 | 376.73 |
| Querétaro | Frijoles | Abr 2026 | 259.00 |
| León | Cilantro | Jun 2026 | 258.33 |

**Julio 2026** es el mes pico más frecuente (temporada vacacional de verano).

---

### Segmentación de Clientes

**Método:** RFM proxy + KMeans clustering (k optimizado por Silhouette Score)

| Segmento | Clientes | % Total | Frecuencia | Gasto Prom. | Tasa Lealtad |
|----------|---------|---------|------------|-------------|-------------|
| Leales Premium | 320 | 21.3% | 17 visitas/año | $4,409 | 100% |
| Ocasionales | 1,180 | 78.7% | ~6 visitas/año | ~$1,500 | ~11% |

**Oportunidad:** El 78.7% de clientes son Ocasionales con 64-69% de aceptación de promociones → gran potencial de conversión a lealtad.

---

### Propuestas de Solución

**Top platillos a promocionar (por promotion_score):**

| Sucursal | Platillo | Score |
|----------|----------|-------|
| Guadalajara | Enchiladas Verdes | 0.911 |
| Monterrey | Mole Poblano | 0.887 |
| Monterrey | Guacamole con Totopos | 0.871 |
| CDMX Centro | Mole Poblano | 0.847 |

**Plan 30-60-90 días:**
- **30 días:** FEFO en Puebla/Mérida, política de reorden automática, campaña TikTok piloto
- **60 días:** Campañas segmentadas por persona, programa de lealtad ampliado, proveedores alternos
- **90 días:** Menú express hora comida, "Noche Mexicana" sábados, reestructuración costos Cancún

---

### Visualizaciones Generadas

**19 gráficas** en `outputs/charts/`:

| Tipo | Gráficas |
|------|----------|
| Tendencias ventas | `sales_trend_daily.html`, `sales_trend_monthly.html` |
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
