from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from users.models import User
from .models import Admin


# ── Auth ──────────────────────────────────────────────────────────────────────

class AdminLoginSerializer(TokenObtainPairSerializer):
    """
    Authentification d'un Admin par email + mot de passe.
    Vérifie que l'utilisateur possède un profil Admin avant de délivrer les tokens.
    Persiste les tokens en BDD (admin_token + admin_refresh_token).
    """

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)

        try:
            admin = self.user.admin_profile
        except Admin.DoesNotExist:
            raise AuthenticationFailed(
                "Profil administrateur introuvable.",
                code='admin_not_found',
            )

        admin.admin_token = data['access']
        admin.admin_refresh_token = data['refresh']
        admin.save(update_fields=['admin_token', 'admin_refresh_token'])

        data['user'] = {
            'user_id':        str(self.user.user_id),
            'user_fname':     self.user.user_fname,
            'user_lname':     self.user.user_lname,
            'user_mail':      self.user.user_mail,
            'is_super_admin': admin.admin_is_super_admin,
        }

        return data


# ── CRUD ──────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_fname', 'user_lname', 'user_mail']
        read_only_fields = fields


class UserWithAdminStatusSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'user_fname', 'user_lname', 'user_mail', 'is_admin']
        read_only_fields = fields

    def get_is_admin(self, obj) -> bool:
        return hasattr(obj, 'admin_profile') and obj.admin_profile is not None


class AdminListSerializer(serializers.ModelSerializer):
    user_fname = serializers.CharField(source='admin_id.user_fname', read_only=True)
    user_lname = serializers.CharField(source='admin_id.user_lname', read_only=True)
    user_mail  = serializers.EmailField(source='admin_id.user_mail',  read_only=True)
    is_active  = serializers.BooleanField(source='admin_id.is_active', read_only=True)

    class Meta:
        model = Admin
        fields = [
            'admin_id', 'user_fname', 'user_lname', 'user_mail',
            'is_active', 'admin_is_super_admin', 'admin_created_at',
        ]
        read_only_fields = fields


class AdminDetailSerializer(serializers.ModelSerializer):
    user      = UserSerializer(source='admin_id', read_only=True)
    is_active = serializers.BooleanField(source='admin_id.is_active', read_only=True)

    class Meta:
        model = Admin
        fields = [
            'admin_id', 'user', 'is_active',
            'admin_is_super_admin', 'admin_created_at',
            'admin_token', 'admin_refresh_token',
        ]
        read_only_fields = ['admin_id', 'admin_created_at', 'admin_token', 'admin_refresh_token']


class AdminCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Admin
        fields = ['user_id', 'admin_is_super_admin']

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet identifiant.")
        if Admin.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà administrateur.")
        return value

    def create(self, validated_data):
        user = User.objects.get(pk=validated_data.pop('user_id'))
        return Admin.objects.create(admin_id=user, **validated_data)


class AdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['admin_is_super_admin']
