# GLOSSARY

## Schema Mapping
Es una capa de traducción entre nombres originales de columnas y nombres canónicos del pipeline.  
Intuición: evita que el flujo se rompa cuando cambian encabezados entre fuentes (`Sucursal_ID`, `branch_id`, etc.).  
Pros: robustez y mantenibilidad. Contras: requiere mantener actualizado `config/schema_map.yml`.

## Fail Fast
Principio de ingeniería donde el sistema detiene ejecución al detectar un incumplimiento crítico.  
Aquí se aplica para forzar disciplina documental (Study Log) antes de procesar datos y generar reportes.

## Parquet
Formato columnar optimizado para analítica.  
Permite mejor compresión y lectura selectiva de columnas frente a CSV. Si `pyarrow` no está disponible, el pipeline usa CSV como fallback.

## RFM (Recency, Frequency, Monetary)
Marco clásico de segmentación de clientes:
- **Recency**: qué tan reciente fue la última compra.
- **Frequency**: cuántas compras hace en un periodo.
- **Monetary**: cuánto dinero genera.

En este caso es **RFM proxy** porque no existe enlace directo entre tickets y cliente.

## KMeans
Algoritmo de clustering no supervisado que agrupa observaciones similares en `k` grupos.  
Se usa para construir segmentos de clientes y luego traducirlos a personas accionables para marketing.

## Silhouette Score
Métrica de calidad de clustering que compara cohesión interna vs separación entre grupos.  
Valores más altos indican grupos más definidos.

## Exponential Smoothing
Familia de modelos de series de tiempo que asignan mayor peso a observaciones recientes.  
Buena opción cuando hay historial corto y se busca una línea base robusta.

## Punto de Reorden
Umbral de inventario para volver a comprar antes de un quiebre.  
Incluye demanda esperada durante lead time + stock de seguridad.

## Stock de Seguridad
Reserva adicional para cubrir variabilidad de demanda o retrasos de proveedor.  
En el proyecto se aproxima con `z * desviación * sqrt(lead_time)`.

## Diff-style Summary
Resumen con líneas prefijadas:
- `+` para cambios completados.
- `-` para incidencias/warnings.

Facilita lectura rápida del estado del run.

## Command Shim
Pequeño ejecutable/script que actúa como puente entre un comando esperado y una implementación alternativa.  
En este proyecto, se usó para habilitar `make` en PowerShell Windows sin instalar GNU Make completo.

## Downcasting (pandas)
Conversión implícita de tipos a un tipo “más pequeño” o distinto durante operaciones como `replace`.  
Puede producir cambios silenciosos no deseados; por eso se recomienda tipado explícito y transformaciones por columna.

## Delayed Expansion (CMD)
Mecanismo de `cmd.exe` que evalúa variables en tiempo de ejecución dentro de bloques `if/for` usando `!VAR!`.  
Evita errores donde `%VAR%` se expande demasiado pronto y termina vacío o con valores obsoletos.

## LOKY_MAX_CPU_COUNT
Variable de entorno usada por el backend `loky` (joblib) para acotar workers de paralelismo.  
Puede usarse para evitar warnings de detección de núcleos físicos en entornos donde esa detección falla.

## Basetemp (pytest)
Es la carpeta base donde pytest crea los directorios temporales usados por `tmp_path` y `tmp_path_factory`.  
Forzarlo con `--basetemp=...` mejora estabilidad cuando `%TEMP%` del sistema tiene permisos restringidos o residuos corruptos.

## Resolución de Python en Makefile
Patrón para elegir automáticamente el intérprete del entorno virtual (`.venv`) cuando existe.  
Reduce fallos por dependencias instaladas en un Python distinto al que ejecuta `make` y mantiene reproducibilidad local/CI.

## Plugin `tmpdir` (pytest)
Componente interno de pytest que administra directorios temporales para fixtures como `tmp_path`.  
Si el entorno tiene problemas de permisos/ACL al limpiar temporales, puede desactivarse y reemplazarse con una fixture custom controlada por el proyecto.

## E402 (`ruff`)
Regla de estilo que exige imports al inicio del archivo.  
En casos especiales (por ejemplo, preparar `sys.path` o variables de entorno antes de imports dependientes), se puede documentar y excluir por archivo en lugar de desactivar globalmente.

## `pytest_terminal_summary`
Hook de pytest que permite personalizar el resumen final de ejecución en consola.  
Es útil para mostrar métricas de aprendizaje: cuántas pruebas se ejecutaron, qué módulos cubren y cuáles casos pasaron.

## `nodeid` de pytest
Identificador textual de cada prueba con formato `ruta_archivo::nombre_test`.  
Permite construir reportes legibles y trazables sin parsear nombres manualmente.

## 5V de Big Data
Marco clásico para describir complejidad de datos:
- Volumen, Velocidad, Variedad, Veracidad y Valor.
Sirve para justificar por qué no basta “guardar datos”: hay que diseñar pipeline, validación y consumo para decisión.

## Flujo de Control (Pipeline Orchestration)
Secuencia exacta de ejecución entre módulos (qué se llama primero y qué depende de qué).  
En este proyecto lo define `src/pipeline/run_all.py`, y entenderlo evita errores de orden (por ejemplo, modelar antes de limpiar/validar).

## ETL vs ELT
ETL transforma antes de cargar el destino analítico; ELT carga primero y transforma después según necesidad.  
Sabor Mexicano sigue un patrón híbrido orientado a ELT local: ingesta flexible de raw y transformación por etapas modulares.

## Tabla de Contenidos (TOC) en dashboard
Índice navegable generado automáticamente desde encabezados de documentos markdown.  
Mejora la usabilidad en contenido largo al permitir saltos directos por sección sin perder contexto.

## Búsqueda incremental en TOC
Filtro en tiempo real aplicado a los títulos del índice mientras el usuario escribe.  
Reduce tiempo de navegación en documentos largos y mejora la exploración orientada a conceptos.

## Command Palette de estudio
Panel flotante de búsqueda rápida activado por atajo de teclado.  
En este proyecto se usa para consultar definiciones al instante sin abandonar la lectura del documento actual.
