"""
Container monitor script

Uses Docker API to get stats about a running container and outputs resource
usage stats to CSV file. The target container to monitor can be set via
command line argument. The script is designed to run even if the target
container is not running. For example, if the target container is manually
stopped, this script will continue to run and resume logging once the target
container is started again.

Author:
    Masatoshi Tanida

Date:
    2023/11/24
"""
import argparse
import csv
import json
import os
import signal
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, IO

import requests_unixsocket

DEFAULT_CONTAINER_TO_MONITOR = "nginx-alpine"
DEFAULT_LOG_DIR = Path("/mnt/log")
BACKOFF_SECONDS = 1

FIELDS = [
    "timestamp",
    "percent_cpu_usage",
    "used_memory",
]

continue_monitoring = True


def signal_handler(signum, frame) -> None:
    """
    Signal hanlder for proper shutdown
    """
    global continue_monitoring
    continue_monitoring = False


def write_csv_row(csv_writer: csv.DictWriter, data: Dict[str, Any]) -> None:
    """
    Writes a row of data to CSV file

    Args:
        csv_writer (csv.DictWriter): CSV writer object
        data (Dict[str, Any]): JSON object with container stats
    """
    timestamp = data["read"]
    used_memory = data["memory_stats"]["usage"] - data["memory_stats"]["stats"]["cache"]
    cpu_delta = (
        data["cpu_stats"]["cpu_usage"]["total_usage"]
        - data["precpu_stats"]["cpu_usage"]["total_usage"]
    )
    system_cpu_delta = (
        data["cpu_stats"]["system_cpu_usage"] - data["precpu_stats"]["cpu_usage"]["total_usage"]
    )
    number_cpus = data["cpu_stats"]["online_cpus"]
    cpu_usage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0
    row = {
        "timestamp": timestamp,
        "percent_cpu_usage": cpu_usage,
        "used_memory": used_memory,
    }
    csv_writer.writerow(row)


def monitor_container(f: IO, csv_writer: csv.DictWriter, target_container: str) -> None:
    """
    Reads streaming stats for target container using Docker API and writes to CSV

    Args:
        f (IO): file descriptor for CSV file - used so we can flush writes
        csv_writer (csv.DictWriter): CSV writer object
        target_container (str): Name or id of container to monitor
    """
    print(f"Container to monitor: {target_container}", flush=True)
    api_url = f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/{target_container}/stats"
    session = requests_unixsocket.Session()
    response = session.get(api_url, stream=True)
    if response.ok:
        for line in response.iter_lines():
            if not continue_monitoring:
                break
            data = json.loads(line.decode("utf-8"))
            write_csv_row(csv_writer, data)
            f.flush()


def run_monitor_loop(target_container: str, out_file_path: Path) -> None:
    """
    Starts the main monitor loop

    Args:
        target_container (str): Name or id of container to monitor
        out_file_path (Path): CSV output file path
    """
    print(f"Writing to {out_file_path}")
    with open(out_file_path, "w", newline="") as f:
        csv_writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter="|")
        csv_writer.writeheader()
        while continue_monitoring:
            try:
                monitor_container(f, csv_writer, target_container)
            except Exception as e:
                print("Exception: {}".format(e))
            finally:
                # backoff for a period
                time.sleep(BACKOFF_SECONDS)


def main() -> None:
    """
    Application main function
    """
    parser = argparse.ArgumentParser("Monitors a container's stats and logs to file.")
    parser.add_argument(
        "--container",
        default=DEFAULT_CONTAINER_TO_MONITOR,
        help="Name or ID of container to monitor",
    )
    parser.add_argument("--log", help="output log file path")
    args = parser.parse_args()

    target_container = args.container

    datetime_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    out_file_path = args.log or DEFAULT_LOG_DIR / f"{target_container}_{datetime_str}.csv"
    run_monitor_loop(target_container, out_file_path)
    print("Exiting...")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
