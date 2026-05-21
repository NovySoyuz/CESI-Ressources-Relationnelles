.PHONY: help web-up web-down web-logs web-shell web-build cap-sync-dev cap-sync cap-ios-dev cap-ios cap-android

GREEN  := \033[0;32m]
YELLOW := \033[0;33m]
RESET  := \033[0m]

help: ## Affiche cette aide
	@echo ""
	@echo "  $(GREEN)rr-frontend — Web & Mobile$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ── Web ───────────────────────────────────────────────────────────────────────

web-up: ## Démarre Angular Web (port 4200)
	$(MAKE) -C front-web up

web-down: ## Arrête Angular Web
	$(MAKE) -C front-web down

web-logs: ## Logs Angular Web
	$(MAKE) -C front-web logs

web-shell: ## Shell container Web
	$(MAKE) -C front-web shell

web-build: ## Build prod Web
	$(MAKE) -C front-web build

# ── Mobile (Capacitor) ────────────────────────────────────────────────────────

cap-sync-dev: ## Build dev front-web + sync Capacitor
	$(MAKE) -C front-mobile cap-sync-dev

cap-sync: ## Build prod front-web + sync Capacitor
	$(MAKE) -C front-mobile cap-sync

cap-ios-dev: ## Build dev + pod install + ouvre Xcode
	$(MAKE) -C front-mobile cap-ios-dev

cap-ios: ## Build prod + pod install + ouvre Xcode
	$(MAKE) -C front-mobile cap-ios

cap-android: ## Ouvre Android dans Android Studio
	$(MAKE) -C front-mobile cap-android
