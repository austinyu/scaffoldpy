"""Builders for creating a new Python project."""

import json
import subprocess
import sys
from pathlib import Path

import toml

from scaffoldpy import consts, models, templates


def build_toml(config: models.Config) -> models.ProjectToml:
    """Build a pyproject.toml file from a configuration."""
    if config["project_config"]["build_backend"] is not None:
        if config["project_config"]["build_backend"] == "Setuptools":
            build_system: models.BuildSystem = {
                "build-backend": "setuptools.build_meta",
                "requires": ["setuptools"],
            }
        elif config["project_config"]["build_backend"] == "Poetry-core":
            build_system = {
                "build-backend": "poetry.core.masonry.api",
                "requires": ["poetry-core"],
            }
        elif config["project_config"]["build_backend"] == "Hatchling":
            build_system = {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build",
            }
        elif config["project_config"]["build_backend"] == "PDM-backend":
            build_system = {"requires": ["pdm.backend"], "build-backend": "pdm.backend"}
        elif config["project_config"]["build_backend"] == "Flit-core":
            build_system = {
                "requires": ["flit-core"],
                "build-backend": "flit_core.buildapi",
            }
        else:
            raise NotImplementedError(
                f"Build backend {config['project_config']['build_backend']} not supported."
            )
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
        "formatters": [*config["project_config"]["formatters"]],
        "docs": (
            [config["project_config"]["docs"]] if config["project_config"]["docs"] else []
        ),
    }

    tool_config: dict[str, dict] = {}
    if config["project_config"]["build_backend"] == "Hatchling":
        tool_config["hatch"] = {
            "build": {
                "targets": {
                    "sdist": {
                        "include": ["README.md", "LICENSE", "CHANGELOG.md"],
                        "exclude": [],
                    },
                    "wheel": {
                        "packages": [f"src/{config['project_config']['project_name']}"],
                    },
                }
            }
        }

    return {
        "build-system": build_system,
        "project": project,
        "dependency-groups": dependency_groups,
        "tool": tool_config,
    }


def build_pre_commit_config(config: models.Config, project_root: Path) -> None:
    """Build a pre-commit configuration file."""
    if config["project_config"]["pre_commit"]:
        with open(project_root / ".pre-commit-config.yaml", "w", encoding="utf-8") as f:
            f.write(templates.PRE_COMMIT_CONTENT)


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
    if "ruff" in config["project_config"]["formatters"]:
        if file_config:
            with open(project_root / "ruff.toml", "w", encoding="utf-8") as f:
                f.write(templates.RUFF_CONFIG_CONTENT)
        else:
            project_toml["tool"]["ruff"] = {
                "exclude": [],
                "line-length": consts.DEFAULT_RULER_LEN,
                "indent-width": 4,
                "lint": {"ignore": []},
                "format": {"quote-style": "double", "indent-style": "space"},
            }

    if "isort" in config["project_config"]["formatters"]:
        if file_config:
            with open(project_root / ".isort.cfg", "w", encoding="utf-8") as f:
                f.write("[settings]\nprofile=black\n\n")
        else:
            project_toml["tool"]["isort"] = {
                "profile": "black",
                "line_length": consts.DEFAULT_RULER_LEN,
                "indent": 4,
            }

    with open(project_root / consts.PYPROJECT_TOML_FNAME, "w", encoding="utf-8") as f:
        toml.dump(project_toml, f)


def build_tests(config: models.Config, project_root: Path) -> None:
    """Build a test configuration file."""
    tests_folder = project_root / "tests"
    tests_folder.mkdir()
    with open(tests_folder / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    with open(project_root / consts.PYPROJECT_TOML_FNAME, "r", encoding="utf-8") as f:
        project_toml: models.ProjectToml = toml.load(f)  # type: ignore

    file_config: bool = config["project_config"]["configuration_preference"] == "stand_alone"

    if file_config:
        with open(project_root / "pytest.ini", "w", encoding="utf-8") as f:
            f.write(templates.PYTEST_CONFIG_CONTENT)
    else:
        project_toml["tool"]["pytest"] = {"addopts": templates.PYTEST_ADDOPTS}
    with open(project_root / consts.PYPROJECT_TOML_FNAME, "w", encoding="utf-8") as f:
        toml.dump(project_toml, f)


def build_editor_config(config: models.Config, project_root: Path) -> None:
    """Build a code editor configuration file."""
    if config["project_config"]["code_editor"] == "vscode":
        with open(
            project_root / f"{config['project_config']['project_name']}.code-workspace",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(templates.CODE_WORKSPACE_CONTENT, f, indent=2)


def build_docs(config: models.Config, project_root: Path) -> None:
    """Build a documentation configuration file."""
    docs_config: str | None = config["project_config"]["docs"]
    if config["project_config"]["docs"] is None:
        return
    if docs_config == "mkdocs":
        with open(project_root / "mkdocs.yml", "w", encoding="utf-8") as f:
            f.write(templates.build_mk_docs_config(config["project_config"]["project_name"]))
        docs_folder = project_root / "docs"
        docs_folder.mkdir()
        with open(docs_folder / "index.md", "w", encoding="utf-8") as f:
            f.write("# Documentation\n\n")
            f.write("This is the documentation for your project.\n\n")
    else:
        raise NotImplementedError(
            f"{docs_config} documentation generation is not yet implemented."
        )


def build_cloud_code_base(config: models.Config, project_root: Path) -> None:
    """Build a cloud code base configuration file."""
    if config["project_config"]["cloud_code_base"] is None:
        return
    if config["project_config"]["cloud_code_base"] == "github":
        action_path = project_root / ".github" / "workflows"
        action_path.mkdir(parents=True)
        with open(project_root / ".github/workflows/ci.yml", "w", encoding="utf-8") as f:
            f.write(templates.build_gh_action_ci(config["project_config"]["min_py_version"]))
        with open(project_root / ".github/workflows/release.yml", "w", encoding="utf-8") as f:
            f.write(
                templates.build_gh_action_release(config["project_config"]["project_name"])
            )


def build_vcs(project_root: Path) -> None:
    """Build a version control system configuration file."""
    # Create .gitignore file
    with open(project_root / ".gitignore", "w", encoding="utf-8") as f:
        f.write(templates.GITIGNORE_CONTENT)
    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=project_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=project_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["git", "branch", "-M", "main"],
            cwd=project_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to initialize git repository: {e}")
    print(f"📦 Git repository initialized at {project_root}.")


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
        f.write(templates.build_readme(config["project_config"]["project_name"]))

    if config["project_config"]["layout"] == "flat":
        src_folder = project_root / config["project_config"]["project_name"]
    else:
        src_folder = project_root / "src" / config["project_config"]["project_name"]
    src_folder.mkdir(parents=True)
    with open(src_folder / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    build_tests(config, project_root)

    build_pre_commit_config(config, project_root)

    build_static_checkers(config, project_root)
    build_formatter(config, project_root)
    build_editor_config(config, project_root)
    build_docs(config, project_root)
    build_cloud_code_base(config, project_root)
    build_vcs(project_root)

    print(f"🎉 Project {config['project_config']['project_name']} created successfully.")
