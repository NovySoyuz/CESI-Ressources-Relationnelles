import uuid
from django.db import models


class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'category'


class Relation(models.Model):
    relation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'relation'


class Resource(models.Model):
    LABEL_CHOICES = [
        ('reading_sheet', 'Fiche de lecture'),
        ('games', 'Jeu'),
        ('videos', 'Vidéo'),
        ('pdf', 'PDF'),
        ('activity', 'Activité'),
        ('article', 'Article'),
        ('challenge_card', 'Carte défi'),
        ('exercise', 'Exercice'),
    ]

    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_author = models.ForeignKey(
        'users.Citizen',
        on_delete=models.DO_NOTHING,
        db_column='resource_author',
    )
    resource_created_at = models.DateTimeField(auto_now_add=True)
    resource_last_modif = models.DateTimeField(auto_now=True)
    resource_is_visible = models.BooleanField(default=False)
    resource_title = models.CharField(max_length=255)
    resource_description = models.TextField(null=True, blank=True)
    resource_label = models.CharField(
        max_length=100, null=True, blank=True, choices=LABEL_CHOICES
    )
    categories = models.ManyToManyField(
        Category, through='ResourceCategory', blank=True
    )
    relations = models.ManyToManyField(
        Relation, through='ResourceRelation', blank=True
    )

    class Meta:
        managed = False
        db_table = 'resource'


class ResourceCategory(models.Model):
    resource = models.ForeignKey(
        Resource, on_delete=models.DO_NOTHING, db_column='resource_id'
    )
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, db_column='category_id'
    )

    class Meta:
        managed = False
        db_table = 'resource_category'
        unique_together = [('resource', 'category')]


class ResourceRelation(models.Model):
    resource = models.ForeignKey(
        Resource, on_delete=models.DO_NOTHING, db_column='resource_id'
    )
    relation = models.ForeignKey(
        Relation, on_delete=models.DO_NOTHING, db_column='relation_id'
    )

    class Meta:
        managed = False
        db_table = 'resource_relation'
        unique_together = [('resource', 'relation')]


class ResourceReadingSheet(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='reading_sheet',
    )
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_reading_sheet'


class ResourceGames(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='games',
    )
    game_url = models.CharField(max_length=512, null=True, blank=True)
    game_platform = models.CharField(max_length=100, null=True, blank=True)
    game_instructions = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_games'


class ResourceVideos(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='videos',
    )
    video_url = models.CharField(max_length=512)
    video_duration = models.IntegerField()
    video_platform = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_videos'


class ResourcePDF(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='pdf',
    )
    pdf_url = models.CharField(max_length=512)
    pdf_publisher = models.CharField(max_length=255, null=True, blank=True)
    pdf_page_count = models.IntegerField(null=True, blank=True)
    pdf_size = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_pdf'


class ResourceActivity(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='activity',
    )
    activity_instructions = models.TextField(null=True, blank=True)
    activity_duration = models.IntegerField(null=True, blank=True)
    activity_required_materials = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_activity'


class ResourceArticle(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='article',
    )
    article_url = models.CharField(max_length=512)
    article_publisher = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_article'


class ResourceChallengeCard(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='challenge_card',
    )
    challenge_card_duration = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_challenge_card'


class ResourceExercise(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.DO_NOTHING, primary_key=True,
        db_column='resource_id', related_name='exercise',
    )
    exercise_instructions = models.TextField(null=True, blank=True)
    exercise_duration = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_exercise'
