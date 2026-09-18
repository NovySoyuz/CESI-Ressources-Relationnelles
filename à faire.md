Où on en est
Côté outillage SAST (Sonar A) + DAST (ZAP 0 FAIL) + pentest (PT-01→04 corrigés) : c'est propre et validé, dev et prod.

Findings d'audit restants (non bloquants) : #6 tokens JWT en clair en base, #9 politique mot de passe, #10 tokens en localStorage, #11 secrets .env/SECRET_KEY.

On committe ce très gros lot cohérent (tout est testé), ou tu veux enchaîner sur #6/#9 ?