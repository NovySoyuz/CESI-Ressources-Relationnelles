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
        "user_is_modo": "false"
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
            "user_is_modo": "false"
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.citizen.invalidate_tokens()
        except Citizen.DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────────────────────────────────────────
# PROFIL
# ─────────────────────────────────────────────────────────────────────────────

class MeView(APIView):
    """
    GET  /api/auth/me/ — profil de l'utilisateur connecté
    PATCH /api/auth/me/ — modifier prénom, nom et/ou mot de passe
    DELETE /api/auth/me/ — supprimer le compte
    """

    permission_classes = [IsAuthenticated]

    def _profile_data(self, user):
        citizen = user.citizen
        return {
            'user_id':         str(user.user_id),
            'user_fname':      user.user_fname,
            'user_lname':      user.user_lname,
            'user_mail':       user.user_mail,
            'user_is_modo':    citizen.user_is_modo,
            'user_is_actived': citizen.user_is_actived,
            'user_created_at': citizen.user_created_at,
        }

    def get(self, request):
        try:
            return Response(self._profile_data(request.user))
        except Citizen.DoesNotExist:
            return Response({'error': 'Profil citoyen introuvable.'}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request):
        user = request.user
        data = request.data

        if 'user_fname' in data:
            fname = str(data['user_fname']).strip()
            if not fname:
                return Response({'error': 'Le prénom ne peut pas être vide.'}, status=status.HTTP_400_BAD_REQUEST)
            user.user_fname = fname

        if 'user_lname' in data:
            lname = str(data['user_lname']).strip()
            if not lname:
                return Response({'error': 'Le nom ne peut pas être vide.'}, status=status.HTTP_400_BAD_REQUEST)
            user.user_lname = lname

        if 'new_password' in data:
            if not user.check_password(data.get('current_password', '')):
                return Response({'error': 'Mot de passe actuel incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            new_pwd = str(data['new_password'])
            if len(new_pwd) < 8:
                return Response({'error': 'Le mot de passe doit contenir au moins 8 caractères.'}, status=status.HTTP_400_BAD_REQUEST)
            if new_pwd.isdigit():
                return Response({'error': 'Le mot de passe ne peut pas être uniquement numérique.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_pwd)

        user.save()

        try:
            return Response(self._profile_data(user))
        except Citizen.DoesNotExist:
            return Response({'error': 'Profil citoyen introuvable.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)