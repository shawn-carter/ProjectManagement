# Generated by Django 5.0.9 on 2024-10-04 10:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_alter_task_task_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='last_updated_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
