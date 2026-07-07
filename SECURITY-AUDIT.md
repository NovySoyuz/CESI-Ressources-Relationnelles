# Audit de sécurité — Ressources Relationnelles

_Date : 2026-07-07 · Périmètre : `rr-backend` (Django/DRF), `rr-frontend` (Angular), config._

## Synthèse

| # | Sévérité | Titre | Emplacement |
|---|----------|-------|-------------|
| 1 | 🔴 Critique | Élévation de privilège : n'importe quel utilisateur connecté peut se rendre admin/super-admin | `administration/views.py:94` |
| 2 | 🔴 Critique | Vol de session admin : les tokens JWT admin sont exposés par l'API à tout utilisateur connecté | `administration/views.py:113` + `serializers.py:89` |
| 3 | 🟠 Élevé | Élévation de privilège à l'inscription : `user_is_modo` accepté depuis le client | `users/serializers.py:28,57,71` |
| 4 | 🟠 Élevé | `DEBUG = True` en dur | `config/settings.py:9` |
| 5 | 🟠 Élevé | `ALLOWED_HOSTS = ['*']` | `config/settings.py:11` |
| 6 | 🟠 Élevé | Tokens JWT stockés en clair en base | `users/models.py:115`, `administration/models.py:23` |
| 7 | 🟡 Moyen | Aucun throttling → brute-force & énumération de comptes | `config/settings.py` (REST_FRAMEWORK) |
| 8 | 🟡 Moyen | En-têtes de sécurité prod absents (HSTS, cookies secure, SSL redirect) | `config/settings.py` |
| 9 | 🟡 Moyen | Politique de mot de passe faible et incohérente | `users/serializers.py:38`, `users/views.py:247` |
| 10 | 🟢 Faible | Tokens stockés dans `localStorage` (exposés au XSS) | `auth.service.ts:38` |
| 11 | 🟢 Faible | Secrets de dev committés / `db.sqlite3` présent | `.env`, `rr-backend/db.sqlite3` |

---

## 1. 🔴 Élévation de privilège vers admin — `AdminListCreateView`

`administration/views.py:94`

```python
class AdminListCreateView(APIView):
    permission_classes = [IsAuthenticated]   # ⚠️ devrait être [IsAdmin] super-admin
    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)  # user_id + admin_is_super_admin
```

**Impact :** tout citoyen authentifié peut appeler `POST /admin/admins/` avec son propre `user_id` et `admin_is_super_admin: true` → il devient **super-administrateur**. `AdminCreateSerializer` ne vérifie que l'existence de l'utilisateur, jamais que l'appelant est admin. Le `GET` liste également tous les admins.

**Correctif :** `permission_classes = [IsAdmin]` (voire un contrôle super-admin explicite pour la création).

## 2. 🔴 Vol de tokens admin — `AdminDetailView` + `AdminDetailSerializer`

`administration/views.py:113`, `administration/serializers.py:80-91`

```python
class AdminDetailView(APIView):
    permission_classes = [IsAuthenticated]   # ⚠️ pas [IsAdmin]

class AdminDetailSerializer(...):
    fields = [..., 'admin_token', 'admin_refresh_token']   # ⚠️ tokens exposés
```

**Impact :** tout utilisateur connecté peut faire `GET /admin/admins/<id>/` et récupérer les **JWT access/refresh d'un admin** → prise de contrôle complète du compte admin. Il peut aussi `PATCH` (basculer super-admin) ou `DELETE` n'importe quel admin.

**Correctif :** passer la vue en `[IsAdmin]` **et** retirer `admin_token` / `admin_refresh_token` du serializer (aucune raison de les renvoyer par l'API).

## 3. 🟠 Auto-attribution du rôle modérateur à l'inscription

`users/serializers.py:28,57,71` — la vue `RegisterView` est `AllowAny`.

```python
user_is_modo = serializers.BooleanField(default=False, required=False)  # accepté du client
...
Citizen.objects.create(user=user, user_is_modo=is_modo, ...)
```

**Impact :** `POST /api/auth/register/` avec `"user_is_modo": true` crée un compte **modérateur**. Or un modérateur peut modifier/supprimer/publier n'importe quelle ressource (`resources/views.py:194,222,259`). Modération auto-attribuée = prise de contrôle du contenu.

**Correctif :** ignorer `user_is_modo` côté inscription (forcer `False`) ; n'accorder ce rôle que via un endpoint admin protégé.

## 4. 🟠 `DEBUG = True` en dur — `config/settings.py:9`

En production, expose les stack traces, requêtes SQL, variables d'environnement et réglages sur toute erreur 500. **Correctif :** `DEBUG = os.getenv('DEBUG', 'False') == 'True'`.

## 5. 🟠 `ALLOWED_HOSTS = ['*']` — `config/settings.py:11`

Autorise toute valeur d'en-tête `Host` (Host header injection, empoisonnement de cache/liens). **Correctif :** lire une liste depuis l'environnement.

## 6. 🟠 Tokens JWT persistés en clair — `users/models.py:115`, `administration/models.py:23`

`user_token`, `user_refresh_token`, `admin_token`, `admin_refresh_token` sont des `CharField` stockant les JWT en clair. Une fuite BDD (dump, backup, injection) permet le rejeu de toutes les sessions actives. Le design lui-même est discutable (SimpleJWT est stateless ; la persistance n'apporte de valeur qu'avec une vraie blacklist).

**Correctif :** ne pas stocker les tokens ; si une révocation est requise, utiliser `rest_framework_simplejwt.token_blacklist` (stocke un hash du jti, pas le token).

## 7. 🟡 Aucun throttling — brute-force / énumération

`config/settings.py:67` — aucun `DEFAULT_THROTTLE_CLASSES`. Login/register/refresh sont sans limite de débit → brute-force de mots de passe. De plus `validate_user_mail` renvoie « Un compte existe déjà » → **énumération d'emails**.

**Correctif :** activer `AnonRateThrottle`/`ScopedRateThrottle` sur les endpoints d'auth ; message d'inscription générique.

## 8. 🟡 En-têtes de sécurité production manquants

`SecurityMiddleware` est présent mais non configuré. Absents : `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_PROXY_SSL_HEADER`, `SECURE_CONTENT_TYPE_NOSNIFF`. **Correctif :** ajouter ces réglages, conditionnés par un flag prod.

## 9. 🟡 Politique de mot de passe faible et incohérente

Inscription (`serializers.py:38`) : min 8 + non-numérique uniquement. Changement (`views.py:247`) : mêmes règles réimplémentées à la main. Pas de `AUTH_PASSWORD_VALIDATORS`. **Correctif :** définir `AUTH_PASSWORD_VALIDATORS` et appeler `validate_password()` de Django aux deux endroits.

## 10. 🟢 Tokens en `localStorage` — `auth.service.ts:38`

`localStorage` est lisible par tout JavaScript de la page → un XSS exfiltre directement les JWT. **Correctif :** idéalement cookies `HttpOnly`+`Secure` ; a minima, durcir la CSP et l'échappement.

## 11. 🟢 Artefacts sensibles en dev

`.env` contient des identifiants (`rr_secret_password`, `SECRET_KEY=la-cle-generee-juste-avant` — placeholder faible). Il est bien dans `.gitignore` (non versionné), mais `SECRET_KEY` doit être une vraie clé aléatoire en prod. `rr-backend/db.sqlite3` traîne dans l'arbo (non suivi). **Correctif :** générer une vraie `SECRET_KEY`, supprimer le sqlite de dev.

---

## Points positifs

- Mots de passe hachés via `set_password()` (PBKDF2 Django). ✅
- ORM Django partout, aucune SQL brute / `eval` / `exec`. ✅
- Contrôle de propriété correct sur les ressources non visibles et la suppression de commentaires. ✅
- Rotation + durée de vie courte des access tokens (15 min). ✅
- `.env` bien gitignoré. ✅

## Priorisation

1. **Immédiat :** #1, #2, #3 (élévations de privilège exploitables à distance sans conditions).
2. **Avant mise en prod :** #4, #5, #6, #7, #8.
3. **Durcissement :** #9, #10, #11.