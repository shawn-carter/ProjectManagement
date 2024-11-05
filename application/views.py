from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count, When, Case, BooleanField
from django.http import HttpResponse, JsonResponse, FileResponse

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView, DetailView,CreateView, UpdateView, View
from django.urls import reverse_lazy,reverse

from django.shortcuts import redirect

from .models import Project, Task, Stakeholder, Risk, Issue, Assumption, Dependency, Comment, Attachment, Asset, Skill
from .forms import ProjectForm, ProjectUpdateForm, CreateTaskForm, StakeholderForm, RiskForm, IssueForm, AssumptionForm, DependencyForm, EditTaskForm, TaskCompleteForm, ProjectCloseForm, AttachmentForm

import os
import extract_msg  # Library for handling .msg files
import docx2txt  # Library for handling .docx files

from pdfminer.high_level import extract_text

from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage

from django.conf import settings  # Import settings to access MEDIA_ROOT

# Home page view
@login_required
def home(request):
    # Project counts for open and closed using integer IDs for statuses
    projects_open = Project.objects.exclude(project_status=7).count()  # Open Projects (All projects except 'Closed' [7])
    projects_onhold = Project.objects.filter(project_status=4).count()  # Projects with Status ID 4: 'On Hold'
    projects_closed = Project.objects.filter(project_status=7).count()  # Projects with Status ID 7: 'Closed'
    projects_total = Project.objects.count() # All Projects 

    # Task counts for open, completed, and total tasks
    tasks_total = Task.objects.count()
    tasks_open = Task.objects.exclude(task_status=3).count()  # All tasks except 'Completed'
    tasks_completed = Task.objects.filter(task_status=3).count()  # Status ID 3: 'Completed'
    tasks_unassigned = Task.objects.filter(task_status=1).count()  # Status ID 1: 'Unassigned'

    assets_total = Asset.objects.count()
    skills_total = Skill.objects.count()

    context = {
        'projects_total': projects_total,
        'projects_open': projects_open,
        'projects_onhold': projects_onhold,
        'projects_closed': projects_closed,
        'tasks_total': tasks_total,
        'tasks_open': tasks_open,
        'tasks_completed': tasks_completed,
        'tasks_unassigned': tasks_unassigned,
        'assets_total': assets_total,
        'skills_total': skills_total,
    }
    return render(request, 'home.html', context)


# Project Views
class ProjectCreateView(PermissionRequiredMixin,CreateView):
    permission_required = 'application.add_project'  # Only allow users with 'add_project' permission
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('all_projects')

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a new project.")
        # Redirect to a different view or URL
        return redirect(reverse_lazy('all_projects'))  # Redirect to the project list view

class ProjectUpdateView(PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = 'project_edit.html'  # Edit form template
    context_object_name = 'project'
    permission_required = 'application.change_project'  # Only allow users with 'change_project' permission

    def get_object(self):
        # Retrieve the project object using project_id instead of pk
        project_id = self.kwargs.get('project_id')    
        return get_object_or_404(Project, id=project_id)

    def handle_no_permission(self):
        # Retrieve the project ID from kwargs
        project_id = self.kwargs.get('project_id')
        # Add a custom error message
        messages.error(self.request, "You do not have permission to edit this project.")
        # Redirect to the project detail view
        return redirect(reverse('project_detail', kwargs={'project_id': project_id}))  # Redirect to the project detail view

    def dispatch(self, request, *args, **kwargs):
        # Check if the project is closed
        project = self.get_object()
        if project.project_status == 7:  # Status ID 7 represents "Closed"
            messages.error(request, "This project is closed and cannot be edited.")
            return redirect(reverse_lazy('all_projects'))

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect(reverse('project_detail', kwargs={'project_id': self.object.pk}))

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Determine the type of projects based on the URL route name
        route_name = self.request.resolver_match.url_name

        if route_name == 'open_project_list':
            # Filter for open projects (exclude closed projects) and order by priority (descending) and project name
            projects = Project.objects.filter(deleted=None).exclude(project_status=7).order_by('-priority', '-planned_start_date')
        elif route_name == 'closed_project_list':
            # Filter for closed projects and order by priority (descending) and project name
            projects = Project.objects.filter(project_status=7, deleted=None).order_by('-priority', '-planned_start_date')
        else:
            # Default to all projects and order by priority (descending) and project name
            projects = Project.objects.filter(deleted=None).order_by('-priority', '-planned_start_date')

        return projects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_name = self.request.resolver_match.url_name

        if route_name == 'open_project_list':
            context['title'] = "Open Projects"
        elif route_name == 'closed_project_list':
            context['title'] = "Closed Projects"
        else:
            context['title'] = "All Projects"

        return context
 
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'  # Read-only detail view template
    context_object_name = 'project'

    def get_object(self):
        # Retrieve the project object using project_id instead of pk
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Project, id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object  # Get the project instance

        # Check if all tasks for this project are completed
        # Use the corresponding status ID for 'Completed', which is assumed to be 3
        all_tasks_completed = project.task_set.filter(~Q(task_status=3)).count() == 0

        # Pass the 'all_tasks_completed' status to the template
        context['all_tasks_completed'] = all_tasks_completed
        context['comments'] = Comment.objects.filter(content_type__model='project', object_id=self.object.pk)
        return context

class ProjectCloseView(PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectCloseForm
    template_name = 'project_close.html'
    permission_required = 'application.change_project'  # Only allow users with 'change_project' permission

    def get_object(self, queryset=None):
        # Retrieve the project object using project_id instead of pk
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Project, id=project_id)

    def handle_no_permission(self):
        # Retrieve the project ID from kwargs
        project_id = self.kwargs.get('project_id')
        # Add a custom error message
        messages.error(self.request, "You do not have permission to close this project.")
        # Redirect to the project detail view
        return redirect(reverse('project_detail', kwargs={'project_id': project_id}))  # Redirect to the project detail view

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = self.get_object()

        # Check if the project is already closed
        if project.project_status == 7:  # Status ID 7 represents "Closed"
            messages.error(request, "This project is already closed.")
            return redirect('project_detail', project_id=project.id)

        # Check if there are any incomplete tasks for this project
        incomplete_tasks = project.task_set.filter(task_status__in=[1, 2])  # 1 = Unassigned, 2 = Assigned

        if incomplete_tasks.exists():
            # Redirect back to project detail page with an error message if there are incomplete tasks
            messages.error(request, "Project cannot be closed until all tasks are completed.")
            return redirect('project_detail', project_id=project.id)

        # Proceed with the regular dispatch if all tasks are completed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Update project status to closed
        project = form.save(commit=False)
        project.project_status = 7  # Assuming status ID 7 is 'Closed'
        project.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project_detail', kwargs={'project_id': self.object.pk})

# Task Views
class TaskCreateView(PermissionRequiredMixin, CreateView):
    model = Task
    form_class = CreateTaskForm
    template_name = 'project_task_create.html'
    permission_required = 'application.add_task'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to create a new task.")
        return redirect('project_taskview', project_id=self.kwargs['project_id'])

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new tasks cannot be added.")
            return redirect('project_taskview', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Get filtered assets from session if available
        filtered_assets = self.request.session.get('filtered_assets', None)

        if filtered_assets:
            # Filter the assets by the IDs stored in session
            form.fields['assigned_to'].queryset = Asset.objects.filter(asset_id__in=filtered_assets)
        else:
            # If no filtering was applied, show all assets
            form.fields['assigned_to'].queryset = Asset.objects.all()

        return form

    def get_initial(self):
        initial = super().get_initial()
        # Get the 'start_date' from the query parameters and set it as the initial value
        start_date = self.request.GET.get('start_date')
        if start_date:
            initial['planned_start_date'] = start_date
        return initial

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse('project_taskview', kwargs={'project_id': self.kwargs['project_id']})

class TaskUpdateView(PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = EditTaskForm
    template_name = 'project_task_edit.html'
    permission_required = 'application.change_task'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to edit this task.")
        return redirect('task_detail', project_id=self.kwargs['project_id'], task_id=self.kwargs['task_id'])

    def get_object(self):
        # Use project_id and task_id to get the task object
        project_id = self.kwargs.get('project_id')
        task_id = self.kwargs.get('task_id')
        return get_object_or_404(Task, id=task_id, project_id=project_id)

    def dispatch(self, request, *args, **kwargs):
        # Get the project and task objects
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        task = self.get_object()

        # Check if the project is closed
        if project.project_status == 7:  # Status ID 7 is "Closed"
            messages.error(request, "This project is closed and its tasks cannot be edited.")
            return redirect('task_detail', project_id=project.id, task_id=task.id)

        # Check if the task is completed
        if task.task_status == 3:  # Status ID 3 is "Completed"
            messages.error(request, "This task is completed and cannot be edited.")
            return redirect('task_detail', project_id=project.id, task_id=task.id)

        if request.method == 'GET':
            selected_skills = task.skills_required.values_list('pk', flat=True)
            if selected_skills:
                # Filter assets that have ALL the selected skills
                assets = Asset.objects.all()
                for skill_id in selected_skills:
                    assets = assets.filter(skills__pk=skill_id)
                filtered_assets_ids = list(assets.values_list('asset_id', flat=True).distinct())
                request.session['filtered_assets'] = filtered_assets_ids
            else:
                request.session['filtered_assets'] = []

        # Proceed with the regular dispatch if the project is not closed and the task is not completed
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Get filtered assets from session if available
        filtered_assets = self.request.session.get('filtered_assets', None)
        task = self.get_object()
        current_asset = task.assigned_to

        if filtered_assets:
            # Fetch assets based on filtered asset_ids
            assets_queryset = Asset.objects.filter(asset_id__in=filtered_assets)
            if current_asset:
                # Include the current assigned asset if it's not already in the filtered queryset
                if current_asset.asset_id not in filtered_assets:
                    assets_queryset = assets_queryset | Asset.objects.filter(asset_id=current_asset.asset_id)
            kwargs['assets_queryset'] = assets_queryset.distinct()
        else:
            if current_asset:
                # Only include the current assigned asset
                kwargs['assets_queryset'] = Asset.objects.filter(asset_id=current_asset.asset_id)
            else:
                # No assets to include
                kwargs['assets_queryset'] = Asset.objects.none()

        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Clear filtered_assets from session after successful form submission
        if 'filtered_assets' in self.request.session:
            del self.request.session['filtered_assets']
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse('task_detail', kwargs={'project_id': self.kwargs['project_id'], 'task_id': self.object.pk})

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'project_task_list.html'  # Generalized template for task lists
    context_object_name = 'tasks'

    def get_queryset(self):
        route_name = self.request.resolver_match.url_name

        if route_name == 'open_task_list':
            tasks = Task.objects.filter(task_status__in=[1, 2])
        elif route_name == 'completed_task_list':
            tasks = Task.objects.filter(task_status=3)
        elif route_name == 'unassigned_tasks':
            tasks = Task.objects.filter(task_status=1)
        elif 'project_id' in self.kwargs:
            project_id = self.kwargs.get('project_id')
            tasks = Task.objects.filter(project_id=project_id)
        else:
            tasks = Task.objects.all()

        # Use `annotate` to add a `can_be_completed` field to each task
        tasks = tasks.annotate(
            can_be_completed=Case(
                When(dependant_task__task_status=3, then=True),  # Completed dependant task
                When(dependant_task__isnull=True, then=True),    # No dependant task
                default=False,
                output_field=BooleanField()
            )
        )

        return tasks.order_by('-project__priority', '-priority', 'planned_start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determine the type of task list from the URL route name
        route_name = self.request.resolver_match.url_name

        if route_name == 'open_task_list':
            context['title'] = "Open Tasks Across All Projects"
        elif route_name == 'completed_task_list':
            context['title'] = "Completed Tasks Across All Projects"
        elif route_name == 'unassigned_tasks':
            context['title'] = "Unassigned Tasks Across All Projects"
        elif 'project_id' in self.kwargs:
            # If viewing tasks for a specific project
            context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
            context['title'] = f"Tasks for {context['project'].project_name}"
        else:
            context['title'] = "All Tasks"

        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'project_task_detail.html'
    context_object_name = 'task'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        task_id = self.kwargs.get('task_id')
        return get_object_or_404(Task, id=task_id, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the project instance to include in the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Task)

        # Filter comments by the content_type and object_id (task id)
        comments = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)

        # Add project and comments to the context
        context['project'] = project
        context['comments'] = comments
        return context

class TaskCompleteView(PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = TaskCompleteForm
    template_name = 'project_task_complete.html'
    permission_required = 'application.change_task'

    def dispatch(self, request, *args, **kwargs):
        # Get the project and task objects
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        task = get_object_or_404(Task, id=self.kwargs['task_id'], project_id=project.id)

        # Check if the task is already completed
        if task.task_status == 3:  # Status ID 3 is 'Completed'
            messages.error(request, "This task has already been completed.")
            return redirect('task_detail', project_id=project.id, task_id=task.id)

        # Check if the project is closed
        if project.project_status == 7:  # Status ID 7 is 'Closed'
            messages.error(request, "This project is closed and tasks cannot be completed.")
            return redirect('task_detail', project_id=project.id, task_id=task.id)

        # Check if the task has dependencies that are not complete
        if task.dependant_task and task.dependant_task.task_status != 3:  # Status ID 3 is 'Completed'
            messages.error(request, "This task has dependencies that are not yet completed.")
            return redirect('task_detail', project_id=project.id, task_id=task.id)

        # Proceed with the regular dispatch if all conditions are met
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        task_id = self.kwargs.get('task_id')
        return get_object_or_404(Task, id=task_id, project_id=project_id)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to complete this task.")
        return redirect('project_taskview', project_id=self.kwargs['project_id'])

    def form_valid(self, form):
        task = form.save(commit=False)
        task.task_status = 3  # Set status to 'Completed'
        task.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the project and add it to the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        context['project'] = project
        return context

    def get_success_url(self):
        return reverse('task_detail', kwargs={'project_id': self.kwargs['project_id'], 'task_id': self.kwargs['task_id']})


# Views for listing Risks, Assumptions, Issues, and Dependencies

class RiskListView(LoginRequiredMixin, ListView):
    model = Risk
    template_name = 'project_risks_list.html'
    context_object_name = 'risks'  # Updated context name to refer to the risks list

    def get_queryset(self):
        # Get tasks related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Risk.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the project and its associated risks to the context
        context['project'] = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        return context
    
class AssumptionListView(LoginRequiredMixin, ListView):
    model = Assumption
    template_name = 'project_assumptions_list.html'
    context_object_name = 'assumptions'  # Updated context name to refer to the assumption list

    def get_queryset(self):
        # Get tasks related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Assumption.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the project and its associated risks to the context
        context['project'] = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        return context

class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'project_issues_list.html'
    context_object_name = 'issues'  # Updated context name to refer to the issues list

    def get_queryset(self):
        # Get tasks related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Issue.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the project and its associated risks to the context
        context['project'] = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        return context

class DependencyListView(LoginRequiredMixin, ListView):
    model = Dependency
    template_name = 'project_dependencies_list.html'
    context_object_name = 'dependencies'  # Updated context name to refer to the dependencies list

    def get_queryset(self):
        # Get tasks related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Dependency.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the project and its associated risks to the context
        context['project'] = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        return context
    
class StakeholderListView(LoginRequiredMixin, ListView):
    model = Stakeholder
    template_name = 'project_stakeholders_list.html'
    context_object_name = 'stakeholders'

    def get_queryset(self):
        # Get stakeholders related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Stakeholder.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        
        # Fetch the project object using the project_id
        project = get_object_or_404(Project, id=project_id)
        
        # Get all stakeholders related to the project
        stakeholders = Stakeholder.objects.filter(project_id=project.id)

        # Collect emails from stakeholders who have a non-empty email field
        stakeholder_emails = [stakeholder.email for stakeholder in stakeholders if stakeholder.email]

        # Add project, stakeholders, and email list to the context
        context['project'] = project
        context['stakeholders'] = stakeholders
        context['stakeholder_emails'] = stakeholder_emails  # Pass the list of emails
        return context


# Create views for adding new entries

class RiskCreateView(PermissionRequiredMixin, CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'project_risk_add.html'
    permission_required = 'application.add_risk'  # Only allow users with 'add_risk' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a risk.")
        # Redirect to the project risk list view
        return redirect('risk_list', project_id=self.kwargs['project_id'])

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new risks cannot be added.")
            return redirect('risk_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Assign the project instance to the risk instance before saving
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.created_by = self.request.user  # Set the user who created this entry
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        # Redirect back to the project risk list view upon successful form submission
        return reverse_lazy('risk_list', kwargs={'project_id': self.kwargs['project_id']})

class AssumptionCreateView(PermissionRequiredMixin, CreateView):
    model = Assumption
    form_class = AssumptionForm
    template_name = 'project_assumption_add.html'
    permission_required = 'application.add_assumption'  # Only allow users with 'add_assumption' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create an assumption.")
        # Redirect to the project risk list view
        return redirect('assumption_list', project_id=self.kwargs['project_id'])

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new assumptions cannot be added.")
            return redirect('assumption_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Assign the project instance to the assumption instance before saving
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.created_by = self.request.user  # Set the user who created this entry
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        # Redirect back to the project assumption list view upon successful form submission
        return reverse_lazy('assumption_list', kwargs={'project_id': self.kwargs['project_id']})

class IssueCreateView(PermissionRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_issue_add.html'
    permission_required = 'application.add_issue'  # Only allow users with 'add_issue' permission
    
    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create an issue.")
        # Redirect to the project risk list view
        return redirect('issue_list', project_id=self.kwargs['project_id'])
    
    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new issues cannot be added.")
            return redirect('issue_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('issue_list', kwargs={'project_id': self.kwargs['project_id']})

class DependencyCreateView(PermissionRequiredMixin, CreateView):
    model = Dependency
    form_class = DependencyForm
    template_name = 'project_dependency_add.html'
    permission_required = 'application.add_dependency'  # Only allow users with 'add_dependency' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a dependency.")
        # Redirect to the project risk list view
        return redirect('dependency_list', project_id=self.kwargs['project_id'])

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new dependencies cannot be added.")
            return redirect('dependency_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('dependency_list', kwargs={'project_id': self.kwargs['project_id']})
    
class StakeholderCreateView(PermissionRequiredMixin, CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'project_stakeholder_add.html'
    permission_required = 'application.add_stakeholder'  # Only allow users with 'add_stakeholder' permission

    def handle_no_permission(self):
        # Add a custom error message
        messages.error(self.request, "You do not have permission to create a stakeholder.")
        # Redirect to the project risk list view
        return redirect('stakeholder_list', project_id=self.kwargs['project_id'])

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and new stakeholders cannot be added.")
            return redirect('stakeholder_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('stakeholder_list', kwargs={'project_id': self.kwargs['project_id']})


# Update views for editing existing entries

class RiskUpdateView(LoginRequiredMixin, UpdateView):
    model = Risk
    form_class = RiskForm
    template_name = 'project_risk_add.html'
    context_object_name = 'risk'

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and risks cannot be edited.")
            return redirect('risk_detail', project_id=project.id, risk_id=self.kwargs['risk_id'])

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        # Use project_id and risk_id to get the risk object
        project_id = self.kwargs.get('project_id')
        risk_id = self.kwargs.get('risk_id')
        return get_object_or_404(Risk, id=risk_id, project_id=project_id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse('risk_detail', kwargs={'project_id': self.kwargs['project_id'], 'risk_id': self.object.pk})

class AssumptionUpdateView(LoginRequiredMixin, UpdateView):
    model = Assumption
    form_class = AssumptionForm
    template_name = 'project_assumption_add.html'  # Reusing the existing template

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and assumptions cannot be edited.")
            return redirect('assumption_detail', project_id=project.id, assumption_id=self.kwargs['assumption_id'])

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        # Use project_id and risk_id to get the risk object
        project_id = self.kwargs.get('project_id')
        assumption_id = self.kwargs.get('assumption_id')
        return get_object_or_404(Assumption, id=assumption_id, project_id=project_id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('assumption_list', kwargs={'project_id': self.kwargs['project_id']})

class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_issue_add.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and issues cannot be edited.")
            return redirect('issue_detail', project_id=project.id, issue_id=self.kwargs['issue_id'])

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        # Use project_id and risk_id to get the risk object
        project_id = self.kwargs.get('project_id')
        issue_id = self.kwargs.get('issue_id')
        return get_object_or_404(Issue, id=issue_id, project_id=project_id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('issue_list', kwargs={'project_id': self.kwargs['project_id']})

class DependencyUpdateView(LoginRequiredMixin, UpdateView):
    model = Dependency
    form_class = DependencyForm
    template_name = 'project_dependency_add.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and dependencies cannot be edited.")
            return redirect('dependency_detail', project_id=project.id, dependency_id=self.kwargs['dependency_id'])

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        # Use project_id and risk_id to get the risk object
        project_id = self.kwargs.get('project_id')
        dependency_id = self.kwargs.get('dependency_id')
        return get_object_or_404(Dependency, id=dependency_id, project_id=project_id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('dependency_list', kwargs={'project_id': self.kwargs['project_id']})

class StakeholderUpdateView(LoginRequiredMixin, UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'project_stakeholder_add.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the project object
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        # Check if the project is closed
        if project.project_status == 7:
            messages.error(request, "This project is closed and stakeholders cannot be edited.")
            return redirect('stakeholder_list', project_id=project.id)

        # Proceed with the regular dispatch if the project is not closed
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        # Use project_id and risk_id to get the risk object
        project_id = self.kwargs.get('project_id')
        stakeholder_id = self.kwargs.get('stakeholder_id')
        return get_object_or_404(Stakeholder, id=stakeholder_id, project_id=project_id)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('stakeholder_list', kwargs={'project_id': self.kwargs['project_id']})


# Detail Views

class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    template_name = 'project_risk_detail.html'
    context_object_name = 'risk'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        risk_id = self.kwargs.get('risk_id')
        return get_object_or_404(Risk, id=risk_id, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the project instance to include in the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Risk)

        # Filter comments by the content_type and object_id (task id)
        comments = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)

        # Add project and comments to the context
        context['project'] = project
        context['comments'] = comments
        return context

class AssumptionDetailView(LoginRequiredMixin, DetailView):
    model = Assumption
    template_name = 'project_assumption_detail.html'
    context_object_name = 'assumption'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        assumption_id = self.kwargs.get('assumption_id')
        return get_object_or_404(Assumption, id=assumption_id, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the project instance to include in the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Assumption)

        # Filter comments by the content_type and object_id (task id)
        comments = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)

        # Add project and comments to the context
        context['project'] = project
        context['comments'] = comments
        return context

class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'project_issue_detail.html'
    context_object_name = 'issue'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        issue_id = self.kwargs.get('issue_id')
        return get_object_or_404(Issue, id=issue_id, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the project instance to include in the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Issue)

        # Filter comments by the content_type and object_id (task id)
        comments = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)

        # Add project and comments to the context
        context['project'] = project
        context['comments'] = comments
        return context

class DependencyDetailView(LoginRequiredMixin, DetailView):
    model = Dependency
    template_name = 'project_dependency_detail.html'
    context_object_name = 'dependency'

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        dependency_id = self.kwargs.get('dependency_id')
        return get_object_or_404(Dependency, id=dependency_id, project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the project instance to include in the context
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        
        # Get the ContentType instance for the Task model
        task_content_type = ContentType.objects.get_for_model(Dependency)

        # Filter comments by the content_type and object_id (task id)
        comments = Comment.objects.filter(content_type=task_content_type, object_id=self.object.pk)

        # Add project and comments to the context
        context['project'] = project
        context['comments'] = comments
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

def extract_pdf_text(file_path):
    try:
        text = extract_text(file_path)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

class ProjectTaskCalendarView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_task_calendar.html'

    def get_object(self):
        # Retrieve the project object using project_id instead of pk
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Project, id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # Filter tasks for the current project
        tasks = Task.objects.filter(project=project)

        # Prepare task data for FullCalendar
        task_events = []
        colors = {
            1: '#0000FF',  # Low (Blue)
            2: '#008000',  # Medium (Green)
            3: '#FFFF00',  # High (Yellow)
            4: '#FFA500',  # Critical (Orange)
            5: '#FF0000',  # Urgent (Red)
        }
        
        # Define corresponding text colors for each background color
        text_colors = {
            1: '#FFFFFF',  # White for Low (Blue)
            2: '#FFFFFF',  # White for Medium (Green)
            3: '#000000',  # Black for High (Yellow)
            4: '#000000',  # Black for Critical (Orange)
            5: '#FFFFFF',  # White for Urgent (Red)
        }

        for task in tasks:
            # Determine start and end dates
            start_date = task.actual_start_date or task.planned_start_date
            end_date = task.actual_end_date or task.planned_end_date

            # Set color and title for completed tasks
            if task.task_status == 3:  # Assuming status ID 3 means 'Completed'
                background_color = '#808080'  # Grey
                text_color = '#FFFFFF'  # White text for completed tasks
                task_title = f'{task.task_name} (Completed)'  # Add '(Complete)' to the task name
            else:
                # Use the priority color or fallback to grey
                background_color = colors.get(task.priority, '#808080')
                text_color = text_colors.get(task.priority, '#000000')  # Default text color to black if not defined
                task_title = task.task_name

            if start_date and end_date:
                task_events.append({
                    'title': task_title,
                    'start': str(start_date),
                    'end': str(end_date + timedelta(days=1)),  # FullCalendar uses exclusive end dates
                    'backgroundColor': background_color,
                    'borderColor': background_color,
                    'textColor': text_color,
                    'url': reverse('task_detail', kwargs={'project_id': project.pk, 'task_id': task.pk}),
                })

            # Add a separate event for the due date if it exists, but only if the task is not completed
            if task.due_date and task.task_status != 3:
                task_events.append({
                    'title': f'{task.task_name} (Due)',
                    'start': str(task.due_date),
                    'end': str(task.due_date),
                    'backgroundColor': '#FF6347',  # Tomato color for due date
                    'borderColor': '#FF6347',
                    'textColor': '#000000',  # Black text for due dates
                    'url': reverse('task_detail', kwargs={'project_id': project.pk, 'task_id': task.pk}),
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
    
class AttachmentListView(LoginRequiredMixin, ListView):
    model = Attachment
    template_name = 'project_attachments_list.html'
    context_object_name = 'attachments'

    def get_queryset(self):
        # Get attachments related to the project using project_id
        project_id = self.kwargs.get('project_id')
        return Attachment.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        # Add the project instance to the context
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['project_id'])
        context['form'] = AttachmentForm()  # Include the form to handle new uploads
        return context

class AttachmentCreateView(LoginRequiredMixin, CreateView):
    model = Attachment
    form_class = AttachmentForm
    http_method_names = ['post']  # Only allow POST since Dropzone uploads files automatically

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        file = request.FILES.get('file')
        description = request.POST.get('description', 'No description provided')

        if file:
            # Corrected storage path to avoid double 'media/'
            folder_path = os.path.join(settings.MEDIA_ROOT, str(project.id))
            fs = FileSystemStorage(location=folder_path, base_url=f'{settings.MEDIA_URL}{project.id}/')
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            # Create the Attachment instance and save it
            attachment = Attachment(
                project=project,
                uploaded_by=request.user,
                file=os.path.join(str(project.id), filename),  # Save relative path from MEDIA_ROOT
                description=description,
                filename=file.name  # Save the filename properly here
            )
            attachment.save()

            return JsonResponse({'message': 'File uploaded successfully!', 'file_url': file_url, 'description': description}, status=200)
        else:
            return JsonResponse({'error': 'No file provided'}, status=400)

class AttachmentDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        attachment = get_object_or_404(Attachment, id=self.kwargs['attachment_id'], project_id=self.kwargs['project_id'])
        file_path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)

        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')

            # Set the header to `inline` to allow the browser to try to open the file
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

            return response
        else:
            messages.error(request, "The requested file does not exist.")
            return redirect('project_attachments', project_id=self.kwargs['project_id'])

class AttachmentPreviewView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        attachment = get_object_or_404(
            Attachment,
            id=self.kwargs['attachment_id'],
            project_id=self.kwargs['project_id']
        )
        file_path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)

        if os.path.exists(file_path):
            extension = os.path.splitext(attachment.file.name.lower())[1]

            handlers = {
                '.msg': self.handle_msg_file,
                '.docx': self.handle_docx_file,
                '.pdf': self.handle_pdf_file,
                '.txt': self.handle_txt_file,
            }

            handler = handlers.get(extension)
            if handler:
                return handler(file_path)
            else:
                return JsonResponse({'error': 'This file type is not supported for preview.'}, status=200)
        else:
            return JsonResponse({'error': 'File not found'}, status=404)

    def handle_msg_file(self, file_path):
        try:
            msg = extract_msg.Message(file_path)
            preview_data = {
                'type': 'email',
                'from': msg.sender,
                'to': msg.to,
                'subject': msg.subject,
                'has_attachments': len(msg.attachments) > 0,
                'body': msg.body[:500]  # First 500 characters of the body text
            }
            return JsonResponse(preview_data, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Could not parse email: {str(e)}'}, status=200)

    def handle_docx_file(self, file_path):
        try:
            text = docx2txt.process(file_path)
            preview_data = {
                'type': 'docx',
                'body': text[:500]  # First 500 characters of the document text
            }
            return JsonResponse(preview_data, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Could not parse document: {str(e)}'}, status=200)

    def handle_pdf_file(self, file_path):
        try:
            text = extract_pdf_text(file_path)
            preview_data = {
                'type': 'pdf',
                'body': text[:500]  # First 500 characters of the PDF text
            }
            return JsonResponse(preview_data, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Could not parse PDF: {str(e)}'}, status=200)

    def handle_txt_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            preview_data = {
                'type': 'txt',
                'body': text[:500]  # First 500 characters of the text file
            }
            return JsonResponse(preview_data, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Could not read text file: {str(e)}'}, status=200)

    def generate_pdf_thumbnail(self, attachment):
        # Existing code to generate PDF thumbnail
        # Ensure this method is also within the class and properly indented
        pass  # Replace with your actual implementation

class AssetListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of all assets.
    Includes aggregated stats for each asset such as project ownership, tasks assigned, and time spent.
    """
    model = Asset
    template_name = 'asset_list.html'  # Asset list view template
    context_object_name = 'assets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assets = Asset.objects.all()

        # Collecting stats for each asset
        asset_stats = []
        for asset in assets:
            # Number of projects owned by the asset
            projects_owned = Project.objects.filter(project_owner=asset).count()

            # Number of tasks assigned to the asset (including completed)
            tasks_assigned = Task.objects.filter(assigned_to=asset).count()

            # Completed tasks assigned to the asset
            completed_tasks = Task.objects.filter(assigned_to=asset, task_status=3)
            num_completed_tasks = completed_tasks.count()

            # Aggregating total time spent on completed tasks
            total_time_spent = sum(
                [task.actual_time_to_complete for task in completed_tasks if task.actual_time_to_complete],
                timedelta()
            )

            # Calculate average time per completed task
            avg_time_per_task = (
                total_time_spent / num_completed_tasks if num_completed_tasks > 0 else timedelta()
            )
            avg_time_per_task_hours = avg_time_per_task.total_seconds() / 3600 if num_completed_tasks > 0 else 0

            # Collect percentage of tasks assigned compared to all tasks
            total_tasks = Task.objects.count()
            percentage_of_tasks = (tasks_assigned / total_tasks * 100) if total_tasks > 0 else 0

            # Adding stats to list
            asset_stats.append({
                'asset': asset,
                'projects_owned': projects_owned,
                'tasks_assigned': tasks_assigned,
                'total_time_spent_hours': total_time_spent.total_seconds() / 3600 if total_time_spent else 0,
                'percentage_of_tasks': percentage_of_tasks,
                'avg_time_per_task_hours': avg_time_per_task_hours,
            })

        # Add asset stats to the context
        context['asset_stats'] = asset_stats
        return context

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.get_object()

        # Gathering additional context information
        projects_owned_queryset = Project.objects.filter(project_owner=asset).order_by('-priority')
        projects_owned_count = projects_owned_queryset.count()  # Count of projects owned

        # Separate open and closed projects owned by the asset
        projects_owned_open = projects_owned_queryset.exclude(project_status=7)  # Status 7 is 'Closed'
        projects_owned_closed = projects_owned_queryset.filter(project_status=7)

        projects_owned_open_count = projects_owned_open.count()
        projects_owned_closed_count = projects_owned_closed.count()

        # Gathering assigned tasks and sorting them as per the desired order
        assigned_tasks = Task.objects.filter(assigned_to=asset).order_by(
            '-project__priority',  # Project priority (descending)
            '-priority',           # Task priority (descending)
            'planned_start_date'   # Planned start date (ascending)
        )
        all_tasks_count = assigned_tasks.count()  # Count of tasks assigned to the asset
        completed_tasks = assigned_tasks.filter(task_status=3).count()
        incomplete_tasks = assigned_tasks.exclude(task_status=3).count()

        # Calculate total time spent and average time per task
        total_time_spent = sum(
            [task.actual_time_to_complete for task in assigned_tasks if task.actual_time_to_complete],
            timedelta()
        )
        total_time_spent_hours = total_time_spent.total_seconds() / 3600 if total_time_spent else 0

        average_time_per_task = (
            total_time_spent_hours / completed_tasks if completed_tasks > 0 else 0
        )

        # Adding the collected data to the context
        context['projects_owned'] = projects_owned_queryset  # Pass the sorted queryset for the table
        context['projects_owned_count'] = projects_owned_count  # Pass the count for stats
        context['projects_owned_open_count'] = projects_owned_open_count
        context['projects_owned_closed_count'] = projects_owned_closed_count
        context['assigned_tasks'] = assigned_tasks  # Pass sorted queryset for use in template
        context['all_tasks_count'] = all_tasks_count  # Updated to reflect all tasks
        context['completed_tasks'] = completed_tasks
        context['incomplete_tasks'] = incomplete_tasks
        context['total_time_spent_hours'] = round(total_time_spent_hours, 2)
        context['average_time_per_task'] = round(average_time_per_task, 2)

        return context

class SkillListView(LoginRequiredMixin, ListView):
    model = Skill
    template_name = 'skill_list.html'
    context_object_name = 'skill_assets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        skill_assets = []

        # Check for skills without assigned assets
        skills_without_assets_flag = False

        for skill in skills:
            assets_with_skill = Asset.objects.filter(skills=skill)
            skill_assets.append({
                'skill': skill,
                'assets': assets_with_skill,
            })

            # If no assets have this skill, set the flag to True
            if not assets_with_skill.exists():
                skills_without_assets_flag = True

        # Pass the collected data to the template context
        context['skill_assets'] = skill_assets
        context['skills_without_assets'] = skills_without_assets_flag  # Flag for the warning message

        return context

class SkillDetailView(LoginRequiredMixin, DetailView):
    model = Skill
    template_name = 'skill_detail.html'
    context_object_name = 'skill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill = self.get_object()

        # Get tasks that include this skill
        tasks_with_skill = Task.objects.filter(skills_required=skill)

        # Number of tasks using this skill
        tasks_with_skill_count = tasks_with_skill.count()

        # Get assets that have this skill
        assets_with_skill = Asset.objects.filter(skills=skill)

        # Calculate the total time spent on all tasks that require this skill
        total_time_spent = sum(
            [task.actual_time_to_complete for task in tasks_with_skill if task.actual_time_to_complete],
            timedelta()
        )
        total_time_spent_hours = total_time_spent.total_seconds() / 3600 if total_time_spent else 0

        # Calculate average time spent on tasks that use this skill
        average_time_per_task = (
            total_time_spent_hours / tasks_with_skill_count if tasks_with_skill_count > 0 else 0
        )

        # Add collected data to the context
        context['tasks_with_skill'] = tasks_with_skill  # Pass queryset to be used in template
        context['tasks_with_skill_count'] = tasks_with_skill_count  # Total number of tasks using the skill
        context['total_time_spent_hours'] = round(total_time_spent_hours, 2)
        context['average_time_per_task'] = round(average_time_per_task, 2)
        context['assets_with_skill'] = assets_with_skill  # Pass the assets queryset

        return context

@login_required
def filter_assets_by_skills(request):
    if request.method == 'GET':
        skill_ids = request.GET.getlist('skills[]')

        # If skill_ids is empty, return no assets and clear 'filtered_assets' in session
        if not skill_ids:
            request.session['filtered_assets'] = []
            return JsonResponse({'assets': []})

        # Filter assets that contain ALL the selected skills
        assets = Asset.objects.all()
        for skill_id in skill_ids:
            assets = assets.filter(skills__pk=skill_id)

        # Eliminate duplicates and prepare response data
        assets_list = [{'asset_id': asset.asset_id, 'name': asset.name} for asset in assets.distinct()]

        # Save the asset_ids to the session
        request.session['filtered_assets'] = [asset.asset_id for asset in assets.distinct()]

        return JsonResponse({'assets': assets_list})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
