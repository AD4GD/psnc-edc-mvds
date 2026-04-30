%:
	@:
.PHONY: help init check-env deploy-env deploy deploy-vault deploy-all deploy-all-with-init-vault init-vault sync-vault python-venv python-deps configure-participant ensure-connector configure-keycloak-full render-dataspace-config init-identity-hub verify-identity-hub bootstrap-all

ANSIBLE_PLAYBOOK ?= ansible-playbook
ANSIBLE_ARGS ?=

ENV_FILE := .env
SECRETS_FILE := .env.secrets
VAULT_SECRETS_FILE := ./secrets/vault.secrets
DATASPACE_CONFIG_DIR ?= ./.generated/dataspace-config

PROJECT_ROOT := $(abspath ../../..)
PYTHON_VENV ?= $(PROJECT_ROOT)/venv
PYTHON_BIN := $(PYTHON_VENV)/bin/python

SCRIPTS_ROOT := $(if $(wildcard ./scripts),./scripts,../kubernetes/scripts)
VAULT_SCRIPT := $(SCRIPTS_ROOT)/vault-init-unseal.sh
CONFIGURE_SCRIPTS_DIR := $(SCRIPTS_ROOT)/configure
KEYCLOAK_SCRIPTS_DIR := $(SCRIPTS_ROOT)/keycloak

help: ## Show available targets
	@echo 'Usage: make <target>'
	@echo ''
	@echo 'Common flows:'
	@echo '  make deploy-vault init-vault'
	@echo '  make deploy-all-with-init-vault'
	@echo '  make bootstrap-all'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}'

init: deploy-env ## Render .env, .env.secrets and secrets/vault.secrets

deploy-env: ## Render environment files from vars/*.yaml
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_ARGS) deploy-env.yaml

check-env: ## Ensure generated env files exist
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Missing $(ENV_FILE). Run 'make deploy-env' first."; \
		exit 1; \
	fi
	@if [ ! -f $(VAULT_SECRETS_FILE) ]; then \
		echo "Missing $(VAULT_SECRETS_FILE). Run 'make deploy-env' first."; \
		exit 1; \
	fi

deploy-vault: deploy-env ## Deploy only standalone Vault resources
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_ARGS) deploy-vault.yaml

init-vault: check-env ## Initialize/unseal Vault and propagate generated token to connector/identity-hub secrets
	bash $(VAULT_SCRIPT) ./$(ENV_FILE) $(VAULT_SECRETS_FILE)

deploy: deploy-all ## Alias for full deploy

deploy-all: deploy-env ## Deploy full stack (includes deploy-vault)
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_ARGS) deploy.yaml

sync-vault: init-vault ## Re-run Vault token sync to Kubernetes secrets

deploy-all-with-init-vault: deploy-all init-vault ## Full deploy and then Vault init/unseal + token sync

python-venv: ## Create Python virtualenv used by keycloak scripts
	@if [ ! -x "$(PYTHON_BIN)" ]; then \
		echo "Creating virtualenv: $(PYTHON_VENV)"; \
		python3 -m venv "$(PYTHON_VENV)"; \
	fi

python-deps: python-venv ## Install Python dependencies for keycloak scripts
	@set -e; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	python -m pip install -r $(KEYCLOAK_SCRIPTS_DIR)/requirements.txt

configure-participant: check-env python-deps ## Configure participant realm/clients/groups in Keycloak
	@set -a; \
	. ./$(ENV_FILE); \
	set +a; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	$(PYTHON_BIN) $(KEYCLOAK_SCRIPTS_DIR)/configure_participant.py

ensure-connector: check-env python-deps ## Ensure connector client/role/group in Keycloak
	@set -a; \
	. ./$(ENV_FILE); \
	set +a; \
	if [ "$${VIRTUAL_ENV:-}" != "$(PYTHON_VENV)" ]; then \
		. "$(PYTHON_VENV)/bin/activate"; \
	fi; \
	$(PYTHON_BIN) $(KEYCLOAK_SCRIPTS_DIR)/participant_ensure_connector.py

configure-keycloak: configure-participant ensure-connector ## Run full Keycloak bootstrap

render-dataspace-config: check-env ## Render dataspace JSON config based on generated env files
	bash $(CONFIGURE_SCRIPTS_DIR)/render-dataspace-config.sh ./$(ENV_FILE) $(DATASPACE_CONFIG_DIR)

init-identity-hub: render-dataspace-config ## Initialize dataspace objects in IH and connector
	@args="--config $(DATASPACE_CONFIG_DIR)"; \
	if [ -n "$(PARTICIPANT)" ]; then args="$$args --participant $(PARTICIPANT)"; fi; \
	if [ "$(SKIP_VC)" = "true" ] || [ "$(SKIP_VC)" = "1" ]; then args="$$args --skip-vc"; fi; \
	bash $(CONFIGURE_SCRIPTS_DIR)/init-identity-hub.sh $$args

verify-identity-hub: render-dataspace-config ## Verify dataspace state using the same generated config
	@args="--config $(DATASPACE_CONFIG_DIR)"; \
	if [ -n "$(PARTICIPANT)" ]; then args="$$args --participant $(PARTICIPANT)"; fi; \
	if [ "$(VERIFY_VERBOSE)" = "true" ] || [ "$(VERIFY_VERBOSE)" = "1" ]; then args="$$args --verbose"; fi; \
	bash $(CONFIGURE_SCRIPTS_DIR)/verify-identity-hub.sh $$args

bootstrap-all: deploy-all-with-init-vault configure-keycloak-full init-identity-hub verify-identity-hub ## Full end-to-end deploy + init + keycloak + dataspace config
