// Utilisé uniquement pour le build de déploiement Render (`--configuration
// production,render`) : front (Static Site) et back (Web Service) vivent sur
// deux sous-domaines onrender.com distincts, donc pas d'origine commune
// possible → on pointe explicitement vers l'URL publique du backend.
// À adapter si le nom du service Render change (cf. render.yaml).
export const environment = {
  androidApiHost: '10.0.2.2',
  apiUrl: 'https://rr-backend-63e6.onrender.com',
};
