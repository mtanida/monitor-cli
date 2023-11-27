# Container Monitor CLI

CLI tool for monitoring a container's resource usage. Logs the usage stats to file.

## Implementation Details

This example application consists of 3 parts:
1. target container - This is the example container that will be monitored by the monitoring service.
2. monitor container - This is the container responsible for monitoring the target container
3. monitor-cli - This is a Python CLI that is used to start, stop, and configure the monitor container

I chose to use a container to implement the monitoring process for several reasons. First, we can specify a restart policy so that the monitoring can resume in the event of a crash or reboot. Second, containers are _somewhat_ OS-agnostic, unlike an alternative implementation, such as a systemd service which is specific to *NIX variants. Finally, Docker's tools and API make containers easier to manage than a detatched sub process.

The name of the monitor contaner is always `monitor-<name of target container>`. By ensuring this naming convention, we can detect if a container is already being monitored. Logs are written to a CSV file in the project's root folder. I chose this rather than a conventional log directory, such as `/var/log` to keep the application as OS-agnostic as possible and to prevent the need to run the application with privilege escalation.

Though most of the application is OS-agnostic, the CLI and monitor service interact with Docker using a unix-domain socket (`/var/run/docker.sock`). Hence, it will currently only run on *NIX hosts. This will need to be updated in order to support other operating systems.

## Prerequisites

The following need to be installed on the host system:
1. docker
3. docker buildx plugin
4. docker-compose
5. python3.7 or higher

Note: the CLI currently only supports Linux hosts.

## Install Instructions

### Using poetry (Recommended)

1. Install [Python Poetry](https://python-poetry.org/docs/#installation) if necessary
2. Install the CLI
    ```
    cd monitor-cli
    poetry install --no-dev
    ```

### Using venv

1. Create the virtual environment:
    ```
    cd monitor-cl
    python3 -m venv .venv
    ```
2. Activate the virtual environment:
    ```
    source .venv/bin/activate
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```


## Instructions for running:

1. Build the monitor service container image
    ```
    cd monitor-cli
    DOCKER_BUILDKIT=1 docker build -t monitor-srv service
    ```
2. Start nginx container
    ```
    docker compose up -d
    ```
3. Start monitoring service
    1. Using poetry
        ```
        poetry run monitor-cli start
        ```
    2. Using venv
        ```
        source .venv/bin/activate
        export PYTHONPATH=$(pwd)
        python monitorcli/cli.py start
        ```
4. Stop monitoring service
    1. Using poetry
        ```
        poetry run monitor-cli stop
        ```
    2. Using venv
        ```
        source .venv/bin/activate
        export PYTHONPATH=$(pwd)
        python monitorcli/cli.py stop
        ```
