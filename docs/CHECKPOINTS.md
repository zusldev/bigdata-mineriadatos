# CHECKPOINTS

Checklist de hitos del pipeline y documentación.

- [x] Estructura de proyecto creada (`src`, `apps`, `config`, `outputs`, `docs`, `tests`).
- [x] Loader flexible JSON/CSV/XLSX con deduplicación de workbooks.
- [x] Limpieza + validación con schema mapping configurable.
- [x] Persistencia parquet + fallback CSV implementada.
- [x] EDA con export de charts y tablas.
- [x] Análisis de rentabilidad, inventario y digital.
- [x] Forecast mensual por sucursal/ingrediente (top 12, 6 meses).
- [x] Segmentación RFM proxy + clustering KMeans.
- [x] Recomendaciones de marketing e inventario.
- [x] Dashboard con 7 pestañas funcionales.
- [x] Pestaña 📚 Aprender / Study Mode implementada.
- [x] Study Guard en pipeline (fail-fast documental).
- [x] Run summary automático en `outputs/logs/run_summary.md`.
- [x] Documentación de estudio creada: Study Log, Glossary, Decisions, Checkpoints.
- [x] Shim `make` habilitado para PowerShell Windows.
- [x] Shim `make` corregido (delayed expansion para argumentos pipeline).
- [x] Fix de warnings de limpieza (`FutureWarning` + `postal_code` para parquet).
- [x] Fix de warnings runtime `loky/joblib` en ejecución de pipeline.

## Run activo para validación documental
- [x] Run ID preparado en Study Log: `2026-02-11`
- [x] Run ID de verificación rápida (NO_CHANGES): `2026-02-11-quickcheck-01`
- [x] Run ID de corrección make/clean: `2026-02-11-fix-make-clean`
- [x] Run ID de corrección argumentos make: `2026-02-11-fix-make-args`
- [x] Run ID de limpieza runtime/logs: `2026-02-11-fix-runtime-noise`
- [x] Run ID de endurecimiento make/pytest: `2026-02-11-hardening-make-pytest`
- [x] Run ID de feedback de pruebas: `2026-02-11-test-feedback`
- [x] Run ID de estudio flujo big data/minería: `2026-02-11-study-flow-bigdata-mining`
- [x] Run ID índice lateral study: `2026-02-11-study-index-right-panel`
- [x] Run ID índice con búsqueda/scroll: `2026-02-11-study-index-search-scroll`
- [x] Run ID atajo global slash: `2026-02-11-study-shortcut-slash`
- [x] Hardening de tests Windows: fixture `tmp_path` custom sin plugin `tmpdir`.
- [x] Gate de calidad validado: `make lint` + `make test` en verde.
- [x] `make test` con resumen extendido (conteos, detalle por archivo y tests aprobados).
- [x] Documento de estudio de flujo creado: `docs/STUDY_FLOW_BIGDATA_MINING.md`.
- [x] Dashboard Study Mode extendido con sección de flujo, Mermaid copiables y checklist.
- [x] Dashboard Study Mode con índice lateral derecho por encabezados.
- [x] Índice Study con búsqueda en tiempo real y scroll interno.
- [x] Paleta global de conceptos con atajo `/` + búsqueda instantánea sin Enter.

- [x] Pipeline completado para Run ID: 2026-02-11-quickcheck-01

- [x] Pipeline completado para Run ID: 2026-02-11-hardening-make-pytest

- [x] Pipeline completado para Run ID: 2026-02-11-mi-run
