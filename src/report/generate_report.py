from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.io import ArtifactTracker


def _register_text(path: Path, tracker: ArtifactTracker | None, module: str) -> None:
    if tracker:
        tracker.register(path, "document", module, "md", None)


def _fmt_currency(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "N/D"


def _top_row(
    df: pd.DataFrame, sort_col: str, ascending: bool = False
) -> dict[str, Any]:
    if df.empty or sort_col not in df.columns:
        return {}
    row = df.sort_values(sort_col, ascending=ascending).head(1)
    return row.to_dict(orient="records")[0] if len(row) else {}


def _write_data_profile(
    path: Path,
    raw_profile: dict[str, dict[str, Any]],
    source_report: dict[str, dict[str, Any]],
) -> None:
    lines = [
        "# DATA_PROFILE",
        "",
        "Resumen de perfil de datos inferido antes de modelar.",
        "",
    ]
    for dataset, profile in raw_profile.items():
        source = source_report.get(dataset, {}).get("source", "N/D")
        source_file = source_report.get(dataset, {}).get(
            "source_file", source_report.get(dataset, {}).get("selected_file", "N/D")
        )
        lines.append(f"## {dataset}")
        lines.append(f"- Fuente seleccionada: `{source}`")
        lines.append(f"- Archivo: `{source_file}`")
        lines.append(f"- Filas: {profile.get('rows', 0)}")
        lines.append(
            f"- Columnas ({len(profile.get('columns', []))}): {', '.join(profile.get('columns', []))}"
        )
        missing_pct = profile.get("missing_pct", {})
        top_missing = sorted(missing_pct.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_missing:
            lines.append("- Top faltantes (%):")
            for col, pct in top_missing:
                lines.append(f"  - `{col}`: {pct:.2f}%")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_data_dictionary(path: Path, clean_tables: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# DATA_DICTIONARY",
        "",
        "Diccionario inferido desde tablas limpias canónicas.",
        "",
    ]
    for dataset, df in clean_tables.items():
        lines.append(f"## {dataset}")
        if df.empty:
            lines.append("- Tabla vacía")
            lines.append("")
            continue
        lines.append("| Columna | Tipo inferido | % Nulos |")
        lines.append("|---|---|---:|")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = df[col].isna().mean() * 100
            lines.append(f"| `{col}` | `{dtype}` | {null_pct:.2f}% |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_methodology(path: Path) -> None:
    content = """# METHODOLOGY

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
"""
    path.write_text(content, encoding="utf-8")


def _write_assumptions(path: Path) -> None:
    content = """# ASSUMPTIONS

1. Se utiliza español en documentación, reporte y dashboard.
2. Runtime objetivo: Python 3.11.
3. RFM se construye en modo proxy desde `clientes` (no existe llave `cliente_id` en ventas).
4. Pronóstico mensual: top 12 ingredientes por impacto, horizonte de 6 meses.
5. Parquet es preferente; CSV actúa como fallback operativo.
6. `POLARS=1` es opcional para acelerar lecturas/agregaciones.
7. El costo de ingredientes faltante se estima por receta o razón por categoría.
8. El costo operativo se prorratea por ticket mensual en cada sucursal.
"""
    path.write_text(content, encoding="utf-8")


def _write_results_summary(
    path: Path,
    branch_best: dict[str, Any],
    branch_worst: dict[str, Any],
    waste_driver: dict[str, Any],
    top_persona: dict[str, Any],
) -> None:
    content = f"""# RESULTS_SUMMARY

## Decisiones clave para directores
- Sucursal líder en desempeño: **{branch_best.get('branch_name', 'N/D')}** con utilidad proxy acumulada de {_fmt_currency(branch_best.get('total_profit_proxy'))}.
- Sucursal con mayor oportunidad de mejora: **{branch_worst.get('branch_name', 'N/D')}** (utilidad proxy acumulada de {_fmt_currency(branch_worst.get('total_profit_proxy'))}).
- Principal driver de merma: ingrediente **{waste_driver.get('ingredient', 'N/D')}** con costo estimado de desperdicio {_fmt_currency(waste_driver.get('total_waste_cost'))}.
- Segmento más numeroso: **{top_persona.get('persona', 'N/D')}** con {int(top_persona.get('customers', 0) or 0)} clientes.

## Acciones de corto plazo (30-60 días)
1. Ajustar punto de reorden y stock de seguridad en ingredientes de prioridad alta.
2. Ejecutar campañas por persona en sucursales con menor margen proxy.
3. Impulsar promociones de platillos con alto score (volumen + margen + señal digital).
4. Reducir merma con políticas FEFO y control de almacenamiento para ingredientes críticos.

## KPI sugeridos de seguimiento
- Margen proxy por sucursal (% mensual).
- Costo de desperdicio / costo de compra (%).
- Tasa de quiebre de inventario por ingrediente.
- Conversión digital por plataforma y campaña.
- Ingreso incremental por campañas segmentadas.
"""
    path.write_text(content, encoding="utf-8")


def _write_final_report(
    path: Path,
    *,
    branch_best: dict[str, Any],
    branch_worst: dict[str, Any],
    top_dish: dict[str, Any],
    waste_driver: dict[str, Any],
    peak_example: dict[str, Any],
    top_persona: dict[str, Any],
) -> None:
    content = f"""# Reporte Final - Sabor Mexicano

## 1. Executive Summary
Este estudio integra datos de ventas, clientes, sucursales, inventarios y canales digitales para identificar oportunidades de crecimiento y eficiencia operativa.

- Mejor sucursal por utilidad proxy: **{branch_best.get('branch_name', 'N/D')}**.
- Sucursal con menor utilidad proxy: **{branch_worst.get('branch_name', 'N/D')}**.
- Platillo con mayor utilidad proxy total: **{top_dish.get('dish', 'N/D')}**.
- Driver de merma más costoso: **{waste_driver.get('ingredient', 'N/D')}**.

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

Ejemplo de pico esperado: ingrediente **{peak_example.get('ingredient', 'N/D')}** en sucursal **{peak_example.get('branch_name', 'N/D')}** durante **{peak_example.get('peak_month', 'N/D')}**.

## 8. Customer Segments and Personas
Segmentación RFM proxy (desde `clientes`) con KMeans:
- Segmentos: `outputs/tables/customer_segments.csv`
- Personas: `outputs/tables/customer_personas_summary.csv`

Persona principal identificada: **{top_persona.get('persona', 'N/D')}**.

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
"""
    path.write_text(content, encoding="utf-8")


def generate_documents_and_reports(
    *,
    settings: dict[str, Any],
    raw_profile: dict[str, dict[str, Any]],
    source_report: dict[str, dict[str, Any]],
    clean_tables: dict[str, pd.DataFrame],
    analysis_outputs: dict[str, pd.DataFrame],
    model_outputs: dict[str, pd.DataFrame],
    tracker: ArtifactTracker | None,
    logger,
) -> None:
    module = "report.generate_report"
    docs_dir = Path(settings["paths"]["docs"])
    reports_dir = Path(settings["paths"]["reports"])
    docs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    data_profile_path = docs_dir / "DATA_PROFILE.md"
    data_dictionary_path = docs_dir / "DATA_DICTIONARY.md"
    methodology_path = docs_dir / "METHODOLOGY.md"
    assumptions_path = docs_dir / "ASSUMPTIONS.md"
    final_report_path = reports_dir / "final_report.md"
    summary_path = reports_dir / "RESULTS_SUMMARY.md"

    _write_data_profile(
        data_profile_path, raw_profile=raw_profile, source_report=source_report
    )
    _write_data_dictionary(data_dictionary_path, clean_tables=clean_tables)
    _write_methodology(methodology_path)
    _write_assumptions(assumptions_path)

    profitability_branch = analysis_outputs.get(
        "profitability_branch_ranking", pd.DataFrame()
    )
    profitability_dish = analysis_outputs.get(
        "profitability_dish_ranking", pd.DataFrame()
    )
    waste_drivers = analysis_outputs.get("inventory_waste_drivers", pd.DataFrame())
    peak_months = model_outputs.get("forecast_peak_months", pd.DataFrame())
    personas = model_outputs.get("customer_personas_summary", pd.DataFrame())

    branch_best = _top_row(profitability_branch, "total_profit_proxy", ascending=False)
    branch_worst = _top_row(profitability_branch, "total_profit_proxy", ascending=True)
    top_dish = _top_row(profitability_dish, "total_profit_proxy", ascending=False)
    waste_driver = _top_row(waste_drivers, "total_waste_cost", ascending=False)
    peak_example = _top_row(peak_months, "peak_forecast_qty", ascending=False)
    top_persona = _top_row(personas, "customers", ascending=False)

    _write_results_summary(
        summary_path,
        branch_best=branch_best,
        branch_worst=branch_worst,
        waste_driver=waste_driver,
        top_persona=top_persona,
    )
    _write_final_report(
        final_report_path,
        branch_best=branch_best,
        branch_worst=branch_worst,
        top_dish=top_dish,
        waste_driver=waste_driver,
        peak_example=peak_example,
        top_persona=top_persona,
    )

    for file_path in [
        data_profile_path,
        data_dictionary_path,
        methodology_path,
        assumptions_path,
        final_report_path,
        summary_path,
    ]:
        _register_text(file_path, tracker=tracker, module=module)
    logger.info("Documentación y reportes generados en docs/ y reports/.")
