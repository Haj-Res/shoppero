# Generated by Django 3.1.3 on 2020-11-18 14:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('items', '0001_initial'),
        ('shopping_list', '0009_sharedshoppinglist_access_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharedshoppinglist',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='shoppinglist',
            name='items',
        ),
        migrations.RemoveField(
            model_name='shoppinglistitem',
            name='deleted',
        ),
        migrations.AlterField(
            model_name='sharedshoppinglist',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shoppinglistitem',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.item'),
        ),
        migrations.AlterField(
            model_name='shoppinglistitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='Item',
                ),
            ],
            # The model was moved from this module to the items module, the deletion of the table is faked
            database_operations=[]
        )

    ]