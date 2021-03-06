# Generated by Django 3.0.4 on 2020-03-19 11:26

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='_default_avatar',
            field=models.ImageField(default='default-profile-image.png', upload_to=account.models.avatar_file_path),
        ),
    ]
