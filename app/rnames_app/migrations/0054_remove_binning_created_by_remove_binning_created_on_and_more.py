# Generated by Django 4.1.3 on 2022-12-12 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rnames_app', '0053_binninggeneralised'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='binning',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='binning',
            name='created_on',
        ),
        migrations.RemoveField(
            model_name='binning',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='binning',
            name='modified_on',
        ),
        migrations.DeleteModel(
            name='HistoricalBinning',
        ),
    ]
