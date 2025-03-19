"""Constants for the create_py_project package."""

import os
from pathlib import Path

README_FNAME = "README.md"
SELF_CONFIG_FNAME: str = "config_create_py_project.json5"
SELF_CONFIG_SCHEMA_FNAME: str = "schema_create_py_project.json"
SELF_WSP_FNAME: str = "create-py-project.code-workspace"
CWD: Path = Path(os.getcwd())
