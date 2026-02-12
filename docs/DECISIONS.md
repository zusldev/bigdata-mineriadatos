# DECISIONS

Registro de decisiones arquitectónicas y de modelado.

## D-001 Dashboard en `apps/dashboard/app.py`
- Decisión:
  - Ubicar la app Streamlit en `apps/dashboard/`.
- Razón:
  - Separación clara entre app de presentación y código de pipeline/modelado.
- Alternativas rechazadas:
  - `dashboard/app.py` en raíz: menos consistente al crecer el proyecto.

## D-002 Import absoluto con raíz del repo en `sys.path`
- Decisión:
  - Insertar raíz del repo al inicio de `sys.path` en la app Streamlit.
- Razón:
  - Evita `ModuleNotFoundError: apps` por diferencias de ejecución.
- Alternativas rechazadas:
  - Import relativo profundo: menos legible y frágil ante refactors.

## D-003 Study Guard obligatorio en pipeline
- Decisión:
  - Fallar pipeline si no existe entrada de Study Log para el `run_id`.
- Razón:
  - Asegura aprendizaje documentado y trazabilidad por corrida.
- Alternativas rechazadas:
  - Solo warning sin bloqueo: permite saltar la rutina de estudio.

## D-004 Salida automática `outputs/logs/run_summary.md`
- Decisión:
  - Generar resumen automático por run y anexarlo a Study Log.
- Razón:
  - Facilita ver “qué cambió” sin inspección manual extensa.
- Alternativas rechazadas:
  - Solo logs de consola: no es amigable para estudio y revisión histórica.

## D-005 Persistencia preferente Parquet con fallback CSV
- Decisión:
  - Intentar Parquet primero; si falla dependencia, escribir CSV y continuar.
- Razón:
  - Balance entre rendimiento y resiliencia operativa.
- Alternativas rechazadas:
  - Fallar si no hay pyarrow: reduce portabilidad del proyecto.

## D-006 Segmentación RFM proxy
- Decisión:
  - Construir RFM desde tabla `clientes`.
- Razón:
  - No existe llave `cliente_id` en `ventas` para RFM transaccional real.
- Alternativas rechazadas:
  - Join probabilístico cliente-ticket: introduce ruido y supuestos fuertes.

## D-007 Forecast top 12 ingredientes / 6 meses
- Decisión:
  - Limitar pronóstico a ingredientes de mayor impacto por costo/volumen.
- Razón:
  - Mejora estabilidad con historial mensual corto.
- Alternativas rechazadas:
  - Todos los ingredientes a 6 meses: mayor riesgo de error.

## D-008 Habilitar `make` en Windows con shim
- Decisión:
  - Instalar un `make.cmd` en PATH de usuario para ejecutar los targets principales.
- Razón:
  - `make` no estaba disponible en PowerShell, pero el equipo ya usa flujo tipo Makefile.
- Alternativas rechazadas:
  - Forzar instalación de GNU Make vía gestor externo: no siempre disponible en el entorno.
  - Pedir solo comandos manuales: menor ergonomía para el usuario.

## D-009 Tipado explícito de `branches` para escritura Parquet
- Decisión:
  - Castear campos textuales de `branches` a `string`, incluyendo `postal_code`.
- Razón:
  - Evitar error de pyarrow por mezcla de tipos (`int` y `str`) en columnas objeto.
- Alternativas rechazadas:
  - Desactivar Parquet para toda la tabla: pérdida de beneficio columnar.
  - Convertir todo a string: degrada calidad de features numéricas.

## D-010 Delayed expansion en shim `make.cmd`
- Decisión:
  - Usar `!SEED!`, `!HORIZON!`, `!TOP_INGREDIENTS!`, `!RUN_ID!` dentro del bloque `pipeline`.
- Razón:
  - Evitar expansión temprana de `%VAR%` que dejaba argumentos vacíos en argparse.
- Alternativas rechazadas:
  - Hardcodear argumentos y eliminar variables: menos flexible para pruebas/runs.

## D-011 Reducción de ruido de `loky/joblib` en runtime
- Decisión:
  - Inicializar `LOKY_MAX_CPU_COUNT=1` y filtrar warning específico de detección de cores.
- Razón:
  - El warning no era accionable en este entorno y ensuciaba logs de corrida.
- Alternativas rechazadas:
  - Ignorar el warning permanentemente: degrada lectura operativa.
  - Silenciar todos los warnings globalmente: riesgo de ocultar señales reales.

## D-012 Priorizar `.venv` en `Makefile`
- Decisión:
  - Resolver `PYTHON` automáticamente hacia `.venv` cuando exista.
- Razón:
  - Evita ejecutar herramientas (`ruff`, `pytest`, pipeline) con Python global sin dependencias del proyecto.
- Alternativas rechazadas:
  - Mantener `python` del PATH: provoca inconsistencias por máquina.
  - Forzar una ruta absoluta local: poco portable.

## D-013 Forzar `pytest --basetemp` dentro del repositorio (transitorio)
- Decisión:
  - Probar `--basetemp` local para sacar temporales de `%LOCALAPPDATA%\\Temp`.
- Razón:
  - Mitigar errores de permisos en `%LOCALAPPDATA%\\Temp` en Windows.
- Alternativas rechazadas:
  - Limpiar manualmente `%TEMP%` en cada corrida: frágil y no reproducible.
  - Depender de defaults de pytest: no controla ACL del sistema.
- Estado:
  - Estrategia reemplazada por D-014 cuando persistieron errores de ACL al cierre de sesión de pytest.

## D-014 Reemplazar `tmpdir` por fixture `tmp_path` custom
- Decisión:
  - Desactivar plugin `tmpdir` en tests y proveer `tmp_path` propio en `tests/conftest.py`.
- Razón:
  - Persistían errores de ACL en limpieza de temporales incluso con `basetemp` local.
- Alternativas rechazadas:
  - Seguir cambiando rutas `basetemp`: no resolvía la causa en este entorno.
  - Ignorar fallos de tests por permisos: invalida la señal de calidad.

## D-015 Mantener gate de calidad estricto (`ruff` + `black --check`)
- Decisión:
  - Corregir causas reales de lint (imports/unused) y formatear todo el código.
- Razón:
  - Asegurar consistencia para ejecución por fases y mantenimiento colaborativo.
- Alternativas rechazadas:
  - Relajar reglas globales: reduce calidad de largo plazo.
  - Ignorar black: aumenta diffs ruidosos y deuda de estilo.

## D-016 Feedback pedagógico en pruebas vía hook de pytest
- Decisión:
  - Implementar resumen personalizado en `tests/conftest.py` usando `pytest_terminal_summary`.
- Razón:
  - Mejorar la experiencia de estudio en `make test` mostrando conteo total, cobertura por archivo y lista de tests aprobados.
- Alternativas rechazadas:
  - Confiar solo en salida por defecto de `-q`: insuficiente para aprendizaje.
  - Script externo que parsea consola: más frágil y acoplado al formato de pytest.

## D-017 Documento dedicado de flujo Big Data -> Minería de Datos
- Decisión:
  - Crear `docs/STUDY_FLOW_BIGDATA_MINING.md` como material de estudio profundo.
- Razón:
  - Explicar con rigor el control de flujo real del pipeline y su relación con arquitectura de datos, modelado y BI.
- Alternativas rechazadas:
  - Repartir explicación en docs existentes: quedaba fragmentado y difícil de estudiar.
  - Solo explicación en dashboard sin documento persistente: menor trazabilidad académica.

## D-018 Extensión de Study Mode con sección de flujo y Mermaid copiable
- Decisión:
  - Agregar en dashboard la sección `🧠 Flujo: Big Data → Minería de Datos`, render del doc, diagramas Mermaid copiables y checklist de comprensión.
- Razón:
  - Facilitar estudio guiado directamente desde la app de presentación.
- Alternativas rechazadas:
  - Mostrar solo links a archivos: menos útil en clase.
  - Ocultar diagramas dentro del markdown sin bloque copiable: peor reutilización en apuntes.

## D-019 Índice lateral derecho para navegación de estudio
- Decisión:
  - Renderizar un TOC en columna derecha para documentos de estudio y para el documento de flujo Big Data/Mining.
- Razón:
  - Mejorar navegación cuando el contenido es largo.
- Alternativas rechazadas:
  - Dejar solo scroll vertical: navegación lenta en clase.
  - Mover índice al sidebar global: mezcla contexto con filtros de negocio.

## D-020 Índice con búsqueda y scroll independiente
- Decisión:
  - Añadir búsqueda en el índice y contenedor con scroll interno.
- Razón:
  - Acelerar localización de secciones sin desplazar toda la página.
- Alternativas rechazadas:
  - Índice estático sin filtro: poco eficiente con documentos extensos.
  - Uso de anclas sin panel dedicado: menor descubribilidad.

## D-021 Atajo global `/` para diccionario contextual
- Decisión:
  - Implementar paleta flotante de conceptos con atajo `/` (y `Ctrl/Cmd+K`) a nivel página.
- Razón:
  - Reducir fricción de estudio: consultar definiciones sin cambiar de documento ni perder hilo de lectura.
- Alternativas rechazadas:
  - Mantener solo diccionario en panel lateral: requiere desplazamiento y cambio de foco.
  - Forzar navegación al glosario: interrumpe flujo cognitivo.

## D-022 Integrar CI de calidad y smoke pipeline en GitHub Actions
- Decisión:
  - Crear workflow `.github/workflows/ci.yml` con `make lint`, `make test` y `make pipeline`.
- Razón:
  - Asegurar que cada push/PR mantenga calidad de código y ejecutabilidad end-to-end.
- Alternativas rechazadas:
  - Ejecutar solo tests unitarios: no detecta regresiones de orquestación completa.
  - CI parcial sin lint: degrada consistencia de estilo y calidad.

## D-023 Estandarizar colaboración con plantillas de Issue y PR
- Decisión:
  - Añadir plantillas para bug, feature y PR con checklist de validación.
- Razón:
  - Reducir ambigüedad en reportes/cambios y mejorar trazabilidad de decisiones técnicas.
- Alternativas rechazadas:
  - Dejar Issues/PR libres: menor estructura y más retrabajo en revisión.
  - Plantilla única para todo: baja precisión para casos de bug vs mejora.

## D-024 Versionado explícito con release `v0.1.1` y notas automáticas
- Decisión:
  - Publicar release incremental con `gh release create ... --generate-notes`.
- Razón:
  - Comunicar cambios de forma auditable y facilitar consumo externo del estado del proyecto.
- Alternativas rechazadas:
  - No versionar: dificulta reproducibilidad histórica.
  - Escribir notas manuales siempre: mayor costo operativo y riesgo de omisiones.
