# Sabor Mexicano - Proyecto Integral de Data Mining y Big Data Style

Proyecto reproducible para analizar una cadena de 10 sucursales en México, respondiendo preguntas de negocio de ventas, rentabilidad, inventario, pronóstico de demanda y segmentación de clientes.

## 1) Objetivo del proyecto

Este repositorio implementa:
- Ingesta flexible de `JSON`, `CSV` y `XLSX` con mapeo de esquema configurable.
- Pipeline modular por fases ejecutable como módulo de Python.
- EDA + análisis de rentabilidad/inventario/digital.
- Pronóstico mensual por sucursal e ingrediente.
- Segmentación de clientes (RFM proxy + clustering).
- Recomendaciones accionables.
- Dashboard web con Streamlit para presentación.
- Documentación técnica en español.

## 2) Estructura principal

```text
.
├── apps/dashboard/app.py
├── config/settings.yml
├── config/schema_map.yml
├── config/recipe_map.yml
├── src/pipeline/run_all.py
├── src/data/
├── src/features/
├── src/analysis/
├── src/models/
├── src/reco/
├── src/report/
├── data/raw/
├── data/processed/
├── outputs/
├── reports/
└── docs/
```

## 3) Requisitos

- Python `3.11` recomendado.
- Datos en:
  - `data/raw/json/*.json`
  - `data/raw/csv/*.csv` (opcional)
  - `data/raw/xlsx/*.xlsx`

Instalación:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

También puedes usar:

```bash
make setup
```

## 4) Ejecución del pipeline end-to-end

Comando principal (obligatorio):

```bash
python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id <RUN_ID>
```

Este comando ejecuta las 4 fases:
1. Ingesta + limpieza + validación + EDA base + perfilado.
2. Análisis de rentabilidad, inventario y digital.
3. Pronóstico + segmentación.
4. Recomendaciones + generación de reportes y documentación.

### Requisito no negociable: rutina de estudio
Antes de correr pipeline debes actualizar:
- `docs/STUDY_LOG.md`
- `docs/GLOSSARY.md`
- `docs/DECISIONS.md`
- `docs/CHECKPOINTS.md`

El pipeline valida esto en modo fail-fast:
- `STUDY_LOG.md` debe contener `Run ID: <run_id>` o `NO_CHANGES: <run_id>`.
- Si no existe, la ejecución termina con error para forzar trazabilidad de aprendizaje.
- Ejemplo de run id: `2026-02-11-a`.

Corrida rápida de verificación (sin cambios de código), ya preparada en Study Log:

```bash
python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id 2026-02-11-quickcheck-01
```

## 5) Ejecutar dashboard

```bash
streamlit run apps/dashboard/app.py
```

Incluye pestaña dedicada: `📚 Aprender / Study Mode` con:
- resumen de conceptos por módulo,
- render de docs de estudio,
- sección “What changed in this run?” (diff-style),
- autoquiz (flashcards Q&A).

## 6) Comandos Makefile

```bash
make lint
make test
make pipeline
make dashboard
make all
```

Si estás en Windows PowerShell y no tienes GNU Make, se instaló un shim `make` compatible con estos targets.
Puedes forzar intérprete Python con variable de entorno:

```powershell
$env:PYTHON = "python"
make pipeline
```

Nota:
- El `Makefile` prioriza automáticamente `./.venv` si existe.
- `pytest` usa `outputs/.pytest_tmp` como temporal para evitar errores de permisos en `%TEMP%`.

## 7) Reproducibilidad y fallback parquet/csv

- Seed global controlado (`--seed`, default `42`).
- Persistencia preferente en Parquet.
- Si `pyarrow` no está disponible, el sistema cae automáticamente a CSV y lo registra en logs/manifest.
- Manifest de artefactos: `outputs/manifests/artifacts_manifest.csv`.

## 8) Modo opcional POLARS=1

Para lecturas/agregaciones más rápidas (si tienes `polars` instalado):

```bash
POLARS=1 python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12
```

Por defecto se usa `pandas` para simplicidad.

## 9) Archivos de salida relevantes

- `outputs/charts/*.html`: visualizaciones EDA.
- `outputs/tables/*.csv`: tablas analíticas, pronóstico, segmentación y recomendaciones.
- `outputs/models/*.pkl`: artefactos de modelos.
- `outputs/logs/run_summary.md`: resumen automático de la corrida.
- `reports/final_report.md`: reporte final integral.
- `reports/RESULTS_SUMMARY.md`: resumen ejecutivo para directores.
- `docs/*.md`: metodología, supuestos, diccionario de datos, perfil y rutina de estudio.

## 10) Docker (opcional)

Construir imagen:

```bash
docker build -t sabor-mexicano .
```

Ejecutar pipeline:

```bash
docker run --rm sabor-mexicano
```

Ejecutar dashboard:

```bash
docker run --rm -p 8501:8501 sabor-mexicano streamlit run apps/dashboard/app.py --server.address=0.0.0.0
```

## 11) Notas metodológicas importantes

- El proyecto adopta prácticas “Big Data style” sin sobreafirmar infraestructura distribuida:
  - pipeline modular y escalable,
  - schema mapping desacoplado,
  - outputs columnares parquet,
  - agregaciones partition-friendly.
- La segmentación RFM se construye en modo proxy con `clientes` (no hay llave transaccional cliente-venta).
