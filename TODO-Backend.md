# TODO — Back-end (RE)Sources Relationnelles

## Partie 1 — FLO : Auth + Utilisateurs

- [ ] **1.1** `users/models.py` — User + Citizen (`managed=False`)
- [ ] **1.2** `users/serializers.py` — Register + Login + Profil
- [ ] **1.3** `users/views.py` — Auth (Register, Login, Refresh, Logout)
- [ ] **1.4** `users/urls.py` — `/api/auth/` + `/api/users/`

---

## Partie 2 — ALEX : Ressources + Catalogue

- [ ] **2.1** `resources/models.py` — Resource + 8 sous-types (`managed=False`)
- [ ] **2.2** `resources/serializers.py` — Resource + sous-types
- [ ] **2.3** `resources/views.py` — CRUD + validation + publication
- [ ] **2.4** `resources/urls.py` — `/api/resources/`

---

## Partie 3 — ILYECE : Interactions + Progression

- [ ] **3.1** `interactions/models.py` — Interactions + Comments (`managed=False`)
- [ ] **3.2** `interactions/serializers.py` — Interactions + Comments
- [ ] **3.3** `interactions/views.py` — Like, favori, bookmark, commentaires
- [ ] **3.4** `interactions/urls.py` — `/api/interactions/` + `/api/comments/`

---

## Partie 4 — ADELIN : Admin + Stats

- [ ] **4.1** `admin_rr/models.py` — Admin + Category + Relation (`managed=False`)
- [ ] **4.2** `admin_rr/serializers.py` — Admin + Category + Relation
- [ ] **4.3** `admin_rr/views.py` — Back-office + modération
- [ ] **4.4** `admin_rr/urls.py` — `/api/admin/` + `/api/stats/`