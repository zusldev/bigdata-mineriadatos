"""
Genera gráficas adicionales para el informe del caso de estudio.
Exporta PNG estáticos que se incrustarán en el .docx final.
"""

import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TABLES = os.path.join(BASE, "outputs", "tables")
CHARTS = os.path.join(BASE, "outputs", "charts")
os.makedirs(CHARTS, exist_ok=True)

# ── Utilidad para guardar ───────────────────────────────────────────
def _save(fig, name, w=1000, h=600):
    path_html = os.path.join(CHARTS, f"{name}.html")
    path_png = os.path.join(CHARTS, f"{name}.png")
    fig.write_html(path_html)
    try:
        fig.write_image(path_png, width=w, height=h, scale=2)
        print(f"  ✓ {path_png}")
    except Exception as e:
        print(f"  ⚠ PNG falló ({e}), solo HTML guardado: {path_html}")


# ═══════════════════════════════════════════════════════════════════
# 1. Waterfall de rentabilidad – Cancún vs León (casos extremos)
# ═══════════════════════════════════════════════════════════════════
def chart_waterfall():
    branches = pd.read_csv(os.path.join(BASE, "data", "processed", "branches_clean.csv"))
    ranking = pd.read_csv(os.path.join(TABLES, "profitability_branch_ranking.csv"))
    drivers = pd.read_csv(os.path.join(TABLES, "profitability_drivers.csv"))

    for bname, color_rev, color_cost in [
        ("Cancún", "#2ecc71", "#e74c3c"),
        ("León", "#2ecc71", "#e74c3c"),
    ]:
        d = drivers[drivers["branch_name"] == bname]
        rev = d["revenue"].sum()
        ing_cost = d["ingredient_cost"].sum()
        op_cost = d["op_alloc"].sum()
        profit = rev - ing_cost - op_cost

        fig = go.Figure(go.Waterfall(
            x=["Ingresos", "Costo ingredientes", "Costo operativo", "Utilidad proxy"],
            y=[rev, -ing_cost, -op_cost, 0],
            measure=["absolute", "relative", "relative", "total"],
            text=[f"${rev:,.0f}", f"-${ing_cost:,.0f}", f"-${op_cost:,.0f}", f"${profit:,.0f}"],
            textposition="outside",
            connector={"line": {"color": "#95a5a6"}},
            increasing={"marker": {"color": "#2ecc71"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            totals={"marker": {"color": "#3498db"}},
        ))
        fig.update_layout(
            title=f"Cascada de Rentabilidad — {bname}",
            yaxis_title="MXN $",
            template="plotly_white",
            font=dict(size=13),
        )
        _save(fig, f"waterfall_{bname.lower().replace(' ', '_')}", w=900, h=550)


# ═══════════════════════════════════════════════════════════════════
# 2. Pareto de platillos (revenue acumulado, regla 80/20)
# ═══════════════════════════════════════════════════════════════════
def chart_pareto_dishes():
    df = pd.read_csv(os.path.join(TABLES, "profitability_dish_ranking.csv"))
    df = df.sort_values("total_revenue", ascending=False).reset_index(drop=True)
    df["cum_pct"] = df["total_revenue"].cumsum() / df["total_revenue"].sum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df["dish"], y=df["total_revenue"], name="Ingreso",
               marker_color="#3498db"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df["dish"], y=df["cum_pct"], name="% Acumulado",
                   line=dict(color="#e74c3c", width=2.5), mode="lines+markers",
                   marker=dict(size=5)),
        secondary_y=True,
    )
    # 80% line
    fig.add_hline(y=80, line_dash="dash", line_color="#95a5a6",
                  annotation_text="80%", secondary_y=True)
    fig.update_layout(
        title="Diagrama de Pareto — Ingresos por Platillo",
        xaxis_title="Platillo",
        template="plotly_white",
        font=dict(size=12),
        xaxis_tickangle=-45,
        legend=dict(x=0.01, y=0.99),
    )
    fig.update_yaxes(title_text="Ingreso (MXN $)", secondary_y=False)
    fig.update_yaxes(title_text="% Acumulado", secondary_y=True, range=[0, 105])
    _save(fig, "pareto_dishes", w=1100, h=600)


# ═══════════════════════════════════════════════════════════════════
# 3. Radar multi-sucursal (revenue, avg_ticket, margen, merma, digital)
# ═══════════════════════════════════════════════════════════════════
def chart_radar_branches():
    rank = pd.read_csv(os.path.join(TABLES, "branch_ranking_sales_margin.csv"))
    inv = pd.read_csv(os.path.join(TABLES, "inventory_branch_kpis.csv"))
    dig = pd.read_csv(os.path.join(TABLES, "digital_branch_summary.csv"))

    df = rank.merge(inv[["branch_id", "waste_cost_total", "shortage_rate"]], on="branch_id")
    df = df.merge(dig[["branch_id", "avg_sentiment_score"]], on="branch_id")

    # Normalize 0-1
    def norm(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-9)

    cats = ["Ingresos", "Ticket Promedio", "Margen Bruto",
            "Bajo desperdicio", "Bajo quiebre", "Sentimiento Digital"]

    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, (_, row) in enumerate(df.iterrows()):
        vals = [
            norm(df["total_revenue"]).iloc[i],
            norm(df["avg_ticket"]).iloc[i],
            norm(df["total_margin"]).iloc[i],
            1 - norm(df["waste_cost_total"]).iloc[i],  # inverse: low waste = good
            1 - norm(df["shortage_rate"]).iloc[i],      # inverse: low shortage = good
            norm(df["avg_sentiment_score"]).iloc[i],
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            name=row["branch_name"],
            line=dict(color=colors[i % len(colors)]),
            fill=None,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.05])),
        title="Radar Multi-Dimensión por Sucursal",
        template="plotly_white",
        font=dict(size=12),
        legend=dict(font=dict(size=10)),
    )
    _save(fig, "radar_branches", w=950, h=700)


# ═══════════════════════════════════════════════════════════════════
# 4. Scatter RFM de segmentos de clientes
# ═══════════════════════════════════════════════════════════════════
def chart_rfm_scatter():
    segs = pd.read_csv(os.path.join(TABLES, "customer_segments.csv"))

    # Map persona labels if present
    persona_col = "persona" if "persona" in segs.columns else "segment_id"

    fig = px.scatter(
        segs,
        x="recency_days",
        y="frequency",
        size="monetary",
        color=persona_col,
        hover_data=["monetary"],
        size_max=20,
        opacity=0.6,
        color_discrete_sequence=["#e74c3c", "#3498db", "#2ecc71", "#f39c12"],
        title="Segmentación de Clientes — RFM Proxy (Recencia vs Frecuencia)",
    )
    fig.update_layout(
        xaxis_title="Recencia (días desde última interacción)",
        yaxis_title="Frecuencia (visitas)",
        template="plotly_white",
        font=dict(size=13),
        legend=dict(title="Segmento"),
    )
    _save(fig, "rfm_scatter_segments", w=1000, h=650)


# ═══════════════════════════════════════════════════════════════════
# 5. Estructura de costos apilada por sucursal
# ═══════════════════════════════════════════════════════════════════
def chart_cost_structure():
    drivers = pd.read_csv(os.path.join(TABLES, "profitability_drivers.csv"))
    agg = drivers.groupby("branch_name").agg(
        revenue=("revenue", "sum"),
        ingredient_cost=("ingredient_cost", "sum"),
        op_alloc=("op_alloc", "sum"),
    ).reset_index()
    agg = agg.sort_values("revenue", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=agg["branch_name"], x=agg["ingredient_cost"],
        name="Costo Ingredientes", orientation="h",
        marker_color="#e67e22",
    ))
    fig.add_trace(go.Bar(
        y=agg["branch_name"], x=agg["op_alloc"],
        name="Costo Operativo Asignado", orientation="h",
        marker_color="#e74c3c",
    ))
    fig.add_trace(go.Bar(
        y=agg["branch_name"], x=agg["revenue"],
        name="Ingreso", orientation="h",
        marker_color="#2ecc71",
    ))
    fig.update_layout(
        barmode="group",
        title="Estructura de Costos vs Ingresos por Sucursal",
        xaxis_title="MXN $",
        template="plotly_white",
        font=dict(size=12),
        legend=dict(x=0.55, y=0.15),
    )
    _save(fig, "cost_structure_branches", w=1050, h=600)


# ═══════════════════════════════════════════════════════════════════
# 6. Top merma por sucursal (barras horizontales)
# ═══════════════════════════════════════════════════════════════════
def chart_waste_by_branch():
    inv = pd.read_csv(os.path.join(TABLES, "inventory_branch_kpis.csv"))
    inv = inv.sort_values("waste_cost_total", ascending=True)

    fig = go.Figure(go.Bar(
        y=inv["branch_name"],
        x=inv["waste_cost_total"],
        orientation="h",
        marker_color=["#e74c3c" if v > 70000 else "#f39c12" if v > 50000 else "#2ecc71"
                       for v in inv["waste_cost_total"]],
        text=[f"${v:,.0f}" for v in inv["waste_cost_total"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Costo Total de Merma por Sucursal",
        xaxis_title="Costo de Merma (MXN $)",
        template="plotly_white",
        font=dict(size=13),
    )
    _save(fig, "waste_cost_by_branch", w=900, h=550)


# ═══════════════════════════════════════════════════════════════════
# 7. Forecast picos – top 15 ingredients/branches
# ═══════════════════════════════════════════════════════════════════
def chart_forecast_peaks():
    pk = pd.read_csv(os.path.join(TABLES, "forecast_peak_months.csv"))
    pk = pk.sort_values("peak_forecast_qty", ascending=False).head(15)
    pk["label"] = pk["branch_name"].astype(str) + " — " + pk["ingredient"].astype(str)

    fig = go.Figure(go.Bar(
        y=pk["label"][::-1],
        x=pk["peak_forecast_qty"][::-1],
        orientation="h",
        marker_color="#3498db",
        text=[f"{v:.0f} uds" for v in pk["peak_forecast_qty"][::-1]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top 15 Picos de Demanda Pronosticados (6 meses)",
        xaxis_title="Cantidad Pronosticada (unidades)",
        template="plotly_white",
        font=dict(size=12),
    )
    _save(fig, "forecast_peaks_top15", w=1000, h=650)


# ═══════════════════════════════════════════════════════════════════
# 8. Ranking de sucursales por revenue (ref rápida)
# ═══════════════════════════════════════════════════════════════════
def chart_branch_revenue_rank():
    rank = pd.read_csv(os.path.join(TABLES, "branch_ranking_sales_margin.csv"))
    rank = rank.sort_values("total_revenue", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=rank["branch_name"],
        x=rank["total_revenue"],
        orientation="h",
        name="Ingresos",
        marker_color="#3498db",
        text=[f"${v:,.0f}" for v in rank["total_revenue"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Ranking de Sucursales por Ingresos Totales",
        xaxis_title="Ingresos (MXN $)",
        template="plotly_white",
        font=dict(size=13),
    )
    _save(fig, "branch_revenue_ranking", w=900, h=550)


# ═══════════════════════════════════════════════════════════════════
# 9. Segmentación clientes – resumen de personas
# ═══════════════════════════════════════════════════════════════════
def chart_personas_summary():
    personas = pd.read_csv(os.path.join(TABLES, "customer_personas_summary.csv"))

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Clientes por Segmento", "Gasto Promedio por Segmento"),
                        specs=[[{"type": "pie"}, {"type": "bar"}]])
    labels = [f"Seg {r['segment_id']}: {r['persona']}" for _, r in personas.iterrows()]
    fig.add_trace(
        go.Pie(labels=labels, values=personas["customers"],
               marker=dict(colors=["#e74c3c", "#3498db", "#2ecc71"]),
               textinfo="percent+value"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=labels, y=personas["monetary_mean"],
               marker_color=["#e74c3c", "#3498db", "#2ecc71"],
               text=[f"${v:,.0f}" for v in personas["monetary_mean"]],
               textposition="outside"),
        row=1, col=2,
    )
    fig.update_layout(
        title="Perfiles de Segmentación de Clientes",
        template="plotly_white",
        font=dict(size=12),
        showlegend=False,
    )
    _save(fig, "personas_summary", w=1100, h=500)


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
def main():
    print("Generando gráficas para informe del caso de estudio…\n")
    chart_waterfall()
    chart_pareto_dishes()
    chart_radar_branches()
    chart_rfm_scatter()
    chart_cost_structure()
    chart_waste_by_branch()
    chart_forecast_peaks()
    chart_branch_revenue_rank()
    chart_personas_summary()
    print("\n✅ Todas las gráficas generadas en:", CHARTS)


if __name__ == "__main__":
    main()
