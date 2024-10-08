from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView, DetailView,CreateView, UpdateView
from django.urls import reverse_lazy,reverse

from .models import Project, ProjectStatus, Task, Stakeholder, Risk, Issue, Assumption, Dependency
from .forms import ProjectForm, ProjectUpdateForm, TaskForm, StakeholderForm, RiskForm, IssueForm, AssumptionForm, DependencyForm

# Home page view
@login_required  # Optional: Use this decorator if you want to restrict access to authenticated users only
def home(request):
    return render(request, 'home.html')

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

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'  # New read-only detail view template
    context_object_name = 'project'

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = 'project_edit.html'  # Edit form template
    context_object_name = 'project'

    def form_valid(self, form):
        form.save()
        return redirect(reverse('project_detail', kwargs={'pk': self.object.pk}))


class ProjectCreateView(LoginRequiredMixin,CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('project_list')

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

class TaskCreateView(LoginRequiredMixin,CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'project_task_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the project instance to the form for context if needed
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        # Assign the project instance to the task instance before saving
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Add the project object to the context
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Redirect back to the project task view upon successful form submission
        return reverse('project_taskview', kwargs={'pk': self.kwargs['pk']})

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'project_task_edit.html'  # Create this new template based on project_task_create.html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the project information to the template
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context

    def get_success_url(self):
        # Redirect back to the project task list upon successful form submission
        return reverse('project_taskview', kwargs={'pk': self.kwargs['project_pk']})

class TaskDetailView(LoginRequiredMixin,DetailView):
    model = Task
    template_name = 'project_task_detail.html'
    context_object_name = 'task'

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
    
class StakeholderListView(ListView):
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
    
class StakeholderCreateView(CreateView):
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
    
class RiskUpdateView(UpdateView):
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

# Assumption Update View
class AssumptionUpdateView(UpdateView):
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


# Similar update views for Issue, Dependency, and Stakeholder
class IssueUpdateView(UpdateView):
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


class DependencyUpdateView(UpdateView):
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


class StakeholderUpdateView(UpdateView):
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