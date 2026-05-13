# (RE)Sources Relationnelles — Guide développeur

Plateforme de partage de ressources pour le bien-être relationnel.  
Stack : Django 5 + DRF · Angular 21 · PostgreSQL · Docker · DSFR

---

## Sommaire

1. [Prérequis](#prérequis)
2. [Démarrage rapide](#démarrage-rapide)
3. [Commandes disponibles](#commandes-disponibles)
4. [Architecture du projet](#architecture-du-projet)
5. [Frontend — Conventions Angular](#frontend--conventions-angular)
6. [Frontend — DSFR (design system)](#frontend--dsfr-design-system)
7. [Répartition des parties](#répartition-des-parties)
8. [Dépannage courant](#dépannage-courant)
9. [Références](#références)

---

## Prérequis

| Outil | Version minimale |
|-------|-----------------|
| Docker Desktop | dernière version stable |
| Git | — |

Aucune installation locale de Node, Python ou Angular CLI n'est nécessaire — tout tourne dans Docker.

---

## Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd ressources-relationnelles

# 2. Copier et remplir les variables d'environnement
cp .env.example .env   # éditer .env avec vos valeurs

# 3. Démarrer l'infra complète
make up
```

L'ordre de démarrage est géré automatiquement : Postgres → Liquibase (migrations) → Django → Angular.

| Service | URL |
|---------|-----|
| Frontend Angular | http://localhost:4200 |
| Backend Django | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

---

## Commandes disponibles

Toutes les commandes se lancent depuis la **racine du projet**.

```bash
make up              # Démarre toute l'infra (build inclus)
make down            # Arrête les containers (conserve les volumes)
make destroy         # Supprime tout, y compris les volumes BDD

make logs            # Logs de tous les services
make logs-back       # Logs Django uniquement
make logs-front      # Logs Angular uniquement

make status          # État des containers

make migrate         # Relance les migrations Liquibase

make shell-back      # Shell Python Django (manage.py shell)
make shell-db        # Shell psql PostgreSQL

make reinstall-front # Réinstalle npm dans le container (après modif package.json)
make restart-front   # Redémarre le serveur Angular (après modif angular.json)
```

---

## Architecture du projet

```
ressources-relationnelles/
├── docker-compose-root.yml   ← orchestrateur unique
├── Makefile                  ← toutes les commandes
├── .env                      ← variables d'environnement (ne pas commiter)
│
├── rr-infra/                 ← migrations Liquibase (SQL versionné)
│   └── liquibase/
│       └── db.changelog-master.yaml
│
├── rr-backend/               ← Django REST API
│   ├── users/
│   ├── resources/
│   ├── interactions/
│   └── administration/
│
└── rr-frontend/              ← Angular 21
    └── src/app/
        ├── core/             ← services, guards, interceptors, modèles
        ├── features/         ← pages (resources, auth, profile, …)
        └── shared/           ← composants réutilisables (navbar, cards, …)
```

### Règles backend importantes

- **Pas de `python manage.py migrate`** — la BDD est gérée exclusivement par Liquibase.
- Tous les modèles Django ont `managed = False` (ils ne créent pas de table).
- Auth JWT : access token 15 min, refresh token 7 jours.

---

## Frontend — Conventions Angular

Le frontend utilise les fonctionnalités modernes d'Angular 21. Voici les patterns à respecter.

### Composants standalone

Tous les composants sont **standalone** — pas de NgModule.

```typescript
@Component({
  selector: 'app-mon-composant',
  standalone: true,
  imports: [RouterLink, DatePipe, MonAutreComposant],
  templateUrl: './mon-composant.html',
})
export class MonComposant { }
```

### Signaux (signals)

Les données réactives utilisent `signal()` et `computed()`, pas `BehaviorSubject`.

```typescript
// Dans le composant
data    = signal<MaType | null>(null);
loading = signal(true);
error   = signal<string | null>(null);

// Computed
hasData = computed(() => this.data() !== null);
```

### Injection de dépendances

```typescript
private readonly service = inject(MonService);
readonly auth            = inject(AuthService);
```

### Flux de données asynchrones

```typescript
ngOnInit(): void {
  this.service.list().subscribe({
    next:  data  => { this.data.set(data);  this.loading.set(false); },
    error: ()    => { this.error.set('Erreur.'); this.loading.set(false); },
  });
}
```

### Syntaxe template (control flow)

```html
@if (loading()) {
  <p>Chargement…</p>
} @else if (error()) {
  <p class="fr-alert fr-alert--error">{{ error() }}</p>
} @else {
  @for (item of data(); track item.id) {
    <app-mon-card [item]="item" />
  }
}

@switch (resource().resource_label) {
  @case ('article') { … }
  @case ('videos')  { … }
  @default          { … }
}
```

### Inputs typés

```typescript
// Obligatoire
readonly resource = input.required<Resource>();

// Optionnel avec défaut
readonly compact = input(false);
```

### Structure des dossiers features

```
features/ma-feature/
├── ma-feature.ts          ← composant principal (logique)
├── ma-feature.html        ← template
└── services/
    └── ma-feature.service.ts
```

---

## Frontend — DSFR (design system)

Le projet utilise le **Système de Design de l'État** (DSFR v1.13.0).  
Documentation officielle : https://www.systeme-de-design.gouv.fr/

### Comment ça marche dans ce projet

Le CSS DSFR est chargé via `angular.json` (pas dans les fichiers `.scss`).  
Le fichier `src/styles.scss` contient **uniquement** les ajustements propres au projet.

### Classes essentielles

**Mise en page**
```html
<div class="fr-container">          <!-- Conteneur centré avec marges -->
<div class="fr-grid-row fr-grid-row--gutters">  <!-- Grille avec espacement -->
<div class="fr-col-12 fr-col-md-4"> <!-- Colonne responsive -->
```

**Composants courants**
```html
<!-- Carte -->
<div class="fr-card fr-card--shadow fr-enlarge-link">
  <div class="fr-card__body">
    <div class="fr-card__content">
      <h3 class="fr-card__title"><a href="#">Titre</a></h3>
      <p class="fr-card__desc">Description</p>
    </div>
  </div>
</div>

<!-- Boutons -->
<button class="fr-btn">Principal</button>
<button class="fr-btn fr-btn--secondary">Secondaire</button>
<button class="fr-btn fr-btn--tertiary fr-btn--sm">Petit tertiaire</button>

<!-- Champ texte -->
<div class="fr-input-group">
  <label class="fr-label" for="champ">Label</label>
  <input class="fr-input" type="text" id="champ">
</div>

<!-- Select -->
<div class="fr-select-group">
  <label class="fr-label" for="select">Label</label>
  <select class="fr-select" id="select">
    <option>Option</option>
  </select>
</div>

<!-- Alerte / info contextuelle -->
<div class="fr-callout">
  <p class="fr-callout__title">Titre</p>
  <p class="fr-callout__text">Contenu</p>
</div>

<!-- Badge -->
<p class="fr-badge fr-badge--green-emeraude">Publié</p>
<p class="fr-badge fr-badge--warning">En attente</p>

<!-- Tag (étiquette) -->
<p class="fr-tag fr-tag--sm">Catégorie</p>
```

**Navigation**
```html
<!-- Fil d'ariane -->
<nav aria-label="Vous êtes ici :">
  <ol class="fr-breadcrumb__list">
    <li><a class="fr-breadcrumb__link" href="/">Accueil</a></li>
    <li><span class="fr-breadcrumb__link">Page courante</span></li>
  </ol>
</nav>
```

### Classes utilitaires propres au projet (préfixe `rr-`)

Définies dans `src/styles.scss` :

| Classe | Usage |
|--------|-------|
| `.rr-pre-line` | Texte multi-lignes (descriptions) |
| `.rr-status-badges` | Groupe de badges côte à côte |
| `.rr-placeholder` | Zone réservée (composants pas encore intégrés) |

### Couleurs DSFR disponibles

Les couleurs utilisent des variables CSS : `var(--text-action-high-blue-france)`, `var(--background-alt-grey)`, etc.  
Voir la documentation DSFR pour la liste complète.

---

## Répartition des parties

| Membre | Partie | Fonctionnalités |
|--------|--------|-----------------|
| **FLO** | Partie 1 | Fondations (ApiService, intercepteurs, guards), Auth (login/register/logout), Profil utilisateur, Navbar |
| **ALEX** | Partie 2 | ✅ Ressources (liste, détail, formulaire, mes ressources, composants partagés) |
| **ILYECE** | Partie 3 | Interactions (like, favori, bookmark, exploité), Commentaires, Tableau de bord |
| **ADELIN** | Partie 4 | Modération (validation ressources/commentaires), Administration (users, catégories, stats) |

Voir `TODO-Frontend.md` pour le détail des tâches de chaque partie.

### Dépendances entre parties

```
Partie 1 (FLO) ──────────────────────────────────────────────────────────────────┐
  └─ ApiService, AuthService, AuthInterceptor, authGuard                          │
                                                                                   │
Partie 2 (ALEX) ────────────────────────────────────────────────────────────────→ ┤ ✅ Fait
  └─ ResourceService, resource-list, resource-detail, resource-form, my-resources │
                                                                                   │
Partie 3 (ILYECE) — dépend de Partie 1 + resource-detail de Partie 2            │
  └─ Boutons d'interaction dans resource-detail (placeholders .rr-placeholder)    │
                                                                                   │
Partie 4 (ADELIN) — dépend de Partie 1 + ModoGuard                              │
  └─ Pages modération/admin, protégées par modo.guard.ts                          ┘
```

### Routes existantes (Partie 2)

| Route | Composant | Auth |
|-------|-----------|------|
| `/resources` | Liste des ressources | Non |
| `/resources/:id` | Détail d'une ressource | Non |
| `/resources/new` | Formulaire de création | Oui |
| `/resources/:id/edit` | Formulaire d'édition | Oui |
| `/resources/mine` | Mes ressources | Oui |

Ajouter vos routes dans `src/app/app.routes.ts` en suivant le même pattern (lazy-loading + guard si nécessaire).

---

## Dépannage courant

### Les styles DSFR n'apparaissent pas

Le serveur Angular lit `angular.json` **une seule fois au démarrage**. Si vous modifiez `angular.json`, il faut redémarrer :

```bash
make restart-front
# puis attendre "Application bundle generation complete" dans les logs
make logs-front
```

### DSFR n'est pas installé dans le container

Si `node_modules/@gouvfr/dsfr` est absent (après un `make destroy` ou un premier démarrage) :

```bash
make reinstall-front
make restart-front
```

### Les styles apparaissent mais les icônes/polices sont absentes

Les assets DSFR (fonts, icons) sont copiés lors du build via `angular.json`. Vérifiez que les dossiers `/fonts` et `/icons` sont servis. Un `make restart-front` suffit généralement.

### Le backend renvoie des erreurs 401

Le token JWT a expiré (durée de vie : 15 min). L'intercepteur de refresh (Partie 1) doit le renouveler automatiquement. En attendant la Partie 1, rafraîchissez manuellement via `POST /api/auth/refresh/`.

### `make up` échoue sur Liquibase

La base de données n'était peut-être pas prête. Relancez :

```bash
make down
make up
```

Si ça persiste : `make destroy` puis `make up` (réinitialise la BDD).

### Modifications de `package.json` non prises en compte

Le volume Docker `node_modules` persiste entre les rebuilds. Après toute modification de `package.json` :

```bash
make reinstall-front   # installe dans le container actif
make restart-front     # redémarre ng serve
```

---

## Références

| Document | Contenu |
|----------|---------|
| [`ROUTES.md`](ROUTES.md) | Toutes les routes API avec méthodes et niveaux d'accès |
| [`TODO-Frontend.md`](TODO-Frontend.md) | Détail des tâches par partie |
| [`TODO-Backend.md`](TODO-Backend.md) | État du backend |
| [`Contexte.md`](Contexte.md) | Résumé architectural du projet |
| [Documentation DSFR](https://www.systeme-de-design.gouv.fr/) | Composants, classes, accessibilité |
| [Angular Signals](https://angular.dev/guide/signals) | Guide officiel sur les signaux |
