"""Utility functions for scaffoldpy."""

from pathlib import Path

import ujson5

from scaffoldpy.models import Config, PydConfig


def dump_config(path: Path, config: Config) -> None:
    """Dump the configuration to a file."""
    with open(path, "w", encoding="utf8") as f:
        ujson5.dump(config, f, Config, indent=2)


def dump_schema(path: Path) -> None:
    """Dump the schema to a file."""
    with open(path, "w", encoding="utf8") as f:
        ujson5.dump(PydConfig.json_schema(), f, indent=2)
