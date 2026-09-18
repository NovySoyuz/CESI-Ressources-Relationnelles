"""
Middleware de durcissement des en-têtes HTTP.

Ajoute les en-têtes de sécurité que Django ne pose pas par défaut :
CSP, Permissions-Policy, Cross-Origin-Resource-Policy, Referrer-Policy,
et masque la version du serveur (`Server`).

L'API renvoie du JSON : une CSP très restrictive (`default-src 'none'`)
est adaptée et sans impact fonctionnel.
"""


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response.setdefault(
            'Content-Security-Policy',
            # Directives sans fallback sur default-src explicitées (base-uri,
            # form-action, frame-ancestors) pour une CSP complète.
            "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        response.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=(), browsing-topics=()',
        )
        response.setdefault('Cross-Origin-Resource-Policy', 'same-origin')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        # Réponses d'API : ne pas mettre en cache (données potentiellement sensibles).
        response.setdefault('Cache-Control', 'no-store')

        # Ne pas divulguer la version du serveur / framework.
        response['Server'] = 'server'

        return response
