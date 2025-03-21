"""Models for the create_py_project package."""

import sys
from typing import Any, Literal

import pydantic

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class ProjectConfig(TypedDict):
    """A configuration for a python project."""

    project_name: str
    pkg_license: Literal["MIT", "GPL", "Apache", "BSD", "Proprietary"]
    # build backends are used to build and distribute your project as a package
    build_backend: (
        Literal["Poetry-core", "Setuptools", "Hatchling", "PDM-backend", "Flit-core"] | None
    )
    min_py_version: str
    layout: Literal["src", "flat"]
    configuration_preference: Literal["stand_alone", "pyproject_toml"]
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

    user_config: UserConfig
    project_config: ProjectConfig


PydConfig = pydantic.TypeAdapter(Config)

DEFAULT_PROJECT_CONFIG: ProjectConfig = {
    "project_name": "example",
    "pkg_license": "MIT",
    "min_py_version": "3.10",
    "layout": "src",
    "configuration_preference": "stand_alone",
    "build_backend": "Hatchling",
    "dependency_manager": "uv",
    "static_code_checkers": ["flake8", "mypy", "pyright", "pylint"],
    "formatter": ["ruff", "isort"],
    "spell_checker": "cspell",
    "docs": "mkdocs",
    "code_editor": "vs_code",
    "pre_commit": True,
    "cloud_code_base": "github",
}

BuildSystem = TypedDict("BuildSystem", {"requires": list[str], "build-backend": str})
NameContact = TypedDict("NameContact", {"name": str, "email": str})
ProjectUrls = TypedDict(
    "ProjectUrls",
    {
        "homepage": str,
        "source": str,
        "download": str,
        "changelog": str,
        "releasenotes": str,
        "documentation": str,
        "issues": str,
        "funding": str,
    },
    total=False,
)
Dependencies = dict[str, list[str]]

ProjectTable = TypedDict(
    "ProjectTable",
    {
        "name": str,
        "version": str,
        "description": str,
        "readme": str,
        "requires-python": str,
        "license": str,
        "license-files": list[str],
        "authors": list[NameContact],
        "maintainers": list[NameContact],
        "keywords": list[str],
        "classifiers": list[str],
        "urls": ProjectUrls,
        "scripts": Any,
        "entry-points": Any,
        "gui-scripts": Any,
        "dependencies": list[str],
        "optional-dependencies": Dependencies,
        "dynamic": list[str],
    },
    total=False,
)

ProjectToml = TypedDict(
    "ProjectToml",
    {
        "build-system": BuildSystem,
        "project": ProjectTable,
        "dependency-groups": Dependencies,
        "tool": Any,
    },
)
