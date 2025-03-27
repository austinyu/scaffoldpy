"""Templates for scaffoldpy."""

from scaffoldpy import consts


def build_gh_action_ci(min_py_version: str) -> str:
    """Build GitHub Action CI configuration."""
    supported_python_versions = {
        "3.10": ["3.10", "3.11", "3.12", "3.13"],
        "3.11": ["3.11", "3.12", "3.13"],
        "3.12": ["3.12", "3.13"],
        "3.13": ["3.13"],
    }
    return (
        f"""name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: write

jobs:
  develop:
    strategy:
      fail-fast: false
      matrix:
        python-version: {supported_python_versions[min_py_version]}
        os: [ubuntu-latest, macos-latest, windows-latest]
    defaults:
      run:
        shell: bash
"""
        + """
    runs-on: ${{ matrix.os }}
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Fetch all history for all tags and branches

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Build package
        run: |
          python -m pip install --upgrade pip
          python -m pip install build
          python -m build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts-${{ runner.os }}-py${{ matrix.python-version }}
          path: dist/*

"""
    )


def build_gh_action_release(project_name: str) -> str:
    """Build GitHub Action release configuration."""
    return f"""name: release

on:
  release:
    types: [published]

permissions:
  contents: write
  id-token: write

jobs:
  release-build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Fetch all history for all tags and branches

      - uses: actions/setup-python@v5
        with:
          python-version: 3.x

      - name: Build release distributions
        run: |
          python -m pip install build
          python -m build

      - name: Upload distributions
        uses: actions/upload-artifact@v4
        with:
          name: release-dists
          path: dist/

  pypi-publish:
    runs-on: ubuntu-latest
    needs:
      - release-build
    environment:
      name: pypi
      url: https://pypi.org/project/{project_name}/

    steps:
      - name: Retrieve release distributions
        uses: actions/download-artifact@v4
        with:
          name: release-dists
          path: dist/

      - name: Publish release distributions to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: dist/

"""


def build_mk_docs_config(project_name: str) -> str:
    """Build mkdocs.yml configuration."""
    return f"""site_name: {project_name}
nav:
  - Home: index.md

"""


RUFF_CONFIG_CONTENT = f"""
exclude = []
line-length = {consts.DEFAULT_RULER_LEN}
indent-width = 4

[lint]
ignore = []

[format]
quote-style = \"double\"
indent-style = \"space\"

"""

PRE_COMMIT_CONTENT = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files

"""

CODE_WORKSPACE_CONTENT: dict = {
    "folders": [{"path": "."}],
    "settings": {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
        "pylint.interpreter": ["${workspaceFolder}/.venv/Scripts/python.exe"],
        "editor.rulers": [consts.DEFAULT_RULER_LEN],
        "mypy-type-checker.importStrategy": "fromEnvironment",
        "mypy-type-checker.interpreter": ["${workspaceFolder}/.venv/Scripts/python.exe"],
    },
}

PYTEST_ADDOPTS = (
    "--cov . --cov-report xml:tests/.coverage/cov.xml --cov-report html:tests/.coverage/html"
)

PYTEST_CONFIG_CONTENT = f"""[pytest]
; https://pytest-cov.readthedocs.io/en/latest/config.html
addopts = {PYTEST_ADDOPTS}

"""

GITIGNORE_CONTENT = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# pytest
.cache/

# Coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Built wheels
*.whl
dist/*

site/*

.venv/*
.benchmarks/*
.codspeed/*

demo/*
.venv/

_version.py
"""


def build_readme(project_name: str) -> str:
    """Build README.md configuration."""
    return f"""# {project_name}

This is a Python project scaffolded with scaffoldpy. Here is what you need to do next:
1. Install the dependencies: `uv sync`
2. Install the pre-commit hooks: `pre-commit install`
3. Create repo on Github
4. Run `git remote add origin https://github.com/austinyu/<repo-name>.git`
5. Push to remote: `git push -u origin main`
6. Register your project on PyPi
7. Release a new version on github.
8. Release pipeline will automatically publish the package to PyPi.

"""
