from __future__ import annotations

import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

from scaffoldpy import config

PluginConfig = TypeVar("PluginConfig", bound=type[BaseModel])


class BaseConfig(BaseModel):
    project_root: Path
    project_name: str
    user_config: config.UserConfig


class Plugin(Generic[PluginConfig]):
    Config: PluginConfig
    dependencies: list[type[Plugin]]

    @staticmethod
    def build(base_config: BaseConfig, plugin_config: PluginConfig) -> None:
        raise NotImplementedError("Plugin must implement build method")


class Core(Plugin):
    class Config(BaseModel):
        layout: Literal["src", "flat"]

    dependencies = []

    @staticmethod
    def build(base_config: BaseConfig, plugin_config: Core.Config) -> None:
        project_root: Path = base_config.project_root

        if project_root.exists() and project_root.is_dir() and any(project_root.iterdir()):
            print(f"🚨 Project directory {project_root} already exists and is not empty.")
            sys.exit(1)
        project_folder_name: str = base_config.project_name.replace("-", "_")
        if plugin_config.layout == "flat":
            src_folder = project_root / project_folder_name
        else:
            src_folder = project_root / "src" / project_folder_name

        src_folder.mkdir(parents=True)


class ReadMe(Plugin):
    class Config(BaseModel):
        pass

    dependencies = [Core]

    @staticmethod
    def build(base_config: BaseConfig, plugin_config: ReadMe.Config) -> None:
        readme_file = base_config.project_root / "README.md"
        with open(readme_file, "w") as f:
            f.write(f"""# {base_config.project_name}

This is a Python project scaffolded with scaffoldpy. Here is what you need to do next:
1. Install the dependencies: `uv sync`
2. Install the pre-commit hooks: `pre-commit install`
3. Create repo on Github
4. Run `git remote add origin https://github.com/<user-name>/<repo-name>.git`
5. Push to remote: `git push -u origin main`
6. Register your project on PyPi
7. Release a new version on github.
8. Release pipeline will automatically publish the package to PyPi.

""")


class PyProjectToml(Plugin):
    class Config(BaseModel):
        dynamic_version: bool

    dependencies = [Core]

    @staticmethod
    def build(base_config: BaseConfig, plugin_config: PyProjectToml.Config) -> None:
        pyproject_file = base_config.project_root / "pyproject.toml"
        with open(pyproject_file, "w") as f:
            f.write("")


class PluginDependencyGraph:
    def __init__(self) -> None:
        self._graph: dict[type[Plugin], list[type[Plugin]]] = defaultdict(list)
        self._plugins: set[type[Plugin]] = set()

    def add_plugin(self, plugin: type[Plugin]) -> None:
        for dep in plugin.dependencies:
            self._graph[dep].append(plugin)
            self._plugins.add(dep)
        self._plugins.add(plugin)

    def get_build_order(self) -> list[type[Plugin]]:
        # Calculate in-degrees of all nodes
        in_degree = {node: 0 for node in self._plugins}
        for dependencies in self._graph.values():
            for dependent in dependencies:
                in_degree[dependent] += 1

        # Collect nodes with no incoming edges
        queue = deque([node for node in self._plugins if in_degree[node] == 0])
        build_order = []

        while queue:
            current = queue.popleft()
            build_order.append(current)

            # Reduce in-degree for all neighbors
            for neighbor in self._graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If build_order doesn't contain all nodes, there's a cycle
        if len(build_order) != len(self._plugins):
            raise ValueError("Cycle detected in dependencies!")

        return build_order
