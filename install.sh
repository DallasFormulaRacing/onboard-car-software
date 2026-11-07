#!/bin/bash
set -e

cd ./services/deserializer

curl -LsSf https://astral.sh/uv/install.sh | sh

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
      iproute2 \
      can-utils \
      net-tools \
      kmod \
      build-essential

uv venv
uv pip install -r requirements.txt
