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

## CI (Integración Continua)
Práctica donde cada cambio de código se valida automáticamente en un servidor (por ejemplo GitHub Actions).  
En este proyecto, la CI ejecuta `make lint`, `make test` y `make pipeline` para asegurar calidad y ejecutabilidad completa.

## Workflow de GitHub Actions
Archivo YAML dentro de `.github/workflows/` que define jobs, pasos, variables de entorno y disparadores (`push`, `pull_request`, etc.).  
Permite automatizar verificaciones repetibles sin depender del entorno local de cada desarrollador.

## Issue Template
Formulario estructurado para abrir incidencias con campos obligatorios (contexto, pasos de reproducción, impacto).  
Mejora calidad de los reportes y acelera el diagnóstico técnico.

## PR Template
Plantilla que aparece al abrir una Pull Request para obligar contexto, checklist y evidencia de pruebas.  
Ayuda a que las revisiones sean consistentes y con criterios de calidad homogéneos.

## Release Notes Automáticas
Resumen de cambios generado por GitHub al crear un release con `--generate-notes`.  
Reduce trabajo manual y deja una bitácora versionada de lo que cambió entre tags.

## Ticket Promedio
Ingreso medio por transacción, calculado como ventas totales ÷ número de tickets.  
En Sabor Mexicano indica cuánto gasta un comensal por visita y permite comparar sucursales o franjas horarias.  
Un ticket promedio bajo puede sugerir oportunidades de up-selling o combos.

## Holt-Winters
Variante de Exponential Smoothing que captura nivel, tendencia y estacionalidad simultáneamente.  
Es el motor de pronóstico del tab «Pronósticos»: ajusta tres componentes suavizados para proyectar demanda mensual.  
Funciona bien con series estacionales cortas como las de un restaurante (picos en fin de semana, temporada alta, etc.).

## FEFO (First Expired, First Out)
Política de rotación de inventario que despacha primero el producto con fecha de caducidad más próxima.  
Es crítica en un restaurante porque reduce merma de ingredientes perecederos.  
El módulo de inventario la asume implícitamente al calcular días de cobertura y alertas de vencimiento.

## Margen / Utilidad Proxy
Aproximación al beneficio real cuando no se dispone de costos exactos por platillo.  
Se estima como `precio_venta − costo_estimado`, usando porcentajes estándar de la industria restaurantera (~30-35 % food cost).  
Permite rankear sucursales y platillos por rentabilidad relativa aunque el dato contable completo no esté disponible.

## Merma
Pérdida de inventario por caducidad, deterioro, errores de preparación o robo.  
En el dashboard se visualiza por sucursal e ingrediente para identificar focos de desperdicio.  
Reducir la merma impacta directamente el margen operativo de cada unidad.

## Quiebre de Inventario
Situación donde un ingrediente se agota antes de la siguiente entrega, provocando ventas perdidas o sustituciones.  
El heatmap de inventario resalta sucursales con quiebres frecuentes para priorizar ajustes de reorden.  
Su costo incluye no solo la venta perdida sino también la insatisfacción del cliente.

## Lead Time
Tiempo transcurrido entre la solicitud de compra y la recepción efectiva del ingrediente en sucursal.  
Es un parámetro clave de la fórmula de punto de reorden: a mayor lead time, mayor stock de seguridad necesario.  
En Sabor Mexicano se estima por proveedor/ingrediente a partir del historial de entregas.

## Engagement Rate
Proporción de interacciones (likes, comentarios, compartidos) respecto al alcance o seguidores en redes sociales.  
El tab «Digital» lo reporta por plataforma (TikTok, Instagram, Facebook) para evaluar qué contenido conecta mejor.  
Un engagement alto con sentimiento positivo señala campañas que vale la pena replicar.

## Sentimiento (Análisis de Sentimiento)
Clasificación automática de texto (reseñas, comentarios) en categorías positivo, neutro o negativo.  
En el proyecto se agrega por plataforma y sucursal para detectar patrones de satisfacción o quejas recurrentes.  
Complementa métricas cuantitativas de ventas con la voz cualitativa del cliente.

## Clustering / Segmentación
Técnica de aprendizaje no supervisado que agrupa observaciones similares sin etiquetas previas.  
Aquí se aplica con KMeans sobre variables RFM para crear segmentos de clientes accionables.  
El resultado alimenta las «Personas» de marketing y las recomendaciones de campaña.

## Daypart (Franja Horaria)
División del día en bloques operativos: desayuno, comida, merienda, cena.  
Permite analizar tendencias de venta y mix de platillos por momento del día.  
El heatmap de ventas por hora y día de la semana usa dayparts para identificar picos y valles de demanda.

## Score Compuesto
Indicador único que combina múltiples métricas ponderadas en una sola puntuación comparable.  
Por ejemplo, el ranking de sucursales pondera ventas, margen, merma y satisfacción digital en un score 0-100.  
Facilita la toma de decisiones al resumir dimensiones heterogéneas en un solo eje de comparación.

## Persona (Marketing)
Arquetipo ficticio de cliente construido a partir de datos reales de comportamiento (frecuencia, gasto, horario).  
Cada cluster de KMeans se traduce en una persona con nombre, descripción y estrategia de retención sugerida.  
Es el puente entre el análisis estadístico y las acciones concretas de marketing.

## Fórmula de Safety Stock (Stock de Seguridad)
`SS = z × σ_demanda × √lead_time`, donde `z` es el nivel de servicio deseado (e.g., 1.65 para 95 %).  
Cuantifica cuánta reserva extra mantener para absorber variabilidad de demanda y retrasos de proveedor.  
El módulo de inventario la aplica por ingrediente-sucursal para generar políticas de reorden automatizadas.

## Pipeline de Datos
Secuencia orquestada de pasos que transforman datos crudos en artefactos analíticos listos para consumo.  
En Sabor Mexicano sigue el flujo: ingesta → limpieza → features → modelado → visualización → reporte.  
Está codificado en `src/pipeline/run_all.py` y se ejecuta de forma reproducible con `make pipeline`.

## Forecast Horizon (Horizonte de Pronóstico)
Número de periodos futuros que el modelo proyecta más allá de los datos observados.  
En el tab «Pronósticos» se configura típicamente a 3-6 meses para planificación de compras e inventario.  
Un horizonte más largo aumenta la incertidumbre; por eso se acompaña de intervalos de confianza.

## Mapa de Calor (Heatmap)
Representación visual de una matriz donde el color codifica la intensidad de un valor numérico.  
Se usa en ventas (hora × día), inventario (merma × sucursal) y digital (sentimiento × plataforma).  
Permite detectar patrones espaciales o temporales de un vistazo sin leer tablas extensas.

## Cross-Selling (Venta Cruzada)
Estrategia de ofrecer productos complementarios al que el cliente ya eligió (e.g., guacamole con tacos).  
El módulo de recomendaciones identifica combinaciones frecuentes de platillos para sugerir promociones de paquete.  
Incrementa el ticket promedio sin necesidad de atraer nuevos clientes.

## Tasa de Conversión
Porcentaje de usuarios que completan una acción deseada respecto al total que la inició.  
En el contexto digital de Sabor Mexicano puede medir cuántos seguidores que ven una promoción terminan visitando la sucursal.  
Permite evaluar la efectividad real de campañas más allá del engagement superficial.

## Outlier (Valor Atípico)
Observación que se desvía significativamente del comportamiento esperado de los datos.  
En ventas puede ser un día festivo con pico inusual o un error de captura; en inventario, una merma anómala.  
El pipeline los detecta durante la limpieza para decidir si corregir, excluir o documentar su tratamiento.

## Normalización de Datos
Transformación que lleva variables a una escala común (e.g., 0-1) para que ninguna domine por magnitud.  
Es necesaria antes de aplicar KMeans u otros algoritmos sensibles a escala sobre variables como monto, frecuencia y recencia.  
Sin normalizar, una variable con rango grande (ventas en pesos) opacaría a otra con rango pequeño (número de visitas).

## Imputación
Técnica para rellenar valores faltantes con estimaciones razonables (media, mediana, moda o modelos).  
En Sabor Mexicano se aplica durante la limpieza para evitar que registros incompletos reduzcan el tamaño de muestra.  
La estrategia elegida se documenta en `ASSUMPTIONS.md` para mantener transparencia analítica.

## Validación de Esquema
Verificación automática de que los datos cumplen tipos, rangos y restricciones esperadas antes de procesarlos.  
Se implementa con `config/schema_map.yml` y funciones de chequeo que aplican el principio Fail Fast.  
Detecta errores tempranos (columnas faltantes, tipos incorrectos) antes de que contaminen análisis posteriores.
