# Routes API — (RE)Sources Relationnelles

## Auth — `/api/auth/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| POST | `/api/auth/register/` | Inscription d'un citoyen | Non |
| POST | `/api/auth/login/` | Connexion + récupération des tokens JWT | Non |
| POST | `/api/auth/refresh/` | Rafraîchir l'access token | Non |
| POST | `/api/auth/logout/` | Révocation du refresh token | Oui |

---

## Utilisateurs — `/api/users/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/users/me/` | Récupérer son profil | Oui |
| PATCH | `/api/users/me/` | Modifier son profil | Oui |
| DELETE | `/api/users/me/` | Supprimer son compte (RGPD) | Oui |
| GET | `/api/users/me/progression/` | Tableau de bord de progression | Oui |
| GET | `/api/users/` | Lister tous les citoyens | Admin |
| PATCH | `/api/users/{id}/activate/` | Activer / désactiver un compte | Admin |

---

## Ressources — `/api/resources/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/resources/` | Lister toutes les ressources publiques | Non |
| GET | `/api/resources/{id}/` | Détail d'une ressource | Non |
| POST | `/api/resources/` | Créer une ressource | Oui |
| PATCH | `/api/resources/{id}/` | Modifier une ressource | Oui (auteur) |
| DELETE | `/api/resources/{id}/` | Supprimer une ressource | Oui (auteur/admin) |
| GET | `/api/resources/search/` | Recherche par mots-clés | Non |
| GET | `/api/resources/filter/` | Filtrer (catégorie, type, relation) | Non |
| POST | `/api/resources/{id}/publish/` | Soumettre pour validation | Oui (auteur) |
| POST | `/api/resources/{id}/validate/` | Valider/refuser une ressource | Modérateur |
| POST | `/api/resources/{id}/like/` | Liker / unliker | Oui |
| POST | `/api/resources/{id}/favori/` | Ajouter / retirer des favoris | Oui |
| POST | `/api/resources/{id}/bookmark/` | Ajouter / retirer bookmark | Oui |
| POST | `/api/resources/{id}/exploit/` | Marquer comme exploitée | Oui |
| GET | `/api/resources/{id}/comments/` | Lister les commentaires | Non |
| POST | `/api/resources/{id}/comments/` | Ajouter un commentaire | Oui |

---

## Interactions — `/api/interactions/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/interactions/likes/` | Toutes les ressources likées | Oui |
| GET | `/api/interactions/favoris/` | Toutes les ressources favorites | Oui |
| GET | `/api/interactions/bookmarks/` | Toutes les ressources mises de côté | Oui |
| GET | `/api/interactions/exploited/` | Toutes les ressources exploitées | Oui |
| GET | `/api/interactions/summary/` | Résumé complet (17 likes, 5 favoris...) | Oui |

---

## Commentaires — `/api/comments/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| PATCH | `/api/comments/{id}/` | Modifier un commentaire | Oui (auteur) |
| DELETE | `/api/comments/{id}/` | Supprimer un commentaire | Oui (auteur/modo) |
| POST | `/api/comments/{id}/reply/` | Répondre à un commentaire | Oui |
| PATCH | `/api/comments/{id}/moderate/` | Modérer un commentaire | Modérateur |

---

## Administration — `/api/administration/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/administration/users/` | Lister tous les utilisateurs | Admin |
| POST | `/api/administration/users/` | Créer un modérateur / admin | Super-admin |
| GET | `/api/administration/categories/` | Lister les catégories | Admin |
| POST | `/api/administration/categories/` | Créer une catégorie | Admin |
| PATCH | `/api/administration/categories/{id}/` | Modifier une catégorie | Admin |
| DELETE | `/api/administration/categories/{id}/` | Supprimer une catégorie | Admin |
| GET | `/api/administration/relations/` | Lister les types de relations | Admin |
| POST | `/api/administration/relations/` | Créer un type de relation | Admin |
| PATCH | `/api/administration/relations/{id}/` | Modifier un type de relation | Admin |
| DELETE | `/api/administration/relations/{id}/` | Supprimer un type de relation | Admin |

---

## Statistiques — `/api/stats/`

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/stats/dashboard/` | Tableau de bord global | Admin |
| GET | `/api/stats/resources/` | Stats par ressource | Admin |
| GET | `/api/stats/users/` | Stats par utilisateur | Admin |
| GET | `/api/stats/export/` | Export CSV des statistiques | Admin |

---

## Légende

| Niveau | Description |
|--------|-------------|
| Non | Accessible sans authentification |
| Oui | Nécessite un access token JWT valide |
| Oui (auteur) | Réservé à l'auteur de la ressource/commentaire |
| Modérateur | Rôle modérateur requis |
| Admin | Rôle administrateur requis |
| Super-admin | Rôle super-administrateur requis |
