.PHONY: help up down logs shell build cap-sync cap-ios cap-android

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RED    := \033[0;31m]
RESET  := \033[0m]

COMPOSE := docker compose -f ../../docker-compose-root.yml --env-file ../../.env

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)front-mobile — Commandes Angular Mobile + Capacitor$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

up: ## Démarre le dev mobile sur http://localhost:4201
	@echo "$(GREEN)→ Démarrage Angular Mobile sur http://localhost:4201...$(RESET)"
	$(COMPOSE) up -d frontend-mobile

down: ## Arrête le frontend mobile
	$(COMPOSE) stop frontend-mobile

logs: ## Logs en temps réel
	$(COMPOSE) logs -f frontend-mobile

shell: ## Shell dans le container mobile
	$(COMPOSE) exec frontend-mobile sh

generate: ## Génère un composant/service (ex: make generate TYPE=component NAME=header)
	@echo "$(GREEN)→ ng generate $(TYPE) $(NAME)...$(RESET)"
	$(COMPOSE) exec frontend-mobile ng generate $(TYPE) $(NAME)

build: ## Build de production
	@echo "$(GREEN)→ Build production mobile...$(RESET)"
	$(COMPOSE) exec frontend-mobile ng build --configuration production

cap-sync: ## Build prod + sync Capacitor (ios & android)
	@echo "$(GREEN)→ Build + cap sync...$(RESET)"
	$(COMPOSE) exec frontend-mobile ng build --configuration production
	$(COMPOSE) exec frontend-mobile npx cap sync

cap-ios: ## Ouvre le projet iOS dans Xcode
	@echo "$(GREEN)→ Ouverture Xcode...$(RESET)"
	open $(CURDIR)/ios/App/App.xcworkspace

cap-android: ## Ouvre le projet Android dans Android Studio
	@echo "$(GREEN)→ Ouverture Android Studio...$(RESET)"
	open -a "Android Studio" $(CURDIR)/android
