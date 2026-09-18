from pathlib import Path
import sys
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# `manage.py test` / pytest : détecté pour isoler le cache (throttling DRF) de
# tout Redis partagé (dev, CI). Sans ça, les compteurs de débit persistent
# entre deux exécutions de la suite et peuvent faire échouer des tests
# indépendants (429 au lieu du code attendu).
TESTING = 'test' in sys.argv or 'pytest' in sys.modules

SECRET_KEY = os.getenv('SECRET_KEY')

# #4 — DEBUG piloté par l'environnement (False par défaut = sûr).
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# #5 — Liste blanche d'hôtes depuis l'environnement.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Render injecte automatiquement le hostname réel du service (utile si un
# suffixe anti-collision a été ajouté au nom, ex. "rr-backend-a1b2.onrender.com"
# au lieu de "rr-backend.onrender.com"). Sans ça, le health check HTTP de
# Render (Host = ce hostname réel) reçoit un 400 DisallowedHost en boucle et
# le déploiement ne devient jamais "live". Voir https://render.com/docs/environment-variables
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'users',
    'interactions',
    'resources',
    'administration',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'config.middleware.SecurityHeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

# Cache Redis — backend du throttling DRF, partagé entre workers/instances.
# En test, on isole avec un cache mémoire local pour ne pas dépendre d'un
# Redis externe ni laisser les compteurs de throttling persister entre runs.
# En production sans REDIS_URL (ex : Render free tier, pas de Redis managé
# gratuit), on retombe aussi sur LocMemCache : le throttling reste fonctionnel
# (par instance) même sans Redis, au prix d'un partage des compteurs entre
# workers d'une même instance seulement (acceptable en mono-instance free tier).
REDIS_URL = os.getenv('REDIS_URL')
if TESTING or not REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Anti brute-force : ScopedRateThrottle ne limite QUE les vues qui
    # déclarent un `throttle_scope` (login/register). Les autres vues ne sont
    # pas affectées. Limite par IP pour les requêtes anonymes.
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login':    '5/min',
        'register': '10/hour',
    },
}

# JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',

}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:4200').split(',')

# ── Sécurité HTTP ────────────────────────────────────────────────────────────
# Toujours actifs (dev + prod)
SECURE_CONTENT_TYPE_NOSNIFF = True          # X-Content-Type-Options: nosniff
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# Actifs uniquement en production (derrière HTTPS) — évite de casser le dev en HTTP.
PRODUCTION = os.getenv('DJANGO_ENV', 'dev') == 'production'
if PRODUCTION:
    # Render termine déjà le TLS à son edge et redirige HTTP→HTTPS lui-même
    # avant d'atteindre le conteneur ; une redirection applicative en plus
    # casse son health check interne (requête HTTP directe, sans passer par
    # l'edge public) qui reste alors bloqué en boucle sur des 301 → déploiement
    # qui ne devient jamais "live". Désactivable via DJANGO_SECURE_SSL_REDIRECT.
    SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
    SECURE_HSTS_SECONDS = 31536000          # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Derrière un reverse-proxy qui termine le TLS :
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Throttling par IP réelle du client (via X-Forwarded-For posé par nginx).
    REST_FRAMEWORK['NUM_PROXIES'] = 1