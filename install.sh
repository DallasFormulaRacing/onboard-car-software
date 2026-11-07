#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    python3 \
    iproute2 \
    can-utils \
    net-tools \
    kmod \
    build-essential

curl -LsSf https://astral.sh/uv/install.sh | sudo -H sh

(
    cd services/deserializer
    sudo /root/.local/bin/uv sync --locked
)

sudo cp daemon/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable slcan0.service deserializer.service
