"""
Implements 'config' subcommand and saving/restoring of configuration settings.

Author:
    Masatoshi Tanida

Date:
    2023/11/24
"""

from pathlib import Path

import typer
import yaml

DEFAULT_CONFIG_DIR_PATH = Path.home() / ".config"
DEFAULT_CONFIG_FILE_PATH = DEFAULT_CONFIG_DIR_PATH / "container-monitor.yaml"
DEFAULT_CONFIG = {
    "target-container-name": "nginx-alpine",
}

# Typer subcommand
config_app = typer.Typer()

# Initialize config data
config = []
if DEFAULT_CONFIG_FILE_PATH.exists():
    with open(DEFAULT_CONFIG_FILE_PATH, "r") as f:
        config = yaml.safe_load(f)

if not config:
    # use default configuration if empty
    config = DEFAULT_CONFIG


@config_app.command()
def list() -> None:
    """
    List all config parameters
    """
    print(config)


@config_app.command()
def get(key: str) -> None:
    """
    Get config parameter

    Usage:
      monitor-cli config get <key>
    """
    print(config[key])


@config_app.command()
def set(key: str, value: str) -> None:
    """
    Set config parameter

    Usage:
      monitor-cli config set <key> <value>
    """
    config[key] = value

    if not DEFAULT_CONFIG_DIR_PATH.exists():
        DEFAULT_CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)

    with open(DEFAULT_CONFIG_FILE_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
