PYTHON ?= python
.PHONY: install load ratios test clean
install:
	$(PYTHON) -m pip install -r requirements.txt
load:
	$(PYTHON) -m src.etl.run
ratios:
	$(PYTHON) -m src.analytics.run_ratios
test:
	pytest tests/etl -v --cov=src/etl --cov-report=term-missing
clean:
	rm -f output/*.csv data/processed/*.csv
