PYTHON ?= python

.PHONY: help install load ratios screener clustering report test dashboard api clean

help:
	@echo "N100 Financial Intelligence Platform - Build Automation"
	@echo "Available commands:"
	@echo "  make install    - Install required dependencies"
	@echo "  make load       - Run ETL pipeline to load Excel files into SQLite and generate audit CSVs"
	@echo "  make ratios     - Run ratio engine to calculate financial ratios and capital allocation"
	@echo "  make screener   - Run equity screener, peer comparison, and generate 92 radar charts"
	@echo "  make clustering - Run K-Means clustering and generate cluster artifacts"
	@echo "  make report     - Generate 92 company tearsheets, 11 sector reports, and portfolio summary"
	@echo "  make test       - Run full pytest suite and generate reports/pytest_report.html"
	@echo "  make dashboard  - Launch Streamlit dashboard on localhost:8501"
	@echo "  make api        - Launch FastAPI server on localhost:8000"
	@echo "  make clean      - Clean temporary cache files without deleting database or deliverables"

install:
	$(PYTHON) -m pip install -r requirements.txt

load:
	$(PYTHON) -m src.etl.run

ratios:
	$(PYTHON) -m src.analytics.run_ratios

screener:
	$(PYTHON) -m src.screener.run_screener

clustering:
	$(PYTHON) -m src.analytics.run_clustering

report:
	$(PYTHON) -m src.reports.run_sprint5

test:
	$(PYTHON) -m pytest --html=reports/pytest_report.html --self-contained-html -v

dashboard:
	$(PYTHON) -m streamlit run src/dashboard/app.py --server.port 8501

api:
	$(PYTHON) -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

clean:
	$(PYTHON) -c "import shutil, os, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/.pytest_cache', recursive=True)]; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True)]"
