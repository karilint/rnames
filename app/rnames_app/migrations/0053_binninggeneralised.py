# Generated by Django 4.1.3 on 2022-11-19 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rnames_app', '0052_alter_historicalabsoluteagevalue_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BinningGeneralised',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('oldest', models.CharField(max_length=255)),
                ('youngest', models.CharField(max_length=255)),
                ('binning_scheme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rnames_app.timescale')),
            ],
        ),
    ]