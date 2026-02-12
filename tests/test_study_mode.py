from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.study_mode import (
    ensure_study_log_updated_for_run,
    render_run_summary_markdown,
)
from src.utils.io import ArtifactTracker


def test_study_log_guard_accepts_run_id(tmp_path: Path):
    study_log = tmp_path / "STUDY_LOG.md"
    study_log.write_text("# log\n\nRun ID: 2026-02-11\n", encoding="utf-8")
    ensure_study_log_updated_for_run(study_log, "2026-02-11")


def test_study_log_guard_rejects_missing_run_id(tmp_path: Path):
    study_log = tmp_path / "STUDY_LOG.md"
    study_log.write_text("# log\n\nRun ID: 2026-02-10\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        ensure_study_log_updated_for_run(study_log, "2026-02-11")


def test_run_summary_contains_diff_and_sections():
    tracker = ArtifactTracker()
    tracker.register(Path("outputs/tables/a.csv"), "table", "m", "csv", 10)
    summary = render_run_summary_markdown(
        run_id="2026-02-11",
        source_report={"sales": {"source": "json", "rows": 100, "columns": ["a", "b"]}},
        clean_tables={"sales": pd.DataFrame({"a": [1, 2]})},
        warning_messages=["warning ejemplo"],
        tracker=tracker,
        step_seconds={"fase_1": 1.2},
        started_at_utc=datetime.now(timezone.utc),
        finished_at_utc=datetime.now(timezone.utc),
    )
    assert "What changed in this run? (diff-style)" in summary
    assert "+ Se generaron" in summary
