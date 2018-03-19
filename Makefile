.PHONY: requirements install lint test

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