from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class BoardModel(models.Model):
    board_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # 管理者が非表示にできる
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_boards')
    participants = models.IntegerField(default=0)
    participant_limit = models.IntegerField(default=0)  # 参加上限
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    participants_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='BoardParticipant',
        related_name='joined_boards'
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)  # 実施日時
    tags = models.ManyToManyField('Tag', related_name='boards', blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BoardParticipant(models.Model):
    board = models.ForeignKey(BoardModel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    SEX_CHOICES = [
        (0, 'Not Specified'),
        (1, 'Male'),
        (2, 'Female'),
    ]

    Profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20)
    sex = models.IntegerField(choices=SEX_CHOICES, default=0)
    bio = models.TextField(blank=True, null=True)
    hobby = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

class UserFavorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='favorites',
        on_delete=models.CASCADE
    )  # お気に入りを登録するユーザー
    favorite_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='favorited_by',
        on_delete=models.CASCADE
    )  # お気に入りされる対象のユーザー
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'favorite_user')  # 同じユーザーを複数回登録するのを防ぐ


class ChatRoom(models.Model):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # ルーム名を追加
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        (1, '違反行為'),
        (2, '迷惑行為'),
        (3, 'その他'),
    ]

    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='reports_received')
    report_type = models.IntegerField(choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporter.username} reported {self.reported_user.username}"
