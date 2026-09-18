export const environment = {
  androidApiHost: '10.0.2.2',  // émulateur QEMU
  // Vide = comportement historique (déduit dynamiquement dans api.service.ts :
  // même origine derrière nginx, ou :8000 en dev). Renseigné uniquement par
  // environment.render.ts pour le déploiement Render (front/back sur des
  // sous-domaines distincts).
  apiUrl: '',
};
