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
    build-essential \
    redis-server

curl -LsSf https://astral.sh/uv/install.sh | sudo -H sh

(
    cd services/deserializer
    sudo /root/.local/bin/uv sync --locked
)

sudo mkdir -p data
sudo chown redis:redis data

sudo cp services/redis/redis.conf /etc/redis/redis.conf
sudo cp services/redis/99-redis.conf /etc/sysctl.d/
sudo sysctl -p /etc/sysctl.d/99-redis.conf

sudo mkdir -p /etc/systemd/system/redis-server.service.d
sudo cp services/redis/override.conf /etc/systemd/system/redis-server.service.d/

sudo cp daemon/* /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable redis-server.service slcan0.service deserializer.service
sudo systemctl restart redis-server.service

sudo systemctl start slcan0.service deserializer.service

echo -e "\nINSTALLED!"
