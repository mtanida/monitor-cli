"""
Implements Container Monitor CLI

CLI is used to start/stop/configure container monitoring service

Author:
    Masatoshi Tanida

Date:
    2023/11/24
"""

import os
import typer

from monitorcli.configure import config, config_app
from monitorcli.docker import ContainerMonitor
from pathlib import Path

app = typer.Typer()
app.add_typer(config_app, name="config", help="configure monitor services")

target_container = config["target-container-name"]
monitor = ContainerMonitor(target_container)


@app.command()
def start() -> None:
    """
    Start monitoring service.
    """
    print("start monitoring")
    monitor.start_monitor()


@app.command()
def stop() -> None:
    """
    Stop monitoring service.
    """
    print("stop monitoring")
    monitor.stop_monitor()


if __name__ == "__main__":
    app()
