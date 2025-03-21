"""A simple CLI tool to generate a python project configuration file."""

import argparse
import os
import sys
from pathlib import Path

import ujson5
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pydantic import ValidationError

from scaffoldpy import consts
from scaffoldpy.builders import build_basic_project
from scaffoldpy.models import (
    DEFAULT_PROJECT_CONFIG,
    Config,
    ProjectConfig,
    PydConfig,
    UserConfig,
)

DEV_MODE: bool = False


def prompt_for_user_config() -> UserConfig:
    """Prompt the user for configuration options."""
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

    config["min_py_version"] = inquirer.select(
        message="🐍 Select the minimum python version for your project:",
        choices=[
            Choice(value="3.9", name="3.9"),
            Choice(value="3.10", name="3.10"),
            Choice(value="3.8", name="3.11"),
            Choice(value="3.7", name="3.12"),
            Choice(value="3.6", name="3.13"),
        ],
        default="3.10",
    ).execute()

    config["layout"] = inquirer.select(
        message="📁 Select a layout for your project:",
        choices=[
            Choice(value="src"),
            Choice(value="flat"),
        ],
        default="src",
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
                value="vscode",
                name="Visual Studio Code (https://code.visualstudio.com/) 💻",
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


def dump_config(path: Path, config: Config) -> None:
    """Dump the configuration to a file."""
    with open(path, "w", encoding="utf8") as f:
        ujson5.dump(config, f, Config, indent=2)


def dump_schema(path: Path) -> None:
    """Dump the schema to a file."""
    with open(path, "w", encoding="utf8") as f:
        ujson5.dump(PydConfig.json_schema(), f, indent=2)


def copy_workspace_file(dest_folder: Path) -> None:
    """Copy a workspace file to the project directory."""
    workspace_file = Path(__file__).parent / consts.CONFIG_FOLDER / consts.SELF_WSP_FNAME
    destination = dest_folder / consts.SELF_WSP_FNAME
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(destination, "w", encoding="utf8") as f:
            f.write(workspace_file.read_text(encoding="utf8"))
    except FileNotFoundError as e:
        print(f"❌ Failed to copy workspace file: {e}")


def main() -> None:
    """Main entry point for the CLI tool."""
    main_args = argparse.ArgumentParser()
    main_args.add_argument(
        "-s",
        "--skip-config",
        action="store_true",
        help="Skip the configuration process and generate a basic project.",
    )

    if main_args.parse_args().skip_config:
        build_basic_project(
            {
                "user_config": {
                    "author": "John",
                    "author_email": "",
                },
                "project_config": DEFAULT_PROJECT_CONFIG,
            }
        )
        return

    if DEV_MODE:
        config_folder = Path(__file__).parent / consts.CONFIG_FOLDER
        config_path = config_folder / consts.SELF_CONFIG_FNAME
        user_config: UserConfig | None = None
        project_config: ProjectConfig = DEFAULT_PROJECT_CONFIG.copy()
    else:
        config_folder = _get_appdata_path() / "create_py_project"
        config_path = config_folder / consts.SELF_CONFIG_FNAME
        try:
            with open(config_path, "r", encoding="utf8") as f:
                config = PydConfig.validate_json(f.read())
                user_config = config["user_config"]
            print(f"🌟 Welcome back {user_config['author']}!")
        except FileNotFoundError:
            print("👋 Looks like you're running this tool for the first time.")
            print("Let's start by setting up your user configuration. 🛠️")
            user_config = None
            project_config = DEFAULT_PROJECT_CONFIG.copy()
            copy_workspace_file(config_folder)
        except ValidationError:
            print("⚠️ Looks like your configuration file is corrupt.")
            print("Don't worry! Let's set up your configuration again. 🛠️")
            user_config = None
            project_config = DEFAULT_PROJECT_CONFIG.copy()
    if user_config is None:
        user_config = prompt_for_user_config()
        project_config = prompt_for_project_config(project_config)
        dump_config(
            config_path,
            {
                "user_config": user_config,
                "project_config": project_config,
            },
        )
        print(f"✅ Configuration saved at {config_path}.")
        dump_schema(config_folder / consts.SELF_CONFIG_SCHEMA_FNAME)
    else:
        use_prev = inquirer.confirm(
            message="👀 Would you like to use your previous configuration?",
            default=True,
        ).execute()
        if not use_prev:
            print("No problem! Let's update your configuration. 🛠️")
            project_config = prompt_for_project_config(project_config)
            save_config = inquirer.confirm(
                message="💾 Would you like to save this configuration for future use?",
                default=True,
            ).execute()
            if save_config:
                dump_config(
                    config_path,
                    {
                        "user_config": user_config,
                        "project_config": project_config,
                    },
                )
                print(f"✅ Configuration saved at {config_path}.")
    build_basic_project(
        {
            "user_config": user_config,
            "project_config": project_config,
        }
    )


if __name__ == "__main__":
    DEV_MODE = True

    args = argparse.ArgumentParser()
    args.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update the configuration file and save configuration schema.",
    )
    args.add_argument(
        "-s",
        "--skip-config",
        action="store_true",
        help="Skip the configuration process and generate a basic project.",
    )

    parsed_args = args.parse_args()

    if parsed_args.update:
        config_folder_path = Path(__file__).parent / consts.CONFIG_FOLDER
        config_folder_path.mkdir(parents=True, exist_ok=True)
        dump_schema(config_folder_path / consts.SELF_CONFIG_SCHEMA_FNAME)
        dump_config(
            config_folder_path / consts.SELF_CONFIG_FNAME,
            {
                "user_config": {
                    "author": "",
                    "author_email": "",
                },
                "project_config": DEFAULT_PROJECT_CONFIG,
            },
        )
        print("✅ Configuration schema and default configuration updated.")
        sys.exit(0)
