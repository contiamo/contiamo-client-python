# Contributing

## Install in dev mode

```
pip install -e .[test]
```

## Github flow

- create a new branch
- branches should always be rebased onto master
- open a PR

## Create new distribution

Bump the version (according to [semver](https://semver.org/)).

Build and push the package to PyPI with

```
make clean
python setup.py sdist bdist_wheel
twine upload dist/*
```