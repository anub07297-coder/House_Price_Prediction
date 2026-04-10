.PHONY: setup train predict test lint clean

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements-dev.txt
	. .venv/bin/activate && pip install -e .

train:
	python scripts/train.py

predict:
	python scripts/predict.py

test:
	pytest

lint:
	python -m py_compile src/house_price_prediction/*.py scripts/*.py

clean:
	rm -rf .pytest_cache
