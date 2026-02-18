> **📋 [Proyecto](../README.md)** · **🧹 [Informe de Limpieza de Datos](informe_limpieza_datos.md)** · **📊 [Informe del Caso de Estudio](informe_caso_estudio.md)**

---

# Informe de Limpieza y Preparación de Datos

## Proyecto: Sabor Mexicano — Caso de Estudio Big Data & Minería de Datos

**Autor:** Liborio Zuñiga  
**Fecha de generación:** Febrero 2026  
**Pipeline:** `src/pipeline/run_all.py` → `src/data/load.py` → `src/data/clean.py` → `src/data/validate.py` → `src/features/build_features.py`

---

## 1. Resumen Ejecutivo

Se trabajaron **5 datasets** con un total de **9,710 registros** y **102 columnas originales**. El proceso de ETL (Extract, Transform, Load) se ejecutó en 4 fases secuenciales: **carga → limpieza → validación → ingeniería de features**. Los principales problemas encontrados fueron: columnas monetarias almacenadas como texto con comas y signos de pesos, strings vacíos (`""`) interpretados como valores presentes en lugar de nulos, columnas booleanas en formato texto (`"Sí"/"No"`), y tipos de dato incorrectos en columnas numéricas.

---

## 2. Inventario de Datasets Crudos

| # | Dataset | Archivo Fuente | Formato | Filas | Columnas |
|---|---------|---------------|---------|-------|----------|
| 1 | Ventas | `data/raw/json/ventascsv.json` | JSON | 5,000 | 18 |
| 2 | Clientes | `data/raw/json/clientes.json` | JSON | 1,500 | 17 |
| 3 | Sucursales | `data/raw/json/sucursales.json` | JSON | 10 | 24 |
| 4 | Inventarios | `data/raw/json/inventarios.json` | JSON | 2,000 | 23 |
| 5 | Canales Digitales | `data/raw/json/canales_digitales.json` | JSON | 1,200 | 20 |
| — | **TOTAL** | — | — | **9,710** | **102** |

> **Nota:** También existen copias en formato `.xlsx` en `data/raw/xlsx/`. El pipeline prioriza JSON > CSV > XLSX al cargar. La prioridad se define en `src/data/load.py` (función `load_raw_datasets`).

---

## 3. Flujo Completo de Limpieza (ETL)

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

## 4. Detalle por Dataset

---

### 4.1 Ventas (`ventascsv.json`)

**Registros:** 5,000 filas × 18 columnas  
**Filas duplicadas encontradas:** 0  
**Nulos encontrados:** 0 en todas las columnas

#### Renombrado de columnas (schema_map.yml → clean.py)

| Columna Original | Columna Limpia | Tipo Original | Tipo Limpio |
|-----------------|----------------|---------------|-------------|
| `Ticket_ID` | `ticket_id` | object | object |
| `Fecha` | `date` | object | **datetime64** |
| `Hora` | `time` | object | object (HH:MM) |
| `Dia_Semana` | `day_of_week` | object | object |
| `Mes` | `month` | object | object |
| `Sucursal_ID` | `branch_id` | object | object |
| `Sucursal_Nombre` | `branch_name` | object | object |
| `Ciudad` | `city` | object | object |
| `Platillo` | `dish` | object | object |
| `Categoria` | `category` | object | object |
| `Precio_Unitario` | `unit_price` | int64 | **float64** (vía `pd.to_numeric`) |
| `Cantidad` | `quantity` | int64 | **float64** (vía `pd.to_numeric`) |
| `Total_Venta` | `total_sale` | int64 | **float64** (vía `pd.to_numeric`) |
| `Costo_Ingredientes` | `ingredient_cost` | int64 | **float64** (vía `pd.to_numeric`) |
| `Margen_Bruto` | `gross_margin` | int64 | **float64** (vía `pd.to_numeric`) |
| `Metodo_Pago` | `payment_method` | object | object (`.str.strip()`) |
| `Propina` | `tip` | float64 | float64 |
| `Total_con_Propina` | `total_with_tip` | **object** | **float64** (vía `pd.to_numeric`) |

#### Problemas detectados y correcciones

| Problema | Columna | Detalle | Corrección aplicada |
|----------|---------|---------|---------------------|
| **Tipo incorrecto** | `Total_con_Propina` | 4 valores no numéricos de 5,000 (tipo `object` con comas) | `_to_numeric()`: elimina comas y `$`, convierte con `pd.to_numeric(errors="coerce")` → los 4 valores no parseables quedan como `NaN` |
| **Tipo incorrecto** | `Fecha` | Almacenada como string `"2025-01-15"` | `pd.to_datetime(errors="coerce")` |
| **Tipo incorrecto** | `Hora` | Almacenada como string `"13:45:00"` | Se trunca a `HH:MM` y se extrae `hour` como entero |
| **Sin columna derivada** | — | No había columna de franja horaria | Se crea `daypart` con regla: 6-11→Mañana, 12-16→Comida, 17-20→Tarde, otro→Noche |
| **Sin columna derivada** | — | No había columna año-mes | Se crea `year_month` desde `date` con `dt.to_period("M")` |
| **Fallback imputación** | `total_sale` | Si hay NaN, se imputa como `unit_price × quantity` | `fillna(unit_price * quantity)` |
| **Fallback imputación** | `ingredient_cost` | Si hay NaN, se imputa con el promedio de la categoría; si aún queda NaN, se usa 35% de `total_sale` | `groupby("category").transform("mean")` luego `fillna(total_sale * 0.35)` |
| **Columna derivada** | `gross_margin` | Si no existe, se crea como `total_sale - ingredient_cost` | Calculada automáticamente |

---

### 4.2 Clientes (`clientes.json`)

**Registros:** 1,500 filas × 17 columnas  
**Filas duplicadas encontradas:** 0  
**Nulos encontrados:** 0 (pero hay problemas de tipo)

#### Renombrado de columnas

| Columna Original | Columna Limpia | Tipo Original | Tipo Limpio |
|-----------------|----------------|---------------|-------------|
| `Cliente_ID` | `customer_id` | object | object |
| `Nombre` | `name` | object | object |
| `Fecha_Registro` | `register_date` | object | **datetime64** |
| `Miembro_Lealtad` | `loyalty_member` | object (`"Sí"/"No"`) | **bool** |
| `Categoria_Cliente` | `customer_category` | object | object |
| `Sucursal_Preferida` | `preferred_branch` | object | object |
| `Ciudad_Preferida` | `preferred_city` | object | object |
| `Visitas_Ultimo_Año` | `visits_last_year` | int64 | float64 |
| `Gasto_Promedio` | `avg_spend` | float64 | float64 |
| `Gasto_Total_Estimado` | `estimated_total_spend` | **object** | **float64** |
| `Puntos_Lealtad` | `loyalty_points` | **object** | **float64** |
| `Ultima_Visita` | `last_visit` | object | **datetime64** |
| `Calificacion_Satisfaccion` | `satisfaction_score` | int64 | float64 |
| `NPS_Score` | `nps_score` | int64 | float64 |
| `Comentario_Encuesta` | `survey_comment` | object | object |
| `Canal_Adquisicion` | `acquisition_channel` | object | object |
| `Acepta_Promociones` | `accepts_promotions` | object (`"Sí"/"No"`) | **bool** |

#### Problemas detectados y correcciones

| Problema | Columna | Detalle | Corrección aplicada |
|----------|---------|---------|---------------------|
| **Formato con comas** | `Gasto_Total_Estimado` | 1,077 de 1,500 valores son strings con comas, ej. `"5,668.20"` | `_to_numeric()`: remueve comas/`$`/espacios → `pd.to_numeric(errors="coerce")` |
| **Formato con comas** | `Puntos_Lealtad` | 1 valor tiene formato `"1,185.00"` (tipo mixto int/string) | `_to_numeric()`: misma función de limpieza numérica |
| **Booleano como texto** | `Miembro_Lealtad` | Valores `"Sí"` y `"No"` como string | `_to_boolean()`: normaliza con Unicode → mapea a `True/False` |
| **Booleano como texto** | `Acepta_Promociones` | Valores `"Sí"` y `"No"` como string | `_to_boolean()`: misma función |
| **Fecha como string** | `Fecha_Registro` | String como `"2023-03-15"` | `pd.to_datetime(errors="coerce")` |
| **Fecha como string** | `Ultima_Visita` | String como `"2025-11-20"` | `pd.to_datetime(errors="coerce")` |
| **Imputación derivada** | `estimated_total_spend` | Si queda NaN después de conversión | `fillna(avg_spend × visits_last_year)` |

> **Categorías de cliente encontradas:** `VIP`, `Regular`, `Ocasional`, `Frecuente`

---

### 4.3 Sucursales (`sucursales.json`)

**Registros:** 10 filas × 24 columnas  
**Filas duplicadas encontradas:** 0  
**Nulos encontrados:** 0

#### Renombrado de columnas

| Columna Original | Columna Limpia | Tipo Original | Tipo Limpio |
|-----------------|----------------|---------------|-------------|
| `Sucursal_ID` | `branch_id` | object | string |
| `Nombre_Sucursal` | `branch_name` | object | string |
| `Ciudad` | `city` | object | string |
| `Direccion` | `address` | object | string |
| `Codigo_Postal` | `postal_code` | object | string |
| `Zona` | `zone` | object | string |
| `Nivel_Socioeconomico` | `socioeconomic_level` | object | string |
| `Capacidad_Personas` | `capacity_people` | int64 | float64 |
| `Numero_Empleados` | `num_employees` | int64 | float64 |
| `Horario_Apertura` | `open_time` | object | string |
| `Horario_Cierre` | `close_time` | object | string |
| `Horarios_Pico` | `peak_hours` | object | string |
| `Renta_Mensual` | `rent_monthly` | **object** (`"85,000.00"`) | **float64** |
| `Servicios_Mensual` | `utilities_monthly` | **object** (`"15,000.00"`) | **float64** |
| `Nomina_Mensual` | `payroll_monthly` | **object** (`"180,000.00"`) | **float64** |
| `Costos_Operativos_Total` | `operational_cost_total` | **object** (`"280,000.00"`) | **float64** |
| `Ingresos_Promedio_Mensual` | `avg_monthly_income` | **object** (`"450,000.00"`) | **float64** |
| `Margen_Operativo` | `operating_margin` | **object** (`"170,000.00"`) | **float64** |
| `Rentabilidad_Porcentaje` | `profitability_pct` | float64 | float64 |
| `Cercania_Puntos_Interes` | `nearby_poi` | object | string |
| `Competencia_Cercana` | `nearby_competitors` | int64 | float64 |
| `Estacionamiento` | `parking` | object | string |
| `Año_Apertura` | `opening_year` | **object** (`"2,018.00"`) | **float64** |
| `Años_Operacion` | `years_operating` | int64 | float64 |

#### Problemas detectados y correcciones

| Problema | Columna(s) | Detalle | Corrección aplicada |
|----------|-----------|---------|---------------------|
| **7 columnas monetarias como string** | `Renta_Mensual`, `Servicios_Mensual`, `Nomina_Mensual`, `Costos_Operativos_Total`, `Ingresos_Promedio_Mensual`, `Margen_Operativo` | Almacenadas como `"85,000.00"` con comas como separador de miles | `_to_numeric()`: remueve comas → `pd.to_numeric(errors="coerce")` |
| **Año como string con comas** | `Año_Apertura` | Almacenado como `"2,018.00"` (¡2018 con coma de miles!) | `_to_numeric()`: remueve la coma → convierte a 2018.0 |
| **Tipo mixto texto/int** | `Codigo_Postal` | Algunos valores son string `"06600"`, otros int `44160` | `_to_string()` → fuerza todo a tipo `string` para evitar errores en Parquet |
| **Conversión explícita a string** | 12 columnas de texto | Para evitar mezcla `int/str` que rompe serialización Parquet | `_to_string()` con `.astype("string")` en cada una |

---

### 4.4 Inventarios (`inventarios.json`)

**Registros:** 2,000 filas × 23 columnas  
**Filas duplicadas encontradas:** 0  
**Nulos encontrados:** 0 (pero hay formatos incorrectos)

#### Renombrado de columnas

| Columna Original | Columna Limpia | Tipo Original | Tipo Limpio |
|-----------------|----------------|---------------|-------------|
| `Registro_ID` | `record_id` | object | object |
| `Fecha` | `date` | object | **datetime64** |
| `Mes` | `month` | object | object |
| `Sucursal_ID` | `branch_id` | object | object |
| `Sucursal_Nombre` | `branch_name` | object | object |
| `Ciudad` | `city` | object | object |
| `Ingrediente` | `ingredient` | object | object |
| `Categoria_Ingrediente` | `ingredient_category` | object | object |
| `Unidad` | `unit` | object | object |
| `Proveedor` | `supplier` | object | object |
| `Cantidad_Pedida` | `qty_ordered` | int64 | float64 |
| `Precio_Unitario` | `unit_price` | float64 | float64 |
| `Costo_Total_Compra` | `total_purchase_cost` | **object** | **float64** |
| `Cantidad_Desperdiciada` | `qty_wasted` | float64 | float64 |
| `Costo_Desperdicio` | `waste_cost` | **object** | **float64** |
| `Porcentaje_Desperdicio` | `waste_pct` | float64 | float64 |
| `Motivo_Desperdicio` | `waste_reason` | object | object |
| `Stock_Actual` | `current_stock` | float64 | float64 |
| `Stock_Minimo` | `min_stock` | float64 | float64 |
| `Estado_Stock` | `stock_status` | object | object |
| `Necesita_Reorden` | `needs_reorder` | object (`"Sí"/"No"`) | **bool** |
| `Frecuencia_Reabastecimiento` | `reorder_frequency` | object | object |
| `Vida_Util_Dias` | `shelf_life_days` | int64 | float64 |

#### Problemas detectados y correcciones

| Problema | Columna | Detalle | Corrección aplicada |
|----------|---------|---------|---------------------|
| **Formato con comas** | `Costo_Total_Compra` | 1,304 de 2,000 valores son strings con comas, ej. `"1,234.56"` | `_to_numeric()`: remueve comas → `pd.to_numeric(errors="coerce")` |
| **Formato con comas** | `Costo_Desperdicio` | 122 de 2,000 valores son strings con comas | `_to_numeric()`: misma función |
| **Booleano como texto** | `Necesita_Reorden` | Valores `"Sí"/"No"` como string | `_to_boolean()`: normaliza Unicode → mapea a `True/False` |
| **Fecha como string** | `Fecha` | String como `"2025-06-15"` | `pd.to_datetime(errors="coerce")` |
| **Valores negativos** | `waste_pct` | Posibles valores negativos por error de captura | `clip(lower=0)`: fuerza mínimo a 0 |
| **Columna derivada** | `year_month` | No existía en los datos crudos | Creada desde `date` con `dt.to_period("M")` |

---

### 4.5 Canales Digitales (`canales_digitales.json`)

**Registros:** 1,200 filas × 20 columnas  
**Filas duplicadas encontradas:** 0  
**Nulos reales:** 0 (pero **1,845 strings vacíos ocultos** tratados como presentes)

#### Renombrado de columnas

| Columna Original | Columna Limpia | Tipo Original | Tipo Limpio |
|-----------------|----------------|---------------|-------------|
| `Registro_ID` | `record_id` | object | object |
| `Fecha` | `date` | object | **datetime64** |
| `Mes` | `month` | object | object |
| `Dia_Semana` | `day_of_week` | object | object |
| `Sucursal_ID` | `branch_id` | object | object |
| `Sucursal_Nombre` | `branch_name` | object | object |
| `Ciudad` | `city` | object | object |
| `Plataforma` | `platform` | object | object |
| `Tipo_Interaccion` | `interaction_type` | object | object |
| `Contenido` | `content` | object | object |
| `Sentimiento` | `sentiment` | object | object (`.str.lower()`) |
| `Calificacion` | `rating` | **object** | **float64** |
| `Alcance` | `reach` | **object** (`"2,857.00"`) | **float64** |
| `Engagement` | `engagement` | **object** | **float64** |
| `Tasa_Engagement` | `engagement_rate` | float64 | float64 |
| `Campaña_Asociada` | `campaign` | object | object |
| `Costo_Campaña` | `campaign_cost` | float64 | float64 |
| `Respondido` | `responded` | object (`"Sí"/"No"`) | **bool** |
| `Tiempo_Respuesta_Horas` | `response_hours` | **object** | **float64** |
| `Conversion` | `conversion` | **object** (`"Sí"/"No"`) | **bool** |

#### Problemas detectados y correcciones

| Problema | Columna | Detalle | Corrección aplicada |
|----------|---------|---------|---------------------|
| **738 strings vacíos** | `Calificacion` | 738 de 1,200 registros son `""` (no hay calificación cuando no aplica) | Paso 1: `""` → `NaN` (regex `\s*`). Paso 2: `_to_numeric()` → `float64` con NaN donde no hay dato |
| **1,107 strings vacíos** | `Tiempo_Respuesta_Horas` | 1,107 de 1,200 son `""` (solo 93 tienen valor real, ej. `8`) | `""` → `NaN` → `_to_numeric()`. La media por sucursal se calcula solo con los 93 valores reales |
| **Formato con comas** | `Alcance` | String con comas como `"2,857.00"` | `_to_numeric()`: remueve comas → float |
| **Numérico como texto** | `Engagement` | Almacenado como string `"258"` | `_to_numeric()` |
| **Booleano como texto** | `Respondido` | `"Sí"/"No"` como string | `_to_boolean()` |
| **Booleano como texto** | `Conversion` | `"Sí"/"No"` como string | `_to_boolean()` |
| **Sentimiento sin normalizar** | `Sentimiento` | Posibles variaciones de mayúsculas/espacios | `.str.strip().str.lower()` → valores consistentes: `positivo`, `neutro`, `negativo` |
| **Columna derivada** | `year_month` | No existía | Creada desde `date` |

> **Dato clave:** De 1,200 registros de interacciones digitales, solo **93 tienen un valor real** en `Tiempo_Respuesta_Horas` (7.75%). Esto es porque el campo solo aplica cuando `Respondido = Sí`. Los 1,107 vacíos no son "datos faltantes" sino "no aplica". Pandas los ignora al calcular `.mean()`, por lo que los promedios por sucursal son válidos.

---

## 5. Operaciones Transversales (Aplican a Todos los Datasets)

### 5.1 Normalización de nombres de columnas

Todas las columnas pasan por `_normalize_token()` que:
1. Aplica **normalización Unicode NFKD** (quita acentos: `é → e`, `ñ → n`, `í → i`)
2. Convierte a **minúsculas**
3. Reemplaza caracteres no alfanuméricos por `_` (guion bajo)
4. Elimina guiones bajos al inicio y final

Ejemplo: `"Categoría_Ingrediente"` → `"categoria_ingrediente"` → (renombra por schema_map) → `"ingredient_category"`

### 5.2 Strings vacíos → NaN

Para todas las columnas de tipo `object` y `string`:
```python
blank_mask = series_str.str.fullmatch(r"\s*", na=False)
clean_df[col] = series_str.mask(blank_mask, pd.NA)
```
Esto convierte cualquier string que sea solo espacios en blanco o vacío (`""`, `" "`, `"   "`) a `NaN`/`pd.NA`, permitiendo un manejo consistente de valores faltantes.

### 5.3 Conversión numérica (`_to_numeric`)

Función reutilizable que limpia valores monetarios:
```python
cleaned = series.str.replace(",", "")      # "85,000.00" → "85000.00"
                  .str.replace("$", "")     # "$450" → "450"
                  .str.replace(" ", "")      # " 100 " → "100"
pd.to_numeric(cleaned, errors="coerce")     # No numéricos → NaN
```

### 5.4 Conversión booleana (`_to_boolean`)

Mapea texto a booleano verdadero:
- **Verdadero:** `si`, `sí`, `yes`, `true`, `1`, `y`
- **Falso:** `no`, `false`, `0`, `n`
- **Otro:** → `NaN`

La función normaliza acentos antes de comparar, así `"Sí"` y `"si"` ambos → `True`.

### 5.5 Eliminación de duplicados

Al final del proceso de limpieza de cada dataset:
```python
clean_df = clean_df.drop_duplicates()
```
**Resultado:** No se encontraron filas duplicadas en ningún dataset (0 eliminadas en los 5 datasets).

---

## 6. Fase de Validación

Después de la limpieza, `src/data/validate.py` verifica:

### Columnas requeridas por dataset

| Dataset | Columnas Requeridas | ¿Todas presentes? |
|---------|--------------------|--------------------|
| Ventas | `ticket_id`, `date`, `branch_id`, `dish`, `quantity`, `total_sale` | ✅ Sí |
| Clientes | `customer_id`, `register_date`, `visits_last_year`, `avg_spend` | ✅ Sí |
| Sucursales | `branch_id`, `branch_name`, `city`, `operational_cost_total` | ✅ Sí |
| Inventarios | `record_id`, `date`, `branch_id`, `ingredient`, `qty_ordered`, `total_purchase_cost` | ✅ Sí |
| Digital | `record_id`, `date`, `branch_id`, `platform`, `sentiment` | ✅ Sí |

### Métricas de calidad post-limpieza

| Dataset | Filas | Duplicados | Nulos en cols requeridas |
|---------|-------|------------|--------------------------|
| Ventas | 5,000 | 0 | 0% en todas |
| Clientes | 1,500 | 0 | 0% en todas |
| Sucursales | 10 | 0 | 0% en todas |
| Inventarios | 2,000 | 0 | 0% en todas |
| Digital | 1,200 | 0 | 0% en todas |

---

## 7. Ingeniería de Features (Post-Limpieza)

Después de la limpieza, `src/features/build_features.py` genera tablas derivadas:

### 7.1 Tabla Analítica `analytics_branch_day_hour`

Se agrupa el dataset de ventas por `branch_id × date × hour × daypart` y se calculan:

| Feature Generada | Fórmula |
|-------------------|---------|
| `tickets` | Conteo de `ticket_id` únicos |
| `total_quantity` | Suma de `quantity` |
| `revenue` | Suma de `total_sale` |
| `ingredient_cost` | Suma de `ingredient_cost` |
| `gross_margin` | Suma de `gross_margin` |
| `tips` | Suma de `tip` |
| `avg_ticket` | `revenue / tickets` (NaN si tickets = 0) |

### 7.2 Features RFM (para segmentación)

| Feature | Cálculo |
|---------|---------|
| `recency_days` | Días desde la última visita hasta la fecha de referencia; NaN → imputado con la mediana |
| `frequency` | `visits_last_year` (ya numérica tras limpieza) |
| `monetary` | `estimated_total_spend`; si NaN → `avg_spend × frequency` |

### 7.3 Score de Sentimiento

| Sentimiento original | Score numérico |
|---------------------|----------------|
| `"positivo"` | 1.0 |
| `"neutro"` | 0.0 |
| `"negativo"` | -1.0 |
| Otro/NaN | 0.0 (default) |

---

## 8. Resumen de Problemas Encontrados y Resueltos

| # | Tipo de Problema | Datasets Afectados | Cantidad de Valores | Método de Corrección |
|---|------------------|--------------------|--------------------|-----------------------|
| 1 | Columnas monetarias como string con comas | Sucursales (7 cols), Inventarios (2 cols), Clientes (2 cols), Digital (1 col), Ventas (1 col) | ~2,510 valores | `_to_numeric()`: strip `,` `$` ` ` → `pd.to_numeric` |
| 2 | Strings vacíos como nulos ocultos | Digital (2 cols: 738 + 1,107) | 1,845 valores | `str.fullmatch(r"\s*")` → `pd.NA` |
| 3 | Booleanos como texto (`"Sí"/"No"`) | Clientes (2 cols), Inventarios (1 col), Digital (2 cols) | 5 columnas completas | `_to_boolean()` con normalización Unicode |
| 4 | Fechas como string | Ventas (1 col), Clientes (2 cols), Inventarios (1 col), Digital (1 col) | 5 columnas completas | `pd.to_datetime(errors="coerce")` |
| 5 | Nombres de columnas en español con acentos | Todos | 102 columnas | `_normalize_token()` + `schema_map.yml` |
| 6 | Tipo mixto int/string | Sucursales (`Codigo_Postal`), Clientes (`Puntos_Lealtad`) | ~10 + ~1 valores | `_to_string()` o `_to_numeric()` según caso |
| 7 | Año con separador de miles | Sucursales (`Año_Apertura`: `"2,018.00"`) | 10 valores | `_to_numeric()` (remueve coma) |
| 8 | Valores negativos potenciales | Inventarios (`waste_pct`) | Preventivo | `clip(lower=0)` |

---

## 9. Archivos de Configuración Utilizados

| Archivo | Propósito |
|---------|-----------|
| `config/schema_map.yml` | Define los nombres canónicos de columnas y sus alias (para renombrado). Define columnas requeridas por dataset. |
| `config/settings.yml` | Rutas de archivos, parámetros del pipeline (seed, horizonte, top ingredientes), valores default |
| `config/recipe_map.yml` | Mapeo de recetas y categorías para análisis |

---

## 10. Código Fuente Relevante

| Archivo | Función Principal | Líneas Clave |
|---------|-------------------|-------------|
| `src/data/load.py` | `load_raw_datasets()` | Carga JSON/CSV/XLSX con prioridad y detección de duplicados |
| `src/data/load.py` | `profile_raw_tables()` | Genera perfil de calidad inicial (% nulos, sample) |
| `src/data/clean.py` | `clean_dataset()` | Limpieza por tipo de dataset con reglas específicas |
| `src/data/clean.py` | `_to_numeric()` | Limpieza de valores monetarios (strip comas, $, espacios) |
| `src/data/clean.py` | `_to_boolean()` | Conversión Sí/No → True/False con normalización Unicode |
| `src/data/clean.py` | `_normalize_token()` | Normalización de nombres a snake_case sin acentos |
| `src/data/clean.py` | `_standardize_columns()` | Renombrado de columnas vía schema_map |
| `src/data/validate.py` | `validate_datasets()` | Validación de columnas requeridas y % nulos |
| `src/features/build_features.py` | `build_features()` | Genera tablas analíticas y features RFM |

---

## 11. Conclusiones

1. **No se perdieron registros:** Los 9,710 registros originales se conservaron íntegros. Ninguna fila fue eliminada por duplicación ni por datos inválidos.

2. **El principal problema fue el formato:** La mayoría de los issues no eran datos faltantes sino **formatos incorrectos** — especialmente valores monetarios almacenados como strings con comas (`"85,000.00"`) que impedían hacer cálculos matemáticos.

3. **Los strings vacíos eran nulos disfrazados:** En el dataset de Canales Digitales, 1,845 campos aparecían como `""` en lugar de `null`/`NaN`. Esto es importante porque un string vacío no es lo mismo que "sin dato" — Pandas los trata diferente al calcular promedios y conteos.

4. **La estandarización fue clave:** Renombrar 102 columnas del español con acentos a snake_case inglés canónico permitió que todo el pipeline posterior funcione de forma consistente, independientemente de si los datos vengan en JSON, CSV o Excel.

5. **Las imputaciones fueron conservadoras:** Solo se imputaron valores cuando existía una fórmula lógica clara (ej. `total_sale = price × qty`, `estimated_spend = avg × visits`). No se inventaron datos.
