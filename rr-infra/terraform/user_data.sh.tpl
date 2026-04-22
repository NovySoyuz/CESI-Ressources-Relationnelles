#!/bin/bash
set -e

# ─── Installation Docker ──────────────────────────────────────────────────────
dnf update -y
dnf install -y docker git
systemctl enable docker
systemctl start docker

# ─── Récupération du projet (adapter l'URL à votre repo Git) ─────────────────
# git clone https://github.com/votre-org/ressources-relationnelles.git /app
# cd /app

# ─── Variables d'environnement ────────────────────────────────────────────────
export POSTGRES_HOST="${postgres_host}"
export POSTGRES_DB="${postgres_db}"
export POSTGRES_USER="${postgres_user}"
export POSTGRES_PASSWORD="${postgres_password}"

# ─── Attente que RDS soit disponible ─────────────────────────────────────────
echo "Attente de RDS..."
until docker run --rm postgres:16-alpine pg_isready \
  -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; do
  sleep 5
done
echo "RDS prêt."

# ─── Migrations Liquibase ─────────────────────────────────────────────────────
docker run --rm \
  -v /app/liquibase/db.changelog-master.yaml:/liquibase/changelog/db.changelog-master.yaml \
  -v /app/liquibase/changelogs:/liquibase/changelog/changelogs \
  -e LIQUIBASE_COMMAND_URL="jdbc:postgresql://$POSTGRES_HOST:5432/$POSTGRES_DB" \
  -e LIQUIBASE_COMMAND_USERNAME="$POSTGRES_USER" \
  -e LIQUIBASE_COMMAND_PASSWORD="$POSTGRES_PASSWORD" \
  -e LIQUIBASE_COMMAND_CHANGELOG_FILE="db.changelog-master.yaml" \
  liquibase/liquibase:4.27 \
  --changelog-file=db.changelog-master.yaml update

echo "Migrations appliquées."
