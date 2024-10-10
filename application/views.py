from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView, DetailView,CreateView, UpdateView
from django.urls import reverse_lazy,reverse

from .models import Project, ProjectStatus, Task, Stakeholder, Risk, Issue, Assumption, Dependency, Comment
from .forms import ProjectForm, ProjectUpdateForm, CreateTaskForm, StakeholderForm, RiskForm, IssueForm, AssumptionForm, DependencyForm, EditTaskForm, TaskCompleteForm

# Home page view
@login_required  # Optional: Use this decorator if you want to restrict access to authenticated users only
def home(request):
    return render(request, 'home.html')

class ProjectCreateView(PermissionRequiredMixin,CreateView):
    permission_required = 'application.add_project'  # Only allow users with 'add_project' permission
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('project_list')

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a new project.")
        # Redirect to a different view or URL
        return redirect(reverse_lazy('project_list'))  # Redirect to the project list view

    def form_valid(self, form):
        # Debugging statements
        print(f"Form is valid: {form.is_valid()}")
        print(f"Form errors: {form.errors}")

        # Set the default status as 'New' when the form is valid
        default_status = ProjectStatus.objects.filter(status_name__iexact='New').first()
        form.instance.project_status = default_status
        return super().form_valid(form)

    def form_invalid(self, form):
        # Additional debug statement to check why the form is invalid
        print(f"Form is invalid: {form.is_valid()}")
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)

class ProjectEditView(LoginRequiredMixin,DetailView):
    """
    View for displaying the details of a project.
    Inherits from LoginRequiredMixin and DetailView.
    Attributes:
        model (Project): The model class for the view.
        template_name (str): The name of the template to be used for rendering the view.
        context_object_name (str): The name of the variable to be used in the template for the project object.
    Methods:
        get_context_data(**kwargs): Overrides the get_context_data method of the parent class to add the form to the context.
        Args:
            **kwargs: Additional keyword arguments.
        Returns:
            dict: The context dictionary with the form added.
    """
    model = Project
    template_name = 'project_edit.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectUpdateForm(instance=self.object)
        return context

class ProjectListView(LoginRequiredMixin,ListView):
    """
    View for displaying a list of active projects.
    Inherits from LoginRequiredMixin and ListView.
    Attributes:
        model (Project): The model to use for the view.
        template_name (str): The name of the template to use for rendering the view.
        context_object_name (str): The name of the context object to use in the template.
    Methods:
        get_queryset(): Returns all active projects (excluding soft-deleted ones) ordered by project name.
    """
    model = Project  # Specify the model
    template_name = 'project_list.html'  # Specify the template to use
    context_object_name = 'projects'  # Name the context object to use in the template

    def get_queryset(self):
        # Return all active projects (excluding soft-deleted ones)
        return Project.objects.filter(deleted=None).order_by('project_name')
 
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'  # Read-only detail view template
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object  # Get the project instance

        # Check if all tasks for this project are completed
        all_tasks_completed = project.task_set.filter(~Q(task_status__status_name='Complete')).count() == 0

        # Pass the 'all_tasks_completed' status to the template
        context['all_tasks_completed'] = all_tasks_completed
        context['comments'] = Comment.objects.filter(content_type__model='project', object_id=self.object.pk)
        return context

class ProjectUpdateView(LoginRequiredMixin,UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = 'project_edit.html'  # Edit form template
    context_object_name = 'project'

    def form_valid(self, form):
        form.save()
        return redirect(reverse('project_detail', kwargs={'pk': self.object.pk}))

class ProjectTaskView(LoginRequiredMixin,DetailView):
    model = Project
    template_name = 'project_task_list.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)
        # Add the list of tasks associated with the project to the context
        context['tasks'] = Task.objects.filter(project=self.object)
        return context


# Task Views

class TaskCreateView(PermissionRequiredMixin, CreateView):
    model = Task
    form_class = CreateTaskForm
    template_name = 'project_task_create.html'

    permission_required = 'application.add_task'  # Only allow users with 'add_task' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a new task.")
        # Redirect to a different view or URL
        return redirect('project_taskview', pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the project instance to the form for context if needed
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        # Assign the project instance to the task instance before saving
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        
        # Set has_dependency to True if a dependant_task is selected
        if form.cleaned_data['dependant_task']:
            form.instance.has_dependency = True

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect back to the project task view upon successful form submission
        return reverse('project_taskview', kwargs={'pk': self.kwargs['pk']})

class TaskUpdateView(PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = EditTaskForm
    template_name = 'project_task_edit.html'

    permission_required = 'application.edit_task'  # Only allow users with 'add_task' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to edit this task.")
        # Redirect to the project task list view
        return redirect('project_taskview', pk=self.kwargs['project_pk'])

    def dispatch(self, request, *args, **kwargs):
        # Get the current task object
        task = self.get_object()

        # Check if the task is already completed (assuming status ID 3 is 'Completed')
        if task.task_status.pk == 3:  
            # Show an error message and redirect to the task detail page
            messages.error(request, "This task is already completed and cannot be edited.")
            return redirect('task_detail', project_pk=task.project.pk, pk=task.pk)

        # Allow normal processing if the task is not completed
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the project instance to the form for context if needed
        task_instance = self.get_object()
        kwargs['project'] = task_instance.project
        return kwargs

    def form_valid(self, form):
        # Set has_dependency to True if a dependant_task is selected, otherwise False
        if form.cleaned_data['dependant_task']:
            form.instance.has_dependency = True
        else:
            form.instance.has_dependency = False

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the project object to the context
        context['project'] = self.get_object().project
        return context

    def get_success_url(self):
        # Redirect back to the project task list upon successful form submission
        return reverse('project_taskview', kwargs={'pk': self.kwargs['project_pk']})

class TaskDetailView(LoginRequiredMixin,DetailView):
    model = Task
    template_name = 'project_task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Task)
        # Filter comments by the content_type and object_id (task id)
        context['comments'] = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)
        return context

class TaskCompleteView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskCompleteForm
    template_name = 'project_task_complete.html'

    def form_valid(self, form):
        # Set the task status to "Completed" (status ID 3)
        task = form.save(commit=False)
        task.task_status_id = 3
        task.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context

    def get_success_url(self):
        return reverse('task_detail', kwargs={'project_pk': self.kwargs['project_pk'], 'pk': self.kwargs['pk']})

# Views for listing Risks, Assumptions, Issues, and Dependencies

class RiskListView(LoginRequiredMixin,ListView):
    model = Risk
    template_name = 'project_risks_list.html'
    context_object_name = 'risks'  # Updated context name to refer to the risks list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the project based on the pk passed in the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Add the project and its associated risks to the context
        context['project'] = project
        context['risks'] = Risk.objects.filter(project=project)
        return context
    
class AssumptionListView(LoginRequiredMixin,ListView):
    model = Assumption
    template_name = 'project_assumptions_list.html'
    context_object_name = 'assumptions'  # Updated context name to refer to the assumption list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the project based on the pk passed in the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Add the project and its associated risks to the context
        context['project'] = project
        context['assumptions'] = Assumption.objects.filter(project=project)
        return context

class IssueListView(LoginRequiredMixin,ListView):
    model = Issue
    template_name = 'project_issues_list.html'
    context_object_name = 'issues'  # Updated context name to refer to the issues list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the project based on the pk passed in the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Add the project and its associated risks to the context
        context['project'] = project
        context['issues'] = Issue.objects.filter(project=project)
        return context

class DependencyListView(LoginRequiredMixin,ListView):
    model = Dependency
    template_name = 'project_dependencies_list.html'
    context_object_name = 'dependencies'  # Updated context name to refer to the dependencies list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the project based on the pk passed in the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Add the project and its associated risks to the context
        context['project'] = project
        context['dependencies'] = Dependency.objects.filter(project=project)
        return context
    
class StakeholderListView(LoginRequiredMixin,ListView):
    model = Stakeholder
    template_name = 'project_stakeholders_list.html'
    context_object_name = 'stakeholders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        stakeholders = Stakeholder.objects.filter(project=project)

        # Collect emails from stakeholders who have a non-empty email field
        stakeholder_emails = [stakeholder.email for stakeholder in stakeholders if stakeholder.email]

        context['project'] = project
        context['stakeholders'] = stakeholders
        context['stakeholder_emails'] = stakeholder_emails  # Pass the list of emails
        return context

# Create views for adding new entries
class RiskCreateView(LoginRequiredMixin,CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'project_risk_add.html'

    def form_valid(self, form):
        # Assign the project instance to the risk instance before saving
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user  # Set the user who created this entry
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect back to the project risk list view upon successful form submission
        return reverse_lazy('risk_list', kwargs={'pk': self.kwargs['pk']})

class AssumptionCreateView(LoginRequiredMixin,CreateView):
    model = Assumption
    form_class = AssumptionForm
    template_name = 'project_assumption_add.html'

    def form_valid(self, form):
        # Assign the project instance to the assumption instance before saving
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user  # Set the user who created this entry
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect back to the project assumption list view upon successful form submission
        return reverse_lazy('assumption_list', kwargs={'pk': self.kwargs['pk']})

class IssueCreateView(LoginRequiredMixin,CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_issue_add.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Ensure project is in the context
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Make sure 'pk' is passed correctly in reverse_lazy
        return reverse_lazy('issue_list', kwargs={'pk': self.kwargs['pk']})

class DependencyCreateView(LoginRequiredMixin,CreateView):
    model = Dependency
    form_class = DependencyForm
    template_name = 'project_dependency_add.html'

    def form_valid(self, form):
        # Associate the dependency with the specific project
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Ensure project is passed to the template context
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect back to the dependency list view after successful creation
        return reverse_lazy('dependency_list', kwargs={'pk': self.kwargs['pk']})
    
class StakeholderCreateView(LoginRequiredMixin,CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'project_stakeholder_add.html'

    def form_valid(self, form):
        # Associate the stakeholder with the project and the user who created it
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Pass the project to the template context
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect to the stakeholder list view upon successful creation
        return reverse_lazy('stakeholder_list', kwargs={'pk': self.kwargs['pk']})

# Update views for editing existing entries

class RiskUpdateView(LoginRequiredMixin,UpdateView):
    model = Risk
    form_class = RiskForm
    template_name = 'project_risk_add.html'
    context_object_name = 'risk'

    def get_object(self, queryset=None):
        return get_object_or_404(Risk, pk=self.kwargs['risk_pk'], project__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['project'] = project  # Ensure project is added to context
        return context

    def get_success_url(self):
        # Pass the correct project ID in reverse_lazy
        return reverse_lazy('risk_list', kwargs={'pk': self.kwargs['pk']})

class AssumptionUpdateView(LoginRequiredMixin,UpdateView):
    model = Assumption
    form_class = AssumptionForm
    template_name = 'project_assumption_add.html'  # Reusing the existing template

    def get_object(self, queryset=None):
        return get_object_or_404(Assumption, pk=self.kwargs['assumption_pk'], project__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['project'] = project  # Ensure project is added to context
        return context

    def get_success_url(self):
        return reverse_lazy('assumption_list', kwargs={'pk': self.kwargs['pk']})

class IssueUpdateView(LoginRequiredMixin,UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_issue_add.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Issue, pk=self.kwargs['issue_pk'], project__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['project'] = project  # Ensure project is added to context
        return context

    def get_success_url(self):
        return reverse_lazy('issue_list', kwargs={'pk': self.kwargs['pk']})

class DependencyUpdateView(LoginRequiredMixin,UpdateView):
    model = Dependency
    form_class = DependencyForm
    template_name = 'project_dependency_add.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Dependency, pk=self.kwargs['dependency_pk'], project__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['project'] = project  # Ensure project is added to context
        return context

    def get_success_url(self):
        return reverse_lazy('dependency_list', kwargs={'pk': self.kwargs['pk']})

class StakeholderUpdateView(LoginRequiredMixin,UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'project_stakeholder_add.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Stakeholder, pk=self.kwargs['stakeholder_pk'], project__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['project'] = project  # Ensure project is added to context
        return context

    def get_success_url(self):
        return reverse_lazy('stakeholder_list', kwargs={'pk': self.kwargs['pk']})

# Detail Views

class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    template_name = 'project_risk_detail.html'
    context_object_name = 'risk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the comments related to the risk
        context['comments'] = Comment.objects.filter(content_type__model='risk', object_id=self.object.pk)
        return context

class AssumptionDetailView(LoginRequiredMixin, DetailView):
    model = Assumption
    template_name = 'project_assumption_detail.html'
    context_object_name = 'assumption'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project  # Include the project in the context
        context['comments'] = Comment.objects.filter(content_type__model='assumption', object_id=self.object.pk)
        return context

class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'project_issue_detail.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add comments related to the issue, using the content type and object ID
        context['comments'] = Comment.objects.filter(content_type__model='issue', object_id=self.object.pk)
        return context

class DependencyDetailView(LoginRequiredMixin, DetailView):
    model = Dependency
    template_name = 'project_dependency_detail.html'
    context_object_name = 'dependency'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add comments related to the dependency, using the content type and object ID
        context['comments'] = Comment.objects.filter(content_type__model='dependency', object_id=self.object.pk)
        return context

@login_required    
def project_calendar(request):
    """Renders the calendar page with project events."""
    return render(request, 'project_calendar.html')

def project_events(request):
    """Returns a JSON response with project events for FullCalendar."""
    projects = Project.objects.all().order_by('planned_start_date')
    events = []
    for project in projects:
        start_date = project.actual_start_date if project.actual_start_date else project.planned_start_date
        end_date = project.actual_end_date if project.actual_end_date else project.revised_target_end_date or project.original_target_end_date

        # Skip projects that don't have a start or end date
        if start_date and end_date:
            # Determine the background colour
            background_color = get_color_for_project(project.pk)
            
            # Set the text colour based on the background colour
            text_color = '#000000' if background_color in ['#FFFF00', '#00FFFF', '#FFFFFF','#00FF00'] else '#FFFFFF'
            
            events.append({
                'title': project.project_name,
                'start': start_date.strftime('%Y-%m-%d'),
                'end': (end_date + timedelta(days=1)).strftime('%Y-%m-%d'),  # Add one day to include end date
                'url': reverse('project_detail', args=[project.pk]),  # Link to project detail page
                'color': background_color,  # Background colour for the event
                'textColor': text_color,  # Text colour based on the background
                'allDay': True,
            })
    return JsonResponse(events, safe=False)

def get_color_for_project(project_id):
    """Generate a color based on the project ID."""
    # Predefined list of colors to cycle through
    colors = ['#0000FF', '#00FF00', '#FF0000', '#00FFFF', '#FF00FF', '#FFFF00']
    return colors[project_id % len(colors)]  # Cycle through the list based on the project ID

class ProjectTaskCalendarView(LoginRequiredMixin,DetailView):
    model = Project
    template_name = 'project_task_calendar.html'  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # Filter tasks for the current project
        tasks = Task.objects.filter(project=project)

        # Prepare task data for FullCalendar
        task_events = []
        colors = {
            1: '#808080',  # Low (grey)
            2: '#008000',  # Medium (green)
            3: '#FFFF00',  # High (yellow)
            4: '#FFA500',  # Critical (orange)
            5: '#FF0000',  # Urgent (red)
        }

        for task in tasks:
            # Determine start and end dates
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.actual_end_date or task.planned_end_date

            if start_date and end_date:
                task_events.append({
                    'title': task.task_name,
                    'start': str(start_date),
                    'end': str(end_date + timedelta(days=1)),  # FullCalendar uses exclusive end dates
                    'backgroundColor': colors.get(task.priority, '#808080'),  # Fallback to grey
                    'borderColor': colors.get(task.priority, '#808080'),
                    'textColor': '#000000',
                    'url': reverse('task_detail', kwargs={'project_pk': project.pk, 'pk': task.pk}),
                })

            # Add a separate event for the due date if it exists
            if task.due_date:
                task_events.append({
                    'title': f'{task.task_name} (Due)',
                    'start': str(task.due_date),
                    'end': str(task.due_date),
                    'backgroundColor': '#FF6347',  # Tomato color for due date
                    'borderColor': '#FF6347',
                    'url': reverse('task_detail', kwargs={'project_pk': project.pk, 'pk': task.pk}),
                })

        context['task_events'] = task_events
        return context
    
@login_required
def add_comment(request, content_type, object_id):
    """View to handle adding a comment via a POST request."""
    if request.method == 'POST':
        content_type_obj = get_object_or_404(ContentType, model=content_type)
        related_object = content_type_obj.get_object_for_this_type(id=object_id)

        # Create a new comment
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(
                user=request.user,
                content_object=related_object,
                comment_text=comment_text
            )
            messages.success(request, 'Comment added successfully.')
        else:
            messages.error(request, 'Comment text cannot be empty.')

        # Redirect back to the detail view of the commented object
        return redirect(related_object.get_absolute_url())  # Ensure `get_absolute_url` is defined in models