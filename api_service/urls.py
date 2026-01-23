from django.urls import path
from .views import trigger_ai_run

urlpatterns = [
    path('run-ai/', trigger_ai_run, name='trigger_ai_run'),
]