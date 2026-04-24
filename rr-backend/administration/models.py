from django.db import models
from users.models import User  # ← inchangé, User reste dans users/models.py


class Admin(models.Model):
    admin_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="admin_id",
        related_name="admin_profile",
    )
    admin_created_at = models.DateTimeField(auto_now_add=True, null=False)
    admin_is_super_admin = models.BooleanField(default=False, null=False)
    admin_token = models.CharField(max_length=512, null=True, blank=True)
    admin_refresh_token = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        app_label = "administration"
        db_table = "admin"
        managed = False  # ← à ajouter, cohérent avec tes autres modèles

    def __str__(self):
        return f"Admin({self.admin_id_id}, super={self.admin_is_super_admin})"