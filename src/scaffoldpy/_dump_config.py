"""Dump configuration schema and default configuration to config folder."""

from pathlib import Path

from scaffoldpy import consts
from scaffoldpy.models import DEFAULT_PROJECT_CONFIG
from scaffoldpy.utils import dump_config, dump_schema

if __name__ == "__main__":
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
