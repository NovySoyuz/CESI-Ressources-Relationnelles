from django.db import transaction
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    Resource, Category, Relation,
    ResourceCategory, ResourceRelation,
)
from .serializers import (
    ResourceListSerializer, ResourceDetailSerializer, ResourceWriteSerializer,
    CategorySerializer, RelationSerializer, SUBTYPE_MAP,
)
from users.models import Citizen

_ERR_RESOURCE_NOT_FOUND = 'Ressource introuvable.'
_ERR_CITIZEN_NOT_FOUND  = 'Citoyen introuvable.'
_ALLOWED_ORDERINGS = {
    'resource_created_at', '-resource_created_at',
    'resource_title', '-resource_title',
}


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(CategorySerializer(Category.objects.all(), many=True).data)


class RelationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(RelationSerializer(Relation.objects.all(), many=True).data)


class ResourceListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        if request.query_params.get('author') == 'me':
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentification requise.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                citizen = Citizen.objects.get(user_id=request.user.user_id)
            except Citizen.DoesNotExist:
                return Response(
                    {'error': _ERR_CITIZEN_NOT_FOUND},
                    status=status.HTTP_403_FORBIDDEN,
                )
            qs = Resource.objects.filter(resource_author=citizen).prefetch_related(
                'categories', 'relations'
            ).order_by('-resource_created_at')
            return Response(ResourceListSerializer(qs, many=True).data)

        qs = Resource.objects.filter(resource_is_visible=True).prefetch_related(
            'categories', 'relations'
        )

        label = request.query_params.get('label')
        if label:
            qs = qs.filter(resource_label=label)

        categories = request.query_params.getlist('category')
        if categories:
            qs = qs.filter(categories__category_id__in=categories)

        relations = request.query_params.getlist('relation')
        if relations:
            qs = qs.filter(relations__relation_id__in=relations)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(resource_title__icontains=search) |
                Q(resource_description__icontains=search)
            )

        ordering = request.query_params.get('ordering', '-resource_created_at')
        if ordering in _ALLOWED_ORDERINGS:
            qs = qs.order_by(ordering)

        return Response(ResourceListSerializer(qs.distinct(), many=True).data)

    @transaction.atomic
    def post(self, request):
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': _ERR_CITIZEN_NOT_FOUND},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ResourceWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        resource = Resource.objects.create(
            resource_author=citizen,
            resource_title=data['resource_title'],
            resource_description=data.get('resource_description'),
            resource_label=data.get('resource_label'),
            resource_is_visible=False,
        )

        for cat_id in data.get('categories', []):
            try:
                ResourceCategory.objects.create(
                    resource=resource,
                    category=Category.objects.get(category_id=cat_id),
                )
            except Category.DoesNotExist:
                pass

        for rel_id in data.get('relations', []):
            try:
                ResourceRelation.objects.create(
                    resource=resource,
                    relation=Relation.objects.get(relation_id=rel_id),
                )
            except Relation.DoesNotExist:
                pass

        label = data.get('resource_label')
        detail_data = data.get('detail', {})
        if label and label in SUBTYPE_MAP and detail_data:
            subtype_model, subtype_serializer_class, _ = SUBTYPE_MAP[label]
            sub = subtype_serializer_class(data=detail_data)
            if sub.is_valid():
                subtype_model.objects.create(resource=resource, **sub.validated_data)

        return Response(
            ResourceDetailSerializer(resource).data,
            status=status.HTTP_201_CREATED,
        )


class ResourceDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_resource_or_404(self, resource_id):
        try:
            return Resource.objects.get(resource_id=resource_id)
        except Resource.DoesNotExist:
            return None

    def get(self, request, resource_id):
        resource = self._get_resource_or_404(resource_id)
        if not resource:
            return Response(
                {'error': _ERR_RESOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not resource.resource_is_visible:
            if not request.user.is_authenticated:
                return Response(
                    {'error': _ERR_RESOURCE_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if str(resource.resource_author.user_id) != str(request.user.user_id):
                return Response(
                    {'error': _ERR_RESOURCE_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(ResourceDetailSerializer(resource).data)

    def patch(self, request, resource_id):
        resource = self._get_resource_or_404(resource_id)
        if not resource:
            return Response(
                {'error': _ERR_RESOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Seul l'auteur peut modifier le contenu de sa ressource (la modération
        # de visibilité est gérée séparément par ResourcePublishView).
        if str(resource.resource_author.user_id) != str(request.user.user_id):
            return Response(
                {'error': 'Modification réservée à l\'auteur de la ressource.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        if 'resource_title' in data:
            resource.resource_title = data['resource_title']
        if 'resource_description' in data:
            resource.resource_description = data['resource_description']
        if 'resource_label' in data:
            resource.resource_label = data['resource_label']
        resource.save()

        return Response(ResourceDetailSerializer(resource).data)

    def delete(self, request, resource_id):
        resource = self._get_resource_or_404(resource_id)
        if not resource:
            return Response(
                {'error': _ERR_RESOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Seul l'auteur peut supprimer sa ressource (idem : la modération de
        # visibilité passe par ResourcePublishView, pas par ce endpoint).
        if str(resource.resource_author.user_id) != str(request.user.user_id):
            return Response(
                {'error': 'Suppression réservée à l\'auteur de la ressource.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourcePendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response({'error': _ERR_CITIZEN_NOT_FOUND}, status=status.HTTP_403_FORBIDDEN)
        if not citizen.user_is_modo:
            return Response({'error': 'Réservé aux modérateurs.'}, status=status.HTTP_403_FORBIDDEN)
        qs = Resource.objects.filter(resource_is_visible=False).prefetch_related(
            'categories', 'relations'
        ).order_by('resource_created_at')
        return Response(ResourceListSerializer(qs, many=True).data)


class ResourcePublishView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, resource_id):
        try:
            citizen = Citizen.objects.get(user_id=request.user.user_id)
        except Citizen.DoesNotExist:
            return Response(
                {'error': _ERR_CITIZEN_NOT_FOUND},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not citizen.user_is_modo:
            return Response(
                {'error': 'Réservé aux modérateurs.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            resource = Resource.objects.get(resource_id=resource_id)
        except Resource.DoesNotExist:
            return Response(
                {'error': _ERR_RESOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        resource.resource_is_visible = not resource.resource_is_visible
        resource.save()
        return Response(ResourceDetailSerializer(resource).data)
