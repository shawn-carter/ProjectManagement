from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectTaskView, TaskCreateView, TaskDetailView, RiskListView, RiskCreateView, AssumptionListView, AssumptionCreateView, IssueListView, IssueCreateView, DependencyListView, DependencyCreateView, StakeholderListView, StakeholderCreateView

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
    path('projects/<int:pk>/tasklist/', ProjectTaskView.as_view(), name='project_taskview'),
    path('projects/<int:pk>/task/add/', TaskCreateView.as_view(), name='task_create'),  # URL pattern for creating a new task
    path('projects/<int:project_pk>/task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),  # New URL pattern for task detail view
    
    # Project Stuff
    path('projects/<int:pk>/risks/', RiskListView.as_view(), name='risk_list'),
    path('projects/<int:pk>/risks/add/', RiskCreateView.as_view(), name='add_risk'),
    path('projects/<int:pk>/assumptions/', AssumptionListView.as_view(), name='assumption_list'),
    path('projects/<int:pk>/assumptions/add/', AssumptionCreateView.as_view(), name='add_assumption'),
    path('projects/<int:pk>/issues/', IssueListView.as_view(), name='issue_list'),
    path('projects/<int:pk>/issues/add/', IssueCreateView.as_view(), name='add_issue'),
    path('projects/<int:pk>/dependencies/', DependencyListView.as_view(), name='dependency_list'),
    path('projects/<int:pk>/dependencies/add/', DependencyCreateView.as_view(), name='add_dependency'),
    path('projects/<int:pk>/stakeholders/', StakeholderListView.as_view(), name='stakeholder_list'),
    path('projects/<int:pk>/stakeholders/add/', StakeholderCreateView.as_view(), name='add_stakeholder'),
]