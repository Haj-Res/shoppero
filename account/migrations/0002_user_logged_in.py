# Generated by Django 3.0.3 on 2020-02-25 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='logged_in',
            field=models.DateTimeField(auto_now=True),
        ),
    ]