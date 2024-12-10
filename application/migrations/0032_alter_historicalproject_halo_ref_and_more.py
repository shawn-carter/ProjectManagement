# Generated by Django 5.0.9 on 2024-12-05 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0031_rename_dependant_task_historicaltask_prereq_task_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalproject',
            name='halo_ref',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='actual_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Actual End Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='actual_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Actual Start Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='actual_time_to_complete',
            field=models.DurationField(blank=True, null=True, verbose_name='Actual Time to Complete (Hours)'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='assigned_to',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='application.asset', verbose_name='Assigned To'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='created_datetime',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='delay_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Reason for Delay'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='estimated_time_to_complete',
            field=models.DurationField(blank=True, null=True, verbose_name='Estimated Time to Complete'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='halo_ref',
            field=models.IntegerField(blank=True, null=True, verbose_name='Halo Reference'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='last_updated_datetime',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='Last Updated'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='planned_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Planned End Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='planned_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Planned Start Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='prereq_task',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='application.task', verbose_name='Prerequisite Task'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')], verbose_name='Priority Level'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='task_details',
            field=models.TextField(null=True, verbose_name='Task Details'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='task_name',
            field=models.CharField(max_length=50, verbose_name='Task Name'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='task_status',
            field=models.IntegerField(choices=[(1, 'Unassigned'), (2, 'Assigned'), (3, 'Completed')], default=1, verbose_name='Task Status'),
        ),
        migrations.AlterField(
            model_name='project',
            name='halo_ref',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='actual_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Actual End Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='actual_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Actual Start Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='actual_time_to_complete',
            field=models.DurationField(blank=True, null=True, verbose_name='Actual Time to Complete (Hours)'),
        ),
        migrations.AlterField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.asset', verbose_name='Assigned To'),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='task',
            name='delay_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Reason for Delay'),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='estimated_time_to_complete',
            field=models.DurationField(blank=True, null=True, verbose_name='Estimated Time to Complete'),
        ),
        migrations.AlterField(
            model_name='task',
            name='halo_ref',
            field=models.IntegerField(blank=True, null=True, verbose_name='Halo Reference'),
        ),
        migrations.AlterField(
            model_name='task',
            name='last_updated_datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Updated'),
        ),
        migrations.AlterField(
            model_name='task',
            name='planned_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Planned End Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='planned_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Planned Start Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='prereq_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.task', verbose_name='Prerequisite Task'),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')], verbose_name='Priority Level'),
        ),
        migrations.AlterField(
            model_name='task',
            name='skills_required',
            field=models.ManyToManyField(to='application.skill', verbose_name='Skills Required'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_details',
            field=models.TextField(null=True, verbose_name='Task Details'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_name',
            field=models.CharField(max_length=50, verbose_name='Task Name'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.IntegerField(choices=[(1, 'Unassigned'), (2, 'Assigned'), (3, 'Completed')], default=1, verbose_name='Task Status'),
        ),
    ]
