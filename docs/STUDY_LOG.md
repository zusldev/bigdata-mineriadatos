# STUDY_LOG

Diario de aprendizaje técnico del proyecto Sabor Mexicano.

## Run ID: 2026-02-11

### Mini-lección 1: Robustez de importación en Streamlit (paquete `apps`)
- Contexto:
  - Al ejecutar `streamlit run apps/dashboard/app.py`, el import absoluto `from apps.dashboard.components ...` podía fallar con `ModuleNotFoundError: 'apps'` por diferencias en `sys.path`.
- Conceptos:
  - `sys.path`: lista de rutas donde Python busca módulos.
  - Paquete Python: carpeta con `__init__.py` para resolver imports de forma explícita.
  - Import absoluto vs relativo: absoluto mejora legibilidad entre módulos de un proyecto grande.
- Implementación:
  - Archivos tocados: `apps/__init__.py`, `apps/dashboard/__init__.py`, `apps/dashboard/app.py`.
  - Se añadió inyección explícita de raíz del repo al inicio de `sys.path`.
  - Se mantuvo `from apps.dashboard.components import ...`.
  - Pseudocódigo:
    - calcular raíz del repo desde `__file__`
    - si no está en `sys.path`, insertarla al índice 0
- Validación:
  - Correr `streamlit run apps/dashboard/app.py`.
  - Esperar carga del dashboard sin error de módulo.
- Errores comunes:
  - Duplicar imports de `Path` o insertar `sys.path` después de imports que ya fallaron.
  - Omitir `__init__.py` y depender de comportamiento implícito del entorno.
- Próximos pasos:
  - Mantener esta convención para cualquier nueva app dentro de `apps/`.

### Mini-lección 2: Study Guard de documentación obligatoria
- Contexto:
  - Se requiere disciplina documental por corrida: si no hay entrada de estudio, el pipeline no debe continuar.
- Conceptos:
  - Fail Fast: detectar incumplimientos temprano para evitar salidas analíticas no auditables.
  - Contrato de ejecución: el pipeline exige prerequisitos antes de procesar datos.
- Implementación:
  - Archivo nuevo: `src/pipeline/study_mode.py`.
  - Archivo modificado: `src/pipeline/run_all.py`.
  - Reglas:
    - deben existir `docs/STUDY_LOG.md`, `docs/GLOSSARY.md`, `docs/DECISIONS.md`, `docs/CHECKPOINTS.md`.
    - `STUDY_LOG.md` debe incluir `Run ID: <run_id>` o `NO_CHANGES: <run_id>`.
  - Pseudocódigo:
    - leer run_id (CLI o fecha UTC)
    - validar docs requeridos
    - buscar run_id en Study Log
    - si no existe, salir con código no cero y mensaje útil
- Validación:
  - Correr pipeline con run válido:
    - `python -m src.pipeline.run_all --run-id 2026-02-11`
  - Probar fallo:
    - usar un run-id inexistente y verificar salida con error.
- Errores comunes:
  - Actualizar docs pero olvidar el `Run ID`.
  - Crear el archivo pero dejarlo vacío.
- Próximos pasos:
  - Añadir plantilla breve de “no cambios” para corridas de verificación.

### Mini-lección 3: Resumen automático de corrida y trazabilidad
- Contexto:
  - Se necesita saber qué cambió en cada run sin abrir múltiples archivos.
- Conceptos:
  - Observabilidad de pipeline: métricas de tiempo por etapa, warnings y artefactos.
  - Trazabilidad: enlazar resultados con una corrida identificable (`run_id`).
- Implementación:
  - Salida nueva: `outputs/logs/run_summary.md`.
  - Se incluye:
    - datasets cargados,
    - filas limpias por tabla,
    - warnings clave,
    - artefactos generados,
    - tiempo por fase,
    - bloque diff-style `+ / -`.
  - El resumen se anexa automáticamente al final de este archivo (`STUDY_LOG.md`).
- Validación:
  - Ejecutar pipeline y confirmar:
    - `outputs/logs/run_summary.md` existe,
    - aparece bloque de resumen al final de `STUDY_LOG.md`.
- Errores comunes:
  - No crear carpeta `outputs/logs`.
  - Cambiar formato del summary y romper lectura en dashboard.
- Próximos pasos:
  - Usar este summary como fuente para retrospectivas de mejora de modelo.

### Mini-lección 4: Pestaña 📚 Aprender / Study Mode en dashboard
- Contexto:
  - El dashboard debía incluir una vista de aprendizaje para estudiar el proyecto mientras se presenta.
- Conceptos:
  - “Learning UX”: combinar resultados y explicación conceptual en la misma interfaz.
  - Flashcards: formato de autoevaluación activa para reforzar comprensión.
- Implementación:
  - Archivo modificado: `apps/dashboard/app.py`.
  - Nueva pestaña:
    - resumen de conceptos por módulo,
    - render de documentos `.md` (Study Log, Glosario, Decisiones, Checkpoints, Metodología),
    - sección “What changed in this run?” con diff-style leído desde `run_summary.md`,
    - sección “Self-quiz” (8 tarjetas Q&A).
- Validación:
  - Abrir dashboard y confirmar la pestaña.
  - Verificar que se renderizan los markdown y el bloque diff.
- Errores comunes:
  - Leer archivos con ruta relativa incorrecta (usar raíz del repo).
  - No manejar ausencia de `run_summary.md`.
- Próximos pasos:
  - Enriquecer flashcards con métricas reales del run actual.

## Run ID: 2026-02-11-fix-make-clean

### Mini-lección 5: Comando `make` funcional en PowerShell (shim en PATH)
- Contexto:
  - En Windows PowerShell, `make` no estaba instalado y `make pipeline` fallaba aunque el proyecto tenía `Makefile`.
- Conceptos:
  - **Command shim**: ejecutable liviano que traduce un comando esperado (`make`) a comandos reales del entorno.
  - **Active interpreter**: usar `python` activo evita romper entornos virtuales o versiones distintas (3.12 vs 3.14).
- Implementación:
  - Se instaló `make.cmd` en una ruta del PATH de usuario.
  - Targets soportados: `setup`, `lint`, `test`, `pipeline`, `dashboard`, `all`.
  - Variables opcionales por entorno: `PYTHON`, `SEED`, `HORIZON`, `TOP_INGREDIENTS`, `RUN_ID`.
  - Pseudocódigo:
    - leer target
    - resolver python (`PYTHON` o `python`)
    - ejecutar comando equivalente del Makefile
- Validación:
  - `make` muestra ayuda.
  - `make pipeline` invoca el pipeline con `run-id`.
- Errores comunes:
  - Usar un `python` sin dependencias instaladas.
  - Ejecutar fuera de la raíz del repo.
- Próximos pasos:
  - Si cambian targets del Makefile, sincronizar el shim.

### Mini-lección 6: Fix de warnings en limpieza para Parquet y pandas
- Contexto:
  - El pipeline mostraba:
    - `FutureWarning` por `replace` sobre todo el DataFrame.
    - fallo al escribir Parquet de `branches` por mezcla `int/str` en `postal_code`.
- Conceptos:
  - **Downcasting warning**: pandas avisa que cambiará reglas implícitas de tipos en futuras versiones.
  - **Type stability**: para serialización robusta (Parquet), columnas de texto deben tener tipo consistente.
- Implementación:
  - Archivo: `src/data/clean.py`.
  - Ajustes:
    - reemplazo de strings vacíos aplicado por columna de tipo objeto/string (no global).
    - casting explícito a string en campos textuales de `branches` (`postal_code`, `address`, etc.).
  - Pseudocódigo:
    - detectar columnas object/string
    - reemplazar blancos por NaN en esas columnas
    - para dataset `branches`, convertir campos textuales a `string`
- Validación:
  - Re-ejecutar pipeline y revisar que desaparezca el error de Parquet en `branches_clean.parquet`.
  - Revisar log para ausencia de ese warning específico.
- Errores comunes:
  - Convertir indiscriminadamente todas las columnas a string y perder semántica numérica.
  - No preservar nulos al castear texto.
- Próximos pasos:
  - Añadir test unitario específico para escritura Parquet de `branches`.

## Run ID: 2026-02-11-fix-make-args

### Mini-lección 7: Bug de argumentos vacíos en `make pipeline` (Windows CMD expansion)
- Contexto:
  - `make pipeline` ejecutaba `run_all.py` con `--seed` vacío y argparse fallaba con `expected one argument`.
- Conceptos:
  - En scripts `.cmd`, `%VAR%` dentro de bloques `if (...)` se expande al parsear el bloque, no después de `set`.
  - Para valores calculados dentro del bloque se debe usar delayed expansion: `!VAR!`.
- Implementación:
  - Archivo afectado: shim global `make.cmd`.
  - Cambio clave:
    - antes: `--seed %SEED%`
    - ahora: `--seed !SEED!`
  - Se aplicó lo mismo para `HORIZON`, `TOP_INGREDIENTS`, `RUN_ID` y `errorlevel`.
- Validación:
  - Re-ejecutar `make pipeline`.
  - Esperado: ya no aparece error de argparse por `--seed`.
- Errores comunes:
  - Mezclar `%VAR%` y `!VAR!` sin entender cuándo se evalúan.
  - No activar `setlocal enabledelayedexpansion`.
- Próximos pasos:
  - Mantener esta convención para cualquier target nuevo en el shim.

## Run ID: 2026-02-11-fix-runtime-noise

### Mini-lección 8: Limpieza de ruido en logs de ejecución
- Contexto:
  - Aunque el pipeline terminaba bien, quedaban advertencias ruidosas que distraían el seguimiento operativo.
- Conceptos:
  - **Signal-to-noise en observabilidad**: logs limpios aceleran diagnóstico real.
  - **Configuración de runtime**: variables de entorno y filtros de warning deben aplicarse antes de importar librerías pesadas.
- Implementación:
  - Archivo: `src/pipeline/run_all.py`.
  - Acciones:
    - Set de `LOKY_MAX_CPU_COUNT=1` al inicio del módulo.
    - Filtro de warnings para el mensaje conocido de cores físicos no detectados.
- Validación:
  - Ejecutar `make pipeline`.
  - Confirmar que desaparece el warning de `joblib/loky` en consola.
- Errores comunes:
  - Setear variable dentro de `main()` cuando los imports de modelos ya ocurrieron.
  - Filtrar warnings demasiado amplio y ocultar mensajes relevantes.
- Próximos pasos:
  - Mantener filtros acotados a mensajes conocidos/no accionables.

### Mini-lección 9: Verificación end-to-end del target `make pipeline`
- Contexto:
  - Se debía confirmar que el flujo con shim + pipeline + docs guard funcionara de forma consistente.
- Conceptos:
  - **Smoke test**: prueba rápida que valida el camino crítico de ejecución.
- Implementación:
  - Se ejecutó `make pipeline` tras los fixes.
  - Resultado: ejecución completa, run summary actualizado y salida sin warnings previos.
- Validación:
  - Revisar:
    - `outputs/logs/run_summary.md`
    - `outputs/manifests/artifacts_manifest.csv`
    - `outputs/manifests/pipeline.log`
- Errores comunes:
  - Correr fuera de raíz del proyecto.
  - Olvidar `run-id` documentado en Study Log.
- Próximos pasos:
  - Correr `make dashboard` y validar pestaña `📚 Aprender / Study Mode` con docs actualizados.

## Run ID: 2026-02-11-hardening-make-pytest

### Mini-lección 10: Endurecimiento del `Makefile` para entorno virtual y defaults estables
- Contexto:
  - Había ejecuciones donde `make` tomaba un Python global sin dependencias (`ruff` ausente) y otras donde variables de entorno vacías dejaban argumentos CLI incompletos.
- Conceptos:
  - **Entorno virtual (`.venv`)**: aisla dependencias del proyecto para evitar conflictos con Python global.
  - **Default estable en Make**: usar `=` en lugar de `?=` evita que una variable de entorno vacía rompa argumentos esperados por `argparse`.
- Implementación:
  - Archivo tocado: `Makefile`.
  - Cambios clave:
    - detección de `VENV_PYTHON` por SO (`.venv/Scripts/python.exe` o `.venv/bin/python`),
    - prioridad al Python del venv cuando existe,
    - defaults de `SEED`, `HORIZON`, `TOP_INGREDIENTS`, `RUN_ID` con asignación estable.
  - Pseudocódigo:
    - detectar ruta de python de venv
    - si existe, usarla como `PYTHON`
    - fijar defaults numéricos/CLI para pipeline
- Validación:
  - Ejecutar `make lint` y confirmar que usa el venv (sin error `No module named ruff`).
  - Ejecutar `make pipeline` y verificar que no falla `--seed expected one argument`.
- Errores comunes:
  - Suponer que `python` del PATH siempre es el del proyecto.
  - Dejar defaults con `?=` cuando el entorno ya define variables vacías.
- Próximos pasos:
  - Mantener consistencia entre `Makefile` y shim `make` en Windows.

### Mini-lección 11: Pytest aislado de `%TEMP%` con `--basetemp` local
- Contexto:
  - Algunas corridas fallaban por permisos en `%LOCALAPPDATA%\\Temp\\pytest-of-libor` antes de ejecutar pruebas de negocio.
- Conceptos:
  - **`tmp_path` fixture**: pytest crea carpetas temporales por prueba.
  - **`--basetemp`**: fuerza dónde se crean esos temporales, útil cuando el temp global del sistema tiene ACL problemáticas.
- Implementación:
  - Archivo tocado: `pytest.ini`.
  - Cambio: `addopts = -p no:cacheprovider -q --basetemp=outputs/.pytest_tmp`.
  - Resultado esperado: todos los tests con `tmp_path` usan carpeta temporal dentro del repo.
  - Pseudocódigo:
    - pytest lee configuración
    - crea temporales bajo `outputs/.pytest_tmp`
    - evita escaneo de `%TEMP%` global
- Validación:
  - Ejecutar `make test` o `python -m pytest`.
  - Confirmar que desaparece `PermissionError` en `pytest-of-libor`.
- Errores comunes:
  - Configurar `basetemp` en una ruta sin permisos de escritura.
  - Limpiar la carpeta temporal mientras tests siguen corriendo.
- Próximos pasos:
  - Mantener esta configuración para CI/local en Windows con permisos restrictivos.

### Mini-lección 12: Fallback de pruebas con `tmp_path` custom (sin plugin `tmpdir`)
- Contexto:
  - En este entorno, el plugin interno de temporales de pytest seguía fallando por ACL al cerrar sesión, incluso cambiando `basetemp`.
- Conceptos:
  - **Plugin `tmpdir` de pytest**: provee `tmp_path`/`tmp_path_factory`, pero depende del ciclo de limpieza interno de pytest.
  - **Fixture custom**: permite controlar exactamente dónde y cómo crear/limpiar temporales.
- Implementación:
  - Archivos tocados: `pytest.ini`, `tests/conftest.py`.
  - Cambios:
    - `pytest.ini`: `-p no:tmpdir` para desactivar el plugin problemático.
    - `tests/conftest.py`: fixture `tmp_path` propia, con creación por `Path.mkdir` + `uuid4`.
    - fixture `autouse` para `LOKY_MAX_CPU_COUNT=1` y eliminar warning de joblib en tests.
  - Pseudocódigo:
    - crear `outputs/test_tmp/case_<uuid>`
    - usar esa ruta en cada test
    - borrar al finalizar
- Validación:
  - `make test` debe terminar en `12 passed` sin warnings.
- Errores comunes:
  - Crear temporales con `tempfile.mkdtemp` en entornos donde aplica ACL no heredada.
  - Desactivar plugin `tmpdir` sin reemplazar la fixture `tmp_path`.
- Próximos pasos:
  - Mantener esta estrategia si reaparecen restricciones de permisos en Windows.

### Mini-lección 13: Cierre de calidad con lint estricto (`ruff` + `black`)
- Contexto:
  - El proyecto debía pasar `make lint` completo, pero había errores `E402` por imports con setup previo y formateo pendiente.
- Conceptos:
  - **`E402`**: import no al inicio del módulo; en ciertos casos (setup de `sys.path`/env runtime) se documenta y se suprime de forma explícita por archivo.
  - **Formateo determinista**: `black` evita drift de estilo entre módulos y reduce ruido en revisión.
- Implementación:
  - Archivos tocados:
    - `apps/dashboard/app.py`, `src/pipeline/run_all.py` (`# ruff: noqa: E402`).
    - `src/models/segmentation.py` (import no usado eliminado).
    - `src/reco/recommendations.py` (variable no usada eliminada).
    - formateo automático en `src/`, `apps/`, `tests/`.
- Validación:
  - `make lint` en verde.
  - `make test` en verde después de ajustes.
- Errores comunes:
  - Silenciar reglas sin justificar por qué son necesarias.
  - Ejecutar `black --check` sin aplicar formato previo.
- Próximos pasos:
  - Mantener `make all` como gate de calidad antes de cambios de negocio.

## Run ID: 2026-02-11-test-feedback

### Mini-lección 14: Feedback enriquecido en `make test`
- Contexto:
  - El comando `make test` corría correctamente, pero el resultado era poco explicativo para estudio (solo puntos y resumen corto).
- Conceptos:
  - **Hook `pytest_terminal_summary`**: extensión de pytest para imprimir un resumen personalizado al final de la corrida.
  - **`nodeid`**: identificador único de prueba (`archivo::test`) útil para trazabilidad.
  - **Calidad observable**: no basta “pasó/falló”; conviene ver cobertura por archivo y lista exacta de pruebas exitosas.
- Implementación:
  - Archivo tocado: `tests/conftest.py`.
  - Se añadió un resumen al final con:
    - total ejecutadas,
    - pasaron/fallaron/errores/saltadas,
    - detalle por archivo,
    - listado de pruebas que pasaron,
    - veredicto final (“TODO BIEN” o “HAY FALLAS”).
  - Pseudocódigo:
    - leer `terminalreporter.stats`
    - agregar conteos por estado y por archivo
    - imprimir bloque resumen
- Validación:
  - Ejecutar `make test`.
  - Verificar que aparece sección `Feedback de pruebas` con conteos y lista de tests.
- Errores comunes:
  - Contar reports de fases equivocadas (`setup/teardown`) sin filtrar correctamente.
  - Duplicar pruebas en el detalle si se mezclan tipos de reportes sin control.
- Próximos pasos:
  - Si crece la suite, agregar export opcional del resumen a `outputs/logs/test_summary.md`.

## Run ID: 2026-02-11-study-flow-bigdata-mining

### Mini-lección 15: Flujo de control completo + conexión Big Data y Minería
- Contexto:
  - Ya existía el módulo de estudio, pero faltaba una guía profunda y ordenada para explicar el **control de flujo completo** del pipeline y su encaje conceptual con Big Data y Minería de Datos.
- Qué se agregó:
  - Documento nuevo: `docs/STUDY_FLOW_BIGDATA_MINING.md` con:
    - conceptos base (5V, minería, BI, pipeline, ETL vs ELT),
    - conexión Big Data -> Data Engineering -> Data Mining -> BI,
    - control de flujo exacto de `src/pipeline/run_all.py` paso por paso,
    - 2 diagramas Mermaid (flujo de datos y orquestación),
    - explicación “big-data-ready” sin sobreafirmar,
    - mini plan de estudio + 10 flashcards,
    - sección de evaluación: “Qué preguntaría un profesor” y “Cómo responderlo”.
  - Dashboard (`apps/dashboard/app.py`) actualizado con sección:
    - `🧠 Flujo: Big Data → Minería de Datos`,
    - render del nuevo documento,
    - expanders con los dos diagramas Mermaid en bloque copiable,
    - checklist de comprensión (`st.checkbox`),
    - manejo amigable si falta el archivo (`st.error` + instrucción).
- Por qué ayuda:
  - Convierte el proyecto en material de estudio de Ingeniería de Software, no solo en ejecución técnica.
  - Facilita explicar en clase el orden de módulos, contratos de datos y decisiones arquitectónicas.
- Dónde encontrarlo:
  - Dashboard -> pestaña `📚 Aprender / Study Mode` -> sección `🧠 Flujo: Big Data → Minería de Datos`.
  - Documento directo: `docs/STUDY_FLOW_BIGDATA_MINING.md`.

## Run ID: 2026-02-11-fix-make-all

### Mini-lección 16: Corrección operativa de `make all` en Windows
- Contexto:
  - `make all` fallaba con `...\\all is not recognized`.
- Qué se hizo:
  - Se corrigió el `make.cmd` global para que el target `all` invoque:
    - `make lint`
    - `make test`
    - `make pipeline`
  - antes intentaba autoreinvocarse de una forma que resolvía mal la ruta en este entorno.
- Por qué ayuda:
  - Permite ejecutar todo el flujo de calidad + pipeline en un solo comando.
- Validación:
  - `make all` ejecutó correctamente lint, tests y pipeline de punta a punta.
- Nota importante:
  - Si usas `RUN_ID` personalizado, recuerda agregar en `docs/STUDY_LOG.md`:
    - `Run ID: <tu_run_id>` o
    - `NO_CHANGES: <tu_run_id>`
  - Esto es obligatorio por el Study Guard.

## Run ID: 2026-02-11-study-index-right-panel

### Mini-lección 17: Índice lateral derecho para navegación en Study Mode
- Contexto:
  - La sección de estudio creció mucho y navegar con scroll era lento.
- Qué se agregó:
  - `apps/dashboard/app.py` ahora construye un índice por encabezados (`#`, `##`, `###`) y lo renderiza en una columna derecha.
  - Se aplicó tanto a:
    - selector de documentos de estudio,
    - sección `🧠 Flujo: Big Data → Minería de Datos`.
  - Se añadieron anclas HTML internas para permitir salto rápido por sección.
- Por qué ayuda:
  - Facilita lectura tipo “manual técnico”, especialmente en presentaciones o repaso de clase.
- Validación:
  - Abrir dashboard -> `📚 Aprender / Study Mode`.
  - Ver columna derecha “Índice”.
  - Hacer clic en una entrada y confirmar navegación dentro del contenido.
- Manejo de errores:
  - Si el documento no existe, se muestra mensaje amigable y el índice indica que no está disponible.

## Run ID: 2026-02-11-study-index-search-scroll

### Mini-lección 18: Índice con búsqueda + scroll y mejoras de legibilidad
- Contexto:
  - El índice derecho ya existía, pero faltaba capacidad de búsqueda y navegación cómoda cuando hay muchas secciones.
- Qué se agregó:
  - `apps/dashboard/app.py`:
    - búsqueda por texto dentro del índice (`st.text_input`),
    - filtrado dinámico de secciones por título,
    - contenedor del índice con altura fija y scroll (`st.container(height=...)`),
    - mejora visual ligera (tarjeta informativa y estilos para lectura).
- Por qué ayuda:
  - Evita recorrer toda la página para localizar un tema específico.
  - Mejora la experiencia en clase y presentación de documentos largos.
- Validación:
  - Abrir Study Mode.
  - Escribir texto en “Buscar en índice”.
  - Confirmar que el listado se filtra y mantiene scroll independiente.

## Run ID: 2026-02-11-study-shortcut-slash

### Mini-lección 19: Atajo global `/` para buscar conceptos sin salir de la lectura
- Contexto:
  - Aunque el índice y diccionario lateral ya ayudaban, hacía falta un acceso ultra-rápido mientras se estudia contenido largo.
- Qué se agregó:
  - `apps/dashboard/app.py` ahora inyecta una paleta flotante global con atajo:
    - `/` para abrir búsqueda de conceptos,
    - `Ctrl+K` / `Cmd+K` como alternativo,
    - `Esc` para cerrar.
  - La búsqueda muestra resultados en tiempo real (sin Enter) y la primera definición aparece automáticamente.
  - Se incluyó diseño visual mejorado (panel flotante, fondo atenuado, resultados clicables, pista inferior).
- Por qué ayuda:
  - Permite resolver dudas de términos (ej. `raw/lake`, `seed`, `logger`, `tracker`) sin cambiar de documento ni perder contexto.
- Validación:
  - Abrir dashboard.
  - Presionar `/` en cualquier pestaña sin foco en input.
  - Escribir término y verificar definición instantánea.

## NO_CHANGES: 2026-02-11-quickcheck-01

### Mini-lección de verificación sin cambios (corrida rápida)
- Contexto:
  - Se quiere validar que el pipeline y dashboard siguen funcionando sin introducir cambios de código o modelo.
- Conceptos:
  - `NO_CHANGES` permite cumplir el guard documental cuando el objetivo es solo verificación operativa.
  - Aun en corridas sin cambios, se mantiene trazabilidad con `run_id` único.
- Implementación:
  - Reutilizar este identificador de run:
    - `2026-02-11-quickcheck-01`
  - Ejecutar:
    - `python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12 --run-id 2026-02-11-quickcheck-01`
- Validación:
  - Debe generarse/actualizar `outputs/logs/run_summary.md`.
  - Debe anexarse resumen automático al final de este documento.
  - Debe abrir dashboard con `streamlit run apps/dashboard/app.py` y verse la pestaña `📚 Aprender / Study Mode`.
- Errores comunes:
  - Olvidar pasar el `--run-id` correcto.
  - Cambiar el `run_id` sin actualizar el encabezado `NO_CHANGES`.
- Próximos pasos:
  - Si se realizan cambios reales, crear un nuevo bloque `Run ID: <nuevo_id>` con mini-lecciones completas.


---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T22:57:42.290388+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T22:57:36.357666+00:00
- Fin UTC: 2026-02-11T22:57:42.289377+00:00
- Duración total (s): 5.93

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.688
- fase_2_analisis_negocio: 0.092
- fase_3_modelado: 4.075
- fase_4_recomendaciones_reportes: 0.060

## Key warnings
- No fue posible escribir parquet en C:\Users\libor\Documents\bigdata-mineriadatos\data\processed\branches_clean.parquet. Error: ("Expected bytes, got a 'int' object", 'Conversion failed for column postal_code with type object')
- pyarrow no disponible o error de parquet. Se escribe CSV como fallback: C:\Users\libor\Documents\bigdata-mineriadatos\data\processed\branches_clean.csv

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
- Se detectaron 2 warning(s); revisar sección 'Key warnings'.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.

## NO_CHANGES: 2026-02-11-mi-run
- Contexto:
  - Corrida operativa para verificar `make all` con entorno estable.
- Estado:
  - Sin cambios funcionales de código en esta corrida.
- Validación esperada:
  - `make all` debe completar lint, tests y pipeline sin bloqueo de Study Guard.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:10:33.433134+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:10:28.020111+00:00
- Fin UTC: 2026-02-11T23:10:33.431957+00:00
- Duración total (s): 5.41

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 2.285
- fase_2_analisis_negocio: 0.093
- fase_3_modelado: 2.961
- fase_4_recomendaciones_reportes: 0.055

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:11:11.183368+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:11:07.078583+00:00
- Fin UTC: 2026-02-11T23:11:11.181092+00:00
- Duración total (s): 4.10

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.188
- fase_2_analisis_negocio: 0.099
- fase_3_modelado: 2.741
- fase_4_recomendaciones_reportes: 0.057

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:11:39.852786+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:11:35.665101+00:00
- Fin UTC: 2026-02-11T23:11:39.851786+00:00
- Duración total (s): 4.19

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.200
- fase_2_analisis_negocio: 0.101
- fase_3_modelado: 2.799
- fase_4_recomendaciones_reportes: 0.068

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:12:07.644345+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:12:03.421450+00:00
- Fin UTC: 2026-02-11T23:12:07.642335+00:00
- Duración total (s): 4.22

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.185
- fase_2_analisis_negocio: 0.107
- fase_3_modelado: 2.843
- fase_4_recomendaciones_reportes: 0.069

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:12:29.801408+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:12:26.535279+00:00
- Fin UTC: 2026-02-11T23:12:29.798894+00:00
- Duración total (s): 3.26

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.250
- fase_2_analisis_negocio: 0.124
- fase_3_modelado: 1.818
- fase_4_recomendaciones_reportes: 0.056

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:13:22.094401+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:13:19.279951+00:00
- Fin UTC: 2026-02-11T23:13:22.092380+00:00
- Duración total (s): 2.81

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.177
- fase_2_analisis_negocio: 0.105
- fase_3_modelado: 1.462
- fase_4_recomendaciones_reportes: 0.052

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-hardening-make-pytest` (2026-02-11T23:25:41.446441+00:00)

# Run Summary - 2026-02-11-hardening-make-pytest

## Metadatos
- Inicio UTC: 2026-02-11T23:25:38.134094+00:00
- Fin UTC: 2026-02-11T23:25:41.444439+00:00
- Duración total (s): 3.31

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.218
- fase_2_analisis_negocio: 0.108
- fase_3_modelado: 1.893
- fase_4_recomendaciones_reportes: 0.074

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:47:57.154016+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:47:54.193875+00:00
- Fin UTC: 2026-02-11T23:47:57.152513+00:00
- Duración total (s): 2.96

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.211
- fase_2_analisis_negocio: 0.098
- fase_3_modelado: 1.576
- fase_4_recomendaciones_reportes: 0.057

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-mi-run` (2026-02-11T23:49:38.950887+00:00)

# Run Summary - 2026-02-11-mi-run

## Metadatos
- Inicio UTC: 2026-02-11T23:49:36.025693+00:00
- Fin UTC: 2026-02-11T23:49:38.948878+00:00
- Duración total (s): 2.92

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.268
- fase_2_analisis_negocio: 0.099
- fase_3_modelado: 1.485
- fase_4_recomendaciones_reportes: 0.053

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:50:35.942924+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:50:32.837389+00:00
- Fin UTC: 2026-02-11T23:50:35.940353+00:00
- Duración total (s): 3.10

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.157
- fase_2_analisis_negocio: 0.094
- fase_3_modelado: 1.780
- fase_4_recomendaciones_reportes: 0.053

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-11T23:56:44.208980+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-11T23:56:41.438696+00:00
- Fin UTC: 2026-02-11T23:56:44.206625+00:00
- Duración total (s): 2.77

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.135
- fase_2_analisis_negocio: 0.100
- fase_3_modelado: 1.464
- fase_4_recomendaciones_reportes: 0.053

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-12T00:36:21.119518+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-12T00:36:18.289360+00:00
- Fin UTC: 2026-02-12T00:36:21.118513+00:00
- Duración total (s): 2.83

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.197
- fase_2_analisis_negocio: 0.102
- fase_3_modelado: 1.460
- fase_4_recomendaciones_reportes: 0.053

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.

---

## Run ID: 2026-02-12-github-ci-release-v0.1.1

### Mini-lección 20: CI + plantillas + release para colaboración profesional
- Contexto:
  - El proyecto ya tenía pipeline y dashboard funcionales, pero faltaba cerrar el ciclo de colaboración en GitHub: validación automática en cada push/PR, plantillas para estandarizar incidencias y un release nuevo para versionar los cambios.
- Conceptos:
  - `CI (Integración Continua)`: proceso automático que ejecuta validaciones técnicas (lint, tests, smoke) cuando alguien sube cambios.
  - `Issue template`: formulario guiado para reportar bugs o solicitar mejoras con datos mínimos necesarios.
  - `PR template`: checklist estándar para que cada pull request tenga contexto, validación y trazabilidad.
  - `Release con notas automáticas`: versión etiquetada (`tag`) que resume cambios con `--generate-notes` para facilitar comunicación y auditoría.
- Implementación:
  - Archivos creados:
    - `.github/workflows/ci.yml`
    - `.github/ISSUE_TEMPLATE/bug_report.yml`
    - `.github/ISSUE_TEMPLATE/feature_request.yml`
    - `.github/ISSUE_TEMPLATE/config.yml`
    - `.github/pull_request_template.md`
  - Ajustes de documentación:
    - `README.md` (sección de colaboración y CI).
    - `docs/DECISIONS.md`, `docs/GLOSSARY.md`, `docs/CHECKPOINTS.md`.
  - Pseudocódigo de la ejecución CI:
    1. Checkout del repo.
    2. Setup Python 3.11.
    3. Instalar `requirements.txt`.
    4. Ejecutar `make lint`.
    5. Ejecutar `make test`.
    6. Ejecutar `make pipeline` (smoke end-to-end).
- Validación:
  - Verificar estado local:
    - `git status --short`
  - Verificar autenticación GitHub:
    - `gh auth status -h github.com`
  - Verificar release:
    - `gh release view v0.1.1 --repo zusldev/bigdata-mineriadatos`
  - Resultado esperado:
    - Workflow visible en pestaña Actions, templates disponibles al crear Issue/PR y release `v0.1.1` publicado con notas automáticas.
- Errores comunes:
  - No estar autenticado en `gh` al crear release.
  - Definir comandos de CI diferentes a los que usa el equipo local (`make` vs comandos ad-hoc).
  - No documentar el run en Study Log y luego fallar en el guard documental al correr pipeline.
- Próximos pasos:
  - Añadir badge de estado CI en README.
  - Extender workflow con matriz de versiones Python si se requiere compatibilidad adicional.



---

### Resumen automático del run `2026-02-11-quickcheck-01` (2026-02-12T00:51:08.839656+00:00)

# Run Summary - 2026-02-11-quickcheck-01

## Metadatos
- Inicio UTC: 2026-02-12T00:51:04.390765+00:00
- Fin UTC: 2026-02-12T00:51:08.837614+00:00
- Duración total (s): 4.45

## Datasets cargados
- sales: fuente=json filas_raw=5000 columnas=18
- customers: fuente=json filas_raw=1500 columnas=17
- branches: fuente=json filas_raw=10 columnas=24
- inventory: fuente=json filas_raw=2000 columnas=23
- digital: fuente=json filas_raw=1200 columnas=20

## Filas después de limpieza
- sales: 5000 filas limpias
- customers: 1500 filas limpias
- branches: 10 filas limpias
- inventory: 2000 filas limpias
- digital: 1200 filas limpias

## Artefactos generados
- Total: 50
- chart: 9
- document: 6
- feature_table: 2
- model: 2
- processed_table: 5
- table: 25
- validation_report: 1

## Tiempo por etapa (segundos)
- fase_1_ingesta_limpieza_eda: 1.312
- fase_2_analisis_negocio: 0.172
- fase_3_modelado: 2.857
- fase_4_recomendaciones_reportes: 0.089

## Key warnings
- Sin warnings relevantes.

## What changed in this run? (diff-style)
+ Se generaron 50 artefactos nuevos/actualizados.
+ Se completaron 4 etapas del pipeline.
+ No se detectaron warnings.

## Verificación rápida
1. Confirmar `reports/final_report.md` actualizado.
2. Confirmar `outputs/tables/*.csv` para tablas de negocio.
3. Ejecutar dashboard y validar pestaña 'Aprender / Study Mode'.

