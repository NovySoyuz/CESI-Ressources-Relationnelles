import uuid
from django.db import models


class Resource(models.Model):
    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_author = models.ForeignKey(
        'users.Citizen',
        on_delete=models.CASCADE,
        db_column='resource_author',
    )
    resource_created_at = models.DateTimeField(auto_now_add=True)
    resource_last_modif = models.DateTimeField(auto_now=True)
    resource_is_visible = models.BooleanField(default=False)
    resource_title = models.CharField(max_length=255)
    resource_description = models.TextField(null=True, blank=True)
    resource_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource'
