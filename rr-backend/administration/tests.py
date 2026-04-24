import uuid
from unittest.mock import patch
from django.test import TestCase
from django.db import IntegrityError, connection
from users.models import User, Citizen
from administration.models import Admin


# ──────────────────────────────────────────────────────────────
# Création des tables non-managed pour les tests
# ──────────────────────────────────────────────────────────────

def setUpModule():
    """Crée les tables managed=False avant tous les tests du fichier."""
    with connection.schema_editor() as schema:
        schema.create_model(User)
        schema.create_model(Citizen)
        schema.create_model(Admin)


def tearDownModule():
    """Supprime les tables après tous les tests du fichier."""
    with connection.schema_editor() as schema:
        schema.delete_model(Admin)
        schema.delete_model(Citizen)
        schema.delete_model(User)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

_user_counter = 0

def make_user(**kwargs) -> User:
    global _user_counter
    _user_counter += 1
    defaults = {
        "user_fname": "Jean",
        "user_lname": "Dupont",
        "user_mail": f"jean.dupont{_user_counter}@example.com",
        "user_password": "hashed_password",
    }
    defaults.update(kwargs)
    user = User.objects.create(**defaults)
    Citizen.objects.create(user=user)
    return user


def make_admin(user=None, **kwargs) -> Admin:
    if user is None:
        user = make_user()
    return Admin.objects.create(admin_id=user, **kwargs)


# ──────────────────────────────────────────────────────────────
# Tests unitaires
# ──────────────────────────────────────────────────────────────

class AdminModelUnitTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.admin = make_admin(user=self.user)

    def test_is_super_admin_default_false(self):
        self.assertFalse(self.admin.admin_is_super_admin)

    def test_token_default_null(self):
        self.assertIsNone(self.admin.admin_token)

    def test_refresh_token_default_null(self):
        self.assertIsNone(self.admin.admin_refresh_token)

    def test_created_at_auto_set(self):
        self.assertIsNotNone(self.admin.admin_created_at)

    def test_token_can_be_blank(self):
        self.admin.admin_token = ""
        self.admin.full_clean()

    def test_token_max_length(self):
        self.admin.admin_token = "x" * 512
        self.admin.full_clean()

    def test_token_too_long_raises(self):
        from django.core.exceptions import ValidationError
        self.admin.admin_token = "x" * 513
        with self.assertRaises(ValidationError):
            self.admin.full_clean()

    def test_primary_key_equals_user(self):
        self.assertEqual(self.admin.pk, self.user.pk)

    def test_str_representation(self):
        self.assertIn("Admin(", str(self.admin))
        self.assertIn("super=False", str(self.admin))

    def test_user_is_active_via_citizen(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_inactive_when_citizen_deactivated(self):
        self.user.citizen.user_is_actived = False
        self.user.citizen.save()
        # Recharger depuis la BDD pour vider le cache
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_user_is_authenticated(self):
        self.assertTrue(self.user.is_authenticated)

    def test_user_is_not_anonymous(self):
        self.assertFalse(self.user.is_anonymous)


# ──────────────────────────────────────────────────────────────
# Tests d'intégration
# ──────────────────────────────────────────────────────────────

class AdminModelIntegrationTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_create_admin(self):
        admin = make_admin(user=self.user)
        self.assertTrue(Admin.objects.filter(pk=self.user.pk).exists())
        self.assertEqual(admin.admin_id, self.user)

    def test_create_super_admin(self):
        make_admin(user=self.user, admin_is_super_admin=True)
        self.assertTrue(Admin.objects.get(pk=self.user.pk).admin_is_super_admin)

    def test_create_admin_with_tokens(self):
        make_admin(
            user=self.user,
            admin_token="access.token.here",
            admin_refresh_token="refresh.token.here",
        )
        fetched = Admin.objects.get(pk=self.user.pk)
        self.assertEqual(fetched.admin_token, "access.token.here")
        self.assertEqual(fetched.admin_refresh_token, "refresh.token.here")

    def test_one_user_one_admin(self):
        make_admin(user=self.user)
        with self.assertRaises(IntegrityError):
            Admin.objects.create(admin_id=self.user)

    def test_delete_user_cascades_to_admin(self):
        make_admin(user=self.user)
        pk = self.user.pk
        self.user.delete()
        self.assertFalse(Admin.objects.filter(pk=pk).exists())

    def test_delete_user_cascades_to_citizen(self):
        pk = self.user.pk
        self.user.delete()
        self.assertFalse(Citizen.objects.filter(pk=pk).exists())

    def test_update_token(self):
        admin = make_admin(user=self.user)
        admin.admin_token = "new.token"
        admin.save()
        self.assertEqual(Admin.objects.get(pk=self.user.pk).admin_token, "new.token")

    def test_update_is_super_admin(self):
        admin = make_admin(user=self.user)
        admin.admin_is_super_admin = True
        admin.save()
        self.assertTrue(Admin.objects.get(pk=self.user.pk).admin_is_super_admin)

    def test_delete_admin_keeps_user_and_citizen(self):
        admin = make_admin(user=self.user)
        pk = self.user.pk
        admin.delete()
        self.assertFalse(Admin.objects.filter(pk=pk).exists())
        self.assertTrue(User.objects.filter(pk=pk).exists())
        self.assertTrue(Citizen.objects.filter(pk=pk).exists())
        
    def test_related_name_from_user(self):
        admin = make_admin(user=self.user)
        self.assertEqual(self.user.admin_profile, admin)

    def test_created_at_not_updated_on_save(self):
        admin = make_admin(user=self.user)
        original_date = admin.admin_created_at
        admin.admin_is_super_admin = True
        admin.save()
        self.assertEqual(Admin.objects.get(pk=self.user.pk).admin_created_at, original_date)

    def test_check_password(self):
        from django.contrib.auth.hashers import make_password
        self.user.user_password = make_password("monmotdepasse")
        self.user.save()
        self.assertTrue(self.user.check_password("monmotdepasse"))
        self.assertFalse(self.user.check_password("mauvaismdp"))

        