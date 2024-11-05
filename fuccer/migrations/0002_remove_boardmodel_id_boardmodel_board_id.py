# Generated by Django 5.1.2 on 2024-10-31 03:11

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuccer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boardmodel',
            name='id',
        ),
        migrations.AddField(
            model_name='boardmodel',
            name='board_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
