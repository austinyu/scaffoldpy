"""Builders for creating a new Python project."""

import sys
import toml

from .models import Config, ProjectToml
from . import consts


def build_toml(config: Config) -> ProjectToml:
    """Build a pyproject.toml file from a configuration."""
    project_toml: ProjectToml = {}
    if config["project_config"]["build_backend"] is not None:
        project_toml["build-system"] = {
            "build-backend": config["project_config"]["build_backend"],
            "requires": [config["project_config"]["build_backend"]],
        }

    project_toml["project"] = {
        "name": config["project_config"]["project_name"],
        "version": "0.0.0",
        "description": "",
        "readme": consts.README_FNAME,
        "requires-python": f">={config['project_config']['min_py_version']}",
        "license": config["project_config"]["pkg_license"],
        "license-files": [],
        "authors": [
            {
                "name": config["user_config"]["author"],
                "email": config["user_config"]["author_email"],
            }
        ],
        "maintainers": [
            {
                "name": config["user_config"]["author"],
                "email": config["user_config"]["author_email"],
            }
        ],
        "keywords": [],
        "classifiers": [],
        "urls": {
            "homepage": "https://todo.com",
            "source": "https://todo.com",
            "download": "https://todo.com",
            "changelog": "https://todo.com",
            "releasenotes": "https://todo.com",
            "documentation": "https://todo.com",
            "issues": "https://todo.com",
            "funding": "https://todo.com",
        },
        "dependencies": [],
        "optional-dependencies": {},
        "dynamic": [],
    }

    project_toml["dependency-groups"] = {
        "tests": ["pytest"],
        "static_checkers": [*config["project_config"]["static_code_checkers"]],
        "formatters": [*config["project_config"]["formatter"]],
        "docs": [config["project_config"]["docs"]] if config["project_config"]["docs"] else [],
    }

    project_toml["tool"] = {}

    toml_config: bool = \
        config["project_config"]["configuration_preference"] == "pyproject_toml"
    if "mypy" in config["project_config"]["static_code_checkers"] and toml_config:
        project_toml["tool"]["mypy"] = {
            "python_version": "3.12",
            "exclude ": []
        }

    return project_toml


def build_basic_project(config: Config) -> None:
    """Build a basic Python project."""
    project_root = consts.CWD / config["project_config"]["project_name"]
    if project_root.exists() and project_root.is_dir() and any(project_root.iterdir()):
        print(f"🚨 Project directory {project_root} already exists and is not empty.")
        sys.exit(1)
    with open(project_root / "pyproject.toml", "w", encoding="utf-8") as f:
        toml.dump(build_toml(config), f)
    with open(project_root / consts.README_FNAME, "w", encoding="utf-8") as f:
        f.write(f"# {config['project_config']['project_name']}\n\n")
    if config["project_config"]["layout"] == "flat":
        src_folder = project_root / config["project_config"]["project_name"]
    else:
        src_folder = project_root / "src" / config["project_config"]["project_name"]
    src_folder.mkdir(parents=True)
    with open(src_folder / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")
    tests_folder = project_root / "tests"
    tests_folder.mkdir()
    with open(tests_folder / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    file_config: bool = config["project_config"]["configuration_preference"] == "stand_alone"
    if "flake8" in config["project_config"]["static_code_checkers"]:
        with open(project_root / ".flake8", "w", encoding="utf-8") as f:
            f.write("[flake8]\nmax-line-length = 95\n")

    if "mypy" in config["project_config"]["static_code_checkers"] and file_config:
        with open(project_root / ".mypy.ini", "w", encoding="utf-8") as f:
            f.write("[mypy]\n\n")
    print(f"🎉 Project {config['project_config']['project_name']} created successfully.")
