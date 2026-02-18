# Reporte Final - Sabor Mexicano

**Autor:** Liborio Zúñiga  
**Materia:** Big Data y Minería de Datos  
**Fecha:** Febrero 2026  

## 1. Executive Summary
Este estudio integra datos de ventas, clientes, sucursales, inventarios y canales digitales para identificar oportunidades de crecimiento y eficiencia operativa.

- Mejor sucursal por utilidad proxy: **León**.
- Sucursal con menor utilidad proxy: **Cancún**.
- Platillo con mayor utilidad proxy total: **Refresco**.
- Driver de merma más costoso: **Carne de Res**.

## 2. Methods
Se implementó pipeline modular con limpieza estandarizada, validación, análisis exploratorio, análisis de rentabilidad/inventario, pronóstico mensual de demanda y segmentación RFM proxy + clustering.

## 3. EDA Findings (con gráficas)
- Tendencias de ventas: `outputs/charts/sales_trend_daily.html`, `outputs/charts/sales_trend_monthly.html`
- Ventas por ciudad y hora/día: `outputs/charts/sales_by_city.html`, `outputs/charts/sales_by_hour_day.html`
- Top platillos por región/franja: `outputs/charts/top_dishes_by_region_daypart.html`
- Sentimiento digital: `outputs/charts/digital_sentiment_platform.html`

## 4. Branch Performance Ranking
El ranking consolidado se encuentra en `outputs/tables/profitability_branch_ranking.csv` y `outputs/tables/branch_ranking_sales_margin.csv`.

## 5. Profitability and Cost Drivers
La utilidad proxy se calculó como:
`revenue - ingredient_cost_proxy - operational_cost_allocation_per_ticket`.

Los principales drivers por categoría/sucursal están en `outputs/tables/profitability_drivers.csv`.

## 6. Inventory Waste / Shortage Analysis
- Drivers de merma: `outputs/tables/inventory_waste_drivers.csv`
- Riesgo de quiebre: `outputs/tables/inventory_shortage_summary.csv`
- Política de reorden sugerida: `outputs/tables/inventory_reorder_policy.csv`

## 7. Forecast Results
Se pronosticó demanda mensual para top ingredientes por sucursal (6 meses):
- Tabla principal: `outputs/tables/forecast_monthly_demand.csv`
- Meses pico: `outputs/tables/forecast_peak_months.csv`

Ejemplo de pico esperado: ingrediente **Carne de Res** en sucursal **Puebla** durante **2026-03**.

## 8. Customer Segments and Personas
Segmentación RFM proxy (desde `clientes`) con KMeans:
- Segmentos: `outputs/tables/customer_segments.csv`
- Personas: `outputs/tables/customer_personas_summary.csv`

Persona principal identificada: **Ocasionales Sensibles a Promoción**.

## 9. Marketing Recommendations per Branch
Recomendaciones de campañas por sucursal/segmento:
- `outputs/tables/recommendations_branch_campaigns.csv`

Promociones sugeridas por platillo y franja:
- `outputs/tables/recommendations_dish_promotions.csv`

## 10. Waste Reduction Plan
- Ajustar punto de reorden y stock de seguridad por ingrediente.
- Priorizar control de almacenamiento en ingredientes con mayor merma.
- Sincronizar compras con meses pico de demanda pronosticada.

## 11. Action Plan + Next Steps
1. Implementar recomendaciones de inventario (prioridad alta) en primer ciclo mensual.
2. Activar campañas segmentadas por persona en sucursales con menor margen.
3. Monitorear KPI operativos y comerciales semanalmente.
4. Reentrenar pronóstico y segmentación mensualmente con datos nuevos.
