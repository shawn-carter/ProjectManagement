from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, Fieldset
from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget
from .models import Project, Asset, Category, Task, Skill, Stakeholder, Risk, Assumption, Issue, Dependency, Attachment
from .widgets import DurationPickerWidget  # Import the custom widget
from django.db.models.functions import Coalesce, Concat

# Helper Functions

def has_circular_dependency(task, prereq_task):
    """
    Checks if adding the given prereq_task would create a circular dependency.
    """
    visited = set()
    current = prereq_task

    while current is not None:
        if current == task:
            return True
        if current.id in visited:
            break  # To avoid being stuck in an infinite loop
        visited.add(current.id)
        current = current.prereq_task

    return False


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

        # Crispy Forms Configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('project_name', css_class='form-control'),
            Row(
                Column(Field('planned_start_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('original_target_end_date', css_class='form-control'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column(Field('project_owner', css_class='form-select'), css_class='col-md-6'),
                Column(Field('priority', css_class='form-select'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Project', css_class='btn btn-primary')
        )

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        planned_start_date = cleaned_data.get("planned_start_date")
        original_target_end_date = cleaned_data.get("original_target_end_date")

        # Check if both dates are provided and end date is not before start date
        if planned_start_date and original_target_end_date and original_target_end_date < planned_start_date:
            self.add_error('original_target_end_date', 'End date cannot be earlier than the start date.')

        return cleaned_data

# Form for Editing Project Details    
class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name',
            'project_description',
            'planned_start_date',
            'original_target_end_date',
            'revised_target_end_date',
            'halo_ref',
            'actual_start_date',
            'actual_end_date',
            'project_owner',
            'project_status',
            'category',
            'priority',
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'readonly': True}),
            'original_target_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'readonly': True}),
            'revised_target_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_owner': forms.Select(attrs={'class': 'form-select'}),
            'project_status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields not mandatory
        self.fields['revised_target_end_date'].required = False
        self.fields['actual_start_date'].required = False
        self.fields['actual_end_date'].required = False

        # Remove "Closed" from the choices for project_status
        status_choices_without_closed = [choice for choice in Project.STATUS_CHOICES if choice[0] != 7]
        self.fields['project_status'].choices = status_choices_without_closed

        # Set initial values for read-only fields
        if self.instance and self.instance.pk:
            self.fields['planned_start_date'].initial = self.instance.planned_start_date
            self.fields['original_target_end_date'].initial = self.instance.original_target_end_date

        # Crispy Forms Configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('project_name', css_class='form-control'),
            Field('project_description', css_class='form-control'),
            Row(
                Column(Field('planned_start_date', css_class='form-control', readonly=True), css_class='col-md-6'),
                Column(Field('original_target_end_date', css_class='form-control', readonly=True), css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column(Field('halo_ref', css_class='form-control'), css_class='col-md-6'),
                Column(Field('revised_target_end_date', css_class='form-control'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column(Field('actual_start_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('actual_end_date', css_class='form-control'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column(Field('project_status', css_class='form-select'), css_class='col-md-6'),
                Column(Field('category', css_class='form-select'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column(Field('project_owner', css_class='form-select'), css_class='col-md-6'),
                Column(Field('priority', css_class='form-select'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Project', css_class='btn btn-primary')
        )

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        Prevent changes to the planned start date and original target end date.
        """
        cleaned_data = super().clean()
        revised_target_end_date = cleaned_data.get("revised_target_end_date")
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")
        planned_start_date = cleaned_data.get("planned_start_date")
        original_target_end_date = cleaned_data.get("original_target_end_date")

        # Check if revised target end date is earlier than actual start date
        if revised_target_end_date and actual_start_date and revised_target_end_date < actual_start_date:
            self.add_error('revised_target_end_date', 'Revised end date cannot be earlier than the actual start date.')

        # Validate actual dates
        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            self.add_error('actual_end_date', 'Actual end date cannot be earlier than the actual start date.')

        # Ensure planned start date and original target end date cannot be changed
        if self.instance and self.instance.pk:
            if planned_start_date != self.instance.planned_start_date:
                self.add_error('planned_start_date', 'Planned start date cannot be changed once set.')
            if original_target_end_date != self.instance.original_target_end_date:
                self.add_error('original_target_end_date', 'Original target end date cannot be changed once set.')

        return cleaned_data
    
class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'task_name', 'task_details', 'priority',
            'prereq_task',  # Move prereq_task up in the list
            'planned_start_date', 'planned_end_date', 'due_date',
            'estimated_time_to_complete', 'skills_required', 'assigned_to',
            'halo_ref',
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'task_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'prereq_task': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-group'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project:
            # Annotate tasks with display_start_date and display_end_date
            tasks_queryset = Task.objects.filter(project=self.project).annotate(
                annotated_start_date=Coalesce('actual_start_date', 'planned_start_date'),
                annotated_end_date=Coalesce('actual_end_date', 'planned_end_date')
            )
            
            # Update the display of the prerequisite tasks to include the dates
            choices = [
                (task.id, f"{task.task_name} (Start: {task.annotated_start_date.strftime('%d/%m/%Y') if task.annotated_start_date else 'N/A'}, End: {task.annotated_end_date.strftime('%d/%m/%Y') if task.annotated_end_date else 'N/A'})")
                for task in tasks_queryset
            ]

            self.fields['prereq_task'].choices = [('', '---------')] + choices

        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'task_name',
            'task_details',
            Field('prereq_task', css_class='form-select'),  # Move prereq_task field to the top of the form layout
            Row(
                Column(Field('planned_start_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('planned_end_date', css_class='form-control'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Div(id='date-warning', css_class='alert alert-danger d-none'),  # Date message placeholder
            Row(
                Column(Field('due_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('halo_ref', css_class='form-control'), css_class='col-md-6'),
            ),
            Row(
                Column(Field('priority', css_class='form-select'), css_class='col-md-6'),
                Column(Field('assigned_to', css_class='form-select'), css_class='col-md-6'),
                css_class='form-row'
            ),
            Field('estimated_time_to_complete', css_class='form-control'),
            Field('skills_required', css_class='checkbox-group'),
            Div(id='no-assets-warning', css_class='alert alert-danger d-none'),  # Warning message placeholder
            Submit('submit', 'Save Task', css_class='btn btn-success')
        )
    
    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        planned_start_date = cleaned_data.get("planned_start_date")
        planned_end_date = cleaned_data.get("planned_end_date")
        due_date = cleaned_data.get("due_date")

        # Check if both dates are provided and end date is not before start date
        if planned_start_date and planned_end_date and planned_end_date < planned_start_date:
            self.add_error('planned_end_date', 'End date cannot be earlier than the start date.')

        if planned_start_date and due_date and due_date < planned_start_date:
            self.add_error('due_date', 'Due date cannot be earlier than the start date.')

        return cleaned_data

class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'task_name', 'task_details', 'priority',
            'planned_start_date', 'planned_end_date', 'due_date', 'actual_start_date', 'actual_end_date',
            'estimated_time_to_complete', 'skills_required', 'assigned_to',
            'prereq_task', 'delay_reason', 'halo_ref',
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'task_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'prereq_task': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-group'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            
            'delay_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        assets_queryset = kwargs.pop('assets_queryset', None)
        super().__init__(*args, **kwargs)

        # Set "Unassigned" as the default option for "assigned_to"
        if assets_queryset is not None:
            self.fields['assigned_to'].queryset = assets_queryset
        else:
            self.fields['assigned_to'].queryset = Asset.objects.none()
        self.fields['assigned_to'].empty_label = "Unassigned"

        if self.project:
            # Annotate tasks with display_start_date and display_end_date
            tasks_queryset = Task.objects.filter(project=self.project).exclude(pk=self.instance.pk).annotate(
                annotated_start_date=Coalesce('actual_start_date', 'planned_start_date'),
                annotated_end_date=Coalesce('actual_end_date', 'planned_end_date')
            )
            
            # Update the display of the prerequisite tasks to include the dates
            choices = [
                (task.id, f"{task.task_name} (Start: {task.annotated_start_date.strftime('%d/%m/%Y') if task.annotated_start_date else 'N/A'}, End: {task.annotated_end_date.strftime('%d/%m/%Y') if task.annotated_end_date else 'N/A'})")
                for task in tasks_queryset
            ]

            self.fields['prereq_task'].choices = [('', '---------')] + choices

        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'task_name',
            'task_details',
            Field('prereq_task', css_class='form-select'),  # Move prereq_task field to the top of the form layout
            Div(id='dependency-warning', css_class='alert alert-warning d-none'),  # Date message placeholder
            Row(
                Column('planned_start_date', css_class='form-group col-md-6 mb-0'),
                Column('planned_end_date', css_class='form-group col-md-6 mb-0'),
            ),
            Div(id='date-warning', css_class='alert alert-danger d-none'),  # Date message placeholder
            Row(
                Column('due_date', css_class='form-group col-md-6 mb-0'),
                Column('halo_ref', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('priority', css_class='form-group col-md-6 mb-0'),
                Column('assigned_to', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('actual_start_date', css_class='form-group col-md-6 mb-0'),
                Column('estimated_time_to_complete', css_class='form-group col-md-6 mb-0'),
            ),
            'skills_required',
            Div(id='no-assets-warning', css_class='alert alert-danger d-none'),  # Warning message placeholder
            'delay_reason',
            Submit('submit', 'Save Changes', css_class='btn btn-danger')
        )

    def clean(self):
        cleaned_data = super().clean()
        prereq_task = cleaned_data.get('prereq_task')

        # Check for circular dependencies only if a dependant task is set
        if prereq_task:
            if has_circular_dependency(self.instance, prereq_task):
                self.add_error('prereq_task', 'Adding this dependency will create a circular reference.')

        # Other validation logic for date fields as in your current code
        planned_start_date = cleaned_data.get("planned_start_date")
        planned_end_date = cleaned_data.get("planned_end_date")
        due_date = cleaned_data.get("due_date")
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")

        # Check if both dates are provided and end date is not before start date
        if planned_start_date and planned_end_date and planned_end_date < planned_start_date:
            self.add_error('planned_end_date', 'End date cannot be earlier than the start date.')

        if planned_start_date and due_date and due_date < planned_start_date:
            self.add_error('due_date', 'Due date cannot be earlier than the start date.')

        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            self.add_error('actual_end_date', 'End date cannot be earlier than the start date.')

        return cleaned_data

class TaskCompleteForm(forms.ModelForm):
    # Override the actual_time_to_complete to accept hours as float
    actual_time_to_complete = forms.FloatField(
        label='Actual Time to Complete (Hours)',
        min_value=0.1,  # Minimum of 0.1 hours (6 minutes)
        error_messages={
            'min_value': 'Estimated time to complete must be a positive number of hours.'
        },
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter hours'}),
    )
    class Meta:
        model = Task
        fields = ['actual_start_date', 'actual_end_date', 'actual_time_to_complete']
        widgets = {
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
             #'actual_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Enforce that all fields are required in the form
        self.fields['actual_start_date'].required = True
        self.fields['actual_end_date'].required = True
        self.fields['actual_time_to_complete'].required = True

        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('actual_start_date', css_class='form-group col-md-6 mb-0'),
                Column('actual_end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'actual_time_to_complete',
            Submit('submit', 'Confirm Completion', css_class='btn btn-success')
        )

    def clean_actual_time_to_complete(self):
        actual_time = self.cleaned_data.get('actual_time_to_complete')
        if actual_time is not None:
            try:
                hours = float(actual_time)
                if hours <= 0:
                    raise ValidationError("Estimated time to complete must be a positive number of hours.")
                return timedelta(hours=hours)
            except (ValueError, TypeError):
                raise ValidationError("Enter a valid number of hours.")
        raise ValidationError("This field is required.")

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")

        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            self.add_error('actual_end_date', 'End date cannot be earlier than the start date.')

        return cleaned_data

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['risk_details', 'impact', 'probability','status']  # Specify the fields to include in the form
        labels = {
            'risk_details': 'Risk Details',
            'impact': 'Impact',
            'probability': 'Probability',
            'status': 'Status',
        }
        widgets = {
            'risk_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'impact': forms.Select(attrs={'class': 'form-select'}),
            'probability': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class AssumptionForm(forms.ModelForm):
    class Meta:
        model = Assumption
        fields = ['assumption_details', 'status']  # Include only the necessary fields
        labels = {
            'assumption_details': 'Assumption Details',
            'status': 'Status',
        }
        widgets = {
            'assumption_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['issue_details', 'status']  # Only include fields present in the model
        labels = {
            'issue_details': 'Issue Details',
            'status': 'Status',
        }
        widgets = {
            'issue_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class DependencyForm(forms.ModelForm):
    class Meta:
        model = Dependency
        fields = ['dependency_details','status']
        labels = {
            'dependency_details': 'Dependency Details',
            'status': 'Status',
        }
        widgets = {
            'dependency_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
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
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'interest_level': forms.Select(attrs={'class': 'form-select'}),
            'influence_level': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProjectCloseForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['actual_start_date', 'actual_end_date']

        widgets = {
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('actual_start_date', css_class='form-group col-md-6 mb-0'),
                Column('actual_end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Close Project', css_class='btn btn-success mt-3')
        )

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")

        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            self.add_error('actual_end_date', 'End date cannot be earlier than the start date.')

        return cleaned_data
    
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Upload'))