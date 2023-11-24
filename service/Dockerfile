# syntax=docker/dockerfile:1.3.1

from python:3.10.13-alpine3.17 as BASE

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    requests-unixsocket \
    "urllib3<2"

COPY monitor_container.py .

ENTRYPOINT ["python", "monitor_container.py"]
