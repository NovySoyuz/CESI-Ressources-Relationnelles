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

## Déploiement Render — statut actuel : ⏸️ en attente

Le job `deploy` existe déjà dans le pipeline mais **ne fait rien pour l'instant** : il vérifie la présence des secrets GitHub `RENDER_DEPLOY_HOOK_BACKEND` et `RENDER_DEPLOY_HOOK_FRONTEND`, et s'arrête proprement (`::warning::`) tant qu'ils ne sont pas configurés.

**Pour l'activer**, une fois les services créés sur Render :
1. Créer les services Render (PostgreSQL managé, Web Service backend, Web Service/Static Site frontend).
2. Récupérer l'URL de *Deploy Hook* de chaque service (Render → Settings → Deploy Hook).
3. Ajouter ces URLs comme secrets du repo GitHub : `Settings → Secrets and variables → Actions` :
   - `RENDER_DEPLOY_HOOK_BACKEND`
   - `RENDER_DEPLOY_HOOK_FRONTEND`
4. Le prochain push sur `main` déclenchera automatiquement le déploiement.

## Points clés pour l'oral

- Pipeline 100 % automatisée : tests → build → scan sécurité → déploiement, sans action manuelle.
- Base de données de test réelle (Postgres), pas de mocks pour l'exécution des 102 tests backend.
- Scan Trivy des images Docker en complément de l'audit de sécurité applicatif (`SECURITY-AUDIT.md`, `PENTEST-REPORT.md`).
- Déploiement découplé du reste : la CI est fonctionnelle indépendamment de l'état de la mise en prod Render.
