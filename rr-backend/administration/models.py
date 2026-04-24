from django.db import models
from django.utils import timezone
from users.models import User


class Admin(models.Model):
    admin_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='admin_id',
        related_name='admin_profile',
    )
    admin_created_at = models.DateTimeField(
        db_column='admin_created_at',
        default=timezone.now,
        editable=False,
    )
    admin_is_super_admin = models.BooleanField(
        default=False,
        db_column='admin_is_super_admin',
    )
    admin_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_column='admin_token',
    )
    admin_refresh_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_column='admin_refresh_token',
    )

    class Meta:
        managed = False
        db_table = 'admin'

    def __str__(self):
        return f"Admin({self.admin_id}, super={self.admin_is_super_admin})"

    def invalidate_tokens(self) -> None:
        self.admin_token = None
        self.admin_refresh_token = None
        self.save(update_fields=['admin_token', 'admin_refresh_token'])
