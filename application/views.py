from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView, DetailView,CreateView, UpdateView
from django.urls import reverse_lazy,reverse

from .models import Project, ProjectStatus, Task
from .forms import ProjectForm, ProjectUpdateForm, TaskForm

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

    def form_valid(self, form):
        # Automatically set the project context for the task
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.project = project
        return super().form_valid(form)

    def get_form_kwargs(self):
        # Pass the project instance to the form
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        # Ensure the project context is passed to the template
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Use self.kwargs['pk'] to ensure the correct project ID is used in the URL reversal
        return reverse('project_taskview', kwargs={'pk': self.kwargs['pk']})

class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'