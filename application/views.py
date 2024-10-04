from django.contrib.auth.decorators import login_required
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

class ProjectListView(ListView):
    model = Project  # Specify the model
    template_name = 'project_list.html'  # Specify the template to use
    context_object_name = 'projects'  # Name the context object to use in the template

    def get_queryset(self):
        # Return all active projects (excluding soft-deleted ones)
        return Project.objects.filter(deleted=None).order_by('project_name')
    
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)
        # Add the form to the context
        context['form'] = ProjectUpdateForm(instance=self.object)
        return context

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectUpdateForm
    template_name = 'project_detail.html'  # Reuse the same template
    context_object_name = 'project'

    def form_valid(self, form):
        form.save()
        return redirect(reverse('project_detail', kwargs={'pk': self.object.pk}))

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
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
    
class ProjectTaskView(DetailView):
    model = Project
    template_name = 'project_taskview.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # Get the context from the parent class
        context = super().get_context_data(**kwargs)
        # Add the list of tasks associated with the project to the context
        context['tasks'] = Task.objects.filter(project=self.object)
        return context
    
class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'

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

class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'

class ProjectSpecificListView(ListView):
    """Base view for listing project-related items."""
    template_name = 'project_specific_list.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

# Views for listing Risks, Assumptions, Issues, and Dependencies
class RiskListView(ProjectSpecificListView):
    model = Risk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['model_name_plural'] = 'risks'
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

class AssumptionListView(ProjectSpecificListView):
    model = Assumption

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['model_name_plural'] = 'assumptions'
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

class IssueListView(ProjectSpecificListView):
    model = Issue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['model_name_plural'] = 'issues'
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

class DependencyListView(ProjectSpecificListView):
    model = Dependency

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['model_name_plural'] = 'dependencies'
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

class StakeholderListView(ProjectSpecificListView):
    model = Stakeholder
    template_name = 'project_specific_list.html'  # Ensure the template path is correct

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['model_name_plural'] = 'stakeholders'
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

# Create views for adding new entries
class RiskCreateView(CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'risk_form.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('risk_list', kwargs={'pk': self.kwargs['pk']})

class AssumptionCreateView(CreateView):
    model = Assumption
    form_class = AssumptionForm
    template_name = 'assumption_form.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('assumption_list', kwargs={'pk': self.kwargs['pk']})

class IssueCreateView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'issue_form.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('assumption_list', kwargs={'pk': self.kwargs['pk']})

class DependencyCreateView(CreateView):
    model = Dependency
    form_class = DependencyForm
    template_name = 'dependency_form.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dependency_list', kwargs={'pk': self.kwargs['pk']})
    
class StakeholderCreateView(CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholder_form.html'

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('stakeholder_list', kwargs={'pk': self.kwargs['pk']})