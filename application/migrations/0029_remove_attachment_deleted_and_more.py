# Generated by Django 5.0.9 on 2024-10-18 16:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_attachment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='deleted_by_cascade',
        ),
        migrations.AddField(
            model_name='attachment',
            name='filename',
            field=models.CharField(default='name', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attachment',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to='media/'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
