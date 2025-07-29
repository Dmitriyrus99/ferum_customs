## Makefile for ferum_customs project

.PHONY: help quick-setup quick-setup-bare-metal setup-env setup-codex check-fixtures db-setup system-status
PG-SETUP: db-setup

help:
	@echo "Makefile targets:"
	@echo "  quick-setup     Run scripts/quick_setup.sh"
	@echo "  setup-env       Run scripts/setup_environment.sh"
	@echo "  setup-codex     Run scripts/setup_codex.sh"
	@echo "  check-fixtures  Run scripts/check_fixtures_doctype.py on JSON fixtures"

quick-setup:
	@bash scripts/quick_setup.sh

quick-setup-bare-metal:
	@bash scripts/quick_setup_bare_metal.sh

setup-env:
	@bash scripts/setup_environment.sh

setup-codex:
	@bash scripts/setup_codex.sh

check-fixtures:
	@python3 scripts/check_fixtures_doctype.py $(git ls-files ferum_customs/fixtures/*.json)

db-setup:
	@bash scripts/setup_db.sh

system-status:
	@bash scripts/check_system_status.sh
