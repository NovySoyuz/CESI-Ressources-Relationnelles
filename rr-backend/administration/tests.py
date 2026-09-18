import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.db import IntegrityError, connection
from django.http import Http404
from rest_framework import serializers as drf_serializers
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from users.models import User, Citizen
from administration.models import Admin
from administration.serializers import AdminLoginSerializer, AdminCreateSerializer
from resources.models import Resource


# ──────────────────────────────────────────────────────────────
# Création des tables non-managed pour les tests
# ──────────────────────────────────────────────────────────────

def setUpModule():
    """Crée les tables managed=False avant tous les tests du fichier."""
    with connection.schema_editor() as schema:
        schema.create_model(User)
        schema.create_model(Citizen)
        schema.create_model(Admin)
        # Nécessaire pour le CASCADE User → Citizen → Resource déclenché par
        # self.user.delete() dans les tests d'intégration ci-dessous.
        schema.create_model(Resource)


def tearDownModule():
    """Supprime les tables après tous les tests du fichier."""
    with connection.schema_editor() as schema:
        schema.delete_model(Resource)
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


# ──────────────────────────────────────────────────────────────
# Tests des Serializers
# ──────────────────────────────────────────────────────────────

class AdminLoginSerializerTest(TestCase):

    def _make_admin(self, is_super=False):
        admin = MagicMock(spec=Admin)
        admin.admin_is_super_admin = is_super
        admin.save = MagicMock()
        return admin

    def _make_user(self, admin=None):
        user = MagicMock(spec=User)
        user.user_id   = '123e4567-e89b-12d3-a456-426614174000'
        user.user_fname = 'Jean'
        user.user_lname = 'Dupont'
        user.user_mail  = 'jean@example.com'
        user.admin_profile = admin or self._make_admin()
        return user

    def _run_validate(self, user, tokens=None):
        tokens = tokens or {'access': 'access_tok', 'refresh': 'refresh_tok'}
        s = AdminLoginSerializer()
        s.user = user
        with patch(
            'rest_framework_simplejwt.serializers.TokenObtainPairSerializer.validate',
            return_value=tokens,
        ):
            return s.validate({})

    def test_tokens_saved_to_db_on_login(self):
        admin = self._make_admin()
        self._run_validate(self._make_user(admin))
        admin.save.assert_called_once_with(update_fields=['admin_token', 'admin_refresh_token'])

    def test_access_token_persisted(self):
        admin = self._make_admin()
        self._run_validate(self._make_user(admin))
        self.assertEqual(admin.admin_token, 'access_tok')
        self.assertEqual(admin.admin_refresh_token, 'refresh_tok')

    def test_response_contains_user_profile(self):
        admin = self._make_admin(is_super=True)
        data = self._run_validate(self._make_user(admin))
        self.assertIn('user', data)
        self.assertEqual(data['user']['user_mail'], 'jean@example.com')
        self.assertTrue(data['user']['is_super_admin'])

    def test_password_not_in_response(self):
        data = self._run_validate(self._make_user())
        self.assertNotIn('password', data)
        self.assertNotIn('password', data.get('user', {}))

    def test_non_admin_raises_authentication_failed(self):
        user = MagicMock(spec=User)
        type(user).admin_profile = property(
            lambda self: (_ for _ in ()).throw(Admin.DoesNotExist())
        )
        s = AdminLoginSerializer()
        s.user = user
        with patch(
            'rest_framework_simplejwt.serializers.TokenObtainPairSerializer.validate',
            return_value={'access': 'a', 'refresh': 'r'},
        ):
            with self.assertRaises(AuthenticationFailed):
                s.validate({})


class AdminCreateSerializerTest(TestCase):

    def test_unknown_user_id_raises(self):
        with patch('administration.serializers.User.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            s = AdminCreateSerializer()
            with self.assertRaises(drf_serializers.ValidationError):
                s.validate_user_id(uuid.uuid4())

    def test_already_admin_raises(self):
        user_id = uuid.uuid4()
        with patch('administration.serializers.User.objects.filter') as mock_user:
            mock_user.return_value.exists.return_value = True
            with patch('administration.serializers.Admin.objects.filter') as mock_admin:
                mock_admin.return_value.exists.return_value = True
                s = AdminCreateSerializer()
                with self.assertRaises(drf_serializers.ValidationError):
                    s.validate_user_id(user_id)

    def test_valid_user_id_passes(self):
        user_id = uuid.uuid4()
        with patch('administration.serializers.User.objects.filter') as mock_user:
            mock_user.return_value.exists.return_value = True
            with patch('administration.serializers.Admin.objects.filter') as mock_admin:
                mock_admin.return_value.exists.return_value = False
                s = AdminCreateSerializer()
                self.assertEqual(s.validate_user_id(user_id), user_id)


# ──────────────────────────────────────────────────────────────
# Tests des Views (API)
# ──────────────────────────────────────────────────────────────

def _mock_auth_user():
    user = MagicMock(spec=User)
    user.is_authenticated = True
    return user


class AdminLoginViewTest(APITestCase):
    url = '/api/administration/login/'

    def test_valid_login_returns_200_with_tokens(self):
        with patch('administration.views.AdminLoginSerializer') as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = None
            instance.validated_data = {
                'access': 'tok', 'refresh': 'ref',
                'user': {'user_id': 'xxx', 'user_fname': 'Jean',
                         'user_lname': 'Dupont', 'user_mail': 'j@j.com',
                         'is_super_admin': False},
            }
            r = self.client.post(self.url, {'user_mail': 'j@j.com', 'password': 'pass'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)

    def test_invalid_credentials_returns_401(self):
        with patch('administration.views.AdminLoginSerializer') as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.side_effect = Exception('bad credentials')
            r = self.client.post(self.url, {'user_mail': 'x@x.com', 'password': 'wrong'}, format='json')
        self.assertEqual(r.status_code, 401)
        self.assertIn('detail', r.data)


class AdminLogoutViewTest(APITestCase):
    url = '/api/administration/logout/'

    def test_unauthenticated_returns_401(self):
        r = self.client.post(self.url, {}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_logout_returns_204(self):
        user = _mock_auth_user()
        user.admin_profile = MagicMock()
        user.admin_profile.invalidate_tokens = MagicMock()
        self.client.force_authenticate(user=user)
        r = self.client.post(self.url, {}, format='json')
        self.assertEqual(r.status_code, 204)

    def test_logout_invalidates_tokens(self):
        user = _mock_auth_user()
        user.admin_profile = MagicMock()
        user.admin_profile.invalidate_tokens = MagicMock()
        self.client.force_authenticate(user=user)
        self.client.post(self.url, {}, format='json')
        user.admin_profile.invalidate_tokens.assert_called_once()


class AdminListCreateViewTest(APITestCase):
    url = '/api/administration/admins/'

    def test_list_unauthenticated_returns_401(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_list_authenticated_returns_200(self):
        self.client.force_authenticate(user=_mock_auth_user())
        with patch('administration.views.Admin.objects.select_related') as mock_qs:
            mock_qs.return_value.all.return_value = []
            with patch('administration.views.AdminListSerializer') as MockSerializer:
                MockSerializer.return_value.data = []
                r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_create_valid_admin_returns_201(self):
        self.client.force_authenticate(user=_mock_auth_user())
        mock_admin = MagicMock(spec=Admin)
        with patch('administration.views.AdminCreateSerializer') as MockCreate:
            instance = MockCreate.return_value
            instance.is_valid.return_value = True
            instance.save.return_value = mock_admin
            with patch('administration.views.AdminDetailSerializer') as MockDetail:
                MockDetail.return_value.data = {'admin_id': str(uuid.uuid4())}
                r = self.client.post(self.url, {'user_id': str(uuid.uuid4())}, format='json')
        self.assertEqual(r.status_code, 201)

    def test_create_invalid_returns_400(self):
        self.client.force_authenticate(user=_mock_auth_user())
        with patch('administration.views.AdminCreateSerializer') as MockCreate:
            instance = MockCreate.return_value
            instance.is_valid.return_value = False
            instance.errors = {'user_id': ['Aucun utilisateur trouvé.']}
            r = self.client.post(self.url, {'user_id': 'invalid'}, format='json')
        self.assertEqual(r.status_code, 400)


class AdminDetailViewTest(APITestCase):

    def _url(self, admin_id=None):
        return f'/api/administration/admins/{admin_id or uuid.uuid4()}/'

    def test_get_unauthenticated_returns_401(self):
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 401)

    def test_get_returns_200(self):
        self.client.force_authenticate(user=_mock_auth_user())
        mock_admin = MagicMock(spec=Admin)
        with patch('administration.views.get_object_or_404', return_value=mock_admin):
            with patch('administration.views.AdminDetailSerializer') as MockSerializer:
                MockSerializer.return_value.data = {'admin_id': str(uuid.uuid4())}
                r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)

    def test_get_not_found_returns_404(self):

        self.client.force_authenticate(user=_mock_auth_user())
        with patch('administration.views.get_object_or_404', side_effect=Http404):
            r = self.client.get(self._url())
        self.assertEqual(r.status_code, 404)

    def test_patch_valid_returns_200(self):
        self.client.force_authenticate(user=_mock_auth_user())
        mock_admin = MagicMock(spec=Admin)
        with patch('administration.views.get_object_or_404', return_value=mock_admin):
            with patch('administration.views.AdminUpdateSerializer') as MockUpdate:
                instance = MockUpdate.return_value
                instance.is_valid.return_value = True
                with patch('administration.views.AdminDetailSerializer') as MockDetail:
                    MockDetail.return_value.data = {'admin_id': str(uuid.uuid4())}
                    r = self.client.patch(self._url(), {'admin_is_super_admin': True}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_patch_invalid_returns_400(self):
        self.client.force_authenticate(user=_mock_auth_user())
        mock_admin = MagicMock(spec=Admin)
        with patch('administration.views.get_object_or_404', return_value=mock_admin):
            with patch('administration.views.AdminUpdateSerializer') as MockUpdate:
                instance = MockUpdate.return_value
                instance.is_valid.return_value = False
                instance.errors = {'admin_is_super_admin': ['Champ invalide.']}
                r = self.client.patch(self._url(), {'admin_is_super_admin': 'pas_un_bool'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_delete_returns_204(self):
        self.client.force_authenticate(user=_mock_auth_user())
        mock_admin = MagicMock(spec=Admin)
        with patch('administration.views.get_object_or_404', return_value=mock_admin):
            r = self.client.delete(self._url())
        self.assertEqual(r.status_code, 204)
        mock_admin.delete.assert_called_once()

    def test_delete_not_found_returns_404(self):

        self.client.force_authenticate(user=_mock_auth_user())
        with patch('administration.views.get_object_or_404', side_effect=Http404):
            r = self.client.delete(self._url())
        self.assertEqual(r.status_code, 404)
