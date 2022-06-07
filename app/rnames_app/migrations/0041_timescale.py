from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('rnames_app', '0040_countrycodes'),
    ]

    operations = [
        migrations.RenameModel('BinningScheme', 'TimeScale'),
        migrations.RenameModel('HistoricalBinningScheme', 'HistoricalTimeScale'),
        migrations.RenameField('TimeScale', 'name', 'ts_name'),
        migrations.RenameField('HistoricalTimeScale', 'name', 'ts_name'),
    ]

