# Generated by Django 5.0.9 on 2024-10-10 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0016_rename_risk_id_risk_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='risk',
            options={},
        ),
        migrations.RenameField(
            model_name='assumption',
            old_name='assumption_id',
            new_name='id',
        ),
    ]
