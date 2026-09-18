from rest_framework import serializers

from .models import (
    Resource, Category, Relation,
    ResourceReadingSheet, ResourceGames, ResourceVideos, ResourcePDF,
    ResourceActivity, ResourceArticle, ResourceChallengeCard, ResourceExercise,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'label']


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ['relation_id', 'label']


# ─────────────────────────────────────────────────────────────────────────────
# Sous-types
# ─────────────────────────────────────────────────────────────────────────────

class ResourceReadingSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceReadingSheet
        fields = ['book_title', 'book_author', 'summary']


class ResourceGamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceGames
        fields = ['game_url', 'game_platform', 'game_instructions']


class ResourceVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceVideos
        fields = ['video_url', 'video_duration', 'video_platform']


class ResourcePDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcePDF
        fields = ['pdf_url', 'pdf_publisher', 'pdf_page_count', 'pdf_size']


class ResourceActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceActivity
        fields = ['activity_instructions', 'activity_duration', 'activity_required_materials']


class ResourceArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceArticle
        fields = ['article_url', 'article_publisher']


class ResourceChallengeCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceChallengeCard
        fields = ['challenge_card_duration']


class ResourceExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceExercise
        fields = ['exercise_instructions', 'exercise_duration']


# label → (Model, Serializer, related_name)
SUBTYPE_MAP = {
    'reading_sheet':  (ResourceReadingSheet,  ResourceReadingSheetSerializer,  'reading_sheet'),
    'games':          (ResourceGames,          ResourceGamesSerializer,          'games'),
    'videos':         (ResourceVideos,         ResourceVideosSerializer,         'videos'),
    'pdf':            (ResourcePDF,            ResourcePDFSerializer,            'pdf'),
    'activity':       (ResourceActivity,       ResourceActivitySerializer,       'activity'),
    'article':        (ResourceArticle,        ResourceArticleSerializer,        'article'),
    'challenge_card': (ResourceChallengeCard,  ResourceChallengeCardSerializer,  'challenge_card'),
    'exercise':       (ResourceExercise,       ResourceExerciseSerializer,       'exercise'),
}


# ─────────────────────────────────────────────────────────────────────────────
# Resource
# ─────────────────────────────────────────────────────────────────────────────

class ResourceAuthorSerializer(serializers.Serializer):
    user_id    = serializers.UUIDField()
    user_fname = serializers.CharField(source='user.user_fname')
    user_lname = serializers.CharField(source='user.user_lname')


class ResourceListSerializer(serializers.ModelSerializer):
    categories      = CategorySerializer(many=True, read_only=True)
    relations       = RelationSerializer(many=True, read_only=True)
    resource_author = ResourceAuthorSerializer(read_only=True)

    class Meta:
        model = Resource
        fields = [
            'resource_id', 'resource_title', 'resource_description',
            'resource_label', 'resource_is_visible', 'resource_created_at',
            'resource_last_modif', 'resource_author', 'categories', 'relations',
        ]


class ResourceDetailSerializer(serializers.ModelSerializer):
    categories      = CategorySerializer(many=True, read_only=True)
    relations       = RelationSerializer(many=True, read_only=True)
    resource_author = ResourceAuthorSerializer(read_only=True)
    detail          = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'resource_id', 'resource_title', 'resource_description',
            'resource_label', 'resource_is_visible', 'resource_created_at',
            'resource_last_modif', 'resource_author', 'categories', 'relations', 'detail',
        ]

    def get_detail(self, obj):
        entry = SUBTYPE_MAP.get(obj.resource_label)
        if not entry:
            return None
        _, SerializerClass, related_name = entry
        try:
            subtype = getattr(obj, related_name)
            return SerializerClass(subtype).data
        except Exception:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        label = instance.resource_label
        detail = data.pop('detail', None)
        if label and detail is not None:
            data[label] = detail
        return data


class ResourceWriteSerializer(serializers.Serializer):
    resource_title = serializers.CharField(max_length=255)
    resource_description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    resource_label = serializers.ChoiceField(
        choices=[k for k in SUBTYPE_MAP], required=True
    )
    categories = serializers.ListField(
        child=serializers.UUIDField(), required=True, min_length=1
    )
    relations = serializers.ListField(
        child=serializers.UUIDField(), required=True, min_length=1
    )
    detail = serializers.DictField(required=False, default=dict)

    def validate(self, attrs):
        label = attrs.get('resource_label')
        detail = attrs.get('detail', {})
        if label and label in SUBTYPE_MAP and detail:
            _, SubtypeSerializer, _ = SUBTYPE_MAP[label]
            sub = SubtypeSerializer(data=detail)
            if not sub.is_valid():
                raise serializers.ValidationError({'detail': sub.errors})
        return attrs
