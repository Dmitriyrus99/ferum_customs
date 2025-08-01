#!/usr/bin/env bash
#
# setup.sh - bootstrap development environment for ferum_customs
#
set -euo pipefail

# Ensure Python virtual environment
if [ ! -d .venv_dev ]; then
    python3 -m venv .venv_dev
fi

# Activate virtual environment
# shellcheck source=/dev/null
source .venv_dev/bin/activate

# Upgrade pip, install runtime requirements, and install project with development and test dependencies
pip install --upgrade pip
pip install -e ".[dev,test]"

# Bootstrap Docker-based ERPNext environment
# Configure Git to use version-controlled hooks and enable the post-commit hook
if [ -d .githooks ]; then
    git config core.hooksPath .githooks
    chmod +x .githooks/post-commit
else
    echo "Warning: .githooks directory not found. Skipping Git hooks configuration."
fi

# Ensure the script exists and is executable before running
if [ -x scripts/quick_setup.sh ]; then
    scripts/quick_setup.sh
else
    echo "Error: scripts/quick_setup.sh not found or not executable."
    exit 1
fi

# Optionally run tests after setup
# Uncomment the following line if tests are to be run automatically
# pytest tests/
