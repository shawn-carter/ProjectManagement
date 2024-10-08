from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget
from .models import Project, Asset, Category, ProjectStatus, Task, TaskStatus, Skill, Stakeholder, Risk, Assumption, Issue, Dependency
from .widgets import DurationPickerWidget  # Import the custom widget

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
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': DurationPickerWidget(attrs={'class': 'form-control'}),  # Use the custom widget here
            'skills_required': forms.CheckboxSelectMultiple(attrs={'style': 'columns: 2;'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)  # Remove 'project' argument from kwargs
        super().__init__(*args, **kwargs)

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['risk_details', 'impact', 'probability']  # Specify the fields to include in the form
        labels = {
            'risk_details': 'Risk Details',
            'impact': 'Impact',
            'probability': 'Probability',
        }
        widgets = {
            'risk_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'impact': forms.Select(attrs={'class': 'form-select'}),
            'probability': forms.Select(attrs={'class': 'form-select'}),
        }

class AssumptionForm(forms.ModelForm):
    class Meta:
        model = Assumption
        fields = ['assumption_details']  # Include only the necessary fields
        labels = {
            'assumption_details': 'Assumption Details',
        }
        widgets = {
            'assumption_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['issue_details']  # Only include fields present in the model
        labels = {
            'issue_details': 'Issue Details',
        }
        widgets = {
            'issue_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DependencyForm(forms.ModelForm):
    class Meta:
        model = Dependency
        fields = ['dependency_details']
        labels = {
            'dependency_details': 'Dependency Details',
        }
        widgets = {
            'dependency_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'interest_level', 'influence_level', 'email']
        labels = {
            'name': 'Stakeholder Name',
            'interest_level': 'Interest Level',
            'influence_level': 'Influence Level',
            'email': 'Email Address (Optional)',
        }
        widgets = {
            'interest_level': forms.Select(attrs={'class': 'form-control'}),
            'influence_level': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }