#!/usr/bin/env bash
# Quick start helper for local development
# Shell settings & verify Docker proxy settings
set -euo pipefail

 # If Docker CLI is not available (e.g., in bare Python-only env), skip Docker setup
if ! command -v docker >/dev/null 2>&1; then
    echo "⚠️ Docker CLI not found, skipping Docker environment setup."
    exit 0
fi

# Check for Docker systemd proxy settings
if [ -d "/etc/systemd/system/docker.service.d" ] && ls /etc/systemd/system/docker.service.d/*proxy*.conf &>/dev/null; then
    echo "Ошибка: в настройках Docker systemd обнаружен прокси (http-proxy.conf)."
    echo "Пожалуйста, удалите или переименуйте этот файл и перезапустите службу Docker:" \
         "sudo systemctl daemon-reload && sudo systemctl restart docker"
    exit 1
fi

DC="docker compose"

if ! command -v docker >/dev/null; then
    echo "Docker is required but not installed." >&2
    exit 1
fi

if ! ${DC} version >/dev/null 2>&1; then
    DC="docker-compose"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
    echo ".env not found, creating from .env.example"
    cp .env.example .env
fi

echo "⚠️ Проверьте, что в настройках Docker Desktop прокси отключен (Settings → Resources → Proxies), иначе могут быть ошибки при загрузке образов."
${DC} up -d --build
