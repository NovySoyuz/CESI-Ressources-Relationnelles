import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'fr.ressourcesrelationnelles.app',
  appName: 'Ressources Relationnelles',
  webDir: '../front-web/dist/rr-frontend/browser',
  server: {
    androidScheme: 'http',
  },
  plugins: {
    CapacitorHttp: {
      // Désactivé : requêtes via WebView (ADB tunnel) plutôt que client natif Java
      enabled: false,
    },
  },
};

export default config;
