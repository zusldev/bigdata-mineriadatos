# Informe Integral — Caso de Estudio: "Sabor Mexicano"

**Materia:** Big Data y Minería de Datos  
**Fecha:** 17 de febrero de 2026  
**Cadena analizada:** Sabor Mexicano — 10 sucursales en México  

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Análisis Exploratorio](#2-análisis-exploratorio)
   - 2.1 Tendencias de ventas
   - 2.2 Platillos más vendidos por región y hora del día
   - 2.3 Sucursales con mejor y peor desempeño
   - 2.4 Métodos de pago
3. [Identificación de Problemas](#3-identificación-de-problemas)
   - 3.1 Factores que influyen en la rentabilidad
   - 3.2 Ineficiencias en el manejo de inventarios
   - 3.3 Impacto en las ventas
4. [Predicción y Decisión](#4-predicción-y-decisión)
   - 4.1 Meses con mayor necesidad de insumos
   - 4.2 Estrategias para aumentar ventas
   - 4.3 Estrategias para optimizar inventario
5. [Propuestas de Solución](#5-propuestas-de-solución)
   - 5.1 Segmentación de clientes por patrones de consumo
   - 5.2 Campañas de marketing dirigidas por sucursal
   - 5.3 Plan para reducir el desperdicio de alimentos
6. [Preguntas Adicionales del Caso de Estudio](#6-preguntas-adicionales)
   - 6.1 Comportamiento del cliente según ubicación y horarios
   - 6.2 Platillos que deben promocionarse más en cada sucursal
   - 6.3 Ajuste de niveles de inventario
   - 6.4 Cambios operativos para mejorar la experiencia del cliente
7. [Conclusión y Pasos Accionables](#7-conclusión-y-pasos-accionables)
8. [Anexo de Gráficas y Visualizaciones](#8-anexo-de-gráficas)

---

## 1. Resumen Ejecutivo

Se analizaron **5 conjuntos de datos** (5,000 transacciones de ventas, 1,500 registros de clientes, 10 sucursales, 2,000 registros de inventario y 1,200 interacciones digitales) para responder preguntas clave de negocio de la cadena "Sabor Mexicano".

**Hallazgos principales:**

| Indicador | Resultado |
|-----------|-----------|
| Sucursal líder en ingresos | **Cancún** — $118,067 MXN |
| Sucursal con mejor eficiencia operativa | **León** — menor costo operativo ($143,500/mes), mejor utilidad proxy |
| Sucursal con mayor oportunidad de mejora | **Cancún** — peor utilidad proxy (-$4,501,497) pese a mayores ingresos |
| Platillo estrella | **Mole Poblano** — $134,575 en ingresos, vendido en las 10 sucursales |
| Hora pico de ventas | **13:00 hrs** (lunes a viernes), segundo pico a las 19:00–20:00 hrs |
| Principal driver de merma | **Carne de Res en Mérida** — $10,470 por caducidad |
| Segmento más grande de clientes | **Ocasionales Sensibles a Promoción** — 1,180 clientes (78.7%) |
| Mes pico pronosticado | **Julio 2026** — mayor demanda de Tequila, Frijoles, Carne de Cerdo |
| Canal digital más efectivo | **TikTok** — 6–12× engagement por peso invertido |

---

## 2. Análisis Exploratorio

### 2.1 Tendencias de ventas

El análisis de las ventas diarias y mensuales revela patrones claros de estacionalidad y comportamiento semanal.

**Visualizaciones:** `outputs/charts/sales_trend_daily.html` · `outputs/charts/sales_trend_monthly.html`

**Hallazgos clave:**

- **Hora pico dominante: 13:00 hrs.** El mayor ingreso ocurre consistentemente a la 1 PM de lunes a viernes, con el lunes liderando con **$35,914** a las 13 hrs.
- **Segundo pico vespertino: 19:00–20:00 hrs**, orientado a cenas, con el sábado 20 hrs alcanzando **$23,364**.
- **Días más fuertes:** Lunes y martes concentran el mayor volumen de ventas. El domingo es el día más débil.
- **Horas de menor actividad:** 11:00 hrs (apertura) y 22:00 hrs (cierre) muestran los menores ingresos.

| Día | Hora Pico | Ingreso en pico |
|-----|-----------|-----------------|
| Lunes | 13:00 | $35,914 |
| Martes | 13:00 | $32,308 |
| Viernes | 13:00 | $31,320 |
| Jueves | 13:00 | $31,157 |
| Sábado | 20:00 | $23,364 |

**Visualización:** `outputs/charts/sales_by_hour_day.html` — Mapa de calor de ingresos por hora y día de la semana.

**Interpretación:** La concentración de ventas en la hora de comida (13:00–14:00) indica que la operación debe estar optimizada para atender la demanda máxima en ese horario. El pico de sábado en la noche sugiere oportunidad de expandir la oferta nocturna en fines de semana.

---

### 2.2 Platillos más vendidos por región y hora del día

**Visualización:** `outputs/charts/top_dishes_by_region_daypart.html` · `outputs/charts/pareto_dishes.html` (nuevo)

**Top 5 platillos a nivel cadena por ingresos:**

| # | Platillo | Categoría | Ingresos | Unidades |
|---|----------|-----------|----------|----------|
| 1 | **Mole Poblano** | Platos Fuertes | **$134,575** | 769 |
| 2 | **Enchiladas Verdes** | Platos Fuertes | $96,660 | 716 |
| 3 | **Margarita** | Bebidas | $67,925 | 715 |
| 4 | **Tacos al Pastor** | Platos Fuertes | $60,775 | 715 |
| 5 | **Guacamole con Totopos** | Entradas | $58,473 | 657 |

**Análisis Pareto (regla 80/20):** Los 5 platillos anteriores representan aproximadamente el **48% del ingreso total**, lo que evidencia una alta concentración. Los primeros 10 platillos acumulan más del 70% del ingreso.

**Platillos líderes por ciudad durante la franja Comida (13:00–15:00):**

| Ciudad | Platillo #1 (ingresos) | Platillo #1 (unidades) |
|--------|----------------------|----------------------|
| Cancún | Mole Poblano ($12,075 / 69 uds) | Tacos al Pastor (75 uds) |
| CDMX Centro | Mole Poblano ($9,275 / 53 uds) | Tacos al Pastor (53 uds) |
| Monterrey | Mole Poblano ($11,025 / 63 uds) | Guacamole con Totopos (73 uds) |
| Guadalajara | Enchiladas Verdes ($9,045 / 67 uds) | Enchiladas Verdes (67 uds) |
| Querétaro | Enchiladas Verdes ($7,560 / 56 uds) | Enchiladas Verdes (56 uds) |
| Puebla | Mole Poblano ($7,350 / 42 uds) | Mole Poblano (42 uds) |
| Mérida | Mole Poblano ($6,825 / 39 uds) | Enchiladas Verdes (45 uds) |
| León | Enchiladas Verdes ($5,670 / 42 uds) | Enchiladas Verdes (42 uds) |
| Tijuana | Enchiladas Verdes ($6,075 / 45 uds) | Tacos al Pastor (47 uds) |

**Interpretación:** Mole Poblano y Enchiladas Verdes dominan el menú en todas las regiones. Las preferencias varían regionalmente: en el norte (Monterrey), Guacamole con Totopos destaca en volumen; en zonas turísticas (Cancún), Tacos al Pastor lidera en cantidad vendida; en el centro-occidente (Guadalajara, Querétaro, León), Enchiladas Verdes es el favorito indiscutible.

---

### 2.3 Sucursales con mejor y peor desempeño

**Visualización:** `outputs/charts/branch_ranking_sales_margin.html` · `outputs/charts/branch_revenue_ranking.png` (nuevo) · `outputs/charts/radar_branches.html` (nuevo)

**Ranking completo por ingresos:**

| Posición | Sucursal | Ciudad | Ingresos | Margen Bruto | Tickets | Ticket Promedio |
|----------|----------|--------|----------|--------------|---------|-----------------|
| 1 | **Cancún** | Cancún | **$118,067** | $82,503 | 650 | $181.64 |
| 2 | CDMX Centro | Ciudad de México | $108,934 | $76,365 | 629 | $173.19 |
| 3 | Monterrey | Monterrey | $101,214 | $70,907 | 570 | $177.57 |
| 4 | Guadalajara | Guadalajara | $93,049 | $65,367 | 542 | $171.68 |
| 5 | Querétaro | Querétaro | $85,947 | $60,197 | 483 | $177.94 |
| 6 | CDMX Sur | Ciudad de México | $83,567 | $58,656 | 527 | $158.57 |
| 7 | León | León | $71,777 | $50,230 | 386 | **$185.95** |
| 8 | Tijuana | Tijuana | $71,327 | $49,873 | 405 | $176.12 |
| 9 | Mérida | Mérida | $70,821 | $49,660 | 405 | $174.87 |
| 10 | **Puebla** | Puebla | **$66,585** | $46,529 | 403 | **$165.22** |

**Hallazgos clave:**

- **Cancún** lidera en ingresos ($118,067), margen bruto ($82,503) y número de tickets (650), impulsada por su ubicación turística, capacidad mayor (150 personas) y economía de alto nivel socioeconómico.
- **Puebla** es la sucursal con menores ingresos ($66,585) y el ticket promedio más bajo ($165.22), con capacidad limitada (80 personas), sin estacionamiento y 7 competidores cercanos.
- **León** tiene el ticket promedio más alto ($185.95) pese a ser la sucursal más pequeña (75 personas, 17 empleados), lo cual indica un servicio premium o una clientela con mayor poder adquisitivo por ticket.

**Gráfica radar multi-dimensión** (`outputs/charts/radar_branches.html`): Esta visualización muestra que no existe una sucursal perfecta en todas las dimensiones. Cancún sobresale en ingresos pero tiene el peor rendimiento en desperdicio relativo. León equilibra eficiencia operativa con buen sentimiento digital.

---

### 2.4 Métodos de pago

**Visualización:** `outputs/charts/payment_method_mix.html`

| Método | Ingresos | Participación |
|--------|----------|---------------|
| Tarjeta de Crédito | $350,263 | **40.2%** |
| Tarjeta de Débito | $227,291 | 26.1% |
| Efectivo | $190,870 | 21.9% |
| App de Pago | $102,864 | **11.8%** |

**Interpretación:** La dominancia de tarjeta de crédito (40.2%) sugiere una clientela de nivel socioeconómico medio-alto. Las apps de pago (11.8%) representan un canal en crecimiento que facilita la integración con programas de lealtad digitales.

---

## 3. Identificación de Problemas

### 3.1 Factores que influyen en la rentabilidad

**Visualización:** `outputs/charts/waterfall_cancún.png` · `outputs/charts/waterfall_león.png` · `outputs/charts/cost_structure_branches.html` (nuevos)

La utilidad proxy se calculó como: **Ingreso − Costo de ingredientes − Costo operativo asignado por ticket**.

**Hallazgo crítico: La sucursal con más ingresos tiene la peor rentabilidad.**

| Sucursal | Utilidad Proxy | Costo Operativo/mes | Empleados | Renta/mes | Competidores |
|----------|---------------|---------------------|-----------|-----------|-------------|
| **León** (mejor) | -$1,671,770 | **$143,500** | 17 | $32,000 | 5 |
| Puebla | -$1,777,471 | $152,000 | 18 | $35,000 | 7 |
| Mérida | -$1,882,340 | $161,000 | 19 | $38,000 | 4 |
| Querétaro | -$2,183,803 | $187,000 | 20 | $48,000 | 3 |
| Tijuana | -$2,326,127 | $198,000 | 20 | $52,000 | 6 |
| Guadalajara | -$2,454,633 | $210,000 | 23 | $55,000 | 5 |
| CDMX Sur | -$2,809,344 | $239,000 | 22 | $72,000 | 4 |
| CDMX Centro | -$3,283,635 | $280,000 | 25 | $85,000 | 3 |
| Monterrey | -$3,373,093 | $287,000 | 28 | $78,000 | 2 |
| **Cancún** (peor) | **-$4,501,497** | **$382,000** | 32 | $120,000 | 8 |

**Nota metodológica:** Las utilidades proxy son negativas porque el costo operativo total mensual se prorratea entre los tickets de cada sucursal, incluyendo renta, nómina y servicios fijos. Esto no significa pérdida real, sino que refleja la carga de costos fijos que cada ticket debe absorber. El valor proxy es útil para **comparar eficiencia relativa** entre sucursales.

**Análisis de cascada (waterfall) — Contraste Cancún vs León:**

**Cancún:**
- Ingresos: $118,067 → Costo ingredientes: -$35,564 → **Costo operativo asignado: -$4,584,000** → Utilidad proxy: -$4,501,497
- El costo operativo mensual de $382,000 con 650 tickets genera una carga insostenible de ~$588 por ticket en costos fijos.

**León:**
- Ingresos: $71,777 → Costo ingredientes: -$21,547 → **Costo operativo asignado: -$1,721,997** → Utilidad proxy: -$1,671,770
- Con $143,500/mes y 386 tickets, la carga es de ~$372 por ticket — **37% menor que Cancún**.

**Factores clave que afectan la rentabilidad:**

1. **Costo operativo desproporcionado:** Cancún paga $382,000/mes (renta $120K, nómina $240K, servicios $22K) para generar $118,067 en el período analizado.
2. **Competencia:** Cancún tiene 8 competidores cercanos, la mayor presión competitiva.
3. **Categoría dominante:** Los Platos Fuertes generan 55-65% de los ingresos con mayor costo de ingredientes (~31% del ingreso).
4. **Platillos de alto volumen vs. margen:** Mole Poblano genera el mayor ingreso pero también el mayor costo de ingredientes; Refresco y Tacos de Carnitas tienen el mejor margen relativo.

---

### 3.2 Ineficiencias en el manejo de inventarios

**Visualización:** `outputs/charts/inventory_waste_shortage_heatmap.html` · `outputs/charts/waste_cost_by_branch.png` (nuevo)

**Costo de merma por sucursal:**

| Sucursal | Costo Merma | Tasa Quiebre | Costo Compra | Merma / Compra |
|----------|-------------|-------------|-------------|----------------|
| **Puebla** (peor merma) | **$91,963** | 7.1% | $498,818 | **18.4%** |
| **Mérida** | **$85,285** | 8.5% | $490,295 | **17.4%** |
| León | $75,801 | **4.4%** (mejor) | $415,363 | 18.2% |
| CDMX Sur | $64,388 | 6.1% | $547,527 | 11.8% |
| Cancún | $63,998 | 6.5% | $443,847 | 14.4% |
| Tijuana | $57,080 | 8.6% | $426,200 | 13.4% |
| Querétaro | $53,604 | 8.2% | $499,296 | 10.7% |
| CDMX Centro | $50,690 | 8.3% | $542,329 | 9.3% |
| **Monterrey** | $43,645 | **9.5%** (peor quiebre) | $646,276 | 6.8% |
| **Guadalajara** (mejor merma) | **$41,095** | 8.9% | $482,277 | 8.5% |

**Top 5 drivers de merma por costo:**

| # | Sucursal | Ingrediente | Razón de merma | Costo | Ratio merma |
|---|----------|------------|----------------|-------|-------------|
| 1 | **Mérida** | Carne de Res | **Caducidad** | **$10,470** | 25% |
| 2 | CDMX Sur | Tequila | Caducidad | $7,813 | — |
| 3 | Puebla | Cerveza | **Daño almacenamiento** | $7,497 | — |
| 4 | Puebla | Carne de Res | Error de preparación | $6,678 | — |
| 5 | Puebla | Tequila | **Exceso de pedido** | $6,355 | — |

**Principales razones de desperdicio:**
- **Caducidad (expiración):** El problema más costoso, especialmente en proteínas (Carne de Res) y bebidas alcohólicas (Tequila).
- **Daño en almacenamiento:** Indica condiciones inadecuadas de refrigeración o manejo.
- **Exceso de pedido:** Desalineación entre compras y demanda real.
- **Error de preparación:** Merma en cocina (mayor en Puebla).

**Ingredientes más problemáticos:** Carne de Res, Tequila, Cerveza, Carne de Cerdo, Aguacate.

---

### 3.3 Impacto en las ventas

Las ineficiencias de inventario impactan directamente las ventas por quiebres de stock (faltantes):

**Top quiebres de inventario (tasa de faltantes):**

| Sucursal | Ingrediente | Tasa Quiebre |
|----------|------------|-------------|
| CDMX Centro | Salsa Verde | **50%** |
| Cancún | Cebolla | **50%** |
| Guadalajara | Pollo | **43%** |
| Monterrey | Salsa Roja | **40%** |
| Puebla | Tequila | **33%** |

**Impacto:** Cuando faltan ingredientes clave como Salsa Verde (50% del tiempo en CDMX Centro) o Cebolla (50% en Cancún), los platillos más vendidos no pueden prepararse, generando ventas perdidas y deterioro de la experiencia del cliente. Un quiebre de Salsa Verde impacta directamente las Enchiladas Verdes — el segundo platillo más vendido de la cadena.

---

## 4. Predicción y Decisión

### 4.1 Meses con mayor necesidad de insumos por sucursal

**Metodología:** Se utilizó **Suavizamiento Exponencial Holt-Winters** (tendencia aditiva, sin estacionalidad) sobre los 12 ingredientes de mayor impacto económico por sucursal, con un horizonte de pronóstico de 6 meses (febrero–julio 2026).

**Visualización:** `outputs/charts/forecast_peaks_top15.png` (nuevo)

**Top 15 picos de demanda pronosticados:**

| Sucursal | Ingrediente | Mes Pico | Cantidad Pronosticada |
|----------|------------|----------|----------------------|
| **Puebla** | **Carne de Res** | **Marzo 2026** | **394.56 uds** |
| Monterrey | Tequila | Julio 2026 | 376.73 uds |
| Querétaro | Frijoles | Abril 2026 | 259.00 uds |
| León | Cilantro | Junio 2026 | 258.33 uds |
| Querétaro | Tequila | Mayo 2026 | 178.77 uds |
| Tijuana | Tequila | Julio 2026 | 167.59 uds |
| CDMX Sur | Frijoles | Julio 2026 | 145.83 uds |
| Tijuana | Frijoles | Julio 2026 | 113.40 uds |
| Guadalajara | Queso Fresco | Abril 2026 | 107.39 uds |
| Tijuana | Queso Fresco | Mayo 2026 | 103.43 uds |
| CDMX Sur | Limón | Junio 2026 | 98.21 uds |
| Monterrey | Cilantro | Julio 2026 | 97.37 uds |
| Monterrey | Queso Fresco | Julio 2026 | 95.99 uds |
| Cancún | Tequila | Julio 2026 | 90.22 uds |
| Monterrey | Refrescos | Abril 2026 | 86.67 uds |

**Patrón estacional identificado:**
- **Julio 2026** es el mes pico más frecuente (aparece en 60%+ de los pronósticos), coincidiendo con temporada vacacional de verano.
- **Ingredientes con mayor demanda estacional:** Tequila (sube en verano por bebidas frías), Frijoles (base de muchos platillos), Carne de Res (demanda sostenida).
- **Alerta temprana:** Puebla necesita 394.56 unidades de Carne de Res en marzo 2026 — el mayor pico individual — requiriendo preparación de proveedores desde febrero.

---

### 4.2 Estrategias para aumentar ventas

Basadas en el análisis exploratorio, la segmentación de clientes y los patrones de demanda:

**Estrategia 1: Maximizar la hora pico (13:00–14:00)**
- Implementar **menú ejecutivo express** (combo Mole Poblano + bebida + postre) a precio competitivo para aumentar tickets sin saturar cocina.
- **Impacto estimado:** Las ventas a las 13 hrs ya generan los mayores ingresos ($35,914 los lunes). Un combo con 10% de descuento podría aumentar el ticket promedio en $15–20.

**Estrategia 2: Activar sábados noche**
- El sábado 20 hrs muestra un pico de $23,364 — hay demanda no explotada.
- Lanzar **"Noche Mexicana"** semanal: mariachi + menú especial + Margarita 2×1 para aumentar tráfico vespertino de fin de semana.

**Estrategia 3: Bundles de platillos estrella**
- Combinar Mole Poblano + Margarita (ambos top 3 en ventas) en un **bundle "Sabor Completo"** con 15% de descuento.
- Promocionar Enchiladas Verdes los miércoles ("Miércoles Verde") para distribuir la demanda semanal.

**Estrategia 4: Impulsar sucursales con ticket alto pero bajo volumen**
- León tiene el ticket promedio más alto ($185.95) pero el menor número de tickets (386).
- Invertir en marketing local y programa de referidos para atraer nuevos comensales sin reducir el nivel de gasto.

**Estrategia 5: Expansión digital**
- CDMX Sur tiene la mayor tasa de conversión digital (10.5%). Replicar sus tácticas (contenido orgánico en Instagram/TikTok) en sucursales con baja conversión como Puebla (4.3%).

---

### 4.3 Estrategias para optimizar inventario

**Estrategia 1: Implementar política de reorden basada en pronóstico**
- El análisis generó puntos de reorden para **242 combinaciones ingrediente-sucursal** con stock de seguridad calculado (z=1.65, nivel de servicio 95%).
- **Acción:** Programar órdenes de compra automáticas cuando el stock caiga al punto de reorden.

**Estrategia 2: FEFO (First Expired, First Out)**
- Aplicar rotación estricta por fecha de caducidad en proteínas (Carne de Res, Carne de Cerdo, Pollo) y perecederos (Aguacate, Cilantro).
- Instalar señalización visual de fechas de vencimiento en cámaras de refrigeración.

**Estrategia 3: Ajustar tamaños de lote por sucursal**
- Las sucursales con mayor merma (Puebla, Mérida) deben reducir la cantidad por pedido y aumentar la frecuencia de reabastecimiento.
- Puebla: Cambiar de pedidos semanales a **pedidos cada 3 días** para Carne de Res y Cerveza.

**Estrategia 4: Sincronizar compras con pronóstico estacional**
- Antes de julio 2026 (mes pico), aumentar gradualmente inventarios de Tequila, Frijoles y Carne de Cerdo.
- Puebla: Preparar proveedor de Carne de Res para marzo 2026 (394.56 unidades pronosticadas).

**Estrategia 5: Proveedores alternos para ingredientes críticos**
- En los 242 items analizados, **todos requieren reorden inmediato** — indicador de que la relación con proveedores debe diversificarse para garantizar disponibilidad.

---

## 5. Propuestas de Solución

### 5.1 Segmentación de clientes por patrones de consumo

**Metodología:** Segmentación RFM proxy (Recencia, Frecuencia, Valor Monetario) construida desde la base de clientes, con **KMeans clustering** optimizado por silhouette score.

**Visualización:** `outputs/charts/rfm_scatter_segments.png` · `outputs/charts/personas_summary.png` (nuevos)

**3 segmentos identificados:**

| Segmento | Persona | Clientes | % del Total | Frecuencia Promedio | Gasto Promedio | Tasa Lealtad | Aceptación Promos |
|----------|---------|----------|-------------|---------------------|----------------|-------------|------------------|
| 0 | **Leales Premium** | **320** | 21.3% | 17.0 visitas/año | **$4,409** | **100%** | 66.3% |
| 1 | Ocasionales Sensibles a Promoción | **896** | 59.7% | 6.0 visitas/año | $1,451 | 9.5% | 64.0% |
| 2 | Ocasionales Sensibles a Promoción | **284** | 18.9% | 6.4 visitas/año | $1,574 | 13.7% | 69.4% |

**Características de cada persona:**

**Leales Premium (320 clientes, 21.3%):**
- Son el **motor de ingresos**: 320 clientes × $4,409 promedio = **$1,410,880 en valor estimado**.
- Frecuencia alta (17 visitas/año), **100% son miembros del programa de lealtad**.
- Aceptan promociones al 66.3% — no necesitan descuentos agresivos, valoran la experiencia.
- **Estrategia:** Experiencias exclusivas, maridajes premium, acceso anticipado a platillos nuevos.

**Ocasionales Sensibles a Promoción (1,180 clientes, 78.7%):**
- Visitan ~6 veces/año con gasto promedio de $1,451–$1,574.
- Solo 9.5–13.7% son miembros de lealtad — **gran oportunidad de conversión**.
- Aceptación de promociones: 64–69% — responden bien a ofertas dirigidas.
- **Estrategia:** Descuentos de primera visita, combos con valor percibido, inscripción automatizada al programa de lealtad con incentivo de bienvenida.

---

### 5.2 Campañas de marketing dirigidas por sucursal

**Visualización:** Datos de `outputs/tables/recommendations_branch_campaigns.csv` y `outputs/tables/recommendations_dish_promotions.csv`

**Top platillos a promocionar por sucursal (score combinando volumen + margen + señal digital):**

| # | Sucursal | Platillo | Franja | Score | Acción |
|---|----------|----------|--------|-------|--------|
| 1 | **Guadalajara** | **Enchiladas Verdes** | Comida | **0.911** | Bundle con CTA digital |
| 2 | **Monterrey** | **Mole Poblano** | Comida | **0.887** | Bundle con CTA digital |
| 3 | **Monterrey** | Guacamole con Totopos | Comida | 0.871 | Bundle con CTA digital |
| 4 | CDMX Centro | Mole Poblano | Comida | 0.847 | Bundle con CTA digital |
| 5 | CDMX Centro | Margarita | Comida | 0.840 | Bundle con CTA digital |
| 6 | Cancún | Mole Poblano | Comida | 0.836 | Bundle con CTA digital |
| 7 | CDMX Centro | Guacamole con Totopos | Comida | 0.832 | Bundle con CTA digital |
| 8 | Guadalajara | Mole Poblano | Comida | 0.823 | Bundle con CTA digital |
| 9 | Querétaro | Enchiladas Verdes | Comida | 0.806 | Bundle con CTA digital |
| 10 | Cancún | Tacos al Pastor | Comida | 0.788 | Bundle con CTA digital |

**Campañas recomendadas por sucursal y segmento:**

**Para Ocasionales (segmento mayoritario):**

| Sucursal | Clientes target | Aceptación promos | Canal | Mensaje |
|----------|----------------|-------------------|-------|---------|
| CDMX Centro | 139 | 64% | WhatsApp + App + Email | "Promociones de entrada y menú destacado" |
| León | 132 | **70%** | WhatsApp + App + Email | "Descuento primera visita + inscripción lealtad" |
| Guadalajara | 121 | 69% | WhatsApp + App + Email | "Combo Enchiladas Verdes de miércoles" |
| Monterrey | 115 | 65% | WhatsApp + App + Email | "Mole Poblano en bundle de comida" |

**Para Leales Premium:**

| Sucursal | Clientes VIP | Aceptación promos | Canal | Mensaje |
|----------|-------------|-------------------|-------|---------|
| Guadalajara | 45 | 67% | Email + App exclusiva | "Experiencias VIP, maridajes premium" |
| Tijuana | 39 | 65% | Email + App exclusiva | "Beneficios exclusivos de lealtad" |
| Mérida | 35 | 66% | Email + App exclusiva | "Acceso anticipado a nuevo menú" |
| CDMX Centro | 33 | **76%** | Email + App exclusiva | "Noche del Socio con chef invitado" |

**Canal digital más efectivo por campaña:**

| Campaña | Mejor plataforma | Engagement/$ |
|---------|-----------------|-------------|
| Día de la Familia | **TikTok** | **12.39×** |
| Noche Mexicana | **TikTok** | **10.11×** |
| Festival del Mole | Instagram | 8.5× |
| Happy Hour Margaritas | Facebook | 7.2× |
| Descuento Cumpleañeros | TikTok | Alta conversión (40%) |

---

### 5.3 Plan para reducir el desperdicio de alimentos

**Costo total de merma en la cadena:** ~$627,550 MXN (suma de todas las sucursales).

**Plan en 5 acciones priorizadas:**

| Prioridad | Acción | Sucursal(es) target | Ingrediente(s) | Ahorro estimado |
|-----------|--------|--------------------|-----------------|-----------------| 
| **1 — Urgente** | Implementar FEFO estricto con señalización visual | Mérida, Puebla | Carne de Res, Tequila | ~$20,000/período |
| **2 — Alta** | Reducir tamaño de lote y aumentar frecuencia de pedido | Puebla, Mérida | Cerveza, Carne de Cerdo | ~$15,000/período |
| **3 — Alta** | Control de temperatura y condiciones de almacenamiento | Puebla | Cerveza (daño almacenamiento) | ~$7,500/período |
| **4 — Media** | Capacitación en preparación para reducir errores | Puebla, León | Carne de Res, Aguacate | ~$10,000/período |
| **5 — Media** | Sincronizar compras con pronóstico de demanda | Todas | Tequila, Frijoles, Carne de Res | ~$12,000/período |

**Meta:** Reducir el costo de merma total en **30% en 90 días** (de $627,550 a ~$440,000), focalizando esfuerzos en las 3 sucursales con mayor desperdicio (Puebla, Mérida, León).

**Métricas de seguimiento:**
1. **Costo de merma / Costo de compra** — meta: bajar de 18.4% a <12% en Puebla.
2. **Ratio de merma por caducidad** — meta: reducir 50% implementando FEFO.
3. **Frecuencia de quiebre** — meta: mantener por debajo del 5% en ingredientes críticos.

---

## 6. Preguntas Adicionales

### 6.1 ¿Cómo varía el comportamiento del cliente según la ubicación y los horarios?

**variaciones por ubicación:**

| Zona | Comportamiento | Ejemplo |
|------|---------------|---------|
| **Turística** (Cancún) | Mayor volumen, clientes de paso, alta competencia (8 competidores), ticket moderado ($181.64), horario extendido hasta medianoche | Tacos al Pastor es el líder en volumen, platos "típicos" para turistas |
| **Corporativa** (CDMX Centro, Monterrey) | Fuerte pico de comida ejecutiva (13:00–14:00), tickets de nivel medio-alto ($173–177), alta concentración empresarial | Mole Poblano y Margarita dominan — comidas de negocio |
| **Residencial** (CDMX Sur, Guadalajara) | Distribución más uniforme entre comida y cena, clientela repetitiva | Enchiladas Verdes y platos familiares lideran |
| **Cultural/Centro histórico** (Puebla, Mérida, Querétaro) | Turismo cultural + local, ticket moderado, horario más temprano | Platillos tradicionales con identidad regional |
| **Fronteriza** (Tijuana) | Influencia binacional, horario de comida similar a EEUU, nivel medio-alto | Tacos al Pastor top en volumen |
| **Industrial** (León) | Menor volumen pero mayor ticket promedio ($185.95), clientes fieles | Enchiladas Verdes y Chiles Rellenos favoritos |

**Variaciones por horario:**
- **11:00–12:00 (Apertura):** Bajo tráfico, ideal para promociones "early bird".
- **13:00–14:00 (Comida):** Pico máximo en TODAS las sucursales — el 40-45% del ingreso diario se concentra aquí.
- **15:00–18:00 (Tarde):** Valle de actividad — oportunidad para cafetería/postres o menú vespertino.
- **19:00–21:00 (Cena):** Segundo pico, especialmente fuerte en Cancún (turismo/cena) y sábados.
- **22:00–00:00:** Solo relevante en Cancún y CDMX Centro (cierre tardío).

---

### 6.2 ¿Qué platillos deben promocionarse más en cada sucursal?

**Top 3 platillos a promocionar por sucursal (ordenados por promotion_score):**

| Sucursal | #1 | #2 | #3 |
|----------|-----|-----|-----|
| **Cancún** | Mole Poblano (0.836) | Tacos al Pastor (0.788) | Margarita (0.774) |
| **CDMX Centro** | Mole Poblano (0.847) | Margarita (0.840) | Guacamole con Totopos (0.832) |
| **Monterrey** | Mole Poblano (0.887) | Guacamole con Totopos (0.871) | Margarita (0.764) |
| **Guadalajara** | **Enchiladas Verdes (0.911)** | Mole Poblano (0.823) | Margarita (0.756) |
| **Querétaro** | Enchiladas Verdes (0.806) | Mole Poblano (0.737) | Guacamole con Totopos (0.643) |
| **CDMX Sur** | Mole Poblano (0.648) | Tacos al Pastor (0.625) | — |
| **Puebla** | Mole Poblano (0.707) | Guacamole con Totopos (0.613) | Enchiladas Verdes (0.600) |
| **Mérida** | Enchiladas Verdes (0.720) | Mole Poblano (0.705) | — |
| **Tijuana** | Enchiladas Verdes (0.627) | — | — |
| **León** | Enchiladas Verdes (0.758) | Mole Poblano (0.749) | Chiles Rellenos (0.635) |

**Criterio del score:** Combina 45% volumen de ventas + 40% margen proxy + 15% sentimiento digital.

---

### 6.3 ¿Cómo ajustar los niveles de inventario para evitar desperdicios o faltantes?

El sistema de reorden propuesto utiliza:
- **Stock de seguridad:** calculado con z=1.65 (nivel de servicio 95%), considerando la variabilidad diaria de consumo.
- **Punto de reorden (ROP):** = (consumo diario promedio × tiempo de entrega) + stock de seguridad.
- **Frecuencia de pedido:** Según la frecuencia del proveedor (diario, semanal, quincenal).

**Acciones inmediatas por sucursal:**

| Sucursal | Problema principal | Acción |
|----------|-------------------|--------|
| **Puebla** | Mayor merma ($91,963) + errores de preparación | Reducir lotes, capacitar personal, FEFO estricto |
| **Mérida** | Caducidad de Carne de Res ($10,470) | FEFO + proveedor local para entregas más frecuentes |
| **Monterrey** | Mayor tasa de quiebre (9.5%) | Aumentar stock de seguridad en Salsa Roja y proteínas |
| **CDMX Centro** | Quiebre de Salsa Verde (50%) | Duplicar stock de seguridad de salsas + proveedor alterno |
| **Cancún** | Quiebre de Cebolla (50%) | Proveedor con entregas diarias para perecederos |
| **Guadalajara** | Quiebre de Pollo (43%) | Congelar reserva mínima + segunda fuente de suministro |
| **León** | Bajo quiebre (4.4%) pero alta merma | Reducir cantidades de pedido manteniendo frecuencia |

**Todos los 242 items** del inventario mostraron la necesidad de reorden inmediato, lo que indica niveles de stock sistemáticamente insuficientes. La implementación de la política de reorden calculada reduciría los quiebres al <5% en todas las sucursales.

---

### 6.4 ¿Qué cambios en las operaciones internas mejorarían la experiencia del cliente?

**1. Reducir tiempos de respuesta digital**
- Actualmente, el tiempo de respuesta promedio varía de **0.67 hrs** (Mérida, el mejor) a **2.10 hrs** (Puebla, el peor).
- **Meta:** Responder en <1 hora en todas las sucursales.
- Puebla y Guadalajara (1.71 hrs) necesitan protocolo de respuesta prioritaria en redes sociales.

| Sucursal | Tiempo Respuesta (hrs) | Estado |
|----------|----------------------|--------|
| Mérida | 0.67 | ✅ Excelente |
| Cancún | 1.14 | ⚠ Aceptable |
| León | 1.20 | ⚠ Aceptable |
| Monterrey | 1.37 | ⚠ A mejorar |
| CDMX Centro | 1.52 | ❌ Requiere acción |
| CDMX Sur | 1.69 | ❌ Requiere acción |
| Guadalajara | 1.71 | ❌ Requiere acción |
| Puebla | **2.10** | ❌ Urgente |

**2. Ampliar programa de lealtad**
- Solo el 21.3% de clientes son miembros de lealtad. El 78.7% restante (Ocasionales) tiene una aceptación de promos del 64–69%.
- **Acción:** Inscripción automática al programa de lealtad con el primer pago por App de Pago. Incentivo de bienvenida: postre gratis en la siguiente visita.

**3. Optimizar la experiencia en hora pico**
- Concentración del 40%+ de ventas en 13:00–14:00 genera potencial saturación.
- **Acción:** Menú express de 3 opciones listo en <10 minutos para la franja de comida. Pedido anticipado vía App.

**4. Mejorar sentimiento digital en sucursales críticas**
- Tijuana tiene el peor sentimiento digital (0.302) y CDMX Sur el segundo peor (0.331).
- **Acción:** Programa de recuperación de servicio (respuesta personalizada a reseñas negativas en Google Reviews, TikTok y Facebook). Capacitación en atención al cliente.

**5. Estacionamiento y accesibilidad**
- Puebla es la única sucursal **sin estacionamiento**, lo que limita el tráfico de clientes con auto.
- **Acción:** Convenio con estacionamiento cercano o servicio de valet parking.

---

## 7. Conclusión y Pasos Accionables

### Resumen de hallazgos principales

1. **La paradoja Cancún:** Genera los mayores ingresos ($118,067) pero la peor rentabilidad (-$4.5M proxy) por un costo operativo de $382,000/mes. Se requiere reestructuración de costos o aumento significativo de tickets.

2. **Modelo León:** Con el menor costo operativo ($143,500/mes), menor número de empleados y la mejor utilidad proxy, León demuestra que la eficiencia operativa supera al volumen puro. Su ticket promedio de $185.95 (el más alto) indica precios bien posicionados.

3. **Concentración de ventas:** Mole Poblano y Enchiladas Verdes generan ~27% del ingreso total. La hora comida (13:00–14:00) concentra el 40%+ del ingreso diario.

4. **Crisis de inventario:** $627,550 en merma total + quiebres de hasta 50% en ingredientes clave. Puebla ($91,963) y Mérida ($85,285) requieren intervención urgente.

5. **Oportunidad digital:** TikTok ofrece 6–12× engagement por peso invertido. CDMX Sur tiene 10.5% de conversión digital — el mejor de la cadena — pese a bajo sentimiento.

6. **78.7% de clientes son Ocasionales:** Con $1,451–$1,574 de gasto y ~64% aceptación de promos, representan el mayor potencial de conversión a lealtad.

### Plan de acción 30-60-90 días

**Primeros 30 días (Urgente):**
- [ ] Implementar FEFO en Puebla y Mérida para Carne de Res, Tequila y Cerveza.
- [ ] Activar política de reorden automática para los 242 items identificados.
- [ ] Lanzar campaña piloto en TikTok para Guadalajara (Enchiladas Verdes, score 0.911).
- [ ] Reducir tiempo de respuesta digital en Puebla a <1.5 hrs.

**30–60 días (Alta prioridad):**
- [ ] Ejecutar campañas segmentadas por persona en sucursales con menor margen (Cancún, Monterrey, CDMX Centro).
- [ ] Implementar programa de lealtad ampliado con inscripción automática vía App.
- [ ] Negociar proveedores alternos para ingredientes con quiebre >30% (Salsa Verde, Cebolla, Pollo).
- [ ] Preparar stock para pico de marzo 2026 (Puebla — Carne de Res: 394 uds).

**60–90 días (Consolidación):**
- [ ] Lanzar menú ejecutivo express en hora comida (13:00–14:00) en todas las sucursales.
- [ ] Activar "Noche Mexicana" en sábados para explotar el pico de 20 hrs.
- [ ] Revisar estructura de costos de Cancún (renta $120K → ¿renegociación?).
- [ ] Capacitación en manejo de almacenamiento y preparación en Puebla y León.
- [ ] Reentrenar modelos de pronóstico y segmentación con datos del nuevo período.

### KPIs de seguimiento mensual

| KPI | Meta | Frecuencia |
|-----|------|-----------|
| Margen proxy por sucursal | Mejorar 15% vs baseline | Mensual |
| Costo de merma / costo de compra | < 12% en todas las sucursales | Mensual |
| Tasa de quiebre de inventario | < 5% por ingrediente | Semanal |
| Conversión digital por plataforma | > 8% promedio cadena | Mensual |
| Tasa de inscripción a lealtad | > 30% de nuevos clientes | Mensual |
| Ingreso incremental por campaña | > $5,000 por campaña | Por campaña |
| Tiempo de respuesta digital | < 1 hora en todas las sucursales | Semanal |

---

## 8. Anexo de Gráficas y Visualizaciones

### Gráficas interactivas (HTML) — Análisis Exploratorio
1. **Tendencia diaria de ventas** — `outputs/charts/sales_trend_daily.html`
2. **Tendencia mensual de ventas** — `outputs/charts/sales_trend_monthly.html`
3. **Ventas por ciudad** — `outputs/charts/sales_by_city.html`
4. **Mapa de calor ventas por hora y día** — `outputs/charts/sales_by_hour_day.html`
5. **Top platillos por región y franja** — `outputs/charts/top_dishes_by_region_daypart.html`
6. **Ranking de sucursales (ventas y margen)** — `outputs/charts/branch_ranking_sales_margin.html`
7. **Mix de métodos de pago** — `outputs/charts/payment_method_mix.html`
8. **Heatmap merma/quiebre inventario** — `outputs/charts/inventory_waste_shortage_heatmap.html`
9. **Sentimiento digital por plataforma** — `outputs/charts/digital_sentiment_platform.html`

### Gráficas generadas para el informe (PNG + HTML)
10. **Cascada de rentabilidad — Cancún** — `outputs/charts/waterfall_cancún.png`
11. **Cascada de rentabilidad — León** — `outputs/charts/waterfall_león.png`
12. **Pareto de platillos por ingreso** — `outputs/charts/pareto_dishes.png`
13. **Radar multi-dimensión por sucursal** — `outputs/charts/radar_branches.png`
14. **Scatter RFM de segmentación** — `outputs/charts/rfm_scatter_segments.png`
15. **Estructura de costos vs ingresos** — `outputs/charts/cost_structure_branches.png`
16. **Merma por sucursal** — `outputs/charts/waste_cost_by_branch.png`
17. **Top 15 picos de demanda pronosticados** — `outputs/charts/forecast_peaks_top15.png`
18. **Ranking de ingresos por sucursal** — `outputs/charts/branch_revenue_ranking.png`
19. **Perfiles de segmentación de clientes** — `outputs/charts/personas_summary.png`

### Tablas de datos completas
- `outputs/tables/branch_ranking_sales_margin.csv`
- `outputs/tables/profitability_branch_ranking.csv`
- `outputs/tables/profitability_dish_ranking.csv`
- `outputs/tables/profitability_drivers.csv`
- `outputs/tables/inventory_branch_kpis.csv`
- `outputs/tables/inventory_waste_drivers.csv`
- `outputs/tables/inventory_shortage_summary.csv`
- `outputs/tables/inventory_reorder_policy.csv`
- `outputs/tables/forecast_monthly_demand.csv`
- `outputs/tables/forecast_peak_months.csv`
- `outputs/tables/customer_segments.csv`
- `outputs/tables/customer_personas_summary.csv`
- `outputs/tables/recommendations_branch_campaigns.csv`
- `outputs/tables/recommendations_dish_promotions.csv`
- `outputs/tables/recommendations_inventory_actions.csv`
- `outputs/tables/digital_platform_sentiment.csv`
- `outputs/tables/digital_branch_summary.csv`
- `outputs/tables/digital_campaign_summary.csv`
- `outputs/tables/sales_by_city.csv`
- `outputs/tables/sales_by_hour_day.csv`
- `outputs/tables/top_dishes_by_region_daypart.csv`
- `outputs/tables/payment_method_mix.csv`

---

*Informe generado con pipeline reproducible. Datos procesados con Python 3.12, Pandas, Scikit-learn, Statsmodels y Plotly. Visualizaciones interactivas disponibles en los archivos HTML listados.*
