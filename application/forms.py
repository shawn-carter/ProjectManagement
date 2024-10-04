from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Asset, Category, ProjectStatus, Task, TaskStatus, Skill

# Form for New Project Creation
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'planned_start_date', 'original_target_end_date', 'project_owner', 'priority']
        widgets = {
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'original_target_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_owner': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default project status as 'New'
        default_status = ProjectStatus.objects.filter(status_name__iexact='New').first()
        if default_status:
            self.instance.project_status = default_status

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        planned_start_date = cleaned_data.get("planned_start_date")
        original_target_end_date = cleaned_data.get("original_target_end_date")

        # Check if both dates are provided and end date is not before start date
        if planned_start_date and original_target_end_date and original_target_end_date < planned_start_date:
            raise ValidationError({
                'original_target_end_date': 'End date cannot be earlier than the start date.'
            })

        return cleaned_data

# Form for Editing Project Details    
class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name',
            'project_description',
            'revised_target_end_date',
            'actual_start_date',
            'actual_end_date',
            'project_owner',
            'project_status',
            'category',
            'priority',
            'halo_ref'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'revised_target_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_owner': forms.Select(attrs={'class': 'form-select'}),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    # Make the new fields not mandatory
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['revised_target_end_date'].required = False
        self.fields['actual_start_date'].required = False
        self.fields['actual_end_date'].required = False

# Form for Creating New Project Task
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'task_name',
            'task_details',
            'task_status',
            'priority',
            'planned_start_date',
            'planned_end_date',
            'due_date',
            'estimated_time_to_complete',
            'skills_required',
            'assigned_to',
            'halo_ref'
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'task_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'task_status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': forms.TextInput(attrs={'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # Removed project-based filtering
        super().__init__(*args, **kwargs)
        # Ensure task status dropdown displays all statuses
        self.fields['task_status'].queryset = TaskStatus.objects.all()