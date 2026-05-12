from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import User, Citizen


# ─────────────────────────────────────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.Serializer):
    """
    Inscription d'un nouveau Citoyen.
    Crée User + Citizen dans une transaction atomique.
    Retourne les données publiques du compte créé (jamais le mot de passe).
    """

    user_fname = serializers.CharField(max_length=100)
    user_lname = serializers.CharField(max_length=100)
    user_mail  = serializers.EmailField(max_length=255)
    password   = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,    # jamais retourné dans la réponse
    )
    user_is_modo = serializers.BooleanField(default=False, required=False)

    def validate_user_mail(self, value: str) -> str:
        """Vérifie qu'aucun compte n'existe déjà avec cet email."""
        if User.objects.filter(user_mail=value).exists():
            raise serializers.ValidationError(
                "Un compte existe déjà avec cette adresse email."
            )
        return value.lower()    # normalisation email en minuscules

    def validate_password(self, value: str) -> str:
        """
        Validations minimales du mot de passe.
        À renforcer selon la politique de sécurité du projet.
        """
        if value.isdigit():
            raise serializers.ValidationError(
                "Le mot de passe ne peut pas être uniquement numérique."
            )
        return value

    @transaction.atomic
    def create(self, validated_data: dict) -> User:
        """
        Crée User + Citizen dans une transaction atomique.
        Si l'une des deux insertions échoue, les deux sont annulées.
        """
        # Extraction du mot de passe avant la création du User
        raw_password = validated_data.pop('password')
        is_modo      = validated_data.pop('user_is_modo', False)

        # Création du User
        user = User(
            user_fname=validated_data['user_fname'],
            user_lname=validated_data['user_lname'],
            user_mail=validated_data['user_mail'],
        )
        user.set_password(raw_password)   # hash via make_password()
        user.save()

        # Création du Citizen lié
        # user_created_at : non fourni → Postgres applique DEFAULT now()
        Citizen.objects.create(
            user=user,
            user_is_modo=is_modo,
            user_is_actived=True,
        )

        return user

    def to_representation(self, instance: User) -> dict:
        """Données retournées après inscription (jamais le mot de passe)."""
        return {
            'user_id':    str(instance.user_id),
            'user_fname': instance.user_fname,
            'user_lname': instance.user_lname,
            'user_mail':  instance.user_mail,
            'user_is_modo': instance.citizen.user_is_modo, # Optionnel : pour confirmer au front
        }


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────

class LoginSerializer(TokenObtainPairSerializer):
    """
    Authentification par email + mot de passe.

    Hérite de TokenObtainPairSerializer pour la génération JWT,
    et surcharge validate() pour persister les tokens en BDD.

    Champ utilisé : user_mail (USERNAME_FIELD du modèle User).
    SimpleJWT lit USERNAME_FIELD automatiquement — pas besoin de renommage.

    Flux :
    1. super().validate() vérifie les credentials et génère access + refresh.
    2. On récupère le Citizen lié à l'utilisateur validé.
    3. On persiste les tokens en BDD (user_token + user_refresh_token).
    4. On retourne la réponse enrichie avec les infos du profil.
    """

    def validate(self, attrs: dict) -> dict:
        """
        Valide les credentials et persiste les tokens JWT en BDD.
        """
        # ── Étape 1 : validation SimpleJWT (credentials + génération tokens) ──
        # super().validate() peuple self.user et retourne {'access': ..., 'refresh': ...}
        data = super().validate(attrs)

        # ── Étape 2 : persistance des tokens en BDD ───────────────────────────
        # self.user est l'instance User validée par SimpleJWT
        try:
            citizen = self.user.citizen
        except Citizen.DoesNotExist:
            raise AuthenticationFailed(
                "Profil citoyen introuvable.",
                code='citizen_not_found',
            )

        # Mise à jour des tokens en BDD — UPDATE ciblé sur 2 colonnes
        citizen.user_token         = data['access']
        citizen.user_refresh_token = data['refresh']
        citizen.save(update_fields=['user_token', 'user_refresh_token'])

        # ── Étape 3 : enrichissement de la réponse ────────────────────────────
        data['user'] = {
            'user_id':    str(self.user.user_id),
            'user_fname': self.user.user_fname,
            'user_lname': self.user.user_lname,
            'user_mail':  self.user.user_mail,
            'user_is_modo': citizen.user_is_modo,
        }

        return data