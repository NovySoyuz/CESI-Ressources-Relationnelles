.PHONY: help up down logs shell generate build test

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

COMPOSE := docker compose -f ../../docker-compose-root.yml --env-file ../../.env

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)front-web — Commandes Angular Web$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Démarre Angular
	@echo "$(GREEN)→ Démarrage Angular sur http://localhost:4200...$(RESET)"
	$(COMPOSE) up -d frontend-web

down: ## Arrête Angular
	$(COMPOSE) stop frontend-web

logs: ## Logs Angular en temps réel
	$(COMPOSE) logs -f frontend-web

shell: ## Shell dans le container Angular
	$(COMPOSE) exec frontend-web sh

generate: ## Génère un composant/service (ex: make generate TYPE=component NAME=header)
	@echo "$(GREEN)→ ng generate $(TYPE) $(NAME)...$(RESET)"
	$(COMPOSE) exec frontend-web ng generate $(TYPE) $(NAME)

build: ## Build de production
	@echo "$(GREEN)→ Build production...$(RESET)"
	$(COMPOSE) exec frontend-web ng build --configuration production

test: ## Lance les tests Angular
	$(COMPOSE) exec frontend-web ng test --watch=false --browsers=ChromeHeadless
