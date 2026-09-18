import uuid
from datetime import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Resource, Category, Relation
from users.models import User, Citizen


class ResourceListViewTests(TestCase):
    """
    Tests pour GET et POST /api/resources/
    """

    def setUp(self):
        self.client = APIClient()
        self.user = MagicMock(spec=User)
        self.user.user_id = uuid.uuid4()

    def test_get_resources_sans_authentification(self):
        """
        GET est public → doit retourner 200
        """
        mock_qs = MagicMock()
        mock_qs.prefetch_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.distinct.return_value = []
        with patch('resources.views.Resource.objects.filter', return_value=mock_qs):
            response = self.client.get('/api/resources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_resource_sans_authentification(self):
        """
        POST sans token → 401
        """
        response = self.client.post(
            '/api/resources/',
            {'resource_title': 'Test'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_resource_citoyen_introuvable(self):
        """
        Si le Citizen n'existe pas → 403
        """
        self.client.force_authenticate(user=self.user)
        with patch('resources.views.Citizen.objects.get') as mock_citizen:
            mock_citizen.side_effect = Citizen.DoesNotExist
            response = self.client.post(
                '/api/resources/',
                {'resource_title': 'Test'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_resource_donnees_invalides(self):
        """
        Si resource_title est absent → 400
        """
        self.client.force_authenticate(user=self.user)
        mock_citizen = MagicMock()
        with patch('resources.views.Citizen.objects.get', return_value=mock_citizen):
            response = self.client.post('/api/resources/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_resource_valide(self):
        """
        Création valide → 201
        """
        self.client.force_authenticate(user=self.user)
        mock_citizen = MagicMock()
        mock_resource = MagicMock()
        mock_resource.resource_id = uuid.uuid4()
        mock_resource.resource_label = 'article'
        mock_resource.resource_title = 'Ma ressource'
        mock_resource.resource_description = None
        mock_resource.resource_created_at = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_last_modif = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_author.user_id = self.user.user_id
        mock_resource.categories = []
        mock_resource.relations = []

        payload = {
            'resource_title': 'Ma ressource',
            'resource_label': 'article',
            'categories': [str(uuid.uuid4())],
            'relations': [str(uuid.uuid4())],
        }

        with patch('resources.views.Citizen.objects.get', return_value=mock_citizen), \
             patch('resources.views.Resource.objects.create', return_value=mock_resource), \
             patch('resources.views.Category.objects.get', return_value=MagicMock()), \
             patch('resources.views.Relation.objects.get', return_value=MagicMock()), \
             patch('resources.views.ResourceCategory.objects.create'), \
             patch('resources.views.ResourceRelation.objects.create'):
            response = self.client.post(
                '/api/resources/',
                payload,
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ResourceDetailViewTests(TestCase):
    """
    Tests pour GET, PATCH, DELETE /api/resources/<resource_id>/
    """

    def setUp(self):
        self.client = APIClient()
        self.user = MagicMock(spec=User)
        self.user.user_id = uuid.uuid4()
        self.resource_id = uuid.uuid4()

    def _make_resource(self, visible=True, author_id=None):
        mock_resource = MagicMock()
        mock_resource.resource_id = self.resource_id
        mock_resource.resource_is_visible = visible
        mock_resource.resource_label = None
        mock_resource.resource_title = 'Test Resource'
        mock_resource.resource_description = 'Description test'
        mock_resource.resource_created_at = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_last_modif = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_author.user_id = author_id or self.user.user_id
        mock_resource.categories = []
        mock_resource.relations = []
        return mock_resource

    def test_get_resource_visible_sans_auth(self):
        """
        Ressource visible → accessible sans authentification
        """
        with patch('resources.views.Resource.objects.get', return_value=self._make_resource()):
            response = self.client.get(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_resource_inexistante(self):
        """
        Ressource inexistante → 404
        """
        with patch('resources.views.Resource.objects.get') as mock_get:
            mock_get.side_effect = Resource.DoesNotExist
            response = self.client.get(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_resource_non_visible_sans_auth(self):
        """
        Ressource non visible + pas connecté → 404
        """
        with patch('resources.views.Resource.objects.get', return_value=self._make_resource(visible=False)):
            response = self.client.get(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_resource_non_visible_par_auteur(self):
        """
        Ressource non visible consultée par son auteur → 200
        """
        self.client.force_authenticate(user=self.user)
        with patch('resources.views.Resource.objects.get', return_value=self._make_resource(visible=False)):
            response = self.client.get(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_resource_sans_authentification(self):
        """
        PATCH sans token → 401
        """
        response = self.client.patch(
            f'/api/resources/{self.resource_id}/',
            {'resource_title': 'Nouveau titre'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_resource_par_autre_utilisateur(self):
        """
        PATCH par un autre utilisateur → 403
        """
        self.client.force_authenticate(user=self.user)
        mock_resource = self._make_resource(author_id=uuid.uuid4())
        with patch('resources.views.Resource.objects.get', return_value=mock_resource):
            response = self.client.patch(
                f'/api/resources/{self.resource_id}/',
                {'resource_title': 'Nouveau titre'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_resource_par_auteur(self):
        """
        PATCH par l'auteur → 200, titre mis à jour
        """
        self.client.force_authenticate(user=self.user)
        mock_resource = self._make_resource()
        with patch('resources.views.Resource.objects.get', return_value=mock_resource):
            response = self.client.patch(
                f'/api/resources/{self.resource_id}/',
                {'resource_title': 'Nouveau titre'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_resource.resource_title, 'Nouveau titre')

    def test_delete_resource_par_auteur(self):
        """
        DELETE par l'auteur → 204
        """
        self.client.force_authenticate(user=self.user)
        mock_resource = self._make_resource()
        with patch('resources.views.Resource.objects.get', return_value=mock_resource):
            response = self.client.delete(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_resource.delete.assert_called_once()

    def test_delete_resource_par_autre_utilisateur(self):
        """
        DELETE par un autre utilisateur → 403
        """
        self.client.force_authenticate(user=self.user)
        mock_resource = self._make_resource(author_id=uuid.uuid4())
        with patch('resources.views.Resource.objects.get', return_value=mock_resource):
            response = self.client.delete(f'/api/resources/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ResourcePublishViewTests(TestCase):
    """
    Tests pour PATCH /api/resources/<resource_id>/publish/
    """

    def setUp(self):
        self.client = APIClient()
        self.user = MagicMock(spec=User)
        self.user.user_id = uuid.uuid4()
        self.resource_id = uuid.uuid4()

    def test_publish_sans_authentification(self):
        """
        Sans token → 401
        """
        response = self.client.patch(f'/api/resources/{self.resource_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_publish_citoyen_introuvable(self):
        """
        Citizen introuvable → 403
        """
        self.client.force_authenticate(user=self.user)
        with patch('resources.views.Citizen.objects.get') as mock_citizen:
            mock_citizen.side_effect = Citizen.DoesNotExist
            response = self.client.patch(f'/api/resources/{self.resource_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_non_moderateur(self):
        """
        Citizen non modo → 403
        """
        self.client.force_authenticate(user=self.user)
        mock_citizen = MagicMock()
        mock_citizen.user_is_modo = False
        with patch('resources.views.Citizen.objects.get', return_value=mock_citizen):
            response = self.client.patch(f'/api/resources/{self.resource_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_ressource_inexistante(self):
        """
        Ressource inexistante → 404
        """
        self.client.force_authenticate(user=self.user)
        mock_citizen = MagicMock()
        mock_citizen.user_is_modo = True
        with patch('resources.views.Citizen.objects.get', return_value=mock_citizen):
            with patch('resources.views.Resource.objects.get') as mock_res:
                mock_res.side_effect = Resource.DoesNotExist
                response = self.client.patch(f'/api/resources/{self.resource_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_publish_par_moderateur(self):
        """
        Modo toggle la visibilité d'une ressource → 200
        """
        self.client.force_authenticate(user=self.user)
        mock_citizen = MagicMock()
        mock_citizen.user_is_modo = True
        mock_resource = MagicMock()
        mock_resource.resource_is_visible = False
        mock_resource.resource_label = None
        mock_resource.resource_title = 'Test Resource'
        mock_resource.resource_description = None
        mock_resource.resource_created_at = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_last_modif = datetime(2026, 1, 1, 12, 0, 0)
        mock_resource.resource_author.user_id = self.user.user_id
        mock_resource.categories = []
        mock_resource.relations = []
        with patch('resources.views.Citizen.objects.get', return_value=mock_citizen):
            with patch('resources.views.Resource.objects.get', return_value=mock_resource):
                response = self.client.patch(f'/api/resources/{self.resource_id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_resource.resource_is_visible)
        mock_resource.save.assert_called_once()


class CategoryRelationViewTests(TestCase):
    """
    Tests pour GET /api/resources/categories/ et /api/resources/relations/
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_categories_public(self):
        """
        GET categories est public → 200
        """
        with patch('resources.views.Category.objects.all', return_value=[]):
            response = self.client.get('/api/resources/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_relations_public(self):
        """
        GET relations est public → 200
        """
        with patch('resources.views.Relation.objects.all', return_value=[]):
            response = self.client.get('/api/resources/relations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
