"""
Implements Container CLI

CLI is used to monitor a container's resource usage and log to a user-specified file.

Author:
    Masatoshi Tanida

Date:
    2023/11/21
"""

from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote_plus

import requests_unixsocket

DOCKER_SOCKET = "/var/run/docker.sock"
BASE_URL = f"http+unix://{quote_plus(DOCKER_SOCKET)}"
MONITOR_SERVICE_CONTAINER_IMAGE = "monitor-srv:latest"
PROJECT_DIR = Path(__file__).absolute().parent.parent


class ContainerMonitor:
    """
    Encapsulates interface for starting/stopping container monitor service

    Attributes:
        target_container (str): Name of the container to monitor
    """

    def __init__(self, target_container: str):
        """
        Constructor for ContainerMonitor
        """
        self.target_container = target_container

    def _get_container(self, stopped: bool = False) -> Dict[str, Any]:
        """
        Gets information about monitor service

        Args:
            stopped (bool): Set to True if the monitor service is stopped

        Returns:
            JSON data returned by the Docker API
        """
        container_name = f"monitor-{self.target_container}"
        url = f"{BASE_URL}/containers/json"

        filter_str = '{"name":["' + container_name + '"]'
        if stopped:
            filter_str += ',"status":["exited"]'
        filter_str += "}"

        params = {
            "filters": filter_str,
        }

        session = requests_unixsocket.Session()
        response = session.get(url, params=params)
        if response.ok:
            return response.json()
        else:
            raise Exception(
                "Creating monitor container ({}) failed with status code {}".format(
                    container_name, response.status_code
                )
            )

    def _is_container_running(self) -> bool:
        """
        Returns:
            True if monitor container is already running
        """
        data = self._get_container()
        return len(data) > 0

    def _is_container_stopped(self) -> bool:
        """
        Returns:
            True if monitor container has been created but is currently stopped
        """
        data = self._get_container(stopped=True)
        return len(data) > 0

    def _create_container(self) -> None:
        """
        Creates monitor container
        """
        container_name = f"monitor-{self.target_container}"
        url = f"{BASE_URL}/containers/create"

        params = {
            "name": container_name,
        }
        headers = {
            "Content-Type": "application/json",
        }
        body = {
            "Image": MONITOR_SERVICE_CONTAINER_IMAGE,
            "HostConfig": {
                "Binds": [
                    f"{DOCKER_SOCKET}:{DOCKER_SOCKET}",
                    f"{PROJECT_DIR}:/mnt/log",
                ],
            },
        }

        session = requests_unixsocket.Session()
        response = session.post(url, params=params, json=body, headers=headers)
        if not response.ok:
            raise Exception(
                "Creating monitor container ({}) failed with status code {}".format(
                    container_name, response.status_code
                )
            )

    def _start_container(self) -> None:
        """
        Starts monitor container
        """
        container_name = f"monitor-{self.target_container}"
        url = f"{BASE_URL}/containers/{container_name}/start"

        session = requests_unixsocket.Session()
        response = session.post(url)
        if not response.ok:
            raise Exception(
                "Starting monitor container ({}) failed with status code {}".format(
                    container_name, response.status_code
                )
            )

    def _stop_container(self) -> None:
        """
        Stops monitor container
        """
        container_name = f"monitor-{self.target_container}"
        url = f"{BASE_URL}/containers/{container_name}/stop"

        session = requests_unixsocket.Session()
        response = session.post(url)
        if not response.ok:
            raise Exception(
                "Stopping monitor container ({}) failed with status code {}".format(
                    container_name, response.status_code
                )
            )

    def _delete_container(self) -> None:
        """
        Deletes monitor container
        """
        container_name = f"monitor-{self.target_container}"
        url = f"{BASE_URL}/containers/{container_name}"

        session = requests_unixsocket.Session()
        response = session.delete(url)
        if not response.ok:
            raise Exception(
                "Deleting monitor container ({}) failed with status code {}".format(
                    container_name, response.status_code
                )
            )

    def start_monitor(self) -> None:
        """
        Creates and starts the monitor container

        Does nothing if a monitor container is already running. Deletes
        existing container and creates/startes a new container if one is
        in a stopped.
        state.
        """
        if self._is_container_running():
            print("Monitor process already running.")
            return

        if self._is_container_stopped():
            self._delete_container()

        self._create_container()
        self._start_container()
        print("Successfully started monitor service")

    def stop_monitor(self) -> None:
        """
        Stops and deletse monitor container

        Does nothing if a monitor container does not exist. If the monitor
        container is in a stopped state, it will be deleted.
        """
        if self._is_container_running():
            self._stop_container()
            self._delete_container()
            print("Successfully stopped monitor service")
        elif self._is_container_stopped():
            self._delete_container()
        else:
            print("Monitor process not running.")
