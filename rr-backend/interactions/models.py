import uuid
from django.db import models


class Citizen(models.Model):
    user_id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'citizen'


class Resource(models.Model):
    resource_id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'resource'


class Interaction(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, db_column='citizen_id')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, db_column='resource_id')
    is_liked = models.BooleanField(default=False)
    is_favorise = models.BooleanField(default=False)
    is_bookmark = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'interactions'
        unique_together = [('citizen', 'resource')]


class Comment(models.Model):
    comments_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, db_column='citizen_id')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, db_column='resource_id')
    comments_text = models.TextField()
    comments_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'comments'
        ordering = ['-comments_created_at']
