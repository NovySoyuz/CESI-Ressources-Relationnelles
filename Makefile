.PHONY: help up down destroy logs status ps

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)Ressources Relationnelles — Orchestrateur$(RESET)"
	@echo "  $(YELLOW)Lance tout dans le bon ordre automatiquement$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Démarre toute l'infra dans le bon ordre
	@echo "$(GREEN)→ Démarrage de l'infra complète...$(RESET)"
	@echo "$(YELLOW)  1. Postgres$(RESET)"
	@echo "$(YELLOW)  2. Liquibase (migrations)$(RESET)"
	@echo "$(YELLOW)  3. Django$(RESET)"
	@echo "$(YELLOW)  4. Angular$(RESET)"
	docker compose -f docker-compose-root.yml up -d --build
	@echo "$(GREEN)✓ Tout est démarré !$(RESET)"
	@echo "$(GREEN)  → Angular  : http://localhost:4200$(RESET)"
	@echo "$(GREEN)  → Django   : http://localhost:8000$(RESET)"
	@echo "$(GREEN)  → Postgres : localhost:5432$(RESET)"

down: ## Arrête tous les containers (conserve les volumes)
	@echo "$(YELLOW)→ Arrêt de tous les containers...$(RESET)"
	docker compose -f docker-compose-root.yml down
	@echo "$(YELLOW)✓ Containers arrêtés$(RESET)"

destroy: ## Supprime tout (containers + volumes)
	@echo "$(RED)→ Suppression complète...$(RESET)"
	docker compose -f docker-compose-root.yml down -v --remove-orphans
	@echo "$(RED)✓ Tout supprimé$(RESET)"

logs: ## Affiche les logs de tous les services
	docker compose -f docker-compose-root.yml logs -f

logs-db: ## Logs Postgres uniquement
	docker compose -f docker-compose-root.yml logs -f postgres

logs-back: ## Logs Django uniquement
	docker compose -f docker-compose-root.yml logs -f backend

logs-front: ## Logs Angular uniquement
	docker compose -f docker-compose-root.yml logs -f frontend

status: ## Affiche l'état de tous les containers
	docker compose -f docker-compose-root.yml ps

migrate: ## Relance uniquement les migrations Liquibase
	docker compose -f docker-compose-root.yml run --rm liquibase

shell-back: ## Shell Python Django
	docker compose -f docker-compose-root.yml exec backend python manage.py shell

shell-db: ## Shell psql PostgreSQL
	docker compose -f docker-compose-root.yml exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

reinstall-front: ## Réinstalle les dépendances npm dans le container frontend (après modif package.json)
	docker compose -f docker-compose-root.yml exec frontend npm install

restart-front: ## Redémarre le serveur Angular (nécessaire après modif angular.json)
	docker compose -f docker-compose-root.yml restart frontend
