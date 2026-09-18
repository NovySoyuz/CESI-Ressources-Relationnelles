# CI/CD — (RE)Sources Relationnelles

Pipeline GitHub Actions : [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
Déclenchée sur chaque `push`/`pull_request` vers `main`, `develop` et `feature/*`.

## Schéma

```
lint ──► backend ──┐
      └► frontend ─┴──► docker-scan ──► deploy (Render, main uniquement)
```

## Les 5 jobs

| Job | Rôle |
|-----|------|
| **lint** | Audit des dépendances : `pip-audit` (backend), `npm audit` + `prettier --check` (frontend, informatif) |
| **backend** | Tests Django (`manage.py test`, 102 tests) + couverture, contre un vrai Postgres en service container |
| **frontend** | Tests Angular/Vitest + couverture + `ng build` production, artefacts uploadés |
| **docker-scan** | Build des images Docker + scan vulnérabilités **Trivy** (non-bloquant, base de données cachée par jour) |
| **deploy** | Déclenche les *Deploy Hooks* Render (back + front) — **uniquement sur push `main`** |

## Déploiement Render

L'infrastructure Render est décrite en Infrastructure-as-Code dans [`render.yaml`](render.yaml) (Render Blueprint) : 1 base Postgres (`rr-postgres`, région Frankfurt/UE), 1 Web Service Docker pour le backend (`rr-backend`, gunicorn), 1 Static Site pour le frontend (`rr-frontend`, build Angular). Les 3 ressources sont créées en une fois via **Dashboard Render → New → Blueprint**.

Les services ont `autoDeployTrigger: off` : Render ne redéploie **pas** automatiquement à chaque push. Le déploiement est piloté par le job `deploy` de la CI (*Deploy Hooks*), pour qu'il n'ait lieu qu'après succès des tests/scans — cohérent avec le critère « environnement de déploiement automatisé ».

**Pour activer le déploiement continu** (une fois le Blueprint créé sur Render) :
1. Dashboard Render → `rr-backend` / `rr-frontend` → *Settings → Deploy Hook* → copier chaque URL.
2. Ajouter ces URLs comme secrets du repo GitHub : `Settings → Secrets and variables → Actions` :
   - `RENDER_DEPLOY_HOOK_BACKEND`
   - `RENDER_DEPLOY_HOOK_FRONTEND`
3. Appliquer le schéma Liquibase sur la base Render **une seule fois** (Django ne le fait pas, `models managed=False`) :
   ```
   make render-migrate RENDER_DB_HOST=... RENDER_DB_NAME=... RENDER_DB_USER=... RENDER_DB_PASSWORD=...
   ```
   (valeurs dans Render → `rr-postgres` → *Connect* → *External*)
4. Le prochain push sur `main` (après succès CI) déclenchera le déploiement des deux services.

**Limites du plan gratuit Render** (assumées, à mentionner à l'oral) : base Postgres free supprimée 30 jours après création (upgrade requis pour la pérenniser), web services free mis en veille après 15 min d'inactivité (cold start ~1 min), pas de Redis managé gratuit — le cache Django (throttling DRF) retombe alors sur un cache mémoire local (`LocMemCache`) au lieu de Redis.

## Points clés pour l'oral

- Pipeline 100 % automatisée : tests → build → scan sécurité → déploiement, sans action manuelle.
- Base de données de test réelle (Postgres), pas de mocks pour l'exécution des 102 tests backend.
- Scan Trivy des images Docker en complément de l'audit de sécurité applicatif (`SECURITY-AUDIT.md`, `PENTEST-REPORT.md`).
- Déploiement découplé du reste : la CI est fonctionnelle indépendamment de l'état de la mise en prod Render.
