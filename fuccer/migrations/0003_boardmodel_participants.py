# Generated by Django 5.1.2 on 2024-11-05 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fuccer', '0002_remove_boardmodel_id_boardmodel_board_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardmodel',
            name='participants',
            field=models.IntegerField(default=0),
        ),
    ]