from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import ProjectListView, ProjectDetailView, ProjectCreateView

urlpatterns = [
    # Unauthorised users URLS    
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, next_page='/'), name='login'),
    
    # Authorised users URLS
    path('', views.home, name='home'),  # Home page view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/add/', ProjectCreateView.as_view(), name='project_create'),

]