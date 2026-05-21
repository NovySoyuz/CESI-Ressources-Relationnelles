.PHONY: help install cap-sync-dev cap-sync cap-ios-dev cap-ios cap-android android-tunnel

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RESET  := \033[0m]

COMPOSE := docker compose -f ../../docker-compose-root.yml --env-file ../../.env

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)rr-frontend/front-mobile — Coquille Capacitor$(RESET)"
	@echo "  $(GREEN)Source web : front-web | Natif : ios/ android/$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

install: ## Installe les dépendances Capacitor sur le host
	npm install

# ── Dev (localhost:8000) ──────────────────────────────────────────────────────

cap-sync-dev: ## Build dev front-web + sync Capacitor
	@echo "$(GREEN)→ Build Angular (dev)...$(RESET)"
	$(COMPOSE) exec frontend-web ng build --configuration development
	@echo "$(GREEN)→ cap sync...$(RESET)"
	npx cap sync

cap-ios-dev: ## Build dev + pod install + ouvre Xcode
	@echo "$(GREEN)→ Build Angular (dev)...$(RESET)"
	$(COMPOSE) exec frontend-web ng build --configuration development
	@echo "$(GREEN)→ cap sync...$(RESET)"
	npx cap sync
	@echo "$(GREEN)→ pod install...$(RESET)"
	cd $(CURDIR)/ios/App && pod install
	@echo "$(GREEN)→ Ouverture Xcode...$(RESET)"
	open $(CURDIR)/ios/App/App.xcworkspace

# ── Prod ──────────────────────────────────────────────────────────────────────

cap-sync: ## Build prod front-web + sync Capacitor
	@echo "$(GREEN)→ Build Angular (prod)...$(RESET)"
	$(COMPOSE) exec frontend-web ng build --configuration production
	@echo "$(GREEN)→ cap sync...$(RESET)"
	npx cap sync

cap-ios: ## Build prod + pod install + ouvre Xcode
	@echo "$(GREEN)→ Build Angular (prod)...$(RESET)"
	$(COMPOSE) exec frontend-web ng build --configuration production
	@echo "$(GREEN)→ cap sync...$(RESET)"
	npx cap sync
	@echo "$(GREEN)→ pod install...$(RESET)"
	cd $(CURDIR)/ios/App && pod install
	@echo "$(GREEN)→ Ouverture Xcode...$(RESET)"
	open $(CURDIR)/ios/App/App.xcworkspace

cap-android: ## Ouvre Android dans Android Studio
	open -a "Android Studio" $(CURDIR)/android

# ── Tunnel ADB ────────────────────────────────────────────────────────────────

ADB := $(HOME)/Library/Android/sdk/platform-tools/adb

android-tunnel: ## Tunnel ADB : redirige localhost:8000 de l'émulateur → Docker
	$(ADB) reverse tcp:8000 tcp:8000
