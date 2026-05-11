from rest_framework import serializers
from .models import Interaction, Comment


class InteractionSerializer(serializers.ModelSerializer):
    citizen_id = serializers.UUIDField(source='citizen.user_id', read_only=True)
    resource_id = serializers.UUIDField(source='resource.resource_id', read_only=True)

    class Meta:
        model = Interaction
        fields = ['citizen_id', 'resource_id', 'is_liked', 'is_favorise', 'is_bookmark', 'is_exploited']


class CommentSerializer(serializers.ModelSerializer):
    citizen_id = serializers.UUIDField(source='citizen.user_id', read_only=True)
    resource_id = serializers.UUIDField(source='resource.resource_id', read_only=True)

    class Meta:
        model = Comment
        fields = ['comments_id', 'citizen_id', 'resource_id', 'comments_text', 'comments_created_at']
        read_only_fields = ['comments_id', 'citizen_id', 'comments_created_at']
