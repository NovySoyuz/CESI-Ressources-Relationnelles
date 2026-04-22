.PHONY: help up down logs shell bash startapp test collectstatic

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

COMPOSE := docker compose -f ../docker-compose-root.yml --env-file ../.env

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)rr-backend — Commandes Django$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Démarre Django
	@echo "$(GREEN)→ Démarrage Django sur http://localhost:8000...$(RESET)"
	$(COMPOSE) up -d backend

down: ## Arrête Django
	$(COMPOSE) stop backend

logs: ## Logs Django en temps réel
	$(COMPOSE) logs -f backend

shell: ## Shell Python Django
	$(COMPOSE) exec backend python manage.py shell

bash: ## Bash dans le container
	$(COMPOSE) exec backend bash

startapp: ## Crée une app Django (ex: make startapp NAME=resources)
	@echo "$(GREEN)→ Création de l'app $(NAME)...$(RESET)"
	$(COMPOSE) exec backend python manage.py startapp $(NAME)

test: ## Lance les tests Django
	$(COMPOSE) exec backend python manage.py test

collectstatic: ## Collecte les fichiers statiques
	$(COMPOSE) exec backend python manage.py collectstatic --noinput
