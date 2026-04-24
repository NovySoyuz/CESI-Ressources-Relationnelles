import uuid
from django.db import models


class Resource(models.Model):
    resource_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_author = models.UUIDField()
    resource_created_at = models.DateTimeField(auto_now_add=True)
    resource_last_modif = models.DateTimeField(auto_now=True)
    resource_is_visible = models.BooleanField(default=False)
    resource_title = models.CharField(max_length=255)
    resource_description = models.TextField(null=True, blank=True)
    resource_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource'


class ResourceReadingSheet(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_reading_sheet'


class ResourceGames(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    game_url = models.CharField(max_length=512, null=True, blank=True)
    game_platform = models.CharField(max_length=100, null=True, blank=True)
    game_instructions = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_games'


class ResourceVideos(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    video_url = models.CharField(max_length=512)
    video_duration = models.IntegerField()
    video_platform = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_videos'


class ResourcePDF(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
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
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    activity_instructions = models.TextField(null=True, blank=True)
    activity_duration = models.IntegerField(null=True, blank=True)
    activity_required_materials = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_activity'


class ResourceArticle(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    article_url = models.CharField(max_length=512)
    article_publisher = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_article'


class ResourceChallengeCard(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    challenge_card_duration = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_challenge_card'


class ResourceExercise(models.Model):
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, primary_key=True, db_column='resource_id'
    )
    exercise_instructions = models.TextField(null=True, blank=True)
    exercise_duration = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'resource_exercise'
