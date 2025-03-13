"""A simple CLI tool to generate a python project configuration file."""

from typing import Literal, TypedDict
import argparse

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


class Config(TypedDict):
    """A configuration for a python project."""
    project_name: str
    pkg_license: Literal["MIT", "GPL", "Apache", "BSD", "Proprietary"]
    build_backend: (
        Literal["Poetry-core", "Setuptools", "Hatchling", "PDM-backend", "Flit-core"] | None
    )
    dependency_manager: Literal["poetry", "uv", "pipenv", "hatch"]
    flake8: bool
    mypy: bool
    pyright: bool
    pylint: bool
    formatter: list[Literal["black", "ruff", "isort"]]
    spell_checker: Literal["cspell", "codespell"] | None
    docs: Literal["mkdocs", "sphinx"] | None
    vs_code: bool
    pre_commit: bool
    cloud_code_base: Literal["github", "gitlab"] | None


DEFAULT_CONFIG: Config = {
    "project_name": "",
    "pkg_license": "MIT",
    "build_backend": "Hatchling",
    "dependency_manager": "uv",
    "flake8": True,
    "mypy": True,
    "pyright": True,
    "pylint": True,
    "formatter": ["black", "isort"],
    "spell_checker": "cspell",
    "docs": "mkdocs",
    "vs_code": True,
    "pre_commit": True,
    "cloud_code_base": "github",
}


def prompt_for_config(config: Config) -> Config:
    """Prompt the user for configuration options."""
    config["build_backend"] = inquirer.select(
        message="Select a build-backend for your package:",
        choices=[
            Choice(
                value="Hatchling",
                name="Hatchling (https://pypi.org/project/hatchling/)",
            ),
            Choice(
                value="Setuptools",
                name=(
                    "Setuptools "
                    + "(https://packaging.python.org/en/latest/key_projects/#setuptools)"
                ),
            ),
            Choice(
                value="Poetry-core",
                name="Poetry-core (https://pypi.org/project/poetry-core/)",
            ),
            Choice(
                value="PDM-backend",
                name="PDM-backend (https://backend.pdm-project.org/)",
            ),
            Choice(
                value="Flit-core",
                name="Flit-core (https://flit.pypa.io/en/stable/pyproject_toml.html)",
            ),
            Choice(value=None, name="No build-backend"),
        ],
        default="Hatchling",
        long_instruction=(
            "Build backends are used to build and distribute your project as a package. "
            + "If you do not need to distribute your project, "
            + "you can select 'No build-backend'."
        ),
    ).execute()

    # static code analysis
    config["flake8"] = inquirer.confirm(
        message="Do you want to enable flake8 for linting?", default=True
    ).execute()
    config["mypy"] = inquirer.confirm(
        message="Do you want to enable mypy for static type checking?", default=True
    ).execute()
    config["pyright"] = inquirer.confirm(
        message="Do you want to enable pyright for static type checking?", default=True
    ).execute()
    config["pylint"] = inquirer.confirm(
        message="Do you want to enable pylint for linting?", default=True
    ).execute()

    config["formatter"] = inquirer.checkbox(
        message="Select formatters for your project:",
        choices=[
            Choice(
                value="ruff",
                name="ruff (https://docs.astral.sh/ruff/formatter/)",
                enabled=True,
            ),
            Choice(
                value="isort",
                name="isort (https://pycqa.github.io/isort/)",
                enabled=True,
            ),
            Choice(
                value="black",
                name="black (https://black.readthedocs.io/en/stable/)",
                enabled=False,
            ),
        ],
        default=["ruff", "isort"],
        instruction="Use space to select, up/down to move, enter to confirm.",
    ).execute()
    config["spell_checker"] = inquirer.select(
        message="Select a spell checker for your project:",
        choices=[
            Choice(value="cspell", name="cspell (https://cspell.org/)"),
            Choice(
                value="codespell",
                name="codespell (https://github.com/codespell-project/codespell)",
            ),
            Choice(value=None, name="No spell checker"),
        ],
        default="cspell",
    ).execute()
    config["docs"] = inquirer.select(
        message="Select a documentation generator for your project:",
        choices=[
            Choice(value="mkdocs", name="mkdocs (https://www.mkdocs.org/)"),
            Choice(value="sphinx", name="sphinx (https://www.sphinx-doc.org/)"),
            Choice(value=None, name="No documentation generator"),
        ],
        default="mkdocs",
    ).execute()

    config["vs_code"] = inquirer.confirm(
        message="Do you want to generate a vs code work-space file?",
        default=True,
    ).execute()

    config["pre_commit"] = inquirer.confirm(
        message="Do you want to generate a pre-commit configuration file?",
        default=True,
    ).execute()

    config["cloud_code_base"] = inquirer.select(
        message="Select a cloud code base for your project:",
        choices=[
            Choice(value="github", name="GitHub (hhttps://github.com/)"),
            Choice(value="gitlab", name="GitLab (https://about.gitlab.com/)"),
            Choice(value=None, name="No cloud code base"),
        ],
        default="github",
        long_instruction=(
            "Cloud code bases are used to host your project's source code. "
            + "If you do not want to host your project's source code, "
            + "you can select 'No cloud code base'."
        ),
    ).execute()

    return config


def main():
    """Main entry point for the CLI tool."""
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d",
        "--default-config",
        action="store_true",
        help="Use the default configuration without prompting for inputs.",
    )
    parsed_args = args.parse_args()
    config = DEFAULT_CONFIG.copy()
    config["project_name"] = inquirer.text(
        message="What's your python project name:",
        validate=lambda result: len(result) > 0,
        invalid_message="Project name cannot be empty.",
    ).execute()

    if not parsed_args.default_config:
        config = prompt_for_config(config)


if __name__ == "__main__":
    main()
