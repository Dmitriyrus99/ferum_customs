#!/usr/bin/env bash
set -euo pipefail

log() { printf "\e[1;34m>>> %s\e[0m\n" "$*"; }

# Allow overriding HTTP(S)_PROXY from environment
export HTTP_PROXY=${HTTP_PROXY:-""}
export HTTPS_PROXY=${HTTPS_PROXY:-""}

# Check for required commands
check_commands() {
  for cmd in apt-get docker git; do
    if ! command -v "$cmd" &> /dev/null; then
      echo "❌ Command '$cmd' is required but not found. Please install it."
      exit 1
    fi
  done
}

# Check if the script is run as root
check_root() {
  if [[ $EUID -eq 0 ]]; then
    echo "❌ Do not run the script as root. Please run it as a regular user."
    exit 1
  fi
}

# Update package list
update_packages() {
  log "Updating package list..."
  sudo apt-get update -y
}

# Install Docker and dependencies
install_docker() {
  log "Installing Docker and dependencies..."
  sudo apt-get install -y docker.io git ca-certificates curl gnupg
  sudo systemctl enable --now docker
}

# Add user to docker group
add_user_to_docker_group() {
  log "Adding user $USER to docker group..."
  if ! groups "$USER" | grep -q '\bdocker\b'; then
    sudo usermod -aG docker "$USER" || { echo "❌ Failed to add user to docker group"; exit 1; }
    NEW_GRP_NOTE=true
  fi
}

# Build Docker image if it doesn't exist
build_docker_image() {
  log "Checking if codex image exists..."
  if ! docker images -q codex >/dev/null 2>&1; then
    log "Building Docker image 'codex'..."
    if [[ ! -d "$HOME/codex" ]]; then
      git clone https://github.com/openai/codex.git "$HOME/codex" || { echo "❌ Failed to clone repository"; exit 1; }
    else
      log "Repository already exists, pulling latest changes..."
      git -C "$HOME/codex" pull --ff-only || { echo "❌ Failed to pull latest changes"; exit 1; }
    fi
    cd "$HOME/codex/codex-cli"
    sudo docker build -t codex . || { echo "❌ Docker build failed"; exit 1; }
    cd -
  else
    log "Image 'codex' already exists — skipping build."
  fi
}

# Disable firewall restrictions in Codex container
disable_firewall_restrictions() {
  log "Disabling firewall restrictions in Codex container..."
  RUN_IN_CONTAINER_PATH=$(sudo find /usr -type f -name run_in_container.sh 2>/dev/null | head -n1 || true)
  if [[ -n "$RUN_IN_CONTAINER_PATH" ]]; then
    sudo sed -i '/init_firewall.sh/s/^/#/' "$RUN_IN_CONTAINER_PATH"
    log "Modified file $RUN_IN_CONTAINER_PATH: network restrictions disabled."
  else
    echo "⚠️  run_in_container.sh not found — Codex CLI may not be installed yet."
  fi
}

# Clean up apt cache
clean_apt_cache() {
  log "Cleaning apt cache..."
  sudo apt-get clean
}

# Main execution
main() {
  check_root
  check_commands
  update_packages
  install_docker
  add_user_to_docker_group
  build_docker_image
  disable_firewall_restrictions
  clean_apt_cache

  log "Setup complete ✅"
  if [[ "${NEW_GRP_NOTE:-false}" == true ]]; then
    echo "ℹ️  Please log out and log back in (or run 'newgrp docker') to apply new group permissions."
  fi
}

main "$@"
