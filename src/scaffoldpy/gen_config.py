"""Dump configuration schema and default configuration to config folder."""

from pathlib import Path

from scaffoldpy import consts
from scaffoldpy.configs import DEFAULT_PROJECT_CONFIG
from scaffoldpy.utils import dump_config, dump_schema

if __name__ == "__main__":
    config_folder_path = Path(__file__).parent / consts.CONFIG_FOLDER
    config_folder_path.mkdir(parents=True, exist_ok=True)
    config_path: Path = config_folder_path / consts.SELF_CONFIG_FNAME
    schema_path: Path = config_folder_path / consts.SELF_CONFIG_SCHEMA_FNAME
    dump_schema(schema_path)
    dump_config(
        config_path,
        {
            "user_config": {
                "author": "",
                "author_email": "",
            },
            "project_config": DEFAULT_PROJECT_CONFIG,
        },
    )
    print(f"✅ Default configuration updated at {config_path}.")
    print(f"✅ Configuration schema updated at {schema_path}.")
