from __future__ import annotations

# ruff: noqa: E402

import re
import sys
import unicodedata
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from apps.dashboard.components import (
    branch_ranking_chart,
    filter_sales,
    forecast_chart,
    friendly_df,
    hourly_heatmap,
    load_csv_if_exists,
    sales_trend_chart,
    segment_chart,
)
from src.utils.io import read_table
from src.utils.logger import get_logger
from src.utils.paths import OUTPUTS_LOGS_DIR, OUTPUTS_TABLES_DIR, PROCESSED_DIR, REPORTS_DIR


st.set_page_config(page_title="Sabor Mexicano Dashboard", layout="wide")
logger = get_logger("dashboard")

MERMAID_HIGH_LEVEL = """flowchart LR
    A["Raw data<br/>data/raw/json|csv|xlsx"] --> B["Processed tables<br/>data/processed/*_clean.parquet|csv"]
    B --> C["Analytics tables<br/>data/processed/analytics_branch_day_hour.parquet|csv<br/>data/processed/analytics_customer_proxy.parquet|csv"]
    C --> D["Modelos<br/>outputs/models/forecast_models.pkl<br/>outputs/models/segmentation_kmeans.pkl"]
    C --> E["EDA + Analysis tables/charts<br/>outputs/charts/*.html<br/>outputs/tables/*.csv"]
    D --> E
    E --> F["Recomendaciones<br/>outputs/tables/recommendations_*.csv"]
    E --> G["Reportes<br/>reports/final_report.md<br/>reports/RESULTS_SUMMARY.md"]
    F --> H["Dashboard<br/>apps/dashboard/app.py"]
    G --> H
    E --> I["Trazabilidad<br/>outputs/manifests/artifacts_manifest.csv<br/>outputs/logs/run_summary.md"]
"""

MERMAID_CONTROL_FLOW = """flowchart TD
    R["python -m src.pipeline.run_all"] --> S["Study guard<br/>docs/STUDY_LOG.md y docs requeridos"]
    S --> L["load_raw_datasets()<br/>data/raw/*"]
    L --> C["clean_datasets()<br/>schema_map.yml"]
    C --> V["validate_datasets()<br/>data/processed/validation_report.parquet|csv"]
    V --> F["build_features()<br/>analytics_branch_day_hour / analytics_customer_proxy"]
    F --> P["Persist processed<br/>data/processed/*_clean.parquet|csv"]
    P --> E["run_eda()<br/>outputs/charts/*.html + outputs/tables/*.csv"]
    E --> A1["run_profitability_analysis()"]
    A1 --> A2["run_inventory_analysis()"]
    A2 --> A3["run_digital_analysis()"]
    A3 --> M1["run_forecast()<br/>outputs/tables/forecast_*.csv<br/>outputs/models/forecast_models.pkl"]
    M1 --> M2["run_segmentation()<br/>outputs/tables/customer_*.csv<br/>outputs/models/segmentation_kmeans.pkl"]
    M2 --> R1["run_recommendations()<br/>outputs/tables/recommendations_*.csv"]
    R1 --> G["generate_documents_and_reports()<br/>docs/*.md + reports/*.md"]
    G --> T["run_summary + manifest<br/>outputs/logs/run_summary.md<br/>outputs/manifests/artifacts_manifest.csv"]
"""

CORE_STUDY_TERMS: dict[str, str] = {
    "raw": "Datos crudos sin limpieza ni estandarización, tal como llegan de origen.",
    "lake": "Repositorio de datos en bruto/semiestructurados para almacenar variedad antes de transformar.",
    "raw/lake": "Zona inicial donde aterrizan datos de múltiples fuentes antes de limpieza/modelado.",
    "seed": "Semilla aleatoria para reproducibilidad; con la misma seed, los resultados deben ser estables.",
    "logger": "Componente que registra eventos y mensajes del pipeline para observabilidad y depuración.",
    "tracker": "Objeto que registra artefactos generados (ruta, tipo, módulo, formato, filas) para trazabilidad.",
    "manifest": "Inventario de artefactos generados por corrida, útil para auditoría y control de cambios.",
}


def _read_markdown(path: Path) -> str:
    if not path.exists():
        return f"Archivo no encontrado: `{path.as_posix()}`"
    return path.read_text(encoding="utf-8")


def _slugify_heading(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^\w\s-]", "", ascii_text)
    ascii_text = re.sub(r"[\s_]+", "-", ascii_text).strip("-")
    return ascii_text or "seccion"


def _normalize_term_key(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^\w\s/+-]", " ", ascii_text)
    ascii_text = re.sub(r"\s+", " ", ascii_text).strip()
    return ascii_text


@st.cache_data
def _load_study_dictionary() -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}

    for term, definition in CORE_STUDY_TERMS.items():
        key = _normalize_term_key(term)
        entries[key] = {"term": term, "definition": definition}

    glossary_path = ROOT / "docs" / "GLOSSARY.md"
    if not glossary_path.exists():
        return entries

    text = glossary_path.read_text(encoding="utf-8")
    current_term: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current_term, buffer
        if not current_term:
            return
        body = "\n".join(buffer).strip()
        if body:
            key = _normalize_term_key(current_term)
            entries[key] = {"term": current_term, "definition": body}
        current_term = None
        buffer = []

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            current_term = line[3:].strip()
        elif current_term is not None:
            buffer.append(line)
    flush()

    return entries


def _search_study_terms(
    query: str, dictionary: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    q = _normalize_term_key(query)
    if not q:
        return []

    exact: list[dict[str, str]] = []
    starts: list[dict[str, str]] = []
    contains: list[dict[str, str]] = []

    for key, item in dictionary.items():
        if key == q:
            exact.append(item)
        elif key.startswith(q):
            starts.append(item)
        elif q in key:
            contains.append(item)

    return exact + starts + contains


def _terms_present_in_text(
    markdown_text: str, dictionary: dict[str, dict[str, str]], limit: int = 12
) -> list[str]:
    normalized_text = _normalize_term_key(markdown_text)
    found: list[str] = []
    for key, item in dictionary.items():
        if len(key) < 3:
            continue
        if key in normalized_text:
            found.append(item["term"])
    found = sorted(set(found), key=lambda x: x.lower())
    return found[:limit]


def _inject_global_study_shortcut(dictionary: dict[str, dict[str, str]]) -> None:
    entries = sorted(
        [
            value
            for value in dictionary.values()
            if value.get("term") and value.get("definition")
        ],
        key=lambda item: item["term"].lower(),
    )
    payload = json.dumps(entries, ensure_ascii=False)
    html_template = """
<script>
(function() {
  const DATA = __PAYLOAD__;
  const PENDING_KEY = "study_pending_terms_v1";

  let hostWindow = window;
  let hostDoc = document;
  try {
    if (window.parent && window.parent.document) {
      hostWindow = window.parent;
      hostDoc = window.parent.document;
    }
  } catch (err) {
    hostWindow = window;
    hostDoc = document;
  }

  const ROOT_ID = "study-shortcut-root";
  const STYLE_ID = "study-shortcut-style";
  const HINT_ID = "study-shortcut-hint";
  const BACKDROP_ID = "study-shortcut-backdrop";
  const PANEL_ID = "study-shortcut-panel";
  const INPUT_ID = "study-shortcut-input";
  const RESULTS_ID = "study-shortcut-results";
  const DEF_ID = "study-shortcut-definition";
  const EMPTY_ID = "study-shortcut-empty";
  const ADD_BTN_ID = "study-shortcut-add";
  const PENDING_ID = "study-shortcut-pending";

  if (hostWindow.__studyShortcutCleanup) {
    hostWindow.__studyShortcutCleanup();
  }

  function normalize(text) {
    return (text || "")
      .normalize("NFKD")
      .replace(/[\\u0300-\\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function isEditableTarget(target) {
    if (!target) return false;
    const tag = (target.tagName || "").toUpperCase();
    if (["INPUT", "TEXTAREA", "SELECT"].includes(tag)) return true;
    if (target.isContentEditable) return true;
    return false;
  }

  function getSelectedText() {
    let text = "";
    try {
      text = (hostWindow.getSelection && hostWindow.getSelection().toString()) || "";
    } catch (err) {
      text = "";
    }
    if (!text) {
      try {
        text = (window.getSelection && window.getSelection().toString()) || "";
      } catch (err) {
        text = "";
      }
    }
    return text.trim();
  }

  function loadPending() {
    try {
      const raw = hostWindow.localStorage.getItem(PENDING_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (err) {
      return [];
    }
  }

  function savePending(list) {
    try {
      hostWindow.localStorage.setItem(PENDING_KEY, JSON.stringify(list));
    } catch (err) {}
  }

  function addPending(term) {
    const clean = term.trim();
    if (!clean) return;
    const list = loadPending();
    if (!list.some(x => normalize(x) === normalize(clean))) {
      list.unshift(clean);
      savePending(list.slice(0, 50));
    }
  }

  const oldRoot = hostDoc.getElementById(ROOT_ID);
  if (oldRoot) oldRoot.remove();
  const oldStyle = hostDoc.getElementById(STYLE_ID);
  if (oldStyle) oldStyle.remove();

  const style = hostDoc.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    #${HINT_ID} {
      position: fixed;
      right: 1rem;
      bottom: 1rem;
      z-index: 9999;
      background: #0f172a;
      color: #f8fafc;
      border: 1px solid #334155;
      border-radius: 999px;
      padding: .42rem .72rem;
      font-size: .78rem;
      box-shadow: 0 6px 18px rgba(15, 23, 42, .35);
      cursor: pointer;
      user-select: none;
    }
    #${BACKDROP_ID} {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, .35);
      z-index: 10000;
    }
    #${PANEL_ID} {
      display: none;
      position: fixed;
      right: 1rem;
      top: 4.3rem;
      width: min(520px, 95vw);
      max-height: calc(100vh - 6.2rem);
      z-index: 10001;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: .85rem;
      box-shadow: 0 16px 40px rgba(15, 23, 42, .25);
      overflow: hidden;
      font-family: "Segoe UI", Arial, sans-serif;
    }
    .study-shortcut-header {
      padding: .72rem .9rem .58rem .9rem;
      border-bottom: 1px solid #e2e8f0;
      background: linear-gradient(180deg, #f8fafc, #ffffff);
    }
    .study-shortcut-title {
      font-size: .95rem;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: .15rem;
    }
    .study-shortcut-sub {
      font-size: .78rem;
      color: #475569;
    }
    #${INPUT_ID} {
      width: 100%;
      border: 1px solid #cbd5e1;
      border-radius: .55rem;
      padding: .55rem .65rem;
      margin-top: .5rem;
      font-size: .9rem;
      outline: none;
      box-sizing: border-box;
    }
    #${INPUT_ID}:focus {
      border-color: #0ea5e9;
      box-shadow: 0 0 0 3px rgba(14, 165, 233, .15);
    }
    #${RESULTS_ID} {
      max-height: 180px;
      overflow: auto;
      border-bottom: 1px solid #e2e8f0;
      padding: .35rem .45rem;
      background: #f8fafc;
    }
    .study-shortcut-item {
      border: 1px solid #dbeafe;
      background: #eff6ff;
      border-radius: .55rem;
      padding: .4rem .5rem;
      margin-bottom: .35rem;
      cursor: pointer;
      color: #0f172a;
      font-size: .86rem;
    }
    .study-shortcut-item:hover {
      background: #dbeafe;
    }
    #${DEF_ID} {
      padding: .75rem .9rem .8rem .9rem;
      font-size: .9rem;
      color: #1e293b;
      line-height: 1.45;
      overflow: auto;
      max-height: 220px;
    }
    #${EMPTY_ID} {
      padding: .8rem .9rem;
      font-size: .84rem;
      color: #64748b;
      display: none;
    }
    #${ADD_BTN_ID} {
      display: none;
      margin: .2rem .9rem .75rem .9rem;
      border: 1px solid #93c5fd;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: .5rem;
      padding: .35rem .55rem;
      font-size: .82rem;
      cursor: pointer;
    }
    #${PENDING_ID} {
      border-top: 1px solid #e2e8f0;
      background: #f8fafc;
      padding: .5rem .9rem .7rem .9rem;
      max-height: 120px;
      overflow: auto;
      font-size: .8rem;
      color: #334155;
    }
    .study-shortcut-chip {
      display: inline-block;
      margin: .16rem .2rem .16rem 0;
      padding: .2rem .45rem;
      border-radius: 999px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      cursor: pointer;
    }
  `;
  hostDoc.head.appendChild(style);

  const root = hostDoc.createElement("div");
  root.id = ROOT_ID;

  const hint = hostDoc.createElement("div");
  hint.id = HINT_ID;
  hint.textContent = "/ Buscar concepto";

  const backdrop = hostDoc.createElement("div");
  backdrop.id = BACKDROP_ID;

  const panel = hostDoc.createElement("div");
  panel.id = PANEL_ID;
  panel.innerHTML = `
    <div class="study-shortcut-header">
      <div class="study-shortcut-title">Diccionario rápido de Study</div>
      <div class="study-shortcut-sub">Atajos: /, Ctrl/Cmd+K. Tip: selecciona una palabra y presiona /</div>
      <input id="${INPUT_ID}" type="text" placeholder="Ej: raw/lake, seed, logger, tracker" />
    </div>
    <div id="${RESULTS_ID}"></div>
    <div id="${EMPTY_ID}">Sin resultados. Puedes agregar el término a pendientes.</div>
    <div id="${DEF_ID}"></div>
    <button id="${ADD_BTN_ID}" type="button">Agregar a diccionario pendiente</button>
    <div id="${PENDING_ID}"></div>
  `;

  root.appendChild(hint);
  root.appendChild(backdrop);
  root.appendChild(panel);
  hostDoc.body.appendChild(root);

  const input = hostDoc.getElementById(INPUT_ID);
  const results = hostDoc.getElementById(RESULTS_ID);
  const definition = hostDoc.getElementById(DEF_ID);
  const empty = hostDoc.getElementById(EMPTY_ID);
  const addBtn = hostDoc.getElementById(ADD_BTN_ID);
  const pendingBox = hostDoc.getElementById(PENDING_ID);

  function filter(query) {
    const q = normalize(query);
    if (!q) return DATA.slice(0, 12);
    const exact = [];
    const starts = [];
    const contains = [];
    DATA.forEach(item => {
      const term = normalize(item.term);
      const desc = normalize(item.definition);
      if (term === q) exact.push(item);
      else if (term.startsWith(q)) starts.push(item);
      else if (term.includes(q) || desc.includes(q)) contains.push(item);
    });
    return exact.concat(starts, contains).slice(0, 20);
  }

  function renderPending() {
    const pending = loadPending();
    if (!pending.length) {
      pendingBox.innerHTML = "<b>Pendientes:</b> (vacío)";
      return;
    }
    const chips = pending
      .map(term => '<span class="study-shortcut-chip" data-term="' + term.replaceAll('"', "&quot;") + '">' + term + "</span>")
      .join("");
    pendingBox.innerHTML = "<b>Pendientes:</b><br/>" + chips;
    pendingBox.querySelectorAll(".study-shortcut-chip").forEach(node => {
      node.addEventListener("click", () => {
        const term = node.getAttribute("data-term") || "";
        input.value = term;
        render(filter(term));
      });
    });
  }

  function render(list) {
    results.innerHTML = "";
    addBtn.style.display = "none";
    if (!list.length) {
      empty.style.display = "block";
      definition.innerHTML = "";
      if (input.value.trim()) {
        addBtn.style.display = "inline-block";
      }
      return;
    }
    empty.style.display = "none";
    list.forEach(item => {
      const button = hostDoc.createElement("div");
      button.className = "study-shortcut-item";
      button.textContent = item.term;
      button.addEventListener("click", () => {
        definition.innerHTML = "<b>" + item.term + "</b><br/><br/>" + item.definition;
      });
      results.appendChild(button);
    });
    const first = list[0];
    definition.innerHTML = "<b>" + first.term + "</b><br/><br/>" + first.definition;
  }

  function openPanel(prefill) {
    backdrop.style.display = "block";
    panel.style.display = "block";
    const value = (prefill || "").trim();
    if (value) {
      input.value = value;
    }
    setTimeout(() => {
      input.focus();
      input.select();
    }, 0);
    render(filter(input.value));
    renderPending();
  }

  function closePanel() {
    backdrop.style.display = "none";
    panel.style.display = "none";
  }

  function onKeyDown(e) {
    const key = (e.key || "").toLowerCase();
    const isSlash = (e.key === "/" || e.code === "Slash") && !e.ctrlKey && !e.metaKey && !e.altKey;
    const isCmdK = key === "k" && (e.ctrlKey || e.metaKey);
    if ((isSlash || isCmdK) && !isEditableTarget(e.target)) {
      e.preventDefault();
      openPanel(getSelectedText());
      return;
    }
    if (e.key === "Escape" && panel.style.display === "block") {
      e.preventDefault();
      closePanel();
    }
  }

  hint.addEventListener("click", () => openPanel(""));
  backdrop.addEventListener("click", closePanel);
  input.addEventListener("input", () => render(filter(input.value)));
  addBtn.addEventListener("click", () => {
    addPending(input.value);
    renderPending();
    addBtn.style.display = "none";
    definition.innerHTML = "<b>Término agregado a pendientes:</b><br/><br/>" + input.value;
  });

  hostDoc.addEventListener("keydown", onKeyDown, true);
  document.addEventListener("keydown", onKeyDown, true);
  hostWindow.__studyShortcutCleanup = function() {
    try { hostDoc.removeEventListener("keydown", onKeyDown, true); } catch (err) {}
    try { document.removeEventListener("keydown", onKeyDown, true); } catch (err) {}
    const currentRoot = hostDoc.getElementById(ROOT_ID);
    if (currentRoot) currentRoot.remove();
    const currentStyle = hostDoc.getElementById(STYLE_ID);
    if (currentStyle) currentStyle.remove();
  };

  render(filter(""));
  renderPending();
})();
</script>
"""
    html = html_template.replace("__PAYLOAD__", payload)
    components.html(html, height=0, width=0)


def _build_toc_and_anchored_markdown(
    markdown_text: str, *, max_level: int = 3
) -> tuple[list[dict[str, str | int]], str]:
    toc: list[dict[str, str | int]] = []
    lines_out: list[str] = []
    anchor_counts: dict[str, int] = {}
    in_code_block = False

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            lines_out.append(line)
            continue

        if in_code_block:
            lines_out.append(line)
            continue

        match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if not match:
            lines_out.append(line)
            continue

        level = len(match.group(1))
        title = match.group(2).strip()
        base_anchor = _slugify_heading(title)
        anchor_counts[base_anchor] = anchor_counts.get(base_anchor, 0) + 1
        suffix = anchor_counts[base_anchor]
        anchor = base_anchor if suffix == 1 else f"{base_anchor}-{suffix}"

        lines_out.append(f'<a id="{anchor}"></a>')
        lines_out.append(line)
        if level <= max_level:
            toc.append({"level": level, "title": title, "anchor": anchor})

    return toc, "\n".join(lines_out)


def _render_study_styles() -> None:
    st.markdown(
        """
<style>
.study-panel-note {
    font-size: 0.9rem;
    color: #4b5563;
    margin-top: -0.35rem;
    margin-bottom: 0.45rem;
}
.study-doc-card {
    padding: 0.55rem 0.8rem;
    border: 1px solid #d1d5db;
    border-radius: 0.6rem;
    background: #f8fafc;
}
.study-lookup-box {
    padding: 0.55rem 0.7rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.55rem;
    background: #ffffff;
    margin-bottom: 0.6rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def _filter_toc(
    toc: list[dict[str, str | int]], query: str
) -> list[dict[str, str | int]]:
    query_clean = query.strip().lower()
    if not query_clean:
        return toc
    return [item for item in toc if query_clean in str(item["title"]).lower()]


def _render_toc(
    toc: list[dict[str, str | int]],
    *,
    title: str = "Índice de contenido",
    key_prefix: str = "toc",
    height: int = 540,
) -> None:
    st.markdown(f"#### {title}")
    search = st.text_input(
        "Buscar en índice",
        value="",
        placeholder="Ej: control de flujo, forecast, recomendaciones",
        key=f"{key_prefix}_search",
        label_visibility="collapsed",
    )
    filtered = _filter_toc(toc, search)
    if not toc:
        st.caption("Sin encabezados detectados.")
        return
    if search and not filtered:
        st.caption(f"Sin resultados para: `{search}`")

    st.markdown(
        f'<div class="study-panel-note">Secciones visibles: {len(filtered)} / {len(toc)}</div>',
        unsafe_allow_html=True,
    )
    with st.container(height=height, border=True):
        for item in filtered:
            level = int(item["level"])
            indent = "&nbsp;" * max(0, (level - 1) * 4)
            st.markdown(
                f"{indent}[{item['title']}](#{item['anchor']})",
                unsafe_allow_html=True,
            )


def _render_term_lookup_panel(
    markdown_text: str, *, key_prefix: str = "study_lookup"
) -> None:
    dictionary = _load_study_dictionary()
    st.markdown("#### Diccionario rápido")
    st.markdown(
        '<div class="study-lookup-box">Busca un término y ve su definición sin salir del documento.</div>',
        unsafe_allow_html=True,
    )
    query = st.text_input(
        "Buscar término",
        value="",
        placeholder="Ej: raw/lake, seed, logger, tracker",
        key=f"{key_prefix}_query",
        label_visibility="collapsed",
    )

    matches = _search_study_terms(query, dictionary) if query else []
    if query:
        if not matches:
            st.caption(f"No encontré definición para: `{query}`")
        else:
            labels = [m["term"] for m in matches]
            selected = st.selectbox(
                "Coincidencias",
                options=labels,
                index=0,
                key=f"{key_prefix}_matches",
                label_visibility="collapsed",
            )
            picked = next((m for m in matches if m["term"] == selected), matches[0])
            st.markdown(f"**{picked['term']}**")
            st.markdown(picked["definition"])

    present_terms = _terms_present_in_text(markdown_text, dictionary, limit=10)
    if present_terms:
        st.markdown("Términos detectados en este documento")
        selected_present = st.selectbox(
            "Selecciona un término detectado",
            options=["(Seleccionar)"] + present_terms,
            index=0,
            key=f"{key_prefix}_present_terms",
            label_visibility="collapsed",
        )
        if selected_present != "(Seleccionar)":
            key = _normalize_term_key(selected_present)
            item = dictionary.get(key)
            if item:
                st.markdown(f"**{item['term']}**")
                st.markdown(item["definition"])


def _extract_diff_lines(run_summary_text: str) -> str:
    lines = []
    in_diff = False
    for line in run_summary_text.splitlines():
        if line.strip().lower().startswith("## what changed in this run?"):
            in_diff = True
            continue
        if in_diff and line.startswith("## "):
            break
        if in_diff and line.strip().startswith(("+", "-")):
            lines.append(line)
    return "\n".join(lines) if lines else "No hay diff-style summary aún."


def _build_flashcards() -> list[tuple[str, str]]:
    return [
        (
            "¿Qué es el schema mapping y por qué lo usamos?",
            "Es una capa de mapeo de nombres alternativos de columnas a nombres canónicos. "
            "Permite que el pipeline funcione incluso si los archivos cambian encabezados (por ejemplo, "
            "`Sucursal_ID` vs `branch_id`).",
        ),
        (
            "¿Por qué preferimos Parquet y cuándo caemos a CSV?",
            "Parquet es columnar y más eficiente en analítica. Si `pyarrow` no está disponible o falla la escritura, "
            "se usa CSV como fallback para no romper el pipeline.",
        ),
        (
            "¿Qué significa RFM y por qué aquí es proxy?",
            "RFM = Recency, Frequency, Monetary. En este caso no hay llave cliente-ticket en ventas, así que se "
            "estima con `clientes` (`ultima_visita`, `visitas_ultimo_ano`, `gasto_total_estimado`).",
        ),
        (
            "¿Qué hace KMeans en segmentación?",
            "Agrupa clientes con patrones similares en el espacio de features. Se usa para descubrir perfiles "
            "accionables (personas) sin etiquetas previas.",
        ),
        (
            "¿Por qué usamos Exponential Smoothing para forecast?",
            "Porque tenemos series mensuales cortas por sucursal-ingrediente. Es un método robusto para tendencia "
            "con pocos puntos y con fallback si no converge.",
        ),
        (
            "¿Qué es el punto de reorden?",
            "Nivel de inventario en el que conviene reabastecer para evitar quiebres. Incluye demanda esperada "
            "durante lead time más stock de seguridad.",
        ),
        (
            "¿Qué integra el score de promociones por platillo?",
            "Volumen de ventas, margen proxy y señal digital (sentimiento/engagement) para priorizar qué promover "
            "por sucursal y franja horaria.",
        ),
        (
            "¿Qué valida el Study Guard del pipeline?",
            "Que existan `docs/STUDY_LOG.md`, `GLOSSARY.md`, `DECISIONS.md`, `CHECKPOINTS.md` y que el Study Log "
            "incluya una entrada para el `Run ID` actual.",
        ),
    ]


def _render_bigdata_mining_flow_section() -> None:
    st.markdown("### 🧠 Flujo: Big Data → Minería de Datos")
    flow_doc = ROOT / "docs" / "STUDY_FLOW_BIGDATA_MINING.md"
    st.caption(f"Ruta: `{flow_doc.as_posix()}`")

    content_col, toc_col = st.columns([3.8, 1.2], gap="large")
    if flow_doc.exists():
        flow_text = flow_doc.read_text(encoding="utf-8")
        toc, anchored = _build_toc_and_anchored_markdown(flow_text, max_level=3)
        with content_col:
            st.markdown(anchored, unsafe_allow_html=True)
        with toc_col:
            _render_toc(
                toc,
                title="Índice Flujo",
                key_prefix="study_flow_toc",
                height=560,
            )
            _render_term_lookup_panel(flow_text, key_prefix="study_flow_lookup")
            st.caption("Tip: usa búsqueda + clic para navegar más rápido.")
    else:
        with content_col:
            st.error(
                "No se encontró `docs/STUDY_FLOW_BIGDATA_MINING.md`.\n\n"
                "Crea el documento para habilitar esta vista de estudio."
            )
            st.info(
                "Sugerencia: agrega el archivo en `docs/` y vuelve a abrir el dashboard."
            )
        with toc_col:
            st.caption("Índice no disponible sin documento.")

    st.markdown("#### Diagramas Mermaid (copiables)")
    with st.expander("Diagrama 1: Flujo de datos de alto nivel (copiar código)"):
        st.code(f"```mermaid\n{MERMAID_HIGH_LEVEL}\n```", language="markdown")

    with st.expander("Diagrama 2: Flujo de control run_all (copiar código)"):
        st.code(f"```mermaid\n{MERMAID_CONTROL_FLOW}\n```", language="markdown")

    st.markdown("#### Checklist de comprensión")
    st.checkbox(
        "Entiendo la diferencia entre Big Data, Minería de Datos y BI.",
        key="study_chk_conceptos_base",
    )
    st.checkbox(
        "Puedo explicar el orden exacto de `src/pipeline/run_all.py`.",
        key="study_chk_control_flow",
    )
    st.checkbox(
        "Puedo identificar inputs, outputs y validaciones por etapa.",
        key="study_chk_inputs_outputs",
    )
    st.checkbox(
        "Sé por qué este repo es Big Data style sin afirmar cómputo distribuido.",
        key="study_chk_bigdata_style",
    )
    st.checkbox(
        "Puedo justificar el uso de `artifacts_manifest.csv` y `run_summary.md` para trazabilidad.",
        key="study_chk_traceability",
    )


@st.cache_data
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    sales = read_table(PROCESSED_DIR / "sales_clean", logger=logger)
    customers = read_table(PROCESSED_DIR / "customers_clean", logger=logger)
    inventory = read_table(PROCESSED_DIR / "inventory_clean", logger=logger)
    digital = read_table(PROCESSED_DIR / "digital_clean", logger=logger)

    tables = {
        "sales": sales,
        "customers": customers,
        "inventory": inventory,
        "digital": digital,
        "branch_ranking": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "profitability_branch_ranking.csv"
        ),
        "profit_dishes": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "profitability_dish_ranking.csv"
        ),
        "inventory_kpis": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "inventory_branch_kpis.csv"
        ),
        "inventory_actions": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "recommendations_inventory_actions.csv"
        ),
        "digital_branch": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "digital_branch_summary.csv"
        ),
        "forecast": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "forecast_monthly_demand.csv"
        ),
        "forecast_peak": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "forecast_peak_months.csv"
        ),
        "segments": load_csv_if_exists(OUTPUTS_TABLES_DIR / "customer_segments.csv"),
        "personas": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "customer_personas_summary.csv"
        ),
        "reco_campaigns": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "recommendations_branch_campaigns.csv"
        ),
        "reco_dishes": load_csv_if_exists(
            OUTPUTS_TABLES_DIR / "recommendations_dish_promotions.csv"
        ),
    }
    return tables


def _render_study_tab() -> None:
    _render_study_styles()
    st.subheader("Aprender / Study Mode")
    st.markdown(
        '<div class="study-doc-card"><b>Navegación recomendada:</b> usa el índice derecho con búsqueda para moverte en documentos largos.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
### Resumen de conceptos por módulo
- **Loader**: detección flexible de JSON/CSV/XLSX, prioridad por fuente y deduplicación de workbooks repetidos.
- **Cleaning**: normalización de columnas, parseo robusto de fechas/números, booleans y manejo de faltantes.
- **EDA**: tendencias de ventas, top platillos, desempeño por sucursal, inventario y señales digitales.
- **Forecasting**: demanda mensual por sucursal-ingrediente con Exponential Smoothing + fallback.
- **Segmentation**: RFM proxy + KMeans para generar personas accionables.
- **Recommendations**: reglas combinadas de margen, volumen, inventario y digital para decisiones operativas.
"""
    )

    st.markdown("### Documentación de estudio")
    doc_paths = {
        "Study Log": ROOT / "docs" / "STUDY_LOG.md",
        "Glosario": ROOT / "docs" / "GLOSSARY.md",
        "Decisiones": ROOT / "docs" / "DECISIONS.md",
        "Checkpoints": ROOT / "docs" / "CHECKPOINTS.md",
        "Metodología": ROOT / "docs" / "METHODOLOGY.md",
        "Flujo Big Data y Minería": ROOT / "docs" / "STUDY_FLOW_BIGDATA_MINING.md",
    }
    selected_doc = st.selectbox(
        "Selecciona un documento", options=list(doc_paths.keys()), index=0
    )
    selected_path = doc_paths[selected_doc]
    st.caption(f"Ruta: `{selected_path.as_posix()}`")
    doc_content_col, doc_toc_col = st.columns([3.8, 1.2], gap="large")
    if selected_path.exists():
        doc_text = selected_path.read_text(encoding="utf-8")
        toc, anchored = _build_toc_and_anchored_markdown(doc_text, max_level=3)
        with doc_content_col:
            st.markdown(anchored, unsafe_allow_html=True)
        with doc_toc_col:
            _render_toc(
                toc,
                title="Índice",
                key_prefix=f"study_doc_{_slugify_heading(selected_doc)}",
                height=520,
            )
            _render_term_lookup_panel(
                doc_text, key_prefix=f"study_lookup_{_slugify_heading(selected_doc)}"
            )
            st.caption("Tip: usa búsqueda + scroll para encontrar secciones rápido.")
    else:
        with doc_content_col:
            st.error(
                f"No se encontró `{selected_path.as_posix()}`.\n\n"
                "Verifica que el archivo exista o ejecuta el pipeline para regenerar documentación."
            )
        with doc_toc_col:
            st.caption("Índice no disponible sin documento.")

    st.markdown("### What changed in this run?")
    run_summary_path = OUTPUTS_LOGS_DIR / "run_summary.md"
    run_summary_text = _read_markdown(run_summary_path)
    diff_block = _extract_diff_lines(run_summary_text)
    st.code(diff_block, language="diff")
    with st.expander("Ver run_summary.md completo"):
        st.markdown(run_summary_text)

    _render_bigdata_mining_flow_section()

    st.markdown("### Self-quiz")
    cards = _build_flashcards()
    for idx, (question, answer) in enumerate(cards, start=1):
        with st.expander(f"{idx}. {question}"):
            st.write(answer)


def main() -> None:
    st.title("Dashboard - Cadena Sabor Mexicano")
    st.caption(
        "Filtros globales y análisis integrado de ventas, clientes, inventario, digital y pronósticos."
    )
    _inject_global_study_shortcut(_load_study_dictionary())

    data = load_dashboard_data()
    sales = data["sales"].copy()

    if sales.empty:
        st.warning(
            "No se encontraron tablas procesadas de ventas. Ejecuta primero:\n\n"
            "`python -m src.pipeline.run_all --seed 42 --forecast-horizon 6 --top-ingredients 12`"
        )
        _render_study_tab()
        return

    sales["date"] = pd.to_datetime(sales.get("date"), errors="coerce")
    for col in ["total_sale"]:
        sales[col] = pd.to_numeric(sales.get(col), errors="coerce").fillna(0.0)

    min_date = sales["date"].min()
    max_date = sales["date"].max()

    st.sidebar.header("Filtros")
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(
            (min_date.date(), max_date.date())
            if pd.notna(min_date) and pd.notna(max_date)
            else None
        ),
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = pd.Timestamp(date_range[0])
        end_date = pd.Timestamp(date_range[1])
    else:
        start_date = min_date
        end_date = max_date

    branches = ["Todas"] + sorted(
        [x for x in sales.get("branch_name", pd.Series(dtype=str)).dropna().unique()]
    )
    categories = ["Todas"] + sorted(
        [x for x in sales.get("category", pd.Series(dtype=str)).dropna().unique()]
    )
    dishes = ["Todos"] + sorted(
        [x for x in sales.get("dish", pd.Series(dtype=str)).dropna().unique()]
    )
    payment_methods = ["Todos"] + sorted(
        [x for x in sales.get("payment_method", pd.Series(dtype=str)).dropna().unique()]
    )

    branch_filter = st.sidebar.selectbox("Sucursal", options=branches, index=0)
    category_filter = st.sidebar.selectbox("Categoría", options=categories, index=0)
    dish_filter = st.sidebar.selectbox("Platillo", options=dishes, index=0)
    payment_filter = st.sidebar.selectbox(
        "Método de pago", options=payment_methods, index=0
    )
    loyalty_filter = st.sidebar.selectbox(
        "Lealtad", options=["Todos", "Solo miembros", "Solo no miembros"], index=0
    )

    filtered_sales = filter_sales(
        sales,
        start_date=start_date,
        end_date=end_date,
        branch=branch_filter,
        category=category_filter,
        dish=dish_filter,
        payment_method=payment_filter,
    )

    if loyalty_filter != "Todos" and not data["customers"].empty:
        st.sidebar.info(
            "El filtro de lealtad se aplica en la pestaña de Clientes (RFM proxy)."
        )

    tabs = st.tabs(
        [
            "Ventas",
            "Rendimiento Sucursales",
            "Clientes",
            "Inventario",
            "Digital",
            "Pronósticos",
            "Recomendaciones",
            "📄 Informe Final",
            "Aprender / Study Mode",
        ]
    )

    # ── Tab 0: Ventas ──────────────────────────────────────────────
    with tabs[0]:
        st.subheader("Ventas")
        st.info(
            "Esta sección muestra el comportamiento general de ventas. "
            "Los tres indicadores superiores resumen ingresos, tickets y ticket "
            "promedio del periodo filtrado. La gráfica de tendencia revela patrones "
            "diarios, y el mapa de calor identifica las horas y días con mayor "
            "actividad — útil para planificar turnos y promociones."
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos", f"${filtered_sales['total_sale'].sum():,.0f}")
        col2.metric(
            "Tickets",
            f"{filtered_sales.get('ticket_id', pd.Series(dtype=str)).nunique():,}",
        )
        avg_ticket = filtered_sales["total_sale"].sum() / max(
            1, filtered_sales.get("ticket_id", pd.Series(dtype=str)).nunique()
        )
        col3.metric("Ticket promedio", f"${avg_ticket:,.2f}")

        trend_fig = sales_trend_chart(filtered_sales)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        heatmap_fig = hourly_heatmap(filtered_sales)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        st.dataframe(
            friendly_df(filtered_sales.head(50), "sales"),
            use_container_width=True,
        )

    # ── Tab 1: Rendimiento Sucursales ──────────────────────────────
    with tabs[1]:
        st.subheader("Rendimiento de sucursales")
        st.info(
            "Ranking de las 10 sucursales ordenadas por utilidad proxy "
            "(ingresos − costos operativos mensuales × meses). León lidera en "
            "eficiencia pese a ser 7ª en ingresos: tiene el menor costo operativo "
            "(\\$143,500/mes) y el ticket promedio más alto (\\$185.95). Cancún, aunque "
            "genera los mayores ingresos (\\$118,067), ocupa la última posición por "
            "costos de \\$382,000/mes."
        )
        branch_rank = data["branch_ranking"]
        fig = branch_ranking_chart(branch_rank)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            friendly_df(branch_rank, "branch_ranking"),
            use_container_width=True,
        )

    # ── Tab 2: Clientes ────────────────────────────────────────────
    with tabs[2]:
        st.subheader("Clientes y segmentación (RFM proxy)")
        st.info(
            "Los clientes se segmentaron usando el método RFM (Recencia, Frecuencia, "
            "Valor Monetario) + clustering KMeans. Se identificaron 2 grandes perfiles: "
            "Leales Premium (21.3 %, visitan 17 veces/año, gastan ~\\$4,400) y Ocasionales "
            "(78.7 %, ~6 visitas/año, ~\\$1,500). El 78.7 % de clientes son Ocasionales "
            "con alta aceptación de promociones → oportunidad de conversión a lealtad."
        )
        personas = data["personas"]
        seg_fig = segment_chart(personas)
        if seg_fig:
            st.plotly_chart(seg_fig, use_container_width=True)
        st.dataframe(
            friendly_df(personas, "personas"),
            use_container_width=True,
        )
        st.dataframe(
            friendly_df(data["segments"].head(100), "segments"),
            use_container_width=True,
        )

    # ── Tab 3: Inventario ──────────────────────────────────────────
    with tabs[3]:
        st.subheader("Inventario")
        st.info(
            "KPIs de inventario por sucursal. La merma total de la cadena es \\$627,550. "
            "Puebla tiene el mayor costo de merma (\\$91,963), mientras que Monterrey "
            "presenta la peor tasa de quiebre (9.5 %). Las acciones sugeridas incluyen "
            "reorden automático, rotación FEFO y validación de proveedores alternos."
        )
        st.dataframe(
            friendly_df(data["inventory_kpis"], "inventory_kpis"),
            use_container_width=True,
        )
        st.markdown("### Acciones sugeridas")
        st.dataframe(
            friendly_df(data["inventory_actions"], "inventory_actions"),
            use_container_width=True,
        )

    # ── Tab 4: Digital ─────────────────────────────────────────────
    with tabs[4]:
        st.subheader("Canales digitales")
        st.info(
            "Resumen del marketing digital por sucursal y plataforma. TikTok genera "
            "6-12× más engagement por peso invertido que otras plataformas. El "
            "sentimiento promedio es positivo en la mayoría de sucursales. La gráfica "
            "inferior muestra la distribución de sentimientos por plataforma."
        )
        st.dataframe(
            friendly_df(data["digital_branch"], "digital_branch"),
            use_container_width=True,
        )
        if not data["digital"].empty:
            sentiment_counts = (
                data["digital"]
                .assign(sentiment=data["digital"]["sentiment"].astype(str))
                .groupby(["platform", "sentiment"], dropna=False)
                .size()
                .reset_index(name="records")
            )
            st.bar_chart(
                sentiment_counts.pivot_table(
                    index="platform",
                    columns="sentiment",
                    values="records",
                    aggfunc="sum",
                    fill_value=0,
                )
            )

    # ── Tab 5: Pronósticos ─────────────────────────────────────────
    with tabs[5]:
        st.subheader("Pronósticos")
        st.info(
            "Pronóstico de demanda mensual por ingrediente y sucursal usando el modelo "
            "Holt-Winters (suavización exponencial). Cada línea representa un ingrediente; "
            "los paneles separan por sucursal. La tabla inferior muestra los picos "
            "pronosticados más importantes — los meses donde se espera mayor demanda, "
            "útil para planificar compras anticipadas. Julio 2026 es el mes pico más "
            "frecuente (temporada vacacional)."
        )
        forecast = data["forecast"]
        fig_forecast = forecast_chart(forecast)
        if fig_forecast:
            st.plotly_chart(fig_forecast, use_container_width=True)
        st.dataframe(
            friendly_df(data["forecast_peak"], "forecast_peak"),
            use_container_width=True,
        )

    # ── Tab 6: Recomendaciones ─────────────────────────────────────
    with tabs[6]:
        st.subheader("Recomendaciones accionables")
        st.info(
            "Acciones concretas generadas por el motor de recomendaciones. Las campañas "
            "por sucursal sugieren mensajes y canales por segmento de clientes. Las "
            "promociones por platillo usan un score compuesto (volumen + margen + señal "
            "digital) para priorizar qué promover en cada franja horaria. Las acciones "
            "de inventario indican cantidades de reorden y medidas de prevención de merma."
        )
        st.markdown("### Campañas por sucursal y segmento")
        st.dataframe(
            friendly_df(data["reco_campaigns"], "reco_campaigns"),
            use_container_width=True,
        )
        st.markdown("### Promociones sugeridas por platillo/franja")
        st.dataframe(
            friendly_df(data["reco_dishes"], "reco_dishes"),
            use_container_width=True,
        )
        st.markdown("### Acciones de inventario")
        st.dataframe(
            friendly_df(data["inventory_actions"], "inventory_actions"),
            use_container_width=True,
        )

    # ── Tab 7: Informe Final ───────────────────────────────────────
    with tabs[7]:
        sub_report, sub_clean = st.tabs(
            ["📄 Caso de Estudio", "🧹 Limpieza de Datos"]
        )

        with sub_report:
            st.subheader("📄 Informe del Caso de Estudio")
            st.info(
                "Documento completo del caso de estudio *Sabor Mexicano* generado "
                "a partir del análisis de datos. Incluye resumen ejecutivo, metodología, "
                "hallazgos clave, visualizaciones y recomendaciones estratégicas."
            )
            report_path = REPORTS_DIR / "informe_caso_estudio.md"
            report_md = _read_markdown(report_path)
            toc_items, anchored_md = _build_toc_and_anchored_markdown(report_md)
            col_toc, col_body = st.columns([1, 3])
            with col_toc:
                _render_toc(
                    toc_items,
                    title="Índice del informe",
                    key_prefix="report_toc",
                    height=600,
                )
            with col_body:
                st.markdown(anchored_md, unsafe_allow_html=True)

        with sub_clean:
            st.subheader("🧹 Informe de Limpieza de Datos")
            st.info(
                "Documento que detalla el flujo completo de limpieza y preparación "
                "de datos: carga, normalización, eliminación de duplicados, imputación "
                "de valores faltantes, validación de tipos y rangos, y resumen de "
                "transformaciones aplicadas a cada tabla."
            )
            clean_path = REPORTS_DIR / "informe_limpieza_datos.md"
            clean_md = _read_markdown(clean_path)
            toc_clean, anchored_clean = _build_toc_and_anchored_markdown(clean_md)
            col_toc_c, col_body_c = st.columns([1, 3])
            with col_toc_c:
                _render_toc(
                    toc_clean,
                    title="Índice de limpieza",
                    key_prefix="clean_toc",
                    height=600,
                )
            with col_body_c:
                st.markdown(anchored_clean, unsafe_allow_html=True)

    # ── Tab 8: Study Mode ──────────────────────────────────────────
    with tabs[8]:
        _render_study_tab()


if __name__ == "__main__":
    main()
