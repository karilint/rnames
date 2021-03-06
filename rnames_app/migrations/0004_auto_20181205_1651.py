# Generated by Django 2.0.9 on 2018-12-05 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rnames_app', '0003_auto_20181205_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='name',
            name='modified_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='name_name_modified', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='name',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='name_name_created', to=settings.AUTH_USER_MODEL),
        ),
    ]
