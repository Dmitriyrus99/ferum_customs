#!/usr/bin/env bash
# Quick start helper for local development
set -euo pipefail

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

${DC} up -d --build
