from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from safedelete.models import SafeDeleteModel, SOFT_DELETE, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords

# We can use Category for Department or Category
class Category(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE  # Configure the soft delete policy
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.category_name

# These can be defined based on the requirements
class ProjectStatus(SafeDeleteModel):
    _safedelete_policy =SOFT_DELETE
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)  # Ensure uniqueness
    description = models.TextField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.status_name

# Same - these can be defined rather than hard coded
class TaskStatus(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)  # Ensure uniqueness
    description = models.TextField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.status_name

# Used this way instead of choice, so that we can filter easier when looking for assets
class DayOfWeek(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    day_name = models.CharField(max_length=10, unique=True)  # Monday, Tuesday, etc.
    abbreviation = models.CharField(max_length=3, unique=True)  # Mon, Tue, etc.
    history = HistoricalRecords()

    def __str__(self):
        return self.day_name

# The Project Details
class Project(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50, unique=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    project_description = models.TextField(null=True)
    planned_start_date = models.DateField(null=True)
    original_target_end_date = models.DateField(null=True)
    revised_target_end_date = models.DateField(null=True)
    actual_start_date = models.DateField(null=True)
    actual_end_date = models.DateField(null=True)
    project_owner = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True)
    project_status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')], null=True)
    halo_ref = models.IntegerField(null=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.project_name
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'project_id': self.id})

# The Task Details
class Task(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=50)
    task_details = models.TextField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_status = models.ForeignKey(TaskStatus, on_delete=models.PROTECT, null=True, default=1)  # Default to 'Unassigned' (assuming 'Unassigned' has ID 1)
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical'), (5, 'Urgent')])
    planned_start_date = models.DateField(blank=True, null=True)  # Non-mandatory
    planned_end_date = models.DateField(blank=True, null=True)  # Non-mandatory
    actual_start_date = models.DateField(blank=True, null=True)
    actual_end_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)  # Non-mandatory
    estimated_time_to_complete = models.DurationField(blank=True, null=True)  # Non-mandatory
    actual_time_to_complete = models.DurationField(blank=True, null=True)  # Non-mandatory
    has_dependency = models.BooleanField(default=False)
    dependant_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    delay_reason = models.TextField(blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    skills_required = models.ManyToManyField('Skill')
    assigned_to = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True, blank=True)  # Non-mandatory
    halo_ref = models.IntegerField(null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.task_name

    def get_absolute_url(self):
        """Return the URL to access the task's detail view."""
        return reverse('task_detail', kwargs={'project_id': self.project.pk, 'task_id': self.pk})
    
# The Asset Details - Assets have a Team and Skills
class Asset(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    asset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    skills = models.ManyToManyField('Skill')
    teams = models.ManyToManyField('Team', blank=True)
    work_days = models.ManyToManyField('DayOfWeek', blank=True)
    normal_work_week = models.IntegerField()
    history = HistoricalRecords()

    def __str__(self):
        return self.name

# The Skill Attributes
class Skill(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    skill_id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=50, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.skill_name

# Holds the Team Name for Assets
class Team(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=50, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.team_name

# Project Management

class Stakeholder(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    interest_level = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    influence_level = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    email = models.EmailField(blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Stakeholder'
        verbose_name_plural = 'Stakeholders'

    def __str__(self):
        return f"Stakeholder: {self.name}"

# RAID Stuff (Suggested by Colin)

class Risk(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    risk_details = models.TextField()
    impact = models.IntegerField(choices=[(1, 'Insignificant'), (2, 'Minor'), (3, 'Significant'), (4, 'Major'), (5, 'Servere')])
    probability = models.IntegerField(choices=[(1, 'Rare'), (2, 'Unlikely'), (3, 'Moderate'),(4,'Likely'),(5,'Almost Certain')])
    risk_score = models.IntegerField(null=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=[(1, 'Open'), (2, 'In Progress'), (3, 'Closed')])
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('risk_detail', kwargs={'project_id': self.project.pk, 'risk_id': self.pk})

    def save(self, *args, **kwargs):
        # Calculate risk score based on probability and impact
        self.risk_score = self.probability * self.impact
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Risk: {self.risk_details[:50]}"
    
class Assumption(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assumption_details = models.TextField()
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=[(1, 'Open'), (2, 'In Progress'), (3, 'Closed')])
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Assumption'
        verbose_name_plural = 'Assumptions'

    def __str__(self):
        return f"Assumption: {self.assumption_details[:50]}"

    # Add this method to specify the URL for each assumption's detail view
    def get_absolute_url(self):
        return reverse('assumption_detail', kwargs={'project_id': self.project.pk, 'assumption_id': self.pk})

class Issue(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    issue_details = models.TextField()
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=[(1, 'Open'), (2, 'In Progress'), (3, 'Closed')])
    history = HistoricalRecords()

    def __str__(self):
        return f"Issue: {self.issue_details[:50]}"

    def get_absolute_url(self):
        return reverse('issue_detail', kwargs={'project_id': self.project.pk, 'issue_id': self.pk})

class Dependency(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    dependency_details = models.TextField()
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=[(1, 'Open'), (2, 'In Progress'), (3, 'Closed')])
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('dependency_detail', kwargs={'project_id': self.project.pk, 'dependency_id': self.pk})

    def __str__(self):
        return f"Dependency: {self.dependency_details[:50]}"

# Comment Class
class Comment(SafeDeleteModel):  # Using SafeDelete for soft delete functionality
    _safedelete_policy = SOFT_DELETE

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who made the comment
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Model type (Task, Project, etc.)
    object_id = models.PositiveIntegerField()  # ID of the specific object
    content_object = GenericForeignKey('content_type', 'object_id')  # Link to the related object
    comment_text = models.TextField()  # The comment text
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated_datetime = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Comment by {self.user} on {self.content_object}"
    
class Attachment(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

class Attachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='media/')
    description = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255)  # This should store the actual file name
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    class Meta:
        ordering = ['-uploaded_at']
