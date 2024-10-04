from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectTaskView, TaskCreateView, TaskDetailView

urlpatterns = [
    # Unauthorised users URLS    
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, next_page='/'), name='login'),
    
    # Authorised users URLS
    path('', views.home, name='home'),  # Home page view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/add/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/taskview/', ProjectTaskView.as_view(), name='project_taskview'),
    path('projects/<int:pk>/task/add/', TaskCreateView.as_view(), name='task_create'),  # URL pattern for creating a new task
    path('projects/<int:project_pk>/task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),  # New URL pattern for task detail view
]