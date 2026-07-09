# Image « prod-like » : build l'Angular en mode production puis le sert derrière
# nginx (TLS + proxy /api/ vers gunicorn). Contexte de build : racine du dépôt.
#   docker compose -f docker-compose-root.yml -f docker-compose.prod.yml build nginx

# ─── Étape 1 : build Angular ──────────────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY rr-frontend/front-web/package*.json ./
RUN npm install
COPY rr-frontend/front-web/ ./
RUN npx ng build --configuration production

# ─── Étape 2 : nginx sert le build + génère son cert TLS ──────────────────────
FROM nginx:alpine
# openssl pour générer le cert auto-signé au démarrage (script docker-entrypoint.d).
RUN apk add --no-cache openssl
COPY rr-infra/nginx/nginx.prod.conf /etc/nginx/conf.d/default.conf
COPY rr-infra/nginx/10-gen-cert.sh /docker-entrypoint.d/10-gen-cert.sh
RUN chmod +x /docker-entrypoint.d/10-gen-cert.sh
COPY --from=build /app/dist/rr-frontend/browser/ /usr/share/nginx/html/
