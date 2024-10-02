from safedelete.models import SafeDeleteModel, SOFT_DELETE
from django.db import models
from django.contrib.auth.models import User

# Replace our SoftDeleteMixin with SafeDeleteModel and configure policies

class Category(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE  # Configure the soft delete policy
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name

class Status(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)  # E.g., Scoping, Unassigned, Assigned, On Hold, Completed

    def __str__(self):
        return self.status_name

class DayOfWeek(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    day_name = models.CharField(max_length=10, unique=True)  # Monday, Tuesday, etc.
    abbreviation = models.CharField(max_length=3, unique=True)  # Mon, Tue, etc.

    def __str__(self):
        return self.day_name

class Project(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50, unique=True)
    planned_start_date = models.DateTimeField()
    original_target_end_date = models.DateTimeField()
    revised_target_end_date = models.DateTimeField(blank=True, null=True)
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)
    project_owner = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')])

    def __str__(self):
        return self.project_name

class Task(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')])
    planned_start_date = models.DateTimeField()
    planned_end_date = models.DateTimeField()
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField()
    has_dependency = models.BooleanField(default=False)
    dependant_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_time_to_complete = models.DurationField()
    actual_time_to_complete = models.DurationField(blank=True, null=True)
    delay_reason = models.TextField(blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    skills_required = models.ManyToManyField('Skill')
    assigned_to = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.task_name

class Asset(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    asset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    skills = models.ManyToManyField('Skill')
    teams = models.ManyToManyField('Team', blank=True)
    work_days = models.ManyToManyField('DayOfWeek', blank=True)  # Use ManyToManyField for work_days
    normal_work_week = models.IntegerField()

    def __str__(self):
        return self.name

class Skill(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    skill_id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.skill_name

class Team(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.team_name
