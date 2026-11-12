PYTHON ?= python3
.PHONY: verify reproduce paper

verify:
	$(PYTHON) scripts/verify_artifacts.py

reproduce: verify
	$(PYTHON) scripts/fetch_dataset.py
	$(PYTHON) paper_v2/build_reference_coverage.py
	$(PYTHON) paper_v2/build_tables.py
	$(PYTHON) paper_v2/build_plots.py
	$(PYTHON) scripts/verify_artifacts.py

paper:
	cd paper_v2 && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
