"""A simple CLI tool to generate a python project configuration file."""

from typing import Literal
import argparse
import os
import sys
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import pydantic
import ujson5

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


DEV_MODE: bool = False
CONFIG_FNAME: str = "config_create_py_project.json5"
CONFIG_SCHEMA_FNAME: str = "schema_create_py_project.json"
DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / CONFIG_FNAME


class ProjectConfig(TypedDict):
    """A configuration for a python project."""

    project_name: str
    pkg_license: Literal["MIT", "GPL", "Apache", "BSD", "Proprietary"]
    # build backends are used to build and distribute your project as a package
    build_backend: (
        Literal["Poetry-core", "Setuptools", "Hatchling", "PDM-backend", "Flit-core"] | None
    )
    # dependency managers are used to manage your project's dependencies
    dependency_manager: Literal["poetry", "uv", "pipenv", "hatch"]
    # static code checkers are used to check your code for errors
    static_code_checkers: list[Literal["flake8", "mypy", "pyright", "pylint"]]
    # formatters are used to format your code
    formatter: list[Literal["black", "ruff", "isort"]]
    # spell checkers are used to check spelling in your code
    spell_checker: Literal["cspell", "codespell"] | None
    # documentation generators are used to generate documentation for your project
    docs: Literal["mkdocs", "sphinx"] | None
    # code editors are used to edit your code
    code_editor: Literal["vs_code"] | None
    # pre-commit is used to run checks before committing code
    pre_commit: bool
    # cloud code bases are used to host your project's source code
    cloud_code_base: Literal["github"] | None


class UserConfig(TypedDict):
    """A configuration for a user."""

    author: str
    author_email: str


class Config(TypedDict):
    """A configuration for a python project."""

    user_config: UserConfig | None
    project_config: ProjectConfig


PydConfig = pydantic.TypeAdapter(Config)

DEFAULT_PROJECT_CONFIG: ProjectConfig = {
    "project_name": "",
    "pkg_license": "MIT",
    "build_backend": "Hatchling",
    "dependency_manager": "uv",
    "static_code_checkers": ["flake8", "mypy", "pyright", "pylint"],
    "formatter": ["black", "isort"],
    "spell_checker": "cspell",
    "docs": "mkdocs",
    "code_editor": "vs_code",
    "pre_commit": True,
    "cloud_code_base": "github",
}

DEFAULT_CONFIG: Config = {
    "user_config": None,
    "project_config": DEFAULT_PROJECT_CONFIG,
}


def prompt_for_user_config() -> UserConfig:
    """Prompt the user for configuration options."""
    print("👋 Looks like you're running this tool for the first time.")
    print("Let's start by setting up your user configuration. 🛠️")
    author: str = inquirer.text(
        message="👤 What's your name:",
        validate=lambda result: len(result) > 0,
        invalid_message="Author name cannot be empty.",
    ).execute()

    author_email: str = inquirer.text(
        message="📧 What's your email address:",
        validate=lambda result: len(result) > 0,
        invalid_message="Author email cannot be empty.",
    ).execute()

    return {
        "author": author,
        "author_email": author_email,
    }


def prompt_for_project_config(config: ProjectConfig) -> ProjectConfig:
    """Prompt the user for configuration options."""

    config["project_name"] = inquirer.text(
        message="🐍 What's your python project name:",
        validate=lambda result: len(result) > 0,
        invalid_message="Project name cannot be empty.",
    ).execute()

    config["build_backend"] = inquirer.select(
        message="🔧 Select a build-backend for your package:",
        choices=[
            Choice(
                value="Hatchling",
                name="Hatchling (https://pypi.org/project/hatchling/) 🐣",
            ),
            Choice(
                value="Setuptools",
                name=(
                    "Setuptools "
                    + "(https://packaging.python.org/en/latest/key_projects/#setuptools) 🛠️"
                ),
            ),
            Choice(
                value="Poetry-core",
                name="Poetry-core (https://pypi.org/project/poetry-core/) 🎭",
            ),
            Choice(
                value="PDM-backend",
                name="PDM-backend (https://backend.pdm-project.org/) 📦",
            ),
            Choice(
                value="Flit-core",
                name="Flit-core (https://flit.pypa.io/en/stable/pyproject_toml.html) 🚀",
            ),
            Choice(value=None, name="No build-backend ❌"),
        ],
        default="Hatchling",
        long_instruction=(
            "Build backends are used to build and distribute your project as a package. "
            + "If you do not need to distribute your project, "
            + "you can select 'No build-backend'."
        ),
    ).execute()

    # static code analysis
    config["static_code_checkers"] = inquirer.checkbox(
        message="🔍 Select static code checkers for your project:",
        choices=[
            Choice(
                value="flake8",
                name="flake8 (https://flake8.pycqa.org/en/latest/) 🐍",
                enabled=True,
            ),
            Choice(
                value="mypy",
                name="mypy (https://mypy-lang.org/) 🧙‍♂️",
                enabled=True,
            ),
            Choice(
                value="pyright",
                name="pyright (https://github.com/microsoft/pyright) 🔍",
                enabled=True,
            ),
            Choice(
                value="pylint",
                name="pylint (https://www.pylint.org/) 🛠️",
                enabled=True,
            ),
        ],
        default=["flake8", "mypy", "pyright", "pylint"],
        instruction="Use space to select, up/down to move, enter to confirm.",
    ).execute()

    config["formatter"] = inquirer.checkbox(
        message="🎨 Select formatters for your project:",
        choices=[
            Choice(
                value="ruff",
                name="ruff (https://docs.astral.sh/ruff/formatter/) 🦊",
                enabled=True,
            ),
            Choice(
                value="isort",
                name="isort (https://pycqa.github.io/isort/) 📜",
                enabled=True,
            ),
            Choice(
                value="black",
                name="black (https://black.readthedocs.io/en/stable/) 🖤",
                enabled=False,
            ),
        ],
        default=["ruff", "isort"],
        instruction="Use space to select, up/down to move, enter to confirm.",
    ).execute()
    config["spell_checker"] = inquirer.select(
        message="🔍 Select a spell checker for your project:",
        choices=[
            Choice(value="cspell", name="cspell (https://cspell.org/) 📝"),
            Choice(
                value="codespell",
                name="codespell (https://github.com/codespell-project/codespell) 🧙‍♂️",
            ),
            Choice(value=None, name="No spell checker ❌"),
        ],
        default="cspell",
    ).execute()
    config["docs"] = inquirer.select(
        message="📚 Select a documentation generator for your project:",
        choices=[
            Choice(value="mkdocs", name="mkdocs (https://www.mkdocs.org/) 📖"),
            Choice(value="sphinx", name="sphinx (https://www.sphinx-doc.org/) 🐍"),
            Choice(value=None, name="No documentation generator ❌"),
        ],
        default="mkdocs",
    ).execute()

    config["code_editor"] = inquirer.select(
        message="📝 Select a code editor for your project:",
        choices=[
            Choice(
                value="vscode", name="Visual Studio Code (https://code.visualstudio.com/) 💻"
            ),
            Choice(value=None, name="No code editor ❌"),
        ],
        default="vscode",
    ).execute()

    config["pre_commit"] = inquirer.confirm(
        message="🔧 Do you want to generate a pre-commit configuration file?",
        default=True,
    ).execute()

    config["cloud_code_base"] = inquirer.select(
        message="☁️ Select a cloud code base for your project:",
        choices=[
            Choice(value="github", name="GitHub (https://github.com/) 🐙"),
            Choice(value=None, name="No cloud code base ❌"),
        ],
        default="github",
        long_instruction=(
            "Cloud code bases are used to host your project's source code. "
            + "If you do not want to host your project's source code, "
            + "you can select 'No cloud code base'."
        ),
    ).execute()

    return config


def _get_appdata_path() -> Path:
    temp_appdata_path = os.getenv("APPDATA")
    if temp_appdata_path is not None:
        return Path(temp_appdata_path)
    if os.name == "nt":  # Windows
        appdata_path = os.getenv("APPDATA")
        if appdata_path is None:
            raise EnvironmentError("APPDATA environment variable is not set.")
        return Path(appdata_path)
    elif os.name == "posix":  # Linux and macOS
        if "darwin" in os.uname().sysname.lower():  # type: ignore
            return Path(os.path.expanduser("~/Library/Application Support"))
        else:  # Linux
            return Path(os.path.expanduser("~/.config"))
    else:
        raise OSError("Unsupported operating system")


def build_project(config: Config) -> None:
    """Build a python project based on the configuration."""
    print("🚧 Building your project...")


def main():
    """Main entry point for the CLI tool."""
    if DEV_MODE:
        config_path = Path(__file__) / CONFIG_FNAME
        valid_config = DEFAULT_CONFIG.copy()
    else:
        config_path = _get_appdata_path() / "create_py_project" / CONFIG_FNAME
        if config_path.exists():
            with open(config_path, "r", encoding="utf8") as f:
                valid_config = PydConfig.validate_json(f.read())
        else:
            valid_config = DEFAULT_CONFIG.copy()
    if valid_config["user_config"] is None:
        valid_config["user_config"] = prompt_for_user_config()
        valid_config["project_config"] = prompt_for_project_config(
            valid_config["project_config"]
        )
    else:
        print(f"👋 Welcome back {valid_config['user_config']['author']}!")
        use_prev = inquirer.confirm(
            message="👀 Would you like to use your previous configuration?", default=True
        ).execute()
        if not use_prev:
            print("No problem! Let's update your configuration. 🛠️")
            valid_config["project_config"] = prompt_for_project_config(
                valid_config["project_config"]
            )
            save_config = inquirer.confirm(
                message="💾 Would you like to save this configuration for future use?",
                default=True,
            ).execute()
            if save_config:
                with open(config_path, "w", encoding="utf8") as f:
                    ujson5.dump(valid_config, f, Config, indent=2)
    print(valid_config)
    build_project(valid_config)


if __name__ == "__main__":
    DEV_MODE = True

    args = argparse.ArgumentParser()
    args.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update the configuration file and save configuration schema.",
    )

    parsed_args = args.parse_args()

    if parsed_args.update:
        with open(Path(__file__).parent / CONFIG_SCHEMA_FNAME, "w", encoding="utf8") as f:
            ujson5.dump(PydConfig.json_schema(), f, indent=2)
        with open(DEFAULT_CONFIG_PATH, "w", encoding="utf8") as f:
            ujson5.dump(DEFAULT_CONFIG, f, Config, indent=2)
        print("✅ Configuration schema and default configuration updated.")
        sys.exit(0)

    main()
