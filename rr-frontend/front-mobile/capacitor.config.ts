import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'fr.ressourcesrelationnelles.app',
  appName: 'Ressources Relationnelles',
  webDir: 'dist/rr-mobile/browser',
  server: {
    androidScheme: 'https',
  },
};

export default config;
