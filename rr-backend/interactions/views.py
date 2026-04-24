from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Interaction, Comment, Citizen, Resource
from .serializers import InteractionSerializer, CommentSerializer


class InteractionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resource_id):
        try:
            interaction = Interaction.objects.get(
                citizen__user_id=request.user.id,
                resource__resource_id=resource_id
            )
            serializer = InteractionSerializer(interaction)
            return Response(serializer.data)
        except Interaction.DoesNotExist:
            return Response({
                'citizen_id': str(request.user.id),
                'resource_id': str(resource_id),
                'is_liked': False,
                'is_favorise': False,
                'is_bookmark': False
            })

    def post(self, request, resource_id):
        try:
            citizen = Citizen.objects.get(user_id=request.user.id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': 'Citoyen introuvable.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            resource = Resource.objects.get(resource_id=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {'error': 'Ressource introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        defaults = {}
        if 'is_liked' in request.data:
            defaults['is_liked'] = request.data['is_liked']
        if 'is_favorise' in request.data:
            defaults['is_favorise'] = request.data['is_favorise']
        if 'is_bookmark' in request.data:
            defaults['is_bookmark'] = request.data['is_bookmark']

        interaction, created = Interaction.objects.update_or_create(
            citizen=citizen,
            resource=resource,
            defaults=defaults
        )
        serializer = InteractionSerializer(interaction)
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=http_status)


class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

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
            citizen = Citizen.objects.get(user_id=request.user.id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': 'Citoyen introuvable.'},
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
        if str(comment.citizen.user_id) != str(request.user.id):
            return Response(
                {'error': 'Vous ne pouvez pas supprimer les commentaires des autres utilisateurs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
