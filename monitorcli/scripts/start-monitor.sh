#!/usr/bin/env bash

NAME_OF_CONTAINER_TO_MONITOR=$1
OUTPUT_FILE_PATH=$2

MONITOR_CONTAINER_IMG=ubuntu
MONITOR_CONTAINER_TAG=jammy-20231004
MONITOR_CONTAINER_NAME="monitor-${NAME_OF_CONTAINER_TO_MONITOR}"

docker ps --format "{{.Names}}" | grep $MONITOR_CONTAINER_NAME > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "Monitor process already running"
    exit 1
else
    echo "Starting monitor process"
    touch $OUTPUT_FILE_PATH
    docker run \
      --rm \
      -d \
      --name $MONITOR_CONTAINER_NAME \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $OUTPUT_FILE_PATH:/log/logfile:rw \
      $MONITOR_CONTAINER_IMG:$MONITOR_CONTAINER_TAG \
      /bin/bash -c "apt-get update; apt-get install -y curl; curl --unix-socket /var/run/docker.sock http://v1.41/containers/nginx-alpine/stats > /log/logfile"
fi
