%:
	@:
.PHONY: help init check-env render render-dataspace-config vault-init up down restart logs ps config validate python-venv python-deps configure-participant ensure-connector configure-keycloak-full init-identity-hub verify-identity-hub pull clean

PROFILES ?=
SERVICE ?=
PARTICIPANT ?=
SKIP_VC ?=false
VERIFY_VERBOSE ?=false
DATASPACE_CONFIG_DIR ?=./.generated/dataspace-config

ENV_FILE := .env
ENV_EXAMPLE := .env.example
COMPOSE_FILE := docker-compose.yaml
ENV_PROFILES := $(shell [ -f $(ENV_FILE) ] && awk -F= '/^COMPOSE_PROFILES=/{v=$$2} END{gsub(/"/,"",v); gsub(/,/," ",v); print v}' $(ENV_FILE))
EFFECTIVE_PROFILES := $(strip $(if $(PROFILES),$(PROFILES),$(ENV_PROFILES)))
PROFILE_ARGS := $(foreach p,$(EFFECTIVE_PROFILES),--profile $(p))
COMPOSE := docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
PROJECT_ROOT := $(abspath ../../..)
PYTHON_VENV ?= ./venv
PYTHON_BIN := $(PYTHON_VENV)/bin/python

help: ## Show help (profiles from .env: COMPOSE_PROFILES)
	@echo 'Usage: make [PROFILES="keycloak identity storage"] <target>'
	@echo ''
	@echo 'Examples:'
	@echo '  make init render up'
	@echo '  # default profiles from .env (COMPOSE_PROFILES=keycloak,identity)'
	@echo '  make up'
	@echo '  make PROFILES="keycloak" up'
	@echo '  make PROFILES="keycloak identity storage" up'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Create .env and .env.secrets from examples
	@if [ ! -f $(ENV_FILE) ]; then \
		cp $(ENV_EXAMPLE) $(ENV_FILE); \
		echo "✓ Created $(ENV_FILE) from $(ENV_EXAMPLE)"; \
	else \
		echo "✓ $(ENV_FILE) already exists"; \
	fi
	@if [ ! -f .env.secrets ]; then \
		cp .env.secrets.example .env.secrets; \
		echo "✓ Created .env.secrets from .env.secrets.example"; \
	else \
		echo "✓ .env.secrets already exists"; \
	fi

check-env: ## Check required env and compose files exist
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "❌ Missing $(ENV_FILE). Run 'make init' first."; \
		exit 1; \
	fi
	@if [ ! -f .env.secrets ]; then \
		echo "❌ Missing .env.secrets. Run 'make init' first."; \
		exit 1; \
	fi
	@if [ ! -f $(COMPOSE_FILE) ]; then \
		echo "❌ Missing $(COMPOSE_FILE)."; \
		exit 1; \
	fi

render: check-env ## Render connector/identity-hub config into .generated/config/
	bash ./scripts/render/render-config.sh ./$(ENV_FILE) ./.env.secrets && bash ./scripts/render/render-dashboard.sh ./$(ENV_FILE)

render-dataspace-config: check-env ## Render init/verify dataspace config JSON from .env into .generated
	bash ./scripts/configure/render-dataspace-config.sh ./$(ENV_FILE) ./.env.secrets $(DATASPACE_CONFIG_DIR)

vault-init: check-env ## Initialize/unseal local Vault for identity profile
	bash ./scripts/vault-init-unseal.sh ./$(COMPOSE_FILE) ./$(ENV_FILE) ./.env.secrets

up: check-env ## Start required section + optional profiles (from .env COMPOSE_PROFILES or PROFILES override)
	bash ./scripts/up.sh ./$(COMPOSE_FILE) ./$(ENV_FILE) ./.env.secrets "$(EFFECTIVE_PROFILES)"

down: check-env ## Stop services
	$(COMPOSE) down

restart: check-env ## Restart services
	$(COMPOSE) $(PROFILE_ARGS) restart

logs: check-env ## Follow logs (make logs [SERVICE] [-f] ...)
	$(COMPOSE) logs $(filter-out $@,$(MAKECMDGOALS))

ps: check-env ## Show container status
	$(COMPOSE) ps

config: check-env ## Print merged compose config for current profiles
	$(COMPOSE) $(PROFILE_ARGS) config

validate: check-env ## Validate compose and check placeholders in env files
	@echo "Validating compose: $(COMPOSE_FILE)"
	@$(COMPOSE) $(PROFILE_ARGS) config >/dev/null && echo "✓ Compose config is valid"
	@echo "Checking placeholders in $(ENV_FILE) and .env.secrets"
	@grep -q 'change-me\|CHANGE_ME' $(ENV_FILE) .env.secrets && echo "⚠️  Placeholder values found. Update before production." || echo "✓ No placeholder values found"

python-venv: ## Create repo Python virtualenv for Keycloak scripts
	@if [ ! -x "$(PYTHON_BIN)" ]; then \
		echo "Creating virtualenv: $(PYTHON_VENV)"; \
		python3 -m venv "$(PYTHON_VENV)"; \
	fi

python-deps: python-venv ## Install Python dependencies into repo virtualenv
	@set -e; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	python -m pip install -r ./scripts/keycloak/requirements.txt

configure-participant: check-env python-venv ## Configure participant Keycloak realm/clients/groups
	@set -a; \
	. ./$(ENV_FILE); \
	. ./.env.secrets; \
	set +a; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	$(PYTHON_BIN) ./scripts/keycloak/configure_participant.py

ensure-connector: check-env python-venv ## Ensure connector client/role/group for participant
	@set -a; \
	. ./$(ENV_FILE); \
	. ./.env.secrets; \
	set +a; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	$(PYTHON_BIN) ./scripts/keycloak/participant_ensure_connector.py

configure-keycloak-full: configure-participant ensure-connector ## Run full Keycloak bootstrap (participant + connector)

init-identity-hub: render-dataspace-config ## Initialize dataspace (IH + connector + VC issuance)
	@args="--config $(DATASPACE_CONFIG_DIR)"; \
	if [ -n "$(PARTICIPANT)" ]; then args="$$args --participant $(PARTICIPANT)"; fi; \
	if [ "$(SKIP_VC)" = "true" ] || [ "$(SKIP_VC)" = "1" ]; then args="$$args --skip-vc"; fi; \
	bash ./scripts/configure/init-identity-hub.sh $$args

verify-identity-hub: render-dataspace-config ## Verify dataspace state using same config as init-identity-hub
	@args="--config $(DATASPACE_CONFIG_DIR)"; \
	if [ -n "$(PARTICIPANT)" ]; then args="$$args --participant $(PARTICIPANT)"; fi; \
	if [ "$(VERIFY_VERBOSE)" = "true" ] || [ "$(VERIFY_VERBOSE)" = "1" ]; then args="$$args --verbose"; fi; \
	bash ./scripts/configure/verify-identity-hub.sh $$args

pull: check-env ## Pull images for selected profiles
	$(COMPOSE) $(PROFILE_ARGS) pull

clean: check-env ## Stop services and remove volumes (destructive)
	@echo "⚠️  This removes volumes. Press Ctrl+C to cancel, Enter to continue."
	@read confirmation
	$(COMPOSE) down -v
