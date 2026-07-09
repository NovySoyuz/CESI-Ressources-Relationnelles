#!/bin/sh
# Génère un certificat TLS auto-signé DANS le conteneur nginx, au démarrage.
# Exécuté automatiquement par l'entrypoint nginx (scripts /docker-entrypoint.d/*.sh)
# avant le lancement du serveur.
#
# Le SAN couvre localhost + 127.0.0.1 + l'IP LAN (variable HOST_IP fournie par
# `make prod`). (Re)génère uniquement si le cert est absent ou ne couvre pas l'IP
# courante — donc stable tant que l'IP ne change pas (cert persisté via volume).
set -e

CERT_DIR=/etc/nginx/certs
HOST_IP="${HOST_IP:-127.0.0.1}"

if openssl x509 -in "$CERT_DIR/server.crt" -noout -ext subjectAltName 2>/dev/null \
   | grep -q "IP Address:$HOST_IP"; then
  echo "→ Certificat TLS déjà présent (couvre $HOST_IP), on le garde."
  exit 0
fi

echo "→ Génération du certificat TLS auto-signé (SAN : localhost, 127.0.0.1, $HOST_IP)"
mkdir -p "$CERT_DIR"
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" \
  -days 365 -subj "/CN=$HOST_IP" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:$HOST_IP"
