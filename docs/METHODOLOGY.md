# METHODOLOGY

## Objetivo
Responder preguntas de negocio de Sabor Mexicano con un pipeline reproducible de analítica, modelado y recomendaciones.

## Enfoque por fases
1. Ingesta, limpieza y validación con mapeo de esquema.
2. EDA y análisis de desempeño (ventas, rentabilidad, inventario, digital).
3. Modelado de pronóstico y segmentación de clientes (RFM proxy).
4. Recomendaciones y exposición ejecutiva (reporte + dashboard).

## Justificación “Big Data style” (sin sobreafirmaciones)
- Diseño escalable por etapas (pipeline modular desacoplado).
- Capa de `schema_map` para absorber variaciones de nombres de columnas.
- Persistencia en formato columnar Parquet cuando está disponible.
- Fallback a CSV si `pyarrow` no está instalado, sin romper ejecución.
- Tablas de agregación “partition-friendly” (por `year_month`, `branch_id`, `ingredient`) para acelerar consultas.
- Opción `POLARS=1` para lecturas/agregaciones más rápidas en volúmenes mayores.
- Nota: no se usa clúster distribuido (Spark), pero sí patrones de ingeniería escalables y reproducibles.

## Validación y calidad
- Validación de columnas requeridas por dataset.
- Monitoreo de duplicados y faltantes críticos.
- Pruebas unitarias para transformaciones y sanidad de modelos.
