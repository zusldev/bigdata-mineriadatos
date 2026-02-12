ifeq ($(OS),Windows_NT)
VENV_PYTHON := .venv/Scripts/python.exe
else
VENV_PYTHON := .venv/bin/python
endif

PYTHON ?= python
ifneq ($(wildcard $(VENV_PYTHON)),)
PYTHON := $(VENV_PYTHON)
endif

SEED = 42
HORIZON = 6
TOP_INGREDIENTS = 12
RUN_ID = 2026-02-11-quickcheck-01

.PHONY: setup lint test pipeline dashboard all

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m ruff check src apps tests
	$(PYTHON) -m black --check src apps tests

test:
	$(PYTHON) -m pytest -q

pipeline:
	$(PYTHON) -m src.pipeline.run_all --seed $(SEED) --forecast-horizon $(HORIZON) --top-ingredients $(TOP_INGREDIENTS) --run-id $(RUN_ID)

dashboard:
	streamlit run apps/dashboard/app.py

all: lint test pipeline
