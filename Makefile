.PHONY: help dev prod up down destroy logs status ps sonar-up sonar sonar-down zap-baseline zap-full zap db-reset db-seed db-rebuild prod-certs prod-up prod-down

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

# Mot de passe admin SonarQube (surchargeable : make sonar SONAR_ADMIN_PASS=...)
SONAR_ADMIN_PASS ?= Sonar_RR_2026!

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)Ressources Relationnelles — Orchestrateur$(RESET)"
	@echo "  $(YELLOW)Lance tout dans le bon ordre automatiquement$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

dev: ## Démarre l'environnement de DÉVELOPPEMENT (runserver + hot-reload)
	docker compose -f docker-compose-root.yml up -d --build
	@echo "$(GREEN)✓ DEV démarré — API http://localhost:8000 · Angular http://localhost:4200 (DEBUG=True)$(RESET)"

prod: prod-certs ## Démarre l'environnement PROD-like (gunicorn + nginx TLS, DEBUG=False)
	$(COMPOSE_PROD) up -d --build backend nginx
	@echo "$(GREEN)✓ PROD démarré — https://localhost:8443 (cert auto-signé) · gunicorn · DEBUG=False$(RESET)"

up: ## Démarre toute l'infra dans le bon ordre (= dev)
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

# ─── SonarQube (profil "tools") ──────────────────────────────────────────────
sonar-up: ## Démarre le serveur SonarQube (http://localhost:9000)
	docker compose -f docker-compose-root.yml --profile tools up -d sonarqube
	@echo "$(GREEN)→ SonarQube démarre sur http://localhost:9000 (patiente ~1-2 min)$(RESET)"

sonar: ## Lance l'analyse SonarQube (génère le token automatiquement)
	@TOKEN="$(SONAR_TOKEN)"; \
	if [ -z "$$TOKEN" ]; then \
		echo "$(GREEN)→ Génération d'un token de scan...$(RESET)"; \
		TOKEN=$$(curl -s -u admin:$(SONAR_ADMIN_PASS) -X POST "http://localhost:9000/api/user_tokens/generate?name=rr-scan-$$(date +%s)" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p'); \
	fi; \
	if [ -z "$$TOKEN" ]; then \
		echo "$(RED)✗ Token introuvable. SonarQube est-il démarré (make sonar-up) et SONAR_ADMIN_PASS correct ?$(RESET)"; exit 1; \
	fi; \
	MSYS_NO_PATHCONV=1 docker run --rm --network rr_network \
		-e SONAR_HOST_URL="http://sonarqube:9000" \
		-e SONAR_TOKEN="$$TOKEN" \
		-v "$(CURDIR):/usr/src" \
		sonarsource/sonar-scanner-cli
	@echo "$(GREEN)✓ Analyse terminée → http://localhost:9000/dashboard?id=ressources-relationnelles$(RESET)"

sonar-down: ## Arrête SonarQube (conserve les données)
	docker compose -f docker-compose-root.yml --profile tools stop sonarqube


# ─── Base de données — reset & seed (Liquibase uniquement) ────────────────────
db-reset: ## Détruit UNIQUEMENT le volume Postgres puis recrée le schéma (Liquibase)
	@echo "$(RED)→ Suppression du volume Postgres (rr_pgdata)...$(RESET)"
	docker compose -f docker-compose-root.yml rm -sf postgres
	-docker volume rm rr_pgdata
	@echo "$(GREEN)→ Recréation Postgres + migrations de structure...$(RESET)"
	docker compose -f docker-compose-root.yml up -d postgres
	docker compose -f docker-compose-root.yml run --rm liquibase
	-docker compose -f docker-compose-root.yml restart backend
	@echo "$(GREEN)✓ Schéma neuf (vide). Lance 'make db-seed' pour le jeu de données.$(RESET)"

db-seed: ## Injecte le jeu de données de démo (changelog seed, contexte "seed")
	@echo "$(GREEN)→ Injection du jeu de données de démo...$(RESET)"
	docker compose -f docker-compose-root.yml run --rm liquibase \
		--changelog-file=db.changelog-seed.yaml --contexts=seed update
	@echo "$(GREEN)✓ Données de démo chargées (mdp de tous les comptes : Password123!)$(RESET)"

db-rebuild: db-reset db-seed ## Reset complet + jeu de données en une commande

# ─── Simulation « prod » (gunicorn + nginx/TLS, DEBUG=False) ──────────────────
COMPOSE_PROD := docker compose -f docker-compose-root.yml -f docker-compose.prod.yml

prod-certs: ## Génère un certificat TLS auto-signé pour nginx (si absent)
	@mkdir -p rr-infra/nginx/certs
	@test -f rr-infra/nginx/certs/server.crt || MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -newkey rsa:2048 \
		-keyout rr-infra/nginx/certs/server.key -out rr-infra/nginx/certs/server.crt \
		-days 365 -subj "/CN=localhost"
	@echo "$(GREEN)✓ Certificat TLS prêt (rr-infra/nginx/certs/)$(RESET)"

prod-up: prod-certs ## Démarre la stack prod-like (gunicorn + nginx TLS) → https://localhost:8443
	$(COMPOSE_PROD) up -d --build backend nginx
	@echo "$(GREEN)✓ Prod-like : https://localhost:8443 (cert auto-signé) · DEBUG=False$(RESET)"

prod-down: ## Arrête la stack prod-like et revient au backend dev
	$(COMPOSE_PROD) rm -sf nginx
	docker compose -f docker-compose-root.yml up -d backend
	@echo "$(YELLOW)✓ Revenu en mode dev (runserver)$(RESET)"

# ─── DAST — OWASP ZAP ─────────────────────────────────────────────────────────
# Scanne l'API Django lancée par `make up` (service "backend" sur rr_network).
# Rapports HTML/JSON déposés dans ./security-reports/.
ZAP_IMAGE   := ghcr.io/zaproxy/zaproxy:stable
ZAP_TARGET  ?= http://backend:8000
ZAP_REPORTS := $(CURDIR)/security-reports

zap-baseline: ## DAST passif rapide (spider + règles passives) → security-reports/
	@mkdir -p $(ZAP_REPORTS)
	@echo "$(GREEN)→ ZAP baseline scan sur $(ZAP_TARGET) ...$(RESET)"
	-MSYS_NO_PATHCONV=1 docker run --rm --network rr_network -v "$(ZAP_REPORTS):/zap/wrk:rw" \
		$(ZAP_IMAGE) zap-baseline.py -t $(ZAP_TARGET) \
		-r zap-baseline.html -J zap-baseline.json
	@echo "$(GREEN)✓ Rapport → security-reports/zap-baseline.html$(RESET)"

zap-full: ## DAST actif complet (injections, XSS… — intrusif, données jetables)
	@mkdir -p $(ZAP_REPORTS)
	@echo "$(YELLOW)→ ZAP FULL scan (actif) sur $(ZAP_TARGET) — sur environnement jetable uniquement$(RESET)"
	-MSYS_NO_PATHCONV=1 docker run --rm --network rr_network -v "$(ZAP_REPORTS):/zap/wrk:rw" \
		$(ZAP_IMAGE) zap-full-scan.py -t $(ZAP_TARGET) \
		-r zap-full.html -J zap-full.json
	@echo "$(GREEN)✓ Rapport → security-reports/zap-full.html$(RESET)"

zap: zap-baseline ## Alias de zap-baseline
