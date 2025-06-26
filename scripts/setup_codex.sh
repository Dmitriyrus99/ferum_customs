#!/usr/bin/env bash
set -euo pipefail

log() { printf "\e[1;34m>>> %s\e[0m\n" "$*"; }

# Allow overriding HTTP(S)_PROXY from environment
export HTTP_PROXY=${HTTP_PROXY:-""}
export HTTPS_PROXY=${HTTPS_PROXY:-""}

# 0. Проверка root/не-root
if [[ $EUID -eq 0 ]]; then
  echo "❌ Запускать скрипт от root не нужно. Запустите под обычным пользователем."
  exit 1
fi

log "Обновление списка пакетов..."
sudo apt-get update -y

log "Установка Docker и вспомогательных пакетов..."
sudo apt-get install -y docker.io git ca-certificates curl gnupg
sudo systemctl enable --now docker

log "Добавление пользователя $USER в группу docker..."
if ! groups $USER | grep -q '\bdocker\b'; then
  sudo usermod -aG docker "$USER"
  NEW_GRP_NOTE=true
fi

log "Проверка: существует ли образ codex?"
if ! docker images -q codex >/dev/null 2>&1; then
  log "Сборка Docker-образа 'codex'..."
  if [[ ! -d "$HOME/codex" ]]; then
    git clone https://github.com/openai/codex.git "$HOME/codex"
  else
    log "Репозиторий уже существует, делаю git pull..."
    git -C "$HOME/codex" pull --ff-only
  fi
  cd "$HOME/codex/codex-cli"
  sudo docker build -t codex .
  cd -
else
  log "Образ 'codex' уже есть — пропускаю сборку."
fi

log "Отключение firewall-ограничений в Codex контейнере..."
RUN_IN_CONTAINER_PATH=$(sudo find /usr -type f -name run_in_container.sh 2>/dev/null | head -n1 || true)
if [[ -n "$RUN_IN_CONTAINER_PATH" ]]; then
  sudo sed -i '/init_firewall.sh/s/^/#/' "$RUN_IN_CONTAINER_PATH"
  log "Изменён файл $RUN_IN_CONTAINER_PATH: сетевые ограничения отключены."
else
  echo "⚠️  Не найден run_in_container.sh — возможно Codex CLI ещё не установлен."
fi

log "Очистка apt кеша..."
sudo apt-get clean

log "Готово ✅"
if [[ "${NEW_GRP_NOTE:-false}" == true ]]; then
  echo "ℹ️  Выйдите из системы и войдите снова (или запустите 'newgrp docker'), чтобы новые групповые права применились."
fi
