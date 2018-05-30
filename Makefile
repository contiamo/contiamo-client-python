.PHONY: clean requirements install lint test

clean:
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf contiamo.egg-info/
	rm -rf dist/

requirements:
	pip install -r requirements.txt

requirements-dev:
	pip install -r requirements-dev.txt

install:
	python setup.py install

lint:
	flake8 contiamo

test:
	pytest contiamo/tests