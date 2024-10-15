import os
from django.core.asgi import get_asgi_application
from whitenoise import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_asgi_application()
application = ASGIStaticFilesHandler(application)