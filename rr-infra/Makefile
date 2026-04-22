.PHONY: help up down migrate psql tf-init tf-plan tf-up tf-destroy

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

COMPOSE := docker compose -f ../docker-compose-root.yml --env-file ../.env
TF_RUN  := docker compose -f ../docker-compose-root.yml --env-file ../.env run --rm terraform

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)rr-infra — Commandes infrastructure$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Démarre Postgres + migrations Liquibase
	@echo "$(GREEN)→ Démarrage Postgres...$(RESET)"
	$(COMPOSE) up -d postgres
	@echo "$(GREEN)→ Application des migrations...$(RESET)"
	$(COMPOSE) run --rm liquibase
	@echo "$(GREEN)✓ Infra prête$(RESET)"

down: ## Arrête Postgres
	$(COMPOSE) stop postgres

migrate: ## Relance uniquement les migrations Liquibase
	@echo "$(GREEN)→ Migrations Liquibase...$(RESET)"
	$(COMPOSE) run --rm liquibase

psql: ## Shell psql PostgreSQL
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

tf-init: ## Initialise Terraform
	$(TF_RUN) init

tf-plan: ## Plan Terraform
	$(TF_RUN) plan

tf-up: ## Déploie sur AWS
	$(TF_RUN) apply -auto-approve

tf-destroy: ## Détruit l'infra AWS
	$(TF_RUN) destroy -auto-approve
