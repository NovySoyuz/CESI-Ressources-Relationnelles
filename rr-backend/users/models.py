import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# 1. On définit l'utilisateur d'abord
class User(models.Model):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='user_id'
    )
    user_fname = models.CharField(max_length=100, db_column='user_fname')
    user_lname = models.CharField(max_length=100, db_column='user_lname')
    user_mail = models.EmailField(
        max_length=255,
        unique=True,
        db_column='user_mail'
    )
    user_password = models.CharField(max_length=255, db_column='user_password')

    USERNAME_FIELD = 'user_mail'
    REQUIRED_FIELDS = ['user_fname', 'user_lname']

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return f"{self.user_fname} {self.user_lname} <{self.user_mail}>"

    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)

    def set_password(self, raw_password):
        self.user_password = make_password(raw_password)

    @property
    def is_active(self):
        try:
            return self.citizen.user_is_actived
        except Exception:
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

# 2. Puis on définit le profil qui pointe vers l'utilisateur
class Citizen(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='user_id',
        related_name='citizen'
    )
    user_created_at = models.DateTimeField(
        db_column='user_created_at',
        auto_now_add=True,
        editable=False
    )
    user_la_mode = models.CharField(
        max_length=10,
        default='light',
        db_column='user_la_mode'
    )
    user_is_actived = models.BooleanField(
        default=True,
        db_column='user_is_actived'
    )
    user_token = models.CharField(max_length=512, null=True, blank=True, db_column='user_token')
    user_refresh_token = models.CharField(max_length=512, null=True, blank=True, db_column='user_refresh_token')

    class Meta:
        managed = False
        db_table = 'citizen'