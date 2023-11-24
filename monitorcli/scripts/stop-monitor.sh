#!/usr/bin/env bash

NAME_OF_CONTAINER_TO_MONITOR=$1
MONITOR_CONTAINER_NAME="monitor-${NAME_OF_CONTAINER_TO_MONITOR}"

docker ps --format "{{.Names}}" | grep $MONITOR_CONTAINER_NAME > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "Stopping monitor process"
    docker stop $MONITOR_CONTAINER_NAME
else
    echo "Monitor process not running"
    exit 1
fi
