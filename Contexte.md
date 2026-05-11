Projet Django REST + Angular + PostgreSQL.
3 sous-repos Git dans un dossier racine (rr-infra, rr-backend, rr-frontend).
Un seul docker-compose-root.yml à la racine, network Docker partagé "rr_network".
Ordre démarrage : postgres → liquibase → backend:8000 → frontend:4200.
BDD gérée par Liquibase (managed=False sur tous les modèles Django).
Auth JWT via SimpleJWT (access 15min, refresh 7j).
Pas de django.contrib.admin. Pas de migrate.
Apps Django : users, resources, interactions, administration.
Stack : Django 5 + DRF + Angular + Tailwind + DaisyUI + Capacitor (mobile).