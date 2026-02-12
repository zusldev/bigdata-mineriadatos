from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reco.recommendations import run_recommendations


def test_recommendations_generate_tables(tmp_path: Path):
    sales = pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02"],
            "branch_id": ["S1", "S1"],
            "branch_name": ["Centro", "Centro"],
            "daypart": ["Comida", "Noche"],
            "dish": ["Taco", "Mole"],
            "category": ["Platos Fuertes", "Platos Fuertes"],
            "total_sale": [100, 200],
            "quantity": [1, 2],
        }
    )
    feature_tables = {"analytics_branch_day_hour": pd.DataFrame()}
    analysis_outputs = {
        "profitability_dish_ranking": pd.DataFrame(
            {"dish": ["Taco", "Mole"], "avg_margin_proxy_pct": [50, 40]}
        ),
        "digital_branch_summary": pd.DataFrame(
            {"branch_id": ["S1"], "avg_sentiment_score": [0.7]}
        ),
        "inventory_reorder_policy": pd.DataFrame(
            {
                "branch_id": ["S1"],
                "ingredient": ["Tomate"],
                "current_stock": [10],
                "reorder_point": [20],
                "recommended_reorder": [True],
                "recommended_qty": [10],
            }
        ),
    }
    model_outputs = {
        "customer_segments": pd.DataFrame(
            {
                "segment_id": [0, 1],
                "persona": ["Leales Premium", "En Riesgo de Churn"],
                "preferred_branch": ["Centro", "Centro"],
                "preferred_city": ["CDMX", "CDMX"],
                "accepts_promotions": [True, False],
            }
        ),
        "forecast_peak_months": pd.DataFrame(
            {
                "branch_id": ["S1"],
                "ingredient": ["Tomate"],
                "peak_month": ["2025-08"],
                "peak_forecast_qty": [30],
            }
        ),
    }
    settings = {"paths": {"outputs_tables": str(tmp_path / "tables")}}

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    outputs = run_recommendations(
        {"sales": sales},
        feature_tables,
        analysis_outputs,
        model_outputs,
        settings=settings,
        tracker=None,
        logger=DummyLogger(),
    )
    assert "recommendations_dish_promotions" in outputs
    assert "recommendations_branch_campaigns" in outputs
    assert "recommendations_inventory_actions" in outputs
