import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Interaction, Comment, Citizen, Resource


class InteractionViewTests(TestCase):
    """
    Tests pour GET et POST /api/interactions/<resource_id>/
    """

    def setUp(self):
        """
        setUp() est exécutée avant CHAQUE test.
        On crée un utilisateur Django + un client HTTP simulé.
        """
        self.client = APIClient()
        # Crée un utilisateur Django pour simuler l'authentification
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.resource_id = uuid.uuid4()

    def test_get_interaction_sans_authentification(self):
        """
        Sans token JWT → doit retourner 401 Unauthorized
        """
        response = self.client.get(f'/api/interactions/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_interaction_inexistante(self):
        """
        Si aucune interaction n'existe pour cet utilisateur/ressource,
        on retourne un objet avec tous les booléens à False.
        """
        self.client.force_authenticate(user=self.user)

        # On simule : Citizen.objects.get() lève DoesNotExist
        # et Interaction.objects.get() lève DoesNotExist
        with patch('interactions.views.Interaction.objects.get') as mock_get:
            mock_get.side_effect = Interaction.DoesNotExist
            response = self.client.get(f'/api/interactions/{self.resource_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_liked'])
        self.assertFalse(response.data['is_favorise'])
        self.assertFalse(response.data['is_bookmark'])

    def test_post_interaction_sans_authentification(self):
        """
        Sans token JWT → doit retourner 401 Unauthorized
        """
        response = self.client.post(
            f'/api/interactions/{self.resource_id}/',
            {'is_liked': True},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_interaction_citoyen_introuvable(self):
        """
        Si l'utilisateur connecté n'a pas de profil Citizen en base
        → doit retourner 403 Forbidden
        """
        self.client.force_authenticate(user=self.user)

        with patch('interactions.views.Citizen.objects.get') as mock_citizen:
            mock_citizen.side_effect = Citizen.DoesNotExist
            response = self.client.post(
                f'/api/interactions/{self.resource_id}/',
                {'is_liked': True},
                format='json'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_post_interaction_ressource_introuvable(self):
        """
        Si la ressource n'existe pas en base → doit retourner 404
        """
        self.client.force_authenticate(user=self.user)

        mock_citizen = MagicMock()
        mock_citizen.user_id = self.user.id

        with patch('interactions.views.Citizen.objects.get', return_value=mock_citizen):
            with patch('interactions.views.Resource.objects.get') as mock_res:
                mock_res.side_effect = Resource.DoesNotExist
                response = self.client.post(
                    f'/api/interactions/{self.resource_id}/',
                    {'is_liked': True},
                    format='json'
                )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentListViewTests(TestCase):
    """
    Tests pour GET et POST /api/interactions/comments/<resource_id>/
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        self.resource_id = uuid.uuid4()

    def test_get_commentaires_sans_authentification(self):
        """
        Sans token JWT → doit retourner 401
        """
        response = self.client.get(f'/api/interactions/comments/{self.resource_id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_commentaire_sans_text(self):
        """
        Si comments_text est absent du body → doit retourner 400
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/interactions/comments/{self.resource_id}/',
            {},  # body vide, pas de comments_text
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_post_commentaire_citoyen_introuvable(self):
        """
        Si le Citizen n'existe pas → 403
        """
        self.client.force_authenticate(user=self.user)

        with patch('interactions.views.Citizen.objects.get') as mock_citizen:
            mock_citizen.side_effect = Citizen.DoesNotExist
            response = self.client.post(
                f'/api/interactions/comments/{self.resource_id}/',
                {'comments_text': 'Super ressource !'},
                format='json'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentDetailViewTests(TestCase):
    """
    Tests pour DELETE /api/interactions/comments/<resource_id>/<comment_id>/
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser3',
            password='testpass123'
        )
        self.resource_id = uuid.uuid4()
        self.comment_id = uuid.uuid4()

    def test_delete_commentaire_sans_authentification(self):
        """
        Sans token JWT → 401
        """
        response = self.client.delete(
            f'/api/interactions/comments/{self.resource_id}/{self.comment_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_commentaire_introuvable(self):
        """
        Si le commentaire n'existe pas → 404
        """
        self.client.force_authenticate(user=self.user)

        with patch('interactions.views.Comment.objects.get') as mock_comment:
            mock_comment.side_effect = Comment.DoesNotExist
            response = self.client.delete(
                f'/api/interactions/comments/{self.resource_id}/{self.comment_id}/'
            )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_commentaire_dautrui(self):
        """
        Un utilisateur ne peut pas supprimer le commentaire d'un autre → 403
        """
        self.client.force_authenticate(user=self.user)

        # On simule un commentaire qui appartient à un AUTRE citoyen
        mock_comment = MagicMock()
        mock_comment.citizen.user_id = uuid.uuid4()  # UUID différent de self.user.id

        with patch('interactions.views.Comment.objects.get', return_value=mock_comment):
            response = self.client.delete(
                f'/api/interactions/comments/{self.resource_id}/{self.comment_id}/'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_son_propre_commentaire(self):
        """
        L'auteur peut supprimer son propre commentaire → 204 No Content
        """
        self.client.force_authenticate(user=self.user)

        mock_comment = MagicMock()
        # UUID identique à celui de l'utilisateur connecté
        mock_comment.citizen.user_id = self.user.id

        with patch('interactions.views.Comment.objects.get', return_value=mock_comment):
            response = self.client.delete(
                f'/api/interactions/comments/{self.resource_id}/{self.comment_id}/'
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_comment.delete.assert_called_once()
