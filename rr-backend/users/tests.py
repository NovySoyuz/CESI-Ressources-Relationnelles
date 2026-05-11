# users/tests.py
from django.test import TestCase
from unittest.mock import patch, MagicMock, PropertyMock
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import User, Citizen
from .serializers import RegisterSerializer, LoginSerializer


# ─────────────────────────────────────────────────────────────────────────────
# REGISTER — Serializer
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializerTest(TestCase):

    valid_payload = {
        'user_fname': 'Jean',
        'user_lname': 'Dupont',
        'user_mail':  'jean.dupont@example.com',
        'password':   'Secure123!',
    }

    def _serializer(self, payload):
        return RegisterSerializer(data=payload)

    # ── Email ──────────────────────────────────────────────────────────────

    def test_email_already_exists_is_rejected(self):
        with patch('users.models.User.objects.filter') as mock:
            mock.return_value.exists.return_value = True
            s = self._serializer(self.valid_payload)
            self.assertFalse(s.is_valid())
            self.assertIn('user_mail', s.errors)

    def test_email_is_normalised_lowercase(self):
        with patch('users.models.User.objects.filter') as mock:
            mock.return_value.exists.return_value = False
            s = self._serializer({
                **self.valid_payload,
                'user_mail': 'Jean.Dupont@EXAMPLE.COM',
            })
            s.is_valid()
            self.assertEqual(
                s.validated_data['user_mail'],
                'jean.dupont@example.com',
            )

    def test_invalid_email_format_is_rejected(self):
        s = self._serializer({**self.valid_payload, 'user_mail': 'not-an-email'})
        self.assertFalse(s.is_valid())
        self.assertIn('user_mail', s.errors)

    # ── Mot de passe ────────────────────────────────────────────────────────

    def test_fully_numeric_password_is_rejected(self):
        with patch('users.models.User.objects.filter') as mock:
            mock.return_value.exists.return_value = False
            s = self._serializer({**self.valid_payload, 'password': '12345678'})
            self.assertFalse(s.is_valid())
            self.assertIn('password', s.errors)

    def test_password_too_short_is_rejected(self):
        with patch('users.models.User.objects.filter') as mock:
            mock.return_value.exists.return_value = False
            s = self._serializer({**self.valid_payload, 'password': 'Ab1!'})
            self.assertFalse(s.is_valid())
            self.assertIn('password', s.errors)

    def test_password_never_returned_in_representation(self):
        mock_user        = MagicMock(spec=User)
        mock_user.user_id    = '123e4567-e89b-12d3-a456-426614174000'
        mock_user.user_fname = 'Jean'
        mock_user.user_lname = 'Dupont'
        mock_user.user_mail  = 'jean.dupont@example.com'
        mock_user.citizen.user_is_modo = False

        data = RegisterSerializer().to_representation(mock_user)
        self.assertNotIn('password', data)

    # ── Champs requis ────────────────────────────────────────────────────────
    @patch('users.serializers.User.objects.filter')
    def test_all_required_fields_must_be_present(self, mock_filter):
        mock_filter.return_value.exists.return_value = False
        for field in ['user_fname', 'user_lname', 'user_mail', 'password']:
            payload = {k: v for k, v in self.valid_payload.items() if k != field}
            s = self._serializer(payload)
            self.assertFalse(s.is_valid(), msg=f"'{field}' devrait être requis")
            self.assertIn(field, s.errors)

    def test_user_is_modo_defaults_to_false(self):
        with patch('users.models.User.objects.filter') as mock:
            mock.return_value.exists.return_value = False
            s = self._serializer(self.valid_payload)
            s.is_valid()
            self.assertFalse(s.validated_data.get('user_is_modo', False))


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN — Serializer
# ─────────────────────────────────────────────────────────────────────────────

class LoginSerializerTest(TestCase):

    def _make_citizen(self, is_actived=True, is_modo=False):
        citizen              = MagicMock(spec=Citizen)
        citizen.user_is_actived = is_actived
        citizen.user_is_modo    = is_modo
        citizen.save            = MagicMock()
        return citizen

    def _make_user(self, citizen=None):
        user             = MagicMock(spec=User)
        user.user_id     = '123e4567-e89b-12d3-a456-426614174000'
        user.user_fname  = 'Jean'
        user.user_lname  = 'Dupont'
        user.user_mail   = 'jean.dupont@example.com'
        user.citizen     = citizen or self._make_citizen()
        return user

    def _run_validate(self, user, tokens=None):
        """Exécute LoginSerializer.validate() avec super() mocké."""
        tokens = tokens or {'access': 'access_tok', 'refresh': 'refresh_tok'}
        s      = LoginSerializer()
        s.user = user
        with patch(
            'rest_framework_simplejwt.serializers.TokenObtainPairSerializer.validate',
            return_value=tokens,
        ):
            return s.validate({})

    # ── Persistance tokens ─────────────────────────────────────────────────

    def test_tokens_are_saved_to_db_on_login(self):
        citizen = self._make_citizen()
        data    = self._run_validate(self._make_user(citizen))

        self.assertEqual(citizen.user_token,         'access_tok')
        self.assertEqual(citizen.user_refresh_token, 'refresh_tok')
        citizen.save.assert_called_once_with(
            update_fields=['user_token', 'user_refresh_token']
        )

    # ── Profil dans la réponse ─────────────────────────────────────────────

    def test_response_contains_user_profile(self):
        citizen = self._make_citizen(is_modo=True)
        data    = self._run_validate(self._make_user(citizen))

        self.assertIn('user', data)
        self.assertEqual(data['user']['user_mail'],  'jean.dupont@example.com')
        self.assertTrue(data['user']['user_is_modo'])

    def test_password_never_in_response(self):
        data = self._run_validate(self._make_user())
        self.assertNotIn('password', data)
        self.assertNotIn('password', data.get('user', {}))

    # ── Citizen manquant ──────────────────────────────────────────────────

    def test_missing_citizen_raises_authentication_failed(self):
        user = MagicMock(spec=User)
        type(user).citizen = property(
            lambda self: (_ for _ in ()).throw(Citizen.DoesNotExist())
        )
        with self.assertRaises(AuthenticationFailed):
            self._run_validate(user)


# ─────────────────────────────────────────────────────────────────────────────
# REGISTER — View
# ─────────────────────────────────────────────────────────────────────────────

class RegisterViewTest(APITestCase):

    url = '/api/auth/register/'

    valid_payload = {
            'user_fname': 'Jean',
            'user_lname': 'Dupont',
            'user_mail':  'jean@example.com',
            'password':   'Secure123!',
        }

    def test_valid_register_returns_201(self):
        mock_user        = MagicMock(spec=User)
        mock_user.user_id    = 'uuid-xxx'
        mock_user.user_fname = 'Jean'
        mock_user.user_lname = 'Dupont'
        mock_user.user_mail  = 'jean@example.com'
        mock_user.citizen    = MagicMock(user_is_modo=False)

        with patch('users.views.RegisterSerializer') as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = True
            instance.save.return_value     = mock_user
            instance.to_representation.return_value = {
                'user_id':      'uuid-xxx',
                'user_fname':   'Jean',
                'user_lname':   'Dupont',
                'user_mail':    'jean@example.com',
                'user_is_modo': False,
            }
            r = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(r.status_code, 201)

    def test_duplicate_email_returns_400(self):
        with patch('users.views.RegisterSerializer') as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = False
            instance.errors = {'user_mail': ['Un compte existe déjà avec cette adresse email.']}
            r = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(r.status_code, 400)
        self.assertIn('user_mail', r.data)

    def test_numeric_password_returns_400(self):
        with patch('users.views.RegisterSerializer') as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = False
            instance.errors = {'password': ['Le mot de passe ne peut pas être uniquement numérique.']}
            r = self.client.post(
                self.url,
                {**self.valid_payload, 'password': '12345678'},
                format='json',
            )

        self.assertEqual(r.status_code, 400)
        self.assertIn('password', r.data)

    def test_missing_field_returns_400(self):
        for field in ['user_fname', 'user_lname', 'user_mail', 'password']:
            with patch('users.views.RegisterSerializer') as MockSerializer:
                instance = MockSerializer.return_value
                instance.is_valid.return_value = False
                instance.errors = {field: ['Ce champ est obligatoire.']}
                payload = {k: v for k, v in self.valid_payload.items() if k != field}
                r = self.client.post(self.url, payload, format='json')

            self.assertEqual(r.status_code, 400, msg=f"'{field}' devrait être requis")

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN — View
# ─────────────────────────────────────────────────────────────────────────────

class LoginViewTest(APITestCase):

    url = '/api/auth/login/'

    def _mock_login(self, user_data):
        """Mock LoginSerializer.validated_data pour simuler un login réussi."""
        return patch(
            'users.serializers.LoginSerializer.validate',
            return_value={
                'access':  'access_tok',
                'refresh': 'refresh_tok',
                'user':    user_data,
            },
        )

    def test_valid_credentials_return_200_with_tokens(self):
        user_data = {
            'user_id':    'uuid-xxx',
            'user_fname': 'Jean',
            'user_lname': 'Dupont',
            'user_mail':  'jean@example.com',
            'user_is_modo': False,
        }
        with self._mock_login(user_data):
            r = self.client.post(
                self.url,
                {'user_mail': 'jean@example.com', 'password': 'Secure123!'},
                format='json',
            )
        self.assertEqual(r.status_code, 200)
        self.assertIn('access',  r.data)
        self.assertIn('refresh', r.data)
        self.assertIn('user',    r.data)

    def test_invalid_credentials_return_401(self):
        with patch(
            'users.serializers.LoginSerializer.validate',
            side_effect=AuthenticationFailed('Identifiants incorrects.'),
        ):
            r = self.client.post(
                self.url,
                {'user_mail': 'x@x.com', 'password': 'wrong'},
                format='json',
            )
        self.assertEqual(r.status_code, 401)


# ─────────────────────────────────────────────────────────────────────────────
# LOGOUT — View
# ─────────────────────────────────────────────────────────────────────────────

class LogoutViewTest(APITestCase):

    url = '/api/auth/logout/'

    def _auth(self):
        mock_user         = MagicMock(spec=User)
        mock_user.is_authenticated = True
        mock_citizen      = MagicMock(spec=Citizen)
        mock_citizen.invalidate_tokens = MagicMock()
        mock_user.citizen = mock_citizen
        self.client.force_authenticate(user=mock_user)
        return mock_user

    def test_logout_invalidates_tokens_in_db(self):
        user = self._auth()
        r    = self.client.post(self.url, {}, format='json')
        user.citizen.invalidate_tokens.assert_called_once()
        self.assertEqual(r.status_code, 204)

    def test_logout_unauthenticated_returns_401(self):
        r = self.client.post(self.url, {}, format='json')
        self.assertEqual(r.status_code, 401)