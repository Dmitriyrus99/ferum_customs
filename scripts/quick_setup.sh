#!/usr/bin/env bash
# Quick start helper for local development
# Shell settings & verify Docker proxy settings
set -euo pipefail

# Function to print error messages
function error_exit {
    echo "$1" >&2
    exit 1
}

# If Docker CLI is not available (e.g., in bare Python-only env), skip Docker setup
if ! command -v docker >/dev/null 2>&1; then
    echo "⚠️ Docker CLI not found, skipping Docker environment setup."
    exit 0
fi

# Check for Docker systemd proxy settings
if [ -d "/etc/systemd/system/docker.service.d" ] && ls /etc/systemd/system/docker.service.d/*proxy*.conf &>/dev/null; then
    error_exit "Error: Proxy settings found in Docker systemd configuration (http-proxy.conf). Please remove or rename this file and restart the Docker service: sudo systemctl daemon-reload && sudo systemctl restart docker"
fi

DC="docker compose"

if ! command -v docker >/dev/null; then
    error_exit "Docker is required but not installed."
fi

if ! ${DC} version >/dev/null 2>&1; then
    DC="docker-compose"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
    echo ".env not found, creating from .env.example"
    if [ -f .env.example ]; then
        cp .env.example .env || error_exit "Failed to copy .env.example to .env"
    else
        error_exit ".env.example not found, please create it."
    fi
fi

echo "⚠️ Please ensure that the proxy is disabled in Docker Desktop settings (Settings → Resources → Proxies), otherwise there may be errors when pulling images."
${DC} up -d --build
