PYTHON ?= python
.PHONY: install load test clean
install:
	$(PYTHON) -m pip install -r requirements.txt
load:
	$(PYTHON) -m src.etl.run
test:
	pytest tests/etl -v --cov=src/etl --cov-report=term-missing
clean:
	rm -f output/*.csv data/processed/*.csv
