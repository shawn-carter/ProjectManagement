# Generated by Django 5.0.9 on 2024-10-02 16:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('skill_id', models.AutoField(primary_key=True, serialize=False)),
                ('skill_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('status_id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('team_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('asset_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('work_days', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thur', 'Thursday'), ('Fri', 'Friday')], max_length=50)),
                ('normal_work_week', models.IntegerField()),
                ('skills', models.ManyToManyField(to='application.skill')),
                ('teams', models.ManyToManyField(blank=True, to='application.team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('project_id', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=50)),
                ('planned_start_date', models.DateTimeField()),
                ('original_target_end_date', models.DateTimeField()),
                ('revised_target_end_date', models.DateTimeField(blank=True, null=True)),
                ('actual_start_date', models.DateTimeField(blank=True, null=True)),
                ('actual_end_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='application.category')),
                ('project_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.asset')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='application.status')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('task_id', models.AutoField(primary_key=True, serialize=False)),
                ('task_name', models.CharField(max_length=50)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')])),
                ('planned_start_date', models.DateTimeField()),
                ('planned_end_date', models.DateTimeField()),
                ('actual_start_date', models.DateTimeField(blank=True, null=True)),
                ('actual_end_date', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateTimeField()),
                ('has_dependency', models.BooleanField(default=False)),
                ('estimated_time_to_complete', models.DurationField()),
                ('actual_time_to_complete', models.DurationField(blank=True, null=True)),
                ('delay_reason', models.TextField(blank=True, null=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_updated_datetime', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.asset')),
                ('dependant_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.task')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='application.project')),
                ('skills_required', models.ManyToManyField(to='application.skill')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='application.status')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
