"""Constants for the create_py_project package."""

import os
from pathlib import Path

CONFIG_FOLDER = "_config"
README_FNAME = "README.md"
PYPROJECT_TOML_FNAME = "pyproject.toml"
SELF_CONFIG_FNAME: str = "config_create_py_project.json5"
SELF_CONFIG_SCHEMA_FNAME: str = "schema_create_py_project.json"
SELF_WSP_FNAME: str = "create-py-project.code-workspace"
CWD: Path = Path(os.getcwd())

DEFAULT_RULER_LEN = 95
