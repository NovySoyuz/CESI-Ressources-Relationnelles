# administration/serializers.py

from rest_framework import serializers
from users.models import User, Citizen
from administration.models import Admin


# ──────────────────────────────────────────────────────────────
# User (lecture seule — géré par l'app users)
# ──────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_id",
            "user_fname",
            "user_lname",
            "user_mail",
        ]
        read_only_fields = fields


# ──────────────────────────────────────────────────────────────
# Admin — liste
# ──────────────────────────────────────────────────────────────

class AdminListSerializer(serializers.ModelSerializer):
    user_fname        = serializers.CharField(source="admin_id.user_fname", read_only=True)
    user_lname        = serializers.CharField(source="admin_id.user_lname", read_only=True)
    user_mail         = serializers.EmailField(source="admin_id.user_mail",  read_only=True)
    is_active         = serializers.BooleanField(source="admin_id.is_active", read_only=True)

    class Meta:
        model = Admin
        fields = [
            "admin_id",
            "user_fname",
            "user_lname",
            "user_mail",
            "is_active",
            "admin_is_super_admin",
            "admin_created_at",
        ]
        read_only_fields = fields


# ──────────────────────────────────────────────────────────────
# Admin — détail (inclut les tokens, pour usage interne)
# ──────────────────────────────────────────────────────────────

class AdminDetailSerializer(serializers.ModelSerializer):
    user              = UserSerializer(source="admin_id", read_only=True)
    is_active         = serializers.BooleanField(source="admin_id.is_active", read_only=True)

    class Meta:
        model = Admin
        fields = [
            "admin_id",
            "user",
            "is_active",
            "admin_is_super_admin",
            "admin_created_at",
            "admin_token",
            "admin_refresh_token",
        ]
        read_only_fields = [
            "admin_id",
            "admin_created_at",
            "admin_token",
            "admin_refresh_token",
        ]


# ──────────────────────────────────────────────────────────────
# Admin — création (POST)
# Reçoit un user_id existant et crée l'entrée admin
# ──────────────────────────────────────────────────────────────

class AdminCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Admin
        fields = [
            "user_id",
            "admin_is_super_admin",
        ]

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet identifiant.")
        if Admin.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà administrateur.")
        return value

    def create(self, validated_data):
        user = User.objects.get(pk=validated_data.pop("user_id"))
        return Admin.objects.create(admin_id=user, **validated_data)


# ──────────────────────────────────────────────────────────────
# Admin — mise à jour (PATCH)
# ──────────────────────────────────────────────────────────────

class AdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = [
            "admin_is_super_admin",
        ]