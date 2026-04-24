from django.test import TestCase
from django.db import IntegrityError
from users.models import User
from administration.models import Admin


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def make_user(**kwargs) -> User:
    defaults = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def make_admin(user=None, **kwargs) -> Admin:
    if user is None:
        user = make_user()
    return Admin.objects.create(admin_id=user, **kwargs)


# ──────────────────────────────────────────────────────────────
# Tests unitaires — logique du modèle isolée
# ──────────────────────────────────────────────────────────────

class AdminModelUnitTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.admin = make_admin(user=self.user)

    # Valeurs par défaut
    def test_is_super_admin_default_false(self):
        self.assertFalse(self.admin.admin_is_super_admin)

    def test_token_default_null(self):
        self.assertIsNone(self.admin.admin_token)

    def test_refresh_token_default_null(self):
        self.assertIsNone(self.admin.admin_refresh_token)

    def test_created_at_auto_set(self):
        self.assertIsNotNone(self.admin.admin_created_at)

    # Champs optionnels
    def test_token_can_be_blank(self):
        self.admin.admin_token = ""
        self.admin.full_clean()  # ne doit pas lever d'exception

    def test_token_max_length(self):
        self.admin.admin_token = "x" * 512
        self.admin.full_clean()

    def test_token_too_long_raises(self):
        from django.core.exceptions import ValidationError
        self.admin.admin_token = "x" * 513
        with self.assertRaises(ValidationError):
            self.admin.full_clean()

    # PK = FK vers User
    def test_primary_key_equals_user(self):
        self.assertEqual(self.admin.pk, self.user.pk)

    # __str__
    def test_str_representation(self):
        result = str(self.admin)
        self.assertIn("Admin(", result)
        self.assertIn("super=False", result)

    def test_str_super_admin(self):
        self.admin.admin_is_super_admin = True
        self.assertIn("super=True", str(self.admin))


# ──────────────────────────────────────────────────────────────
# Tests d'intégration — avec base de données réelle
# ──────────────────────────────────────────────────────────────

class AdminModelIntegrationTests(TestCase):

    def setUp(self):
        self.user = make_user()

    # Création
    def test_create_admin(self):
        admin = make_admin(user=self.user)
        self.assertEqual(Admin.objects.count(), 1)
        self.assertEqual(admin.admin_id, self.user)

    def test_create_super_admin(self):
        admin = make_admin(user=self.user, admin_is_super_admin=True)
        self.assertTrue(Admin.objects.get(pk=self.user.pk).admin_is_super_admin)

    def test_create_admin_with_tokens(self):
        admin = make_admin(
            user=self.user,
            admin_token="access.token.here",
            admin_refresh_token="refresh.token.here",
        )
        fetched = Admin.objects.get(pk=self.user.pk)
        self.assertEqual(fetched.admin_token, "access.token.here")
        self.assertEqual(fetched.admin_refresh_token, "refresh.token.here")

    # Contraintes d'unicité (OneToOne)
    def test_one_user_one_admin(self):
        make_admin(user=self.user)
        with self.assertRaises(IntegrityError):
            Admin.objects.create(admin_id=self.user)

    # Cascade suppression
    def test_delete_user_cascades_to_admin(self):
        make_admin(user=self.user)
        self.user.delete()
        self.assertEqual(Admin.objects.count(), 0)

    # Lecture / mise à jour
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

    # Suppression directe
    def test_delete_admin_keeps_user(self):
        admin = make_admin(user=self.user)
        admin.delete()
        self.assertEqual(Admin.objects.count(), 0)
        self.assertEqual(User.objects.filter(pk=self.user.pk).count(), 1)

    # related_name
    def test_related_name_from_user(self):
        admin = make_admin(user=self.user)
        self.assertEqual(self.user.admin_profile, admin)

    # created_at non modifiable
    def test_created_at_not_updated_on_save(self):
        admin = make_admin(user=self.user)
        original_date = admin.admin_created_at
        admin.admin_is_super_admin = True
        admin.save()
        self.assertEqual(Admin.objects.get(pk=self.user.pk).admin_created_at, original_date)