.PHONY: help \
        dev lan lan-down prod prod-certs prod-up prod-down \
        up down destroy status logs logs-db logs-back logs-front \
        shell-back shell-db migrate reinstall-front restart-front \
        db-reset db-seed db-rebuild \
        sonar-up sonar sonar-down \
        zap-baseline zap-full zap

# ─── Couleurs ─────────────────────────────────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
RESET  := \033[0m

# ─── Compose (stacks) ─────────────────────────────────────────────────────────
COMPOSE      := docker compose -f docker-compose-root.yml
COMPOSE_LAN  := docker compose -f docker-compose-root.yml -f docker-compose.lan.yml
COMPOSE_PROD := docker compose -f docker-compose-root.yml -f docker-compose.prod.yml

# ─── Réseau local ─────────────────────────────────────────────────────────────
# IP LAN active (Wi-Fi en0, puis Ethernet/USB en1 en secours). Injectée dans les
# ALLOWED_HOSTS/CORS Django par les stacks lan & prod.
HOST_IP := $(shell ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

# ─── SonarQube ────────────────────────────────────────────────────────────────
# Mot de passe admin (surchargeable : make sonar SONAR_ADMIN_PASS=...)
SONAR_ADMIN_PASS ?= Sonar_RR_2026!

# ─── OWASP ZAP (DAST) ─────────────────────────────────────────────────────────
ZAP_IMAGE   := ghcr.io/zaproxy/zaproxy:stable
ZAP_TARGET  ?= http://backend:8000
ZAP_REPORTS := $(CURDIR)/security-reports


help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)Ressources Relationnelles — Orchestrateur$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} \
		/^##@/ { printf "\n  $(YELLOW)%s$(RESET)\n", substr($$0, 5); next } \
		/^[a-zA-Z_-]+:.*##/ { printf "    $(GREEN)%-16s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""


##@ Environnements
dev: ## DÉV — runserver + hot-reload (http://localhost:4200, DEBUG=True)
	$(COMPOSE) up -d --build
	@echo "$(GREEN)✓ DEV démarré — API http://localhost:8000 · Angular http://localhost:4200 (DEBUG=True)$(RESET)"

lan: ## DÉV sur le réseau local — toute l'app sur ton IP (auto-détectée)
	@test -n "$(HOST_IP)" || { echo "$(RED)✗ IP LAN introuvable (en0/en1 down ? pas de Wi-Fi ?)$(RESET)"; exit 1; }
	@echo "$(GREEN)→ IP LAN détectée : $(HOST_IP)$(RESET)"
	HOST_IP=$(HOST_IP) $(COMPOSE_LAN) up -d --build
	@echo "$(GREEN)✓ App hébergée sur le réseau local :$(RESET)"
	@echo "$(GREEN)  → Front  : http://$(HOST_IP):4200$(RESET)"
	@echo "$(GREEN)  → API    : http://$(HOST_IP):8000$(RESET)"
	@echo "$(YELLOW)  (accessible depuis tout appareil du même réseau Wi-Fi)$(RESET)"

lan-down: ## Arrête la stack LAN (conserve les volumes)
	$(COMPOSE_LAN) down
	@echo "$(YELLOW)✓ Stack LAN arrêtée$(RESET)"

prod: prod-certs ## PROD-like — nginx sert front + API, gunicorn, TLS, DEBUG=False
	HOST_IP=$(HOST_IP) $(COMPOSE_PROD) up -d --build backend nginx
	@echo "$(GREEN)✓ PROD-like démarré (cert auto-signé · gunicorn · DEBUG=False) :$(RESET)"
	@echo "$(GREEN)  → App (local) : https://localhost:8443$(RESET)"
	@echo "$(GREEN)  → App (LAN)   : https://$(HOST_IP):8443$(RESET)"
	@echo "$(YELLOW)  (front + API servis par nginx sur la même origine)$(RESET)"

prod-certs: ## Génère un certificat TLS auto-signé pour nginx (si absent)
	@mkdir -p rr-infra/nginx/certs
	@test -f rr-infra/nginx/certs/server.crt || MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -newkey rsa:2048 \
		-keyout rr-infra/nginx/certs/server.key -out rr-infra/nginx/certs/server.crt \
		-days 365 -subj "/CN=localhost"
	@echo "$(GREEN)✓ Certificat TLS prêt (rr-infra/nginx/certs/)$(RESET)"

prod-up: prod ## Alias de `make prod`

prod-down: ## Arrête la stack prod-like et revient au backend dev
	$(COMPOSE_PROD) rm -sf nginx
	$(COMPOSE) up -d backend
	@echo "$(YELLOW)✓ Revenu en mode dev (runserver)$(RESET)"


##@ Cycle de vie
up: ## Démarre toute l'infra dans le bon ordre (= dev)
	@echo "$(GREEN)→ Démarrage de l'infra complète...$(RESET)"
	@echo "$(YELLOW)  1. Postgres$(RESET)"
	@echo "$(YELLOW)  2. Liquibase (migrations)$(RESET)"
	@echo "$(YELLOW)  3. Django$(RESET)"
	@echo "$(YELLOW)  4. Angular$(RESET)"
	$(COMPOSE) up -d --build
	@echo "$(GREEN)✓ Tout est démarré !$(RESET)"
	@echo "$(GREEN)  → Angular  : http://localhost:4200$(RESET)"
	@echo "$(GREEN)  → Django   : http://localhost:8000$(RESET)"
	@echo "$(GREEN)  → Postgres : localhost:5432$(RESET)"

down: ## Arrête tous les containers (conserve les volumes)
	@echo "$(YELLOW)→ Arrêt de tous les containers...$(RESET)"
	$(COMPOSE) down
	@echo "$(YELLOW)✓ Containers arrêtés$(RESET)"

destroy: ## Supprime tout (containers + volumes)
	@echo "$(RED)→ Suppression complète...$(RESET)"
	$(COMPOSE) down -v --remove-orphans
	@echo "$(RED)✓ Tout supprimé$(RESET)"

status: ## Affiche l'état de tous les containers
	$(COMPOSE) ps

logs: ## Logs de tous les services
	$(COMPOSE) logs -f

logs-db: ## Logs Postgres uniquement
	$(COMPOSE) logs -f postgres

logs-back: ## Logs Django uniquement
	$(COMPOSE) logs -f backend

logs-front: ## Logs Angular uniquement
	$(COMPOSE) logs -f frontend


##@ Développement
shell-back: ## Shell Python Django
	$(COMPOSE) exec backend python manage.py shell

shell-db: ## Shell psql PostgreSQL
	$(COMPOSE) exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

migrate: ## Relance uniquement les migrations Liquibase
	$(COMPOSE) run --rm liquibase

reinstall-front: ## Réinstalle les dépendances npm du container frontend (après modif package.json)
	$(COMPOSE) exec frontend npm install

restart-front: ## Redémarre le serveur Angular (nécessaire après modif angular.json)
	$(COMPOSE) restart frontend


##@ Base de données (Liquibase uniquement)
db-reset: ## Détruit UNIQUEMENT le volume Postgres puis recrée le schéma (Liquibase)
	@echo "$(RED)→ Suppression du volume Postgres (rr_pgdata)...$(RESET)"
	$(COMPOSE) rm -sf postgres
	-docker volume rm rr_pgdata
	@echo "$(GREEN)→ Recréation Postgres + migrations de structure...$(RESET)"
	$(COMPOSE) up -d postgres
	$(COMPOSE) run --rm liquibase
	-$(COMPOSE) restart backend
	@echo "$(GREEN)✓ Schéma neuf (vide). Lance 'make db-seed' pour le jeu de données.$(RESET)"

db-seed: ## Injecte le jeu de données de démo (changelog seed, contexte "seed")
	@echo "$(GREEN)→ Injection du jeu de données de démo...$(RESET)"
	$(COMPOSE) run --rm liquibase \
		--changelog-file=db.changelog-seed.yaml --contexts=seed update
	@echo "$(GREEN)✓ Données de démo chargées (mdp de tous les comptes : Password123!)$(RESET)"

db-rebuild: db-reset db-seed ## Reset complet + jeu de données en une commande


##@ Qualité — SonarQube (profil "tools")
sonar-up: ## Démarre le serveur SonarQube (http://localhost:9000)
	$(COMPOSE) --profile tools up -d sonarqube
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
	$(COMPOSE) --profile tools stop sonarqube


##@ Sécurité — DAST (OWASP ZAP)
# Scanne l'API Django lancée par `make up` (service "backend" sur rr_network).
# Rapports HTML/JSON déposés dans ./security-reports/.
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
