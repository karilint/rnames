# Generated by Django 4.1.3 on 2022-11-18 18:18

from django.conf import settings
from django.db import migrations
import django.db.models.deletion
import django_userforeignkey.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rnames_api', '0004_keyabsoluteagevalue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userapikey',
            name='user',
            field=django_userforeignkey.models.fields.UserForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='associated_%(class)s', to=settings.AUTH_USER_MODEL, verbose_name='Associated user'),
        ),
    ]