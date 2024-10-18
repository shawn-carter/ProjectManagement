from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import ProjectCreateView, ProjectUpdateView, ProjectListView, ProjectDetailView, TaskCreateView, TaskUpdateView, TaskDetailView, TaskListView, TaskCompleteView, RiskCreateView, RiskUpdateView, RiskListView, RiskDetailView, AssumptionCreateView, AssumptionUpdateView, AssumptionListView, AssumptionDetailView, IssueCreateView, IssueUpdateView, IssueListView, IssueDetailView, DependencyCreateView, DependencyUpdateView, DependencyListView, DependencyDetailView, StakeholderCreateView, StakeholderUpdateView, StakeholderListView, ProjectTaskCalendarView, project_calendar, project_events, add_comment, ProjectCloseView, AttachmentListView, AttachmentCreateView, AttachmentDownloadView

urlpatterns = [
    ################################ Unauthorised users URLS ################################
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, next_page='/'), name='login'),  # Login page view

    ################################## Authorised users URLS ##################################
    # Home Page
    path('', views.home, name='home'),  # Home page view
    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Project Views
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List Projects
    path('projects/add/', ProjectCreateView.as_view(), name='project_create'),  # Create Project
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),  # Project Details
    path('projects/<int:project_id>/edit/', ProjectUpdateView.as_view(), name='project_edit'),  # Edit Project
    path('projects/<int:project_id>/close/', ProjectCloseView.as_view(), name='project_close'),  # Close Project
        
    # Project Task Views
    path('projects/<int:project_id>/tasks/', TaskListView.as_view(), name='project_taskview'),  # List Tasks for Project
    path('projects/<int:project_id>/tasks/add/', TaskCreateView.as_view(), name='task_create'),  # Create Task
    path('projects/<int:project_id>/tasks/<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),  # Task Details
    path('projects/<int:project_id>/tasks/<int:task_id>/edit/', TaskUpdateView.as_view(), name='task_edit'),  # Edit Task
    path('projects/<int:project_id>/tasks/<int:task_id>/complete/', TaskCompleteView.as_view(), name='task_complete'),  # Task Complete

    # Project Risk Views
    path('projects/<int:project_id>/risks/', RiskListView.as_view(), name='risk_list'), # List Risks for Project
    path('projects/<int:project_id>/risks/add/', RiskCreateView.as_view(), name='add_risk'), # Create Risk
    path('projects/<int:project_id>/risks/<int:risk_id>/', RiskDetailView.as_view(), name='risk_detail'), # Risk Details
    path('projects/<int:project_id>/risks/<int:risk_id>/edit/', RiskUpdateView.as_view(), name='edit_risk'), # Edit Risk
    # Do we want to close Risks?

    # Project Assumption Views
    path('projects/<int:project_id>/assumptions/', AssumptionListView.as_view(), name='assumption_list'), # List Assumptions for Project
    path('projects/<int:project_id>/assumptions/add/', AssumptionCreateView.as_view(), name='add_assumption'), # Create Assumption
    path('projects/<int:project_id>/assumptions/<int:assumption_id>/', AssumptionDetailView.as_view(), name='assumption_detail'), # Assumption Details
    path('projects/<int:project_id>/assumptions/<int:assumption_id>/edit/', AssumptionUpdateView.as_view(), name='edit_assumption'), # Edit Assumption
    
    # Project Issue Views
    path('projects/<int:project_id>/issues/', IssueListView.as_view(), name='issue_list'), # List Issues for Project
    path('projects/<int:project_id>/issues/add/', IssueCreateView.as_view(), name='add_issue'), # Create Issue
    path('projects/<int:project_id>/issues/<int:issue_id>/', IssueDetailView.as_view(), name='issue_detail'), # Issue Details
    path('projects/<int:project_id>/issues/<int:issue_id>/edit/', IssueUpdateView.as_view(), name='edit_issue'), # Edit Issue
    # Do we want to close Issues?

    # Project Dependency Views
    path('projects/<int:project_id>/dependencies/', DependencyListView.as_view(), name='dependency_list'), # List Dependencies for Project
    path('projects/<int:project_id>/dependencies/add/', DependencyCreateView.as_view(), name='add_dependency'), # Create Dependency
    path('projects/<int:project_id>/dependencies/<int:dependency_id>/', DependencyDetailView.as_view(), name='dependency_detail'), # Dependency Details
    path('projects/<int:project_id>/dependencies/<int:dependency_id>/edit/', DependencyUpdateView.as_view(), name='edit_dependency'), # Edit Dependency

    # Project Stakeholder Views
    path('projects/<int:project_id>/stakeholders/', StakeholderListView.as_view(), name='stakeholder_list'), # List Stakeholders for Project
    path('projects/<int:project_id>/stakeholders/add/', StakeholderCreateView.as_view(), name='add_stakeholder'), # Create Stakeholder
    path('projects/<int:project_id>/stakeholders/<int:stakeholder_id>/edit/', StakeholderUpdateView.as_view(), name='edit_stakeholder'), # Edit Stakeholder
    #Do we need a Stakeholder Detail View?

    # Comments
    path('add_comment/<str:content_type>/<int:object_id>/', add_comment, name='add_comment'), # Add Comment to an Object

    # Calendar Stuff
    path('projects/events/', project_events, name='project_events'), # Endpoint to retrieve Project Events
    path('projects/calendar/', project_calendar, name='project_calendar'), # Projects Calendar (from Menu)
    path('projects/<int:project_id>/tasks/calendar/', ProjectTaskCalendarView.as_view(), name='project_task_calendar'), # Project Task Calendar
    
    # Attachments Views
    path('projects/<int:project_id>/attachments/', AttachmentListView.as_view(), name='attachment_list'),  # List Tasks for Project
    path('projects/<int:project_id>/attachments/add/', AttachmentCreateView.as_view(), name='add_attachment'),
    path('projects/<int:project_id>/attachments/<int:attachment_id>/download/', AttachmentDownloadView.as_view(), name='download_attachment'),
]