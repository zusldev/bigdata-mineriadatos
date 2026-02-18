# 🌮 Sabor Mexicano — Big Data & Minería de Datos

[![CI](https://github.com/zusldev/bigdata-mineriadatos/actions/workflows/ci.yml/badge.svg)](https://github.com/zusldev/bigdata-mineriadatos/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **📋 [Proyecto](README.md)** · **🧹 [Informe de Limpieza de Datos](reports/informe_limpieza_datos.md)** · **📊 [Informe del Caso de Estudio](reports/informe_caso_estudio.md)**

Proyecto integral de **Big Data y Minería de Datos** que analiza una cadena de **10 sucursales** de comida mexicana en México. Cubre ventas, rentabilidad, inventario, pronóstico de demanda, segmentación de clientes y marketing digital mediante un pipeline end-to-end reproducible.

**Autor:** Liborio Zúñiga

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
| `docs/` | Metodología, supuestos, diccionario de datos, glosario |
