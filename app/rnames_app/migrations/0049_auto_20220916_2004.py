# Generated by Django 3.2.15 on 2022-09-16 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rnames_app', '0048_add_binning_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binning',
            name='oldest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='rnames_app.structuredname'),
        ),
        migrations.AlterField(
            model_name='binning',
            name='structured_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='rnames_app.structuredname'),
        ),
        migrations.AlterField(
            model_name='binning',
            name='youngest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='rnames_app.structuredname'),
        ),
    ]
