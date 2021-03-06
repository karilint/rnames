# Generated by Django 2.0.9 on 2019-01-18 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0017_auto_20190117_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='name',
            field=models.CharField(help_text='Enter the Name of the FoodItem', max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalfooditem',
            name='name',
            field=models.CharField(db_index=True, help_text='Enter the Name of the FoodItem', max_length=250),
        ),
    ]
