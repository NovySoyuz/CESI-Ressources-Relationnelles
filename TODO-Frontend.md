# TODO — Front-end (RE)Sources Relationnelles

> Stack : Angular · Tailwind CSS · DaisyUI · Capacitor (mobile)
> API : Django REST Framework — voir `ROUTES.md`
> 3 parties (le 4ème membre assure la modération/admin avec la Partie 3)

---

## Partie 1 — FLO : Fondations + Auth + Profil

> À livrer en premier — les deux autres parties en dépendent.

### Setup & Infrastructure

- [ ] **1.1** `core/services/api.service.ts` — service HTTP de base (base URL, headers)
- [ ] **1.2** `core/interceptors/auth.interceptor.ts` — injection du Bearer token sur chaque requête
- [ ] **1.3** `core/interceptors/refresh.interceptor.ts` — refresh automatique du token (401 → `/api/auth/refresh/`)
- [ ] **1.4** `core/guards/auth.guard.ts` — redirection vers `/login` si non connecté
- [ ] **1.5** `core/guards/modo.guard.ts` — redirection si pas modérateur
- [ ] **1.6** `core/services/auth.service.ts` — stockage tokens (localStorage), état connecté, helpers `isLogged()` / `isModo()`

### Layout

- [ ] **1.7** `shared/components/navbar/` — logo, liens nav, avatar + menu utilisateur, responsive
- [ ] **1.8** `shared/components/layout/` — structure globale (navbar + `<router-outlet>` + footer)

### Pages Auth

- [ ] **1.9** `features/auth/login/` — formulaire email + mot de passe, appel `POST /api/auth/login/`, stockage tokens
- [ ] **1.10** `features/auth/register/` — formulaire inscription, appel `POST /api/auth/register/`
- [ ] **1.11** `features/auth/logout/` — appel `POST /api/auth/logout/`, vidage tokens, redirection

### Profil utilisateur

- [ ] **1.12** `features/profile/profile-view/` — affichage profil (`GET /api/users/me/`)
- [ ] **1.13** `features/profile/profile-edit/` — formulaire édition (`PATCH /api/users/me/`)
- [ ] **1.14** `features/profile/delete-account/` — confirmation suppression compte (`DELETE /api/users/me/`)

### Routing

- [ ] **1.15** `app.routes.ts` — routes globales, lazy-loading des modules, guards appliqués

---

## Partie 2 — ALEX : Ressources

> Dépend du `AuthService` et de l'`AuthInterceptor` (Partie 1).

### Service

- [ ] **2.1** `features/resources/services/resource.service.ts` — tous les appels API ressources (list, get, create, patch, delete, publish)

### Pages & Composants

- [ ] **2.2** `features/resources/resource-list/` — liste des ressources publiques (`GET /api/resources/`)
  - Filtres : catégorie, type (label), relation
  - Recherche par mots-clés
  - Tri (date, titre)
  - Composant carte ressource réutilisable

- [ ] **2.3** `features/resources/resource-detail/` — page détail (`GET /api/resources/{id}/`)
  - Affichage champs communs + section sous-type dynamique selon `resource_label`
  - Boutons interactions (like, favori, bookmark, exploité) — composants Partie 3

- [ ] **2.4** `features/resources/resource-form/` — formulaire création + édition (`POST` / `PATCH /api/resources/{id}/`)
  - Champs communs (titre, description, catégories, relations)
  - Section sous-type conditionnelle selon le label sélectionné (8 sous-types)
  - Validation côté client

- [ ] **2.5** `features/resources/my-resources/` — liste des ressources de l'utilisateur connecté
  - Indicateur de visibilité (publiée / en attente)
  - Liens édition / suppression

### Composants partagés

- [ ] **2.6** `shared/components/resource-card/` — carte ressource (titre, auteur, catégories, badge type)
- [ ] **2.7** `shared/components/category-badge/` — badge catégorie réutilisable
- [ ] **2.8** `shared/components/filter-bar/` — barre de filtres réutilisable

---

## Partie 3 — ADELIN : Interactions + Modération

> Dépend du `AuthService` (Partie 1) et de `resource-detail` (Partie 2) pour les boutons.

### Services

- [ ] **3.1** `features/interactions/services/interaction.service.ts` — like, favori, bookmark, exploit (`POST /api/resources/{id}/like/` etc.)
- [ ] **3.2** `features/comments/services/comment.service.ts` — liste, ajout, réponse, suppression, modération

### Interactions sur une ressource

- [ ] **3.3** `shared/components/interaction-buttons/` — groupe de boutons (like, favori, bookmark, exploité), état toggle, compteurs
- [ ] **3.4** `features/comments/comment-list/` — liste des commentaires d'une ressource (`GET /api/resources/{id}/comments/`)
- [ ] **3.5** `features/comments/comment-form/` — poster un commentaire (`POST /api/resources/{id}/comments/`)
- [ ] **3.6** `features/comments/comment-reply/` — répondre à un commentaire (`POST /api/comments/{id}/reply/`)

### Tableau de bord utilisateur

- [ ] **3.7** `features/dashboard/my-interactions/` — ressources likées, favorites, bookmarks, exploitées (`GET /api/interactions/*/`)
- [ ] **3.8** `features/dashboard/progression/` — résumé progression (`GET /api/interactions/summary/`)

### Modération

- [ ] **3.9** `features/moderation/resource-moderation/` — liste des ressources en attente de validation, bouton publier/dépublier (`PATCH /api/resources/{id}/publish/`)
- [ ] **3.10** `features/moderation/comment-moderation/` — liste des commentaires signalés, bouton modérer (`PATCH /api/comments/{id}/moderate/`)

### Administration

- [ ] **3.11** `features/admin/user-list/` — liste des citoyens (`GET /api/administration/users/`), activer/désactiver
- [ ] **3.12** `features/admin/category-manager/` — CRUD catégories (`/api/administration/categories/`)
- [ ] **3.13** `features/admin/relation-manager/` — CRUD types de relations (`/api/administration/relations/`)
- [ ] **3.14** `features/admin/stats-dashboard/` — tableau de bord stats (`GET /api/stats/dashboard/`)
