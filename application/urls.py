from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectTaskView, TaskCreateView, TaskDetailView, RiskListView, RiskCreateView, AssumptionListView, AssumptionCreateView, IssueListView, IssueCreateView, DependencyListView, DependencyCreateView, StakeholderListView, StakeholderCreateView, RiskUpdateView, AssumptionUpdateView, IssueUpdateView, DependencyUpdateView, StakeholderUpdateView, TaskUpdateView, project_calendar, project_events, ProjectTaskCalendarView, TaskCompleteView, add_comment, RiskDetailView, AssumptionDetailView, IssueDetailView, DependencyDetailView

urlpatterns = [
    # Unauthorised users URLS    
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, next_page='/'), name='login'),
    
    # Authorised users URLS
    path('', views.home, name='home'),  # Home page view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),  # Read-only detail view
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),  # Edit view
    path('projects/add/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/tasklist/', ProjectTaskView.as_view(), name='project_taskview'),
    path('projects/<int:pk>/task/add/', TaskCreateView.as_view(), name='task_create'),  # URL pattern for creating a new task
    path('projects/<int:project_pk>/task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),  # New URL pattern for task detail view
    path('projects/<int:project_pk>/task/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('projects/<int:project_pk>/task/<int:pk>/complete/', TaskCompleteView.as_view(), name='task_complete'),

    # Project Stuff
    path('projects/<int:pk>/risks/', RiskListView.as_view(), name='risk_list'),
    path('projects/<int:pk>/risks/add/', RiskCreateView.as_view(), name='add_risk'),
    path('projects/<int:pk>/risks/<int:risk_pk>/edit/', RiskUpdateView.as_view(), name='edit_risk'),
    path('projects/<int:project_pk>/risk/<int:pk>/', RiskDetailView.as_view(), name='risk_detail'),

    path('projects/<int:pk>/assumptions/', AssumptionListView.as_view(), name='assumption_list'),
    path('projects/<int:pk>/assumptions/add/', AssumptionCreateView.as_view(), name='add_assumption'),
    path('projects/<int:pk>/assumptions/<int:assumption_pk>/edit/', AssumptionUpdateView.as_view(), name='edit_assumption'),
    path('projects/<int:project_pk>/assumption/<int:pk>/', AssumptionDetailView.as_view(), name='assumption_detail'),

    path('projects/<int:pk>/issues/', IssueListView.as_view(), name='issue_list'),
    path('projects/<int:pk>/issues/add/', IssueCreateView.as_view(), name='add_issue'),
    path('projects/<int:pk>/issues/<int:issue_pk>/edit/', IssueUpdateView.as_view(), name='edit_issue'),
    path('projects/<int:project_pk>/issue/<int:pk>/', IssueDetailView.as_view(), name='issue_detail'),

    path('projects/<int:pk>/dependencies/', DependencyListView.as_view(), name='dependency_list'),
    path('projects/<int:pk>/dependencies/add/', DependencyCreateView.as_view(), name='add_dependency'),
    path('projects/<int:pk>/dependencies/<int:dependency_pk>/edit/', DependencyUpdateView.as_view(), name='edit_dependency'),
    path('projects/<int:project_pk>/dependency/<int:pk>/', DependencyDetailView.as_view(), name='dependency_detail'),

    path('projects/<int:pk>/stakeholders/', StakeholderListView.as_view(), name='stakeholder_list'),
    path('projects/<int:pk>/stakeholders/add/', StakeholderCreateView.as_view(), name='add_stakeholder'),
    path('projects/<int:pk>/stakeholders/<int:stakeholder_pk>/edit/', StakeholderUpdateView.as_view(), name='edit_stakeholder'),    

    # Calendar Stuff
    path('projects/calendar/', project_calendar, name='project_calendar'),
    path('projects/events/', project_events, name='project_events'),
    path('projects/<int:pk>/tasks/calendar/', ProjectTaskCalendarView.as_view(), name='project_task_calendar'),

    # Add Comment to any Object Type
    path('add_comment/<str:content_type>/<int:object_id>/', add_comment, name='add_comment'),
]