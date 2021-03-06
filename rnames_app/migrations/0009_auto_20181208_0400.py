# Generated by Django 2.0.9 on 2018-12-08 02:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rnames_app', '0008_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='first_author',
            field=models.CharField(blank=True, help_text='Enter the name of the first author of the reference', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='reference',
            name='link',
            field=models.URLField(blank=True, help_text='Enter a valid URL for the reference', null=True),
        ),
        migrations.AddField(
            model_name='reference',
            name='year',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2100)]),
        ),
    ]
