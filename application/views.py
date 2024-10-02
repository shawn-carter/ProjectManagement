from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import HttpResponse

# Home page view
@login_required  # Optional: Use this decorator if you want to restrict access to authenticated users only
def home(request):
    return render(request, 'home.html')

