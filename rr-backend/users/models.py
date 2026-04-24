import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class UserManager(models.Manager):

    def get_by_natural_key(self, username: str):
        """
        Récupère un utilisateur par son email.
        'username' est la valeur du champ USERNAME_FIELD = 'user_mail'.
        """
        return self.get(user_mail=username)


class User(models.Model):

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='user_id',
    )
    user_fname = models.CharField(max_length=100, db_column='user_fname')
    user_lname = models.CharField(max_length=100, db_column='user_lname')
    user_mail = models.EmailField(
        max_length=255,
        unique=True,
        db_column='user_mail',
    )
    user_password = models.CharField(max_length=255, db_column='user_password')

    # Manager custom — DOIT être assigné avant USERNAME_FIELD
    objects = UserManager()

    USERNAME_FIELD = 'user_mail'
    REQUIRED_FIELDS = ['user_fname', 'user_lname']

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return f"{self.user_fname} {self.user_lname} <{self.user_mail}>"

    # ── Gestion du mot de passe ───────────────────────────────────────────
    # On n'hérite PAS d'AbstractBaseUser, donc on déclare ces méthodes
    # explicitement. Django les appelle via le backend d'auth.

    def set_password(self, raw_password: str) -> None:
        """Hache et stocke le mot de passe (PBKDF2-SHA256 par défaut)."""
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Vérifie un mot de passe en clair contre le hash stocké."""
        return check_password(raw_password, self.user_password)

    # ── Propriétés requises par DRF et SimpleJWT ──────────────────────────

    @property
    def is_active(self) -> bool:
        """
        Délègue à citizen.user_is_actived.
        SimpleJWT appelle cette propriété pour rejeter les tokens
        de comptes désactivés.
        """
        try:
            return self.citizen.user_is_actived
        except Exception:
            return False

    @property
    def is_authenticated(self) -> bool:
        """Requis par DRF pour distinguer un user authentifié d'un anonyme."""
        return True

    @property
    def is_anonymous(self) -> bool:
        return False


class Citizen(models.Model):
    """
    Table 'citizen' — profil citoyen et tokens JWT.
    Schéma géré par Liquibase (managed=False).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='user_id',
        related_name='citizen',
    )
    # Pas d'auto_now_add : Postgres applique son DEFAULT now() à l'INSERT.
    # editable=False + blank=True = Django ne l'inclut pas dans les writes.
    user_created_at = models.DateTimeField(
        db_column='user_created_at',
        default=timezone.now,
        editable=False,
    )
    user_is_modo = models.CharField(
        max_length=10,
        default='light',
        db_column='user_is_modo',
    )
    user_is_actived = models.BooleanField(
        default=True,
        db_column='user_is_actived',
    )
    # NULL = non connecté ou token révoqué (logout / désactivation compte).
    user_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_column='user_token',
    )
    user_refresh_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        db_column='user_refresh_token',
    )

    class Meta:
        managed = False
        db_table = 'citizen'

    def __str__(self):
        return f"Citoyen {self.user.user_mail} (actif={self.user_is_actived})"

    def invalidate_tokens(self) -> None:
        """
        Révoque les tokens JWT (logout ou désactivation compte).
        UPDATE ciblé sur les deux colonnes uniquement.
        """
        self.user_token = None
        self.user_refresh_token = None
        self.save(update_fields=['user_token', 'user_refresh_token'])