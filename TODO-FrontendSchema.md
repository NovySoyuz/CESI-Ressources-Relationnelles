## Partie 1 — FLO : Fondations + Auth + Profil

Composants / Routes
│
▼
[Guards] ──────────────────────────────────┐
authGuard   → vérifie isLogged()           │
modoGuard   → vérifie isModo()             │  injectent
│                                      ▼
│                               [AuthService]
│                             ┌─────────────────────────────┐
│                             │ - stocke access/refresh     │
│                             │   token + user (localStorage│
│                             │ - signal _user (réactif)    │
│                             │ - computed isLogged/isModo  │
│                             └─────────────────────────────┘
│                                      ▲
▼                                      │
[Requêtes HTTP via ApiService]               │ injectent
│                                      │
├──► authInterceptor ─────────────────►│ lit getAccessToken()
│         │ ajoute header              │ et clone la requête
│         │ Authorization: Bearer xxx  │
│                                      │
└──► refreshInterceptor ──────────────►│ lit getRefreshToken()
│ attrape les 401            │ appelle updateAccessToken()
│ appelle ApiService.post()  │ ou clearSession()
└── redirige vers /login ──► Router


