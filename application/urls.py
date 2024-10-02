from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Unauthorised users URLS    
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, next_page='/'), name='login'),
    
    # Authorised users URLS
    path('', views.home, name='home'),  # Home page view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]