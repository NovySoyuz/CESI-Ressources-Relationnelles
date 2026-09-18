from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Interaction, Comment
from users.models import Citizen
from resources.models import Resource
from .serializers import InteractionSerializer, CommentSerializer

_INTERACTION_FLAGS = ('is_liked', 'is_favorise', 'is_bookmark', 'is_exploited')
_ERR_CITIZEN_NOT_FOUND = 'Citoyen introuvable.'


class InteractionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resource_id):
        try:
            interaction = Interaction.objects.get(
                citizen__user_id=request.user.user_id,
                resource__resource_id=resource_id
            )
            serializer = InteractionSerializer(interaction)
            return Response(serializer.data)
        except Interaction.DoesNotExist:
            return Response({
                'citizen_id': str(request.user.user_id),
                'resource_id': str(resource_id),
                'is_liked': False,
                'is_favorise': False,
                'is_bookmark': False,
                'is_exploited': False,
            })

    def post(self, request, resource_id):
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': _ERR_CITIZEN_NOT_FOUND},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            resource = Resource.objects.get(resource_id=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {'error': 'Ressource introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        defaults = {
            flag: request.data[flag]
            for flag in _INTERACTION_FLAGS
            if flag in request.data
        }
        interaction, created = Interaction.objects.update_or_create(
            citizen=citizen,
            resource=resource,
            defaults=defaults
        )
        serializer = InteractionSerializer(interaction)
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=http_status)


class InteractionFilterView(APIView):
    permission_classes = [IsAuthenticated]
    filter_field = None

    def get(self, request):
        interactions = Interaction.objects.filter(
            citizen__user_id=request.user.user_id,
            **{self.filter_field: True}
        )
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)


class LikesListView(InteractionFilterView):
    filter_field = 'is_liked'

class FavorisListView(InteractionFilterView):
    filter_field = 'is_favorise'

class BookmarksListView(InteractionFilterView):
    filter_field = 'is_bookmark'

class ExploitedListView(InteractionFilterView):
    filter_field = 'is_exploited'


class InteractionSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        base = Interaction.objects.filter(citizen__user_id=request.user.user_id)
        return Response({
            'likes':     base.filter(is_liked=True).count(),
            'favoris':   base.filter(is_favorise=True).count(),
            'bookmarks': base.filter(is_bookmark=True).count(),
            'exploited': base.filter(is_exploited=True).count(),
        })


class CommentListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, resource_id):
        comments = Comment.objects.filter(resource__resource_id=resource_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, resource_id):
        if not request.data.get('comments_text'):
            return Response(
                {'error': 'Le champ comments_text est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': _ERR_CITIZEN_NOT_FOUND},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            resource = Resource.objects.get(resource_id=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {'error': 'Ressource introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        comment = Comment.objects.create(
            citizen=citizen,
            resource=resource,
            comments_text=request.data['comments_text']
        )
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, resource_id, pk):
        try:
            comment = Comment.objects.get(
                comments_id=pk,
                resource__resource_id=resource_id
            )
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Commentaire introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if str(comment.citizen.user_id) != str(request.user.user_id):
            return Response(
                {'error': 'Vous ne pouvez pas supprimer les commentaires des autres utilisateurs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        if not request.data.get('comments_text'):
            return Response(
                {'error': 'Le champ comments_text est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            parent = Comment.objects.get(comments_id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Commentaire introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': _ERR_CITIZEN_NOT_FOUND},
                status=status.HTTP_403_FORBIDDEN
            )
        reply = Comment.objects.create(
            citizen=citizen,
            resource=parent.resource,
            parent=parent,
            comments_text=request.data['comments_text'],
        )
        return Response(CommentSerializer(reply).data, status=status.HTTP_201_CREATED)
