# Generated by Django 2.0.9 on 2019-01-16 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0009_historicalmasterentity_masterentity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmasterreference',
            name='container_title',
            field=models.CharField(blank=True, help_text='Enter the Container Title of the Master Reference', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalmasterreference',
            name='title',
            field=models.CharField(blank=True, help_text='Enter the Title of the Master Reference', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='masterreference',
            name='container_title',
            field=models.CharField(blank=True, help_text='Enter the Container Title of the Master Reference', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='masterreference',
            name='title',
            field=models.CharField(blank=True, help_text='Enter the Title of the Master Reference', max_length=250, null=True),
        ),
    ]