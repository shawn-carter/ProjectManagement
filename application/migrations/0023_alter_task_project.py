# Generated by Django 5.0.9 on 2024-10-14 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0022_historicalasset_historicalcategory_historicalcomment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.project'),
        ),
    ]
