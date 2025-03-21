"""Builders for creating a new Python project."""

import sys
from pathlib import Path

import toml

from . import consts, models

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

CODE_WORKSPACE_CONTENT = """{
    "folders": [
        {
            "path": "."
        }
    ],
    "settings": {
    }
}

"""


def build_toml(config: models.Config) -> models.ProjectToml:
    """Build a pyproject.toml file from a configuration."""
    if config["project_config"]["build_backend"] is not None:
        build_system: models.BuildSystem = {
            "build-backend": config["project_config"]["build_backend"],
            "requires": [config["project_config"]["build_backend"]],
        }
    else:
        build_system = {"requires": [], "build-backend": ""}

    project: models.ProjectTable = {
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

    dependency_groups: models.Dependencies = {
        "tests": ["pytest"],
        "static_checkers": [*config["project_config"]["static_code_checkers"]],
        "formatters": [*config["project_config"]["formatter"]],
        "docs": [config["project_config"]["docs"]] if config["project_config"]["docs"] else [],
    }

    return {
        "build-system": build_system,
        "project": project,
        "dependency-groups": dependency_groups,
        "tool": {},
    }


def build_pre_commit_config(config: models.Config, project_root: Path) -> None:
    """Build a pre-commit configuration file."""
    if config["project_config"]["pre_commit"]:
        with open(project_root / ".pre-commit-config.yaml", "w", encoding="utf-8") as f:
            f.write(PRE_COMMIT_CONTENT)


def build_static_checkers(config: models.Config, project_root: Path) -> None:
    """Build static code checkers configuration files."""
    with open(project_root / consts.PYPROJECT_TOML_FNAME, "r", encoding="utf-8") as f:
        project_toml: models.ProjectToml = toml.load(f)  # type: ignore

    file_config: bool = config["project_config"]["configuration_preference"] == "stand_alone"
    if "flake8" in config["project_config"]["static_code_checkers"]:
        with open(project_root / ".flake8", "w", encoding="utf-8") as f:
            f.write(f"[flake8]\nmax-line-length = {consts.DEFAULT_RULER_LEN}\n")

    if "mypy" in config["project_config"]["static_code_checkers"]:
        if file_config:
            with open(project_root / ".mypy.ini", "w", encoding="utf-8") as f:
                f.write("[mypy]\n\n")
        else:
            project_toml["tool"]["mypy"] = {"python_version": "3.12", "exclude": []}

    if "pyright" in config["project_config"]["static_code_checkers"]:
        if file_config:
            with open(project_root / "pyrightconfig.json", "w", encoding="utf-8") as f:
                f.write("{}\n\n")
        else:
            project_toml["tool"]["pyright"] = {}

    if "pylint" in config["project_config"]["static_code_checkers"]:
        if file_config:
            with open(project_root / ".pylintrc", "w", encoding="utf-8") as f:
                f.write("[MASTER]\n\n")
        else:
            project_toml["tool"]["pylint"] = {"disable": []}

    with open(project_root / consts.PYPROJECT_TOML_FNAME, "w", encoding="utf-8") as f:
        toml.dump(project_toml, f)


def build_formatter(config: models.Config, project_root: Path) -> None:
    """Build a formatter configuration file."""
    with open(project_root / consts.PYPROJECT_TOML_FNAME, "r", encoding="utf-8") as f:
        project_toml: models.ProjectToml = toml.load(f)  # type: ignore

    file_config: bool = config["project_config"]["configuration_preference"] == "stand_alone"
    if "ruff" in config["project_config"]["formatter"]:
        if file_config:
            with open(project_root / "ruff.toml", "w", encoding="utf-8") as f:
                f.write(RUFF_CONFIG_CONTENT)
        else:
            project_toml["tool"]["ruff"] = {
                "exclude": [],
                "line-length": consts.DEFAULT_RULER_LEN,
                "indent-width": 4,
                "lint": {"ignore": []},
                "format": {"quote-style": "double", "indent-style": "space"},
            }

    if "isort" in config["project_config"]["formatter"]:
        if file_config:
            with open(project_root / ".isort.cfg", "w", encoding="utf-8") as f:
                f.write("[settings]\n\n")
        else:
            project_toml["tool"]["isort"] = {}

    with open(project_root / consts.PYPROJECT_TOML_FNAME, "w", encoding="utf-8") as f:
        toml.dump(project_toml, f)


def build_editor_config(config: models.Config, project_root: Path) -> None:
    """Build a code editor configuration file."""
    if config["project_config"]["code_editor"] == "vs_code":
        with open(project_root / consts.SELF_WSP_FNAME, "w", encoding="utf-8") as f:
            f.write(CODE_WORKSPACE_CONTENT)


def build_docs(config: models.Config, project_root: Path) -> None:
    if config["project_config"]["docs"] is None:
        return
    if config["project_config"]["docs"] == "mkdocs":
        with open(project_root / "mkdocs.yml", "w", encoding="utf-8") as f:
            f.write("site_name: My Docs\n\n")
    elif config["project_config"]["docs"] == "sphinx":
        pass


def build_cloud_code_base(config: models.Config, project_root: Path) -> None:
    if config["project_config"]["cloud_code_base"] is None:
        return
    if config["project_config"]["cloud_code_base"] == "github":
        action_path = project_root / ".github" / "workflows"
        action_path.mkdir(parents=True)
        with open(project_root / ".github/workflows/main.yml", "w", encoding="utf-8") as f:
            f.write("name: CI\n\n")


def build_basic_project(config: models.Config) -> None:
    """Build a basic Python project."""
    print("🚧 Building your project...")
    project_root = consts.CWD / config["project_config"]["project_name"]
    if project_root.exists() and project_root.is_dir() and any(project_root.iterdir()):
        print(f"🚨 Project directory {project_root} already exists and is not empty.")
        sys.exit(1)

    project_toml: models.ProjectToml = build_toml(config)
    project_root.mkdir()
    with open(project_root / consts.PYPROJECT_TOML_FNAME, "w", encoding="utf-8") as f:
        toml.dump(project_toml, f)

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

    build_pre_commit_config(config, project_root)

    build_static_checkers(config, project_root)
    build_formatter(config, project_root)
    build_editor_config(config, project_root)
    build_docs(config, project_root)
    build_cloud_code_base(config, project_root)

    print(f"🎉 Project {config['project_config']['project_name']} created successfully.")
