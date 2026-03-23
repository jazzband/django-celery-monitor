PROJ=django_celery_monitor
PYTHON=python
GIT=git
TOX=tox
RUFF=ruff
PRE_COMMIT=pre-commit

TESTDIR=t
SPHINX_DIR=docs/
SPHINX_BUILDDIR="${SPHINX_DIR}/_build"
SPHINX_HTMLDIR="${SPHINX_BUILDDIR}/html"
DOCUMENTATION=Documentation
FLAKEPLUSTARGET=2.7

all: help

help:
	@echo "docs                 - Build documentation."
	@echo "test-all             - Run tests for all supported python versions."
	@echo "distcheck ---------- - Check distribution for problems."
	@echo "  test               - Run unittests using current python."
	@echo "  lint ------------  - Check codebase for problems."
	@echo "    apicheck         - Check API reference coverage."
	@echo "    configcheck      - Check configuration reference coverage."
	@echo "    formatcheck      - Run ruff formatting checks."
	@echo "    ruffcheck        - Run ruff lint checks."
	@echo "    hooks            - Run repository hooks."
	@echo "clean-dist --------- - Clean all distribution build artifacts."
	@echo "  clean-git-force    - Remove all uncommitted files."
	@echo "  clean ------------ - Non-destructive clean"
	@echo "    clean-pyc        - Remove .pyc/__pycache__ files"
	@echo "    clean-docs       - Remove documentation build artifacts."
	@echo "    clean-build      - Remove setup artifacts."
	@echo "bump                 - Bump patch version number."
	@echo "bump-minor           - Bump minor version number."
	@echo "bump-major           - Bump major version number."
	@echo "release              - Make PyPI release."

clean: clean-docs clean-pyc clean-build

clean-dist: clean clean-git-force

bump:
	bumpversion patch

bump-minor:
	bumpversion minor

bump-major:
	bumpversion major

release:
	python -m build
	python -m twine upload dist/*

Documentation:
	(cd "$(SPHINX_DIR)"; $(MAKE) html)
	mv "$(SPHINX_HTMLDIR)" $(DOCUMENTATION)

docs: Documentation

clean-docs:
	-rm -rf "$(SPHINX_BUILDDIR)"

lint: ruffcheck formatcheck apicheck configcheck

apicheck:
	(cd "$(SPHINX_DIR)"; $(MAKE) apicheck)

configcheck:
	true

ruffcheck:
	$(RUFF) check .

formatcheck:
	$(RUFF) format --check .

hooks:
	$(PRE_COMMIT) run --all-files

clean-pyc:
	-find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
	-find . -type d -name "__pycache__" | xargs rm -r

removepyc: clean-pyc

clean-build:
	rm -rf build/ dist/ .eggs/ *.egg-info/ .tox/ .coverage cover/

clean-git:
	$(GIT) clean -xdn

clean-git-force:
	$(GIT) clean -xdf

test-all: clean-pyc
	$(TOX)

test:
	pytest -xv --cov=django_celery_monitor --cov-report=term --cov-report=xml --no-cov-on-fail

build:
	$(PYTHON) -m build

distcheck: lint test clean

dist: clean-dist build
