from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, Fieldset
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectDateWidget
from .models import Project, Asset, Category, Task, Skill, Stakeholder, Risk, Assumption, Issue, Dependency, Attachment
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
                Column(Field('revised_target_end_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('halo_ref', css_class='form-control'), css_class='col-md-6'),
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
            'planned_start_date', 'planned_end_date', 'due_date', 
            'estimated_time_to_complete', 'skills_required', 'assigned_to',
            'dependant_task', 'halo_ref',
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'task_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-group'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'dependant_task': forms.Select(attrs={'class': 'form-select'}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # Set "Unassigned" as the default option for "assigned_to"
        self.fields['assigned_to'].queryset = Asset.objects.none()  # Ensure no assets are initially shown
        self.fields['assigned_to'].empty_label = "Unassigned"

        if self.project:
            # Filter dependant_task to only include tasks from the same project
            self.fields['dependant_task'].queryset = Task.objects.filter(project=self.project)

        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'task_name',
            'task_details',
            Row(
                Column(Field('planned_start_date', css_class='form-control'), css_class='col-md-6'),
                Column(Field('planned_end_date', css_class='form-control'), css_class='col-md-6'),
                css_class='form-row'
            ),
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
            Field('dependant_task', css_class='form-select'),
            Submit('submit', 'Save Task', css_class='btn btn-success')
        )



class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'task_name', 'task_details', 'priority',
            'planned_start_date', 'planned_end_date', 'due_date', 'actual_start_date', 'actual_end_date',
            'estimated_time_to_complete', 'skills_required', 'assigned_to',
            'dependant_task', 'delay_reason', 'halo_ref',
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control'}),
            'task_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'planned_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_required': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-group'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'dependant_task': forms.Select(attrs={'class': 'form-select'}),
            'delay_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'halo_ref': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project:
            # Filter dependant_task to only include tasks from the same project
            self.fields['dependant_task'].queryset = Task.objects.filter(
                project=self.instance.project
            ).exclude(pk=self.instance.pk)
        
        # Crispy forms configuration
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'task_name',
            'task_details',
            Row(
                Column('planned_start_date', css_class='form-group col-md-6 mb-0'),
                Column('planned_end_date', css_class='form-group col-md-6 mb-0'),
            ),
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
                Column('actual_end_date', css_class='form-group col-md-6 mb-0'),
            ),
            'estimated_time_to_complete',
            'skills_required',
            'dependant_task',
            'delay_reason',
            Submit('submit', 'Save Changes', css_class='btn btn-danger')
        )

    def clean(self):
        """
        Custom validation to ensure the end date is not before the start date.
        """
        cleaned_data = super().clean()
        planned_start_date = cleaned_data.get("planned_start_date")
        planned_end_date = cleaned_data.get("planned_end_date")

        # Check if both dates are provided and end date is not before start date
        if planned_start_date and planned_end_date and planned_end_date < planned_start_date:
            self.add_error('planned_end_date', 'End date cannot be earlier than the start date.')

        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")
        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            self.add_error('actual_end_date', 'End date cannot be earlier than the start date.')

        return cleaned_data

class TaskCompleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['actual_start_date', 'actual_end_date', 'actual_time_to_complete']
        widgets = {
            'actual_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
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