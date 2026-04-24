"""
users/views.py

Vues d'authentification :
- RegisterView  : POST /api/auth/register/
- LoginView     : POST /api/auth/login/
- RefreshView   : POST /api/auth/refresh/   (avec persistance du nouveau token en BDD)
- LogoutView    : POST /api/auth/logout/    (révocation des tokens en BDD)

Chaque vue est documentée avec le format exact attendu en entrée/sortie
pour faciliter les tests Postman et l'intégration Angular.
"""

from rest_framework          import status
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views       import TokenRefreshView
from rest_framework_simplejwt.tokens      import RefreshToken
from rest_framework_simplejwt.exceptions  import TokenError, InvalidToken

from .models      import Citizen
from .serializers import RegisterSerializer, LoginSerializer


# ─────────────────────────────────────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    Inscription d'un nouveau Citoyen.

    POST /api/auth/register/
    Permission : publique (AllowAny)

    Body JSON attendu :
    {
        "user_fname":   "Florent",
        "user_lname":   "Dev",
        "user_mail":    "florent@example.com",
        "password":     "monMotDePasse123",
        "user_la_mode": "light"   <- optionnel, défaut "light"
    }

    Réponse 201 :
    {
        "user_id":    "uuid-...",
        "user_fname": "Florent",
        "user_lname": "Dev",
        "user_mail":  "florent@example.com"
    }

    Réponse 400 : erreurs de validation (email déjà pris, password trop court…)
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        return Response(
            serializer.to_representation(user),
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    Connexion d'un Citoyen — génère et persiste les tokens JWT en BDD.

    POST /api/auth/login/
    Permission : publique (AllowAny)

    Body JSON attendu :
    {
        "user_mail": "florent@example.com",
        "password":  "monMotDePasse123"
    }

    Réponse 200 :
    {
        "access":  "<jwt_access_token>",    <- durée de vie 15 min
        "refresh": "<jwt_refresh_token>",   <- durée de vie 7 jours
        "user": {
            "user_id":      "uuid-...",
            "user_fname":   "Florent",
            "user_lname":   "Dev",
            "user_mail":    "florent@example.com",
            "user_la_mode": "light"
        }
    }

    Réponse 401 : credentials incorrects ou compte désactivé
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {'detail': 'Identifiants incorrects ou compte désactivé.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# REFRESH
# ─────────────────────────────────────────────────────────────────────────────

class CustomRefreshView(TokenRefreshView):
    """
    Renouvellement du token d'accès avec rotation + persistance en BDD.

    POST /api/auth/refresh/
    Permission : publique (le refresh token est la preuve d'identité)

    Body JSON attendu :
    {
        "refresh": "<jwt_refresh_token>"
    }

    Réponse 200 :
    {
        "access":  "<nouveau_jwt_access_token>",
        "refresh": "<nouveau_jwt_refresh_token>"   <- rotation activée
    }

    Réponse 401 : refresh token expiré, révoqué ou déjà utilisé
    """

    def post(self, request, *args, **kwargs):
        # ── Étape 1 : validation et rotation SimpleJWT ────────────────────
        # TokenRefreshView gère la validation cryptographique + blacklist
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        # ── Étape 2 : persistance des nouveaux tokens en BDD ─────────────
        # On extrait user_id depuis le nouveau access token pour trouver
        # le Citizen à mettre à jour.
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            new_access  = response.data.get('access')
            new_refresh = response.data.get('refresh')

            decoded = AccessToken(new_access)
            user_id = decoded.get('user_id')

            Citizen.objects.filter(user_id=user_id).update(
                user_token=new_access,
                user_refresh_token=new_refresh,
            )
        except Exception:
            # Si la persistance BDD échoue, on ne bloque pas le refresh.
            # Le token SimpleJWT reste valide côté crypto.
            # En production : logger l'erreur ici.
            pass

        return response


# ─────────────────────────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    Déconnexion — révoque les tokens en BDD et blackliste le refresh JWT.

    POST /api/auth/logout/
    Permission : authentifié (IsAuthenticated)

    Body JSON attendu :
    {
        "refresh": "<jwt_refresh_token>"
    }

    Réponse 204 : déconnexion réussie (No Content)
    Réponse 400 : refresh token manquant ou invalide

    Après ce call :
    - citizen.user_token = NULL
    - citizen.user_refresh_token = NULL
    - Le refresh token est blacklisté côté SimpleJWT
    → Toute requête ultérieure avec l'ancien access token sera rejetée
      par DBValidatedJWTAuthentication (token != celui en BDD = NULL)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token_str = request.data.get('refresh')

        if not refresh_token_str:
            return Response(
                {'detail': 'Le refresh token est requis pour se déconnecter.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Blacklist SimpleJWT ────────────────────────────────────────────
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
        except TokenError:
            # Token déjà expiré ou invalide — on continue quand même
            # pour révoquer en BDD (nettoyage cohérent).
            pass

        # ── Révocation en BDD ──────────────────────────────────────────────
        # request.user est l'instance User injectée par l'authentication backend
        try:
            request.user.citizen.invalidate_tokens()
        except Citizen.DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)