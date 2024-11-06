from django.db import models
from django.utils import timezone
import uuid


# Create your models here.

class User(models.Model):
    userid = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)


class BoardModel(models.Model):
    board_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.IntegerField(default=0)
    participant_limit = models.IntegerField()  # 参加上限
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    participants_list = models.ManyToManyField(User, through='BoardParticipant', related_name='joined_boards')


class BoardParticipant(models.Model):
    board = models.ForeignKey(BoardModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)


class Profile(models.Model):
    Profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

